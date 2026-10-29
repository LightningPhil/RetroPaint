import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';

const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/photo-looks')),origin=option('--origin','http://127.0.0.1:8094/'),phase=option('--phase','looks');
assert(['looks','custom'].includes(phase));await fs.mkdir(out,{recursive:true});
const reportFile=path.join(out,'PHOTO-looks-headless-ui.json');
if(await fs.access(reportFile).then(()=>true,()=>false))throw new Error('Choose a new folder; previous evidence is retained.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,out);
const report={started:new Date().toISOString(),origin,phase,execution:'Isolated headless production UI; actual controls, public preview pixels and real downloads',rows:[],errors:[]};page.on('pageerror',e=>report.errors.push(String(e)));
const look=async value=>{await page.locator('#photoLook').selectOption(value);await driver.ready();assert.equal(await page.locator('#photoLook').inputValue(),value);await driver.record({action:'choose-look',value});};
const done=async label=>{await page.locator('#photoApply').click();await page.locator('#photoPanel').waitFor({state:'hidden'});console.log('SAVE '+label);const file=await driver.download(label);await driver.download(label,'png');return file;};
const pair=async label=>{const file=await driver.download(label);await driver.download(label,'png');return file;};
const preview=async label=>{await driver.group('light','light-basic');await driver.ready();await driver.canvas('#photoMiniCanvas',label+'-preview');await driver.snapshot(label);};
const navigation=async expected=>{for(const category of ['light','colour','curves','detail','effects','geometry']){await driver.group(category);assert.equal(await page.locator('#photoLook').inputValue(),expected,'Category navigation changed the look');}await driver.group('light','light-basic');await driver.record({action:'category-navigation',expected,categories:['light','colour','curves','detail','effects','geometry']});};
let reopenFile;
try{
 await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();
 if(phase==='looks'){
  await driver.open(path.join(root,'evidence/PHOTO-004-saved-before.retropaint'),'project');
  await driver.photo();await driver.group('light','light-basic');await driver.slider('Brightness',17);await driver.ready();
  await driver.group('colour','colour-balance');await driver.slider('Temperature · cool / warm',-12);await driver.ready();
  await driver.group('curves');await page.locator('#photoCurveChannel').selectOption('red');await page.locator('#photoCurvePreset').selectOption('shadows');await driver.ready();
  await look('normal');await preview('baseline');await done('baseline');
  for(const value of ['natural','punch','mono','warm','cool']){
   console.log('LOOK forward '+value);await driver.photo();await look(value);await navigation(value);await preview('forward-'+value);await done('forward-'+value);report.rows.push({order:'forward',value,committed:true});
  }
  await driver.photo();
  for(const value of ['cool','warm','mono','punch','natural']){console.log('LOOK reverse '+value);await look(value);await navigation(value);await preview('reverse-'+value);report.rows.push({order:'reverse',value,committed:false});}
  // Cancel a switch: the previously committed Cool recipe must survive intact.
  await page.locator('#photoCancel').click();await pair('reverse-cancelled');
  await driver.photo();await look('normal');await preview('normal-restored');reopenFile=await done('normal-restored');
  await page.locator('#undoBtn').click();await pair('normal-undone');
  await page.locator('#view').press('Control+Shift+z');await pair('normal-redone');
 }else{
  const fixture=path.resolve(option('--baseline',path.join(root,'headless/PHOTO-015-complete/baseline.retropaint')));await driver.open(fixture,'project');await pair('custom-baseline');
  for(const [index,variant] of ['slider','curve','crop','automatic'].entries()){
   const preset=['natural','punch','warm','cool'][index];console.log('CUSTOM '+variant+' from '+preset);await driver.photo();await look(preset);await navigation(preset);await preview(variant+'-preset');
   if(variant==='slider'){await driver.slider('Brightness',22);}
   if(variant==='curve'){await driver.group('curves');await page.locator('#photoCurveChannel').selectOption('green');await page.locator('#photoCurvePreset').selectOption('fade');}
   if(variant==='crop'){
    await driver.group('geometry','geometry-crop');
    for(const [key,value] of [['width',3400],['height',2100],['x',120],['y',90]]){const field=page.locator('#photoCrop-'+key);await field.fill(String(value));await field.press('Tab');await driver.ready();}
    await driver.group('light','light-basic');await driver.group('geometry','geometry-crop');
    const values={};for(const key of ['x','y','width','height'])values[key]=Number(await page.locator('#photoCrop-'+key).inputValue());assert.deepEqual(values,{x:120,y:90,width:3400,height:2100});await driver.record({action:'verified-crop-fields',values});
   }
   if(variant==='automatic'){await driver.group('light','light-basic');await page.locator('#photoAuto').click();}
   await driver.ready();assert.equal(await page.locator('#photoLook').inputValue(),'custom');await preview(variant+'-custom');
   await done(variant+'-custom');
   // A committed adjustment supports one-step Undo and Redo.
   await page.locator('#undoBtn').click();await pair(variant+'-undone');await page.locator('#view').press('Control+Shift+z');await pair(variant+'-redone');
   // Normal must still restore the original manual baseline after commit/reopen.
   await driver.photo();assert.equal(await page.locator('#photoLook').inputValue(),'custom');await look('normal');await preview(variant+'-normal');reopenFile=await done(variant+'-normal');
   // A cancelled draft must preserve the complete restored baseline too.
   await driver.photo();await look(preset);await driver.group('light','light-basic');await driver.slider('Brightness',-21);await driver.ready();assert.equal(await page.locator('#photoLook').inputValue(),'custom');await page.locator('#photoCancel').click();await pair(variant+'-cancelled');
   report.rows.push({variant,preset,custom_indicated:true,category_navigation_preserved:true,undo_redo:true,normal_after_commit:true,cancelled_draft:true});
  }
 }
 const freshOut=path.join(out,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true}),p=await fresh.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));
 await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(reopenFile,'project');await d.download('reopened');await d.download('reopened','png');await d.snapshot('reopened');await fresh.close();report.fresh_reopen_complete=true;
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);await driver.snapshot('failure').catch(()=>{});}
finally{report.finished=new Date().toISOString();await fs.writeFile(reportFile,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log('PHOTO '+phase+' '+report.status);if(report.status!=='Pass')process.exitCode=1;}
