import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/photo-auto')),origin=option('--origin','http://127.0.0.1:8094/');
await fs.mkdir(out,{recursive:true});const reportFile=path.join(out,'PHOTO-014-headless-ui.json');if(await fs.access(reportFile).then(()=>true,()=>false))throw new Error('Retained evidence exists; choose a new folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,out),report={started:new Date().toISOString(),origin,execution:'Isolated headless production UI; actual controls and downloads',rows:[],errors:[]};page.on('pageerror',e=>report.errors.push(String(e)));
const pair=async label=>{console.log('SAVE '+label);const file=await driver.download(label);await driver.download(label,'png');return file;};
const auto=async()=>{await driver.group('light','light-basic');await page.locator('#photoAuto').click();await driver.ready();};
const values=async()=>{const data={};for(const [category,group,keys] of [['light','light-basic',['Exposure','Contrast']],['light','light-tone',['Shadows','Highlights']],['colour','colour-basic',['Vibrance']]]){await driver.group(category,group);for(const key of keys)data[key.toLowerCase()]=Number(await page.getByRole('slider',{name:key,exact:true}).inputValue());}await driver.group('light','light-basic');return data;};
let finalFile;
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();
 for(const [name,file] of [['dark',path.join(root,'fixtures/AUTO-dark.png')],['bright',path.join(root,'fixtures/AUTO-bright.png')],['empty',path.join(root,'fixtures/HIST-empty.png')],['constant',path.join(root,'fixtures/HIST-rgb-flat.png')],['natural',path.resolve('Example_Images/Laukka sunset.jpg')]]){
  console.log('AUTO '+name);await driver.open(file);await pair(name+'-before');await driver.photo();const originalHistogram=await page.locator('#photoHistogram').getAttribute('aria-label');await auto();const first=await values();await driver.canvas('#photoMiniCanvas',name+'-auto-preview');await driver.snapshot(name+'-auto');
  await page.locator('#photoCompare').click();assert.equal(await page.locator('#photoCompare').getAttribute('aria-pressed'),'true');assert.equal(await page.locator('#photoHistogram').getAttribute('aria-label'),originalHistogram);await driver.snapshot(name+'-before-comparison');await page.locator('#photoCompare').click();await driver.canvas('#photoMiniCanvas',name+'-after-comparison');
  await page.locator('#photoReset').click();await driver.ready();await auto();const repeated=await values();assert.deepEqual(repeated,first);await driver.canvas('#photoMiniCanvas',name+'-repeated-preview');await driver.record({action:'automatic-settings',name,first,repeated});
  await page.locator('#photoCancel').click();await pair(name+'-cancelled');await driver.photo();await auto();await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});finalFile=await pair(name+'-done');
  await page.locator('#undoBtn').click();await pair(name+'-undone');await page.locator('#view').press('Control+Shift+z');await pair(name+'-redone');report.rows.push({name,file,first,repeated,before_histogram:originalHistogram});
 }
 const freshOut=path.join(out,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),p=await fresh.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(finalFile,'project');await d.download('reopened');await d.download('reopened','png');await d.snapshot('reopened');await fresh.close();report.fresh_reopen_complete=true;report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(reportFile,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('AUTO '+report.status);if(report.status!=='Pass')process.exitCode=1;}
