import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
import {controlledRenderClock} from './controlled-render-time.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/clear-mix')),origin=option('--origin','http://127.0.0.1:8094/');await fs.mkdir(out,{recursive:true});const file=path.join(out,'START-006-headless-ui.json');if(await fs.access(file).then(()=>true,()=>false))throw new Error('Choose a fresh output folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Actual Clear/Undo/Redo controls in isolated headless contexts. Age warning uses real elapsed121 seconds. Only completed-art render timestamps are fixed for exact animated-pixel comparisons.',rows:[],errors:[]};
try{
 for(const mode of ['immediate','aged']){
  console.log('CLEAR '+mode);const location=path.join(out,mode);await fs.mkdir(location,{recursive:true});const context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});await context.addInitScript(controlledRenderClock);const page=await context.newPage(),driver=new AcceptanceDriver(page,location);page.on('pageerror',e=>report.errors.push(String(e)));
  const pair=async(d,label)=>{console.log('CLEAR save '+mode+' '+label);const saved=await d.download(label);await d.download(label,'png');return saved;};
  const white=()=>page.waitForFunction(()=>{const c=document.querySelector('#view'),data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;for(const v of data)if(v!==255)return false;return true;});
  try{
   await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.open(path.join(root,'headless/MIX-final/MIX-enriched.retropaint'),'project');const loaded_wall=Date.now(),loaded_native=await page.evaluate(()=>performance.now());
   if(mode==='aged')while(Date.now()-loaded_wall<121000){console.log('CLEAR actual age '+Math.floor((Date.now()-loaded_wall)/1000)+'s');await page.waitForTimeout(Math.min(30000,121000-(Date.now()-loaded_wall)));}
   const before_wall=Date.now(),before_native=await page.evaluate(()=>performance.now()),render_time=Math.floor(before_native);assert(mode==='aged'?before_wall-loaded_wall>=121000:before_wall-loaded_wall<120000);
   await page.evaluate(value=>{window.__acceptanceRenderTime=value;},render_time);await pair(driver,'before');await driver.snapshot('before');
   // Real time resumes during the destructive animation; its completion is
   // measured through stable public output rather than skipped by fake time.
   await page.evaluate(()=>{window.__acceptanceRenderTime=null;});await page.locator('#clearBtn').click();
   if(mode==='aged'){await page.locator('#clearConfirmation[open]').waitFor();assert(await page.locator('#clearConfirmation .keep-picture').evaluate(e=>e===document.activeElement));await driver.snapshot('confirmation');await page.locator('#clearConfirmation .clear-picture').click();}
   else assert.equal(await page.locator('#clearConfirmation').getAttribute('open'),null);
   await white();await page.waitForTimeout(600);await white();await page.evaluate(value=>{window.__acceptanceRenderTime=value;},render_time);await pair(driver,'cleared');await driver.snapshot('cleared');
   await page.locator('#undoBtn').click();const restored=await pair(driver,'undone');await driver.snapshot('undone');await page.locator('#view').press('Control+Shift+z');await white();await pair(driver,'redone');
   const freshOut=path.join(location,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});await fresh.addInitScript(controlledRenderClock);await fresh.addInitScript(value=>{window.__acceptanceRenderTime=value;},render_time);const p=await fresh.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});await d.open(restored,'project');await pair(d,'restored-reopened');await d.snapshot('restored-reopened');await fresh.close();
   report.rows.push({mode,loaded_wall_ms:loaded_wall,before_wall_ms:before_wall,real_elapsed_ms:before_wall-loaded_wall,loaded_native_ms:loaded_native,before_native_ms:before_native,native_elapsed_ms:before_native-loaded_native,render_time_ms:render_time,confirmation_shown:mode==='aged',undo_redo_complete:true,actual_fresh_restored_project_reopen:true});
  }finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await browser.close();console.log('CLEAR '+report.status);if(report.status!=='Pass')process.exitCode=1;}
