import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
import {controlledRenderClock} from './controlled-render-time.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/layer-visibility')),origin=option('--origin','http://127.0.0.1:8094/');await fs.mkdir(out,{recursive:true});const file=path.join(out,'LAYER-003-headless-ui.json');if(await fs.access(file).then(()=>true,()=>false))throw new Error('Choose a new output folder.');
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,execution:'Actual layer eye, colour picker and drawing controls in isolated headless contexts; declared render phase10000ms',rows:[],errors:[]};
try{
 for(const [width,height] of [[1280,720],[320,568],[390,844],[844,390]]){
  console.log('VISIBILITY '+width+'x'+height);const location=path.join(out,width+'x'+height);await fs.mkdir(location,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true});await context.addInitScript(controlledRenderClock);await context.addInitScript(()=>{window.__acceptanceRenderTime=10000;});const page=await context.newPage(),driver=new AcceptanceDriver(page,location);page.on('pageerror',e=>report.errors.push(String(e)));
  page.setDefaultTimeout(20000);
  const layers=async()=>{if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();};
  const pair=async label=>{const saved=await driver.download(label);await driver.download(label,'png');return saved;};
  const point=async(x,y)=>{const r=await page.locator('#view').boundingBox();return {x:r.x+x/960*r.width,y:r.y+y/640*r.height};};
  try{
   await page.goto(origin,{waitUntil:'domcontentloaded'});await driver.advanced();await driver.open(path.join(root,'headless/MIX-final/MIX-enriched.retropaint'),'project');await pair('before');await layers();await page.getByRole('button',{name:'Hide Backdrop',exact:true}).click();await pair('hidden');
   await page.locator('[data-tool="picker"]').click();const sample=await point(900,600);await page.mouse.click(sample.x,sample.y);assert(await page.locator('#tray-solids [data-ink="#FFFFFF"]').evaluate(e=>e.classList.contains('selected')));await driver.record({action:'picked-hidden-guide-background',source_point:[900,600],selected_ink:'#FFFFFF'});await driver.snapshot('hidden-guide-picked-white');
   await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="marker"]').click();if(!await page.locator('[data-target="tray-solids"]').isVisible())await page.locator('#paletteToggle').click();await page.locator('[data-target="tray-solids"]').click();await page.getByRole('button',{name:'Green',exact:true}).click();if(await page.locator('#paletteToggle').getAttribute('aria-expanded')==='true')await page.locator('#paletteToggle').click();const p=await point(600,150),q=await point(800,150);const targets=await page.evaluate(({p,q})=>[p,q].map(point=>document.elementFromPoint(point.x,point.y)?.id),{p,q});assert.deepEqual(targets,['view','view'],'A fixture gesture point is covered by another control');await page.mouse.move(p.x,p.y);await page.mouse.down();await page.mouse.move(q.x,q.y,{steps:15});await page.mouse.up();await driver.record({action:'foreground-stroke',from:[600,150],to:[800,150],colour:'#43A047',applicator:'marker',size:22,actual_hit_targets:targets});await pair('hidden-painted');
   await layers();await page.getByRole('button',{name:'Show Backdrop',exact:true}).click();const saved=await pair('shown-painted');await driver.snapshot('shown-painted');
   for(const label of ['show-undone','paint-undone','hide-undone']){await page.locator('#undoBtn').click();await pair(label);}
   for(const label of ['hide-redone','paint-redone','show-redone']){await page.locator('#view').press('Control+Shift+z');await pair(label);}
   const freshOut=path.join(location,'fresh');await fs.mkdir(freshOut,{recursive:true});const fresh=await browser.newContext({viewport:{width,height},acceptDownloads:true});await fresh.addInitScript(controlledRenderClock);await fresh.addInitScript(()=>{window.__acceptanceRenderTime=10000;});const pp=await fresh.newPage(),d=new AcceptanceDriver(pp,freshOut);pp.on('pageerror',e=>report.errors.push(String(e)));await pp.goto(origin,{waitUntil:'domcontentloaded'});await d.open(saved,'project');await d.download('reopened');await d.download('reopened','png');await d.snapshot('reopened');await fresh.close();report.rows.push({width,height,hidden_background_picker:'#FFFFFF',foreground_target:'Character',visibility_and_paint_history_separate:true,fresh_reopen_complete:true});
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(file,JSON.stringify(report,null,2)+'\n');await browser.close();console.log('VISIBILITY '+report.status);if(report.status!=='Pass')process.exitCode=1;}
