import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
import {controlledRenderClock} from './controlled-render-time.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/workspace-mode')),origin=option('--origin','http://127.0.0.1:8094/');await fs.mkdir(out,{recursive:true});const file=path.join(out,'START-007-headless-ui.json');if(await fs.access(file).then(()=>true,()=>false))throw new Error('Choose a new output folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Isolated headless UI; MIX fixture with render timestamps explicitly held at10000ms for live-art comparisons; no elapsed-time claim',rows:[],errors:[]};
try{
 for(const [width,height] of [[1280,720],[320,568],[390,844],[844,390]]){
  console.log('MODE '+width+'x'+height);const location=path.join(out,width+'x'+height);await fs.mkdir(location,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true});await context.addInitScript(controlledRenderClock);await context.addInitScript(()=>{window.__acceptanceRenderTime=10000;});const page=await context.newPage(),driver=new AcceptanceDriver(page,location);page.on('pageerror',e=>report.errors.push(String(e)));
  const pair=async(d,label)=>{const saved=await d.download(label);await d.download(label,'png');return saved;};
  const set=async(value,label)=>{await driver.drawer();await page.locator('#advancedMode').setChecked(value);await driver.close();assert.equal(await page.locator('#layersToggle').isVisible(),value);assert.equal(await page.locator('#photoToggle').isVisible(),value);await driver.snapshot(label);return pair(driver,label);};
  try{
   await page.goto(origin,{waitUntil:'domcontentloaded'});assert.equal(await page.locator('#layersToggle').isVisible(),false);await driver.open(path.join(root,'headless/MIX-final/MIX-enriched.retropaint'),'project');await pair(driver,'before');
   let saved=await set(true,'advanced-on');await set(false,'advanced-off');await set(true,'advanced-again');
   for(const enabled of [true,false]){
    if(!enabled)saved=await set(false,'persisted-off-source');
    const freshOut=path.join(location,enabled?'fresh-on':'fresh-off');await fs.mkdir(freshOut,{recursive:true});const p=await context.newPage(),d=new AcceptanceDriver(p,freshOut);p.on('pageerror',e=>report.errors.push(String(e)));await p.goto(origin,{waitUntil:'domcontentloaded'});assert.equal(await p.locator('#layersToggle').isVisible(),enabled);assert.equal(await p.locator('#photoToggle').isVisible(),enabled);await d.open(saved,'project');await pair(d,'reopened');await d.snapshot('reopened');await p.close();
   }
   // Mode/preference navigation must not insert a document history step.
   await page.locator('#undoBtn').click();await pair(driver,'modes-undone');await page.locator('#view').press('Control+Shift+z');await pair(driver,'modes-redone');
   await driver.drawer();assert.equal(await page.locator('#advancedMode').isChecked(),false);assert.equal(await page.locator('#openCad').isVisible(),false);await page.locator('#advancedMode').check();await page.locator('#openCad').click();await page.waitForFunction(()=>document.activeElement?.id==='cadCanvas');assert(await page.locator('#cadWorkshop #layersPanel').isVisible());await driver.snapshot('advanced-opened-workshop-layers');
   await page.getByRole('button',{name:'Hide Backdrop',exact:true}).click();await driver.snapshot('workshop-guide-hidden');await page.getByRole('button',{name:'Show Backdrop',exact:true}).click();await page.locator('#cadClose').click();await page.locator('#cadWorkshop').waitFor({state:'hidden'});assert(await page.locator('#layersPanel').isVisible());assert(await page.locator('#layersToggle').isVisible());await driver.snapshot('paint-returned-with-layers');await page.getByRole('button',{name:/^Paint on Character(?:, selected)?$/}).click();await pair(driver,'cad-returned');
   report.rows.push({width,height,render_time_ms:10000,main_modes:[true,false,true],persisted_modes:[true,false],history_exercised:true,workshop_requires_advanced:true,backdrop_hide_show:true,layers_remain_on_return:true,paint_layer_selectable:true});
  }finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await browser.close();console.log('MODE '+report.status);if(report.status!=='Pass')process.exitCode=1;}
