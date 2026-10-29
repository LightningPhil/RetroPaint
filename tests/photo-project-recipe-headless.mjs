import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/photo-project-recipe')),origin=option('--origin','http://127.0.0.1:8094/');
await fs.mkdir(out,{recursive:true});const reportFile=path.join(out,'PHOTO-019-headless-ui.json');if(await fs.access(reportFile).then(()=>true,()=>false))throw new Error('Previous evidence retained; choose a new folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Isolated headless UI; actual file input, controls and downloads',rows:[],errors:[]};
let context,page,driver;
const start=async()=>{const events=driver?.events??[];context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));driver=new AcceptanceDriver(page,out);driver.events=events;await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();};
const pair=async label=>{console.log('SAVE '+label);const file=await driver.download(label);await driver.download(label,'png');return file;};
const done=async label=>{await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});return pair(label);};
try{
 let fixture=option('--fixture',null);
 if(!fixture){
 await start();await driver.open(path.join(root,'headless/PHOTO-015-complete/baseline.retropaint'),'project');await driver.photo();await driver.group('geometry','geometry-crop');
 for(const [key,value] of [['width',3400],['height',2100],['x',120],['y',90]]){const field=page.locator('#photoCrop-'+key);await field.fill(String(value));await field.press('Tab');await driver.ready();}
 await page.locator('#photoLook').selectOption('warm');await driver.ready();await driver.snapshot('saved-cropped-look');fixture=await done('look-cropped');await context.close();
 }else{fixture=path.resolve(fixture);report.external_setup_fixture=fixture;}
 // A genuine new browser context has no recipe/cache from setup.
 await start();await driver.open(fixture,'project');await pair('fresh-cropped');await driver.photo();assert.equal(await page.locator('#photoLook').inputValue(),'warm');await driver.group('geometry','geometry-crop');
 const crop={};for(const key of ['x','y','width','height'])crop[key]=Number(await page.locator('#photoCrop-'+key).inputValue());assert.deepEqual(crop,{x:120,y:90,width:3400,height:2100});await driver.record({action:'fresh-crop-fields',crop});await driver.snapshot('fresh-cropped-recipe');
 await page.locator('#photoLook').selectOption('normal');await driver.ready();await driver.snapshot('normal-cropped-draft');await done('normal-cropped');
 await driver.photo();await driver.group('geometry','geometry-crop');await page.locator('#photoCropReset').click();await driver.ready();const whole=await done('whole-restored');
 await page.locator('#undoBtn').click();await pair('whole-undone');await page.locator('#view').press('Control+Shift+z');await pair('whole-redone');
 const source=JSON.parse(await fs.readFile(fixture,'utf8'));
 for(const kind of ['numeric','curve','look']){
  const corrupt=structuredClone(source);let expected;
  if(kind==='numeric'){corrupt.layers[0].photo.settings.exposure='1';expected='Invalid photo adjustment value.';}
  if(kind==='curve'){corrupt.layers[0].photo.settings.curves.red=[{x:0,y:0},{x:.8,y:.5},{x:.5,y:.6},{x:1,y:1}];expected='Photo curve points must be ordered.';}
  if(kind==='look'){corrupt.layers[0].photo.look='unrecognised-look';expected='Invalid photo look.';}
  const filename=path.join(out,'invalid-'+kind+'.retropaint'),bytes=Buffer.from(JSON.stringify(corrupt));await fs.writeFile(filename,bytes,{flag:'wx'});await driver.record({action:'negative-fixture-from-actual-download',kind,path:filename,sha256:createHash('sha256').update(bytes).digest('hex')});
  await driver.drawer();const pending=page.waitForEvent('filechooser');await page.getByRole('button',{name:'Open project',exact:true}).click();await(await pending).setFiles(filename);await page.locator('#editorStatus').getByText(expected,{exact:true}).waitFor();await driver.record({action:'actual-rejection',kind,expected});await driver.snapshot('rejected-'+kind);await driver.close();await pair('rejected-'+kind);
  await driver.open(whole,'project');await driver.download('valid-retry-'+kind);report.rows.push({kind,expected,retry_complete:true});
 }
 await context.close();await start();await driver.open(whole,'project');await pair('final-reopened');await driver.snapshot('final-reopened');report.fresh_reopen_complete=true;report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver?.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(reportFile,JSON.stringify(report,null,2)+'\n');await context?.close();await browser.close();console.log('PHOTO-019 '+report.status);if(report.status!=='Pass')process.exitCode=1;}
