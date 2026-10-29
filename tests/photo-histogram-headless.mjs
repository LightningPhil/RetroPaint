import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/photo-histogram')),origin=option('--origin','http://127.0.0.1:8093/');
await fs.mkdir(out,{recursive:true});
if(await fs.access(path.join(out,'PHOTO-017-headless-ui.json')).then(()=>true,()=>false))throw new Error('Choose a new output folder; previous evidence is retained here.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,out);
const report={started:new Date().toISOString(),origin,execution:'Isolated headless UI; real controls and actual downloads',rows:[],errors:[]};page.on('pageerror',error=>report.errors.push(String(error)));
let tonalFile;
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();
 for(const name of ['tonal-ramp','nearly-black','nearly-white','clear-half','empty','rgb-flat']){
  console.log('HIST '+name);await driver.open(path.join(root,'fixtures',name==='tonal-ramp'?'TONAL.png':'HIST-'+name+'.png'));await driver.download(name+'-before');await driver.photo();await driver.snapshot(name+'-histogram');await driver.canvas('#photoHistogram',name+'-histogram');
  const row={name,states:[{state:'original',label:await page.locator('#photoHistogram').getAttribute('aria-label')}]};
  if(name==='rgb-flat'||name==='tonal-ramp'){
   await driver.group('light','light-basic');await driver.slider('Exposure',1);await driver.ready();await driver.canvas('#photoHistogram',name+'-after');row.states.push({state:'exposure-1',label:await page.locator('#photoHistogram').getAttribute('aria-label')});
   await page.locator('#photoCompare').click();await driver.canvas('#photoHistogram',name+'-before-comparison');row.states.push({state:'before',label:await page.locator('#photoHistogram').getAttribute('aria-label')});
   await page.locator('#photoCompare').click();await driver.canvas('#photoHistogram',name+'-after-comparison');row.states.push({state:'after',label:await page.locator('#photoHistogram').getAttribute('aria-label')});
  }
  await page.locator('#photoCancel').click();await driver.download(name+'-cancelled');await driver.download(name+'-cancelled','png');
  if(name==='tonal-ramp'){
   await driver.photo();await driver.group('light','light-basic');await driver.slider('Exposure',1);await driver.ready();row.full_export_preview_label=await page.locator('#photoHistogram').getAttribute('aria-label');await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});tonalFile=await driver.download(name+'-exposure-1');await driver.download(name+'-exposure-1','png');
   await page.locator('#undoBtn').click();await driver.download(name+'-undone');await driver.download(name+'-undone','png');
   await page.locator('#view').press('Control+Shift+z');await driver.download(name+'-redone');await driver.download(name+'-redone','png');
  }
  report.rows.push(row);console.log(JSON.stringify(row));
 }
 const freshOut=path.join(out,'fresh');await fs.mkdir(freshOut,{recursive:true});
 const freshContext=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),freshPage=await freshContext.newPage(),freshDriver=new AcceptanceDriver(freshPage,freshOut);
 freshPage.on('pageerror',error=>report.errors.push(String(error)));await freshPage.goto(origin,{waitUntil:'domcontentloaded'});await freshDriver.open(tonalFile,'project');await freshDriver.download('tonal-ramp-reopened');await freshDriver.download('tonal-ramp-reopened','png');await freshDriver.snapshot('tonal-ramp-reopened');await freshContext.close();report.fresh_reopen_complete=true;
 const bad=report.rows.filter(row=>!row.states[0].label.includes(row.name==='tonal-ramp'?'1% shadow clipping; 1% highlight clipping.':'0% shadow clipping; 0% highlight clipping.'));
 report.status=bad.length||report.errors.length?'Fail':'Pass';report.unexpected_original_clipping=bad.map(row=>row.name);
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'PHOTO-017-headless-ui.json'),JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();if(report.status==='Fail')process.exitCode=1;console.log('HIST '+report.status);}
