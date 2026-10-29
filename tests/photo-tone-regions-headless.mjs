import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/photo-tone-regions')),origin=option('--origin','http://127.0.0.1:8094/');
await fs.mkdir(out,{recursive:true});const reportFile=path.join(out,'PHOTO-tone-regions-ui.json');if(await fs.access(reportFile).then(()=>true,()=>false))throw new Error('Previous evidence retained; use a new output folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,out);
const report={started:new Date().toISOString(),origin,execution:'Isolated headless UI; actual input controls and downloaded project/PNG bytes',rows:[],errors:[]};page.on('pageerror',e=>report.errors.push(String(e)));
const pair=async label=>{console.log('SAVE '+label);const file=await driver.download(label);await driver.download(label,'png');return file;};
const done=async label=>{await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});return pair(label);};
let finalFile;
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();await driver.open(path.join(root,'fixtures/TONAL.png'));await pair('source');
 for(const key of ['Highlights','Shadows','Whites','Blacks'])for(const value of [-100,-30,0,30,100]){
  const label=key.toLowerCase()+'-'+(value<0?'minus'+(-value):value);console.log('TONE '+label);
  await driver.open(path.join(root,'fixtures/TONAL.png'));await driver.photo();await driver.group('light','light-tone');await driver.slider(key,value);await driver.ready();
  const row={key:key.toLowerCase(),value,label,histogram:await page.locator('#photoHistogram').getAttribute('aria-label'),controls:{}};
  for(const other of ['Highlights','Shadows','Whites','Blacks'])row.controls[other.toLowerCase()]=Number(await page.getByRole('slider',{name:other,exact:true}).inputValue());
  await driver.snapshot(label);await done(label);report.rows.push(row);
 }
 // Independent controls, group Reset, Cancel and history on one actual draft.
 await driver.open(path.join(root,'fixtures/TONAL.png'));await driver.photo();await driver.group('light','light-tone');
 for(const [key,value] of [['Highlights',-30],['Shadows',30],['Whites',30],['Blacks',-30]])await driver.slider(key,value);
 await driver.ready();await driver.snapshot('combined');await done('combined');
 await driver.photo();await driver.group('light','light-tone');await page.locator('#photoGroupReset').click();await driver.ready();
 for(const key of ['Highlights','Shadows','Whites','Blacks'])assert.equal(Number(await page.getByRole('slider',{name:key,exact:true}).inputValue()),0);
 await driver.snapshot('group-reset-draft');await page.locator('#photoCancel').click();await pair('reset-cancelled');
 await driver.photo();await driver.group('light','light-tone');await page.locator('#photoGroupReset').click();await driver.ready();finalFile=await done('reset-done');
 await page.locator('#undoBtn').click();await pair('reset-undone');await page.locator('#view').press('Control+Shift+z');await pair('reset-redone');
 const freshOut=path.join(out,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),p=await fresh.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(finalFile,'project');await d.download('reopened');await d.download('reopened','png');await d.snapshot('reopened');await fresh.close();report.fresh_reopen_complete=true;report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(reportFile,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('TONE '+report.status);if(report.status!=='Pass')process.exitCode=1;}
