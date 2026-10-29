import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
import {controlledRenderClock} from './controlled-render-time.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/layer-merge')),origin=option('--origin','http://127.0.0.1:8096/');
await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0,'Choose a fresh evidence directory');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Actual combine controls, disabled native attempts, downloads and chooser reopens in isolated headless contexts. Captured live phase10000ms; predeclared composite tolerance2/255 for flattening alpha rounding.',rows:[],errors:[]};
const create=async(width,height,folder)=>{await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true});await context.addInitScript(controlledRenderClock);await context.addInitScript(()=>{window.__acceptanceRenderTime=10000;});const page=await context.newPage(),driver=new AcceptanceDriver(page,folder);page.setDefaultTimeout(30000);page.on('pageerror',e=>report.errors.push(String(e)));await page.goto(origin,{waitUntil:'domcontentloaded'});return{context,page,driver};};
const pair=async(d,label)=>{const saved=await d.download(label);await d.download(label,'png');return saved;};
const list=async page=>{if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();if(await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();};
const options=async page=>{if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();if(!await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();};
try{
 for(const [width,height] of [[1280,720],[320,568],[390,844],[844,390]])for(const variant of ['Character','Caption','CAD-rejection']){
  console.log('MERGE '+width+'x'+height+' '+variant);const folder=path.join(out,width+'x'+height,variant),{context,page,driver}=await create(width,height,folder);
  try{
   await driver.advanced();await driver.open(path.join(root,variant==='CAD-rejection'?'backups/artwork-before-acceptance-audit.retropaint':'headless/MIX-final/MIX-enriched.retropaint'),'project');
   if(variant==='CAD-rejection'){
    const original=JSON.parse(await fs.readFile(path.join(root,'backups/artwork-before-acceptance-audit.retropaint'),'utf8')),cad=original.layers.find(l=>l.cad),paint=original.layers[original.layers.indexOf(cad)+1];
    await pair(driver,'before');await list(page);await page.getByRole('button',{name:new RegExp('^Paint on '+paint.name+'(?:, selected)?$')}).click();await options(page);assert(await page.locator('#mergeLayer').isDisabled());const rect=await page.locator('#mergeLayer').boundingBox();await page.mouse.click(rect.x+rect.width/2,rect.y+rect.height/2);await driver.record({action:'native-disabled-merge-into-CAD-attempt',rect});await pair(driver,'neighbour-attempt');
    await list(page);await page.getByRole('button',{name:new RegExp('^Paint on '+cad.name.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'(?:, selected)?$')}).click();await page.waitForFunction(()=>document.activeElement?.id==='cadCanvas');assert(await page.locator('#cadWorkshop #layersPanel').isVisible());assert(await page.locator('#mergeLayer').isDisabled());
    let unavailable='hidden';if(await page.locator('#layerOptions summary').isVisible()){await options(page);const r=await page.locator('#mergeLayer').boundingBox();await page.mouse.click(r.x+r.width/2,r.y+r.height/2);unavailable='disabled native attempt';}
    await driver.snapshot('CAD-merge-unavailable');await page.locator('#cadClose').click();await page.locator('#cadWorkshop').waitFor({state:'hidden'});const saved=await pair(driver,'cad-attempt');
    const fresh=await create(width,height,path.join(folder,'fresh'));try{await fresh.driver.open(saved,'project');await pair(fresh.driver,'reopened');}finally{await fresh.context.close();}
    report.rows.push({width,height,variant,merge_into_CAD_disabled:true,merge_CAD_unavailable:unavailable,fresh_reopen_complete:true});
   }else{
    await list(page);await page.getByRole('button',{name:new RegExp('^Paint on '+variant+'(?:, selected)?$')}).click();await pair(driver,'before');await options(page);assert.equal(await page.locator('#mergeLayer').isDisabled(),false);await page.locator('#mergeLayer').click();const saved=await pair(driver,'merged');await driver.snapshot('merged');
    await page.locator('#undoBtn').click();await pair(driver,'undone');await page.locator('#view').press('Control+Shift+z');await pair(driver,'redone');
    const fresh=await create(width,height,path.join(folder,'fresh'));try{await fresh.driver.open(saved,'project');await pair(fresh.driver,'reopened');await fresh.driver.snapshot('reopened');}finally{await fresh.context.close();}
    report.rows.push({width,height,variant,captured_frame_ms:10000,history_and_fresh_reopen_complete:true});
   }
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'LAYER-009-ui.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log('MERGE '+report.status);if(report.status!=='Pass')process.exitCode=1;}
