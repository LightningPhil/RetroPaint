import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/photo-fullsize')),origin=option('--origin','http://127.0.0.1:8094/');
await fs.mkdir(out,{recursive:true});const reportFile=path.join(out,'PHOTO-018-headless-ui.json');if(await fs.access(reportFile).then(()=>true,()=>false))throw new Error('Previous evidence retained; use a new folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,out),report={started:new Date().toISOString(),origin,execution:'Isolated headless UI; actual fine-detail/crop controls and full-size file downloads',errors:[]};page.on('pageerror',e=>report.errors.push(String(e)));
const pair=async label=>{console.log('SAVE '+label);const file=await driver.download(label);await driver.download(label,'png');return file;};
const done=async label=>{await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});return pair(label);};
const fine=async()=>{await driver.group('detail','detail-sharp');await driver.slider('Sharpness',80);await driver.slider('Threshold · protect smooth areas',5);await driver.ready();};
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();await driver.open(path.join(root,'headless/PHOTO-008-production-20261020/PHOTO-008-all-settings-reset-done.retropaint'),'project');await pair('before');
 await driver.photo();await fine();await driver.canvas('#photoMiniCanvas','fine-draft-preview');await driver.snapshot('fine-draft');await page.locator('#photoCancel').click();await pair('cancelled');
 await driver.photo();await fine();await done('fine-full');await page.locator('#undoBtn').click();await pair('fine-undone');await page.locator('#view').press('Control+Shift+z');await pair('fine-redone');
 await driver.photo();await driver.group('geometry','geometry-crop');for(const [key,value] of [['width',3400],['height',2100],['x',120],['y',90]]){const field=page.locator('#photoCrop-'+key);await field.fill(String(value));await field.press('Tab');await driver.ready();}await driver.snapshot('fine-cropped-draft');const cropped=await done('fine-cropped');
 await page.locator('#undoBtn').click();await pair('crop-undone');await page.locator('#view').press('Control+Shift+z');await pair('crop-redone');
 const freshOut=path.join(out,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),p=await fresh.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(cropped,'project');await d.download('reopened');await d.download('reopened','png');await d.snapshot('reopened');await fresh.close();report.fresh_reopen_complete=true;report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(reportFile,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('PHOTO-018 '+report.status);if(report.status!=='Pass')process.exitCode=1;}
