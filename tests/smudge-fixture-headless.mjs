import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {AcceptanceDriver} from './acceptance-driver.mjs';
import {controlledRenderClock} from './controlled-render-time.mjs';
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.join(root,'headless/SMUDGE-producer'),origin='http://127.0.0.1:8103/';await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0);const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,harness_sha256:createHash('sha256').update(await fs.readFile(new URL(import.meta.url))).digest('hex'),scope:'Fixture production only, not PAINT-013 execution. Actual source image chooser, layer/colour/Bucket controls, saved files and fresh chooser input. Moving water compared at declared render times; no age/performance claim.',errors:[]};
const frames=page=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
const create=async folder=>{await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width:1280,height:720},acceptDownloads:true});await context.addInitScript(controlledRenderClock);const page=await context.newPage(),d=new AcceptanceDriver(page,folder);page.on('pageerror',e=>report.errors.push(String(e)));await page.goto(origin);await page.bringToFront();return{context,page,d};};
const pair=async(d,label)=>{const file=await d.download(label);await d.download(label,'png');return file;};let context;
try{
 const current=await create(out);context=current.context;const {page,d}=current;await d.open(path.join(root,'fixtures/SMUDGE.png'),'image');await d.advanced();
 const layers=async()=>{if(!await page.locator('#layersPanel').isVisible())await page.locator('#layersToggle').click();};
 const options=async()=>{await layers();if(!await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();};
 const hide=async()=>{if(await page.locator('#layersPanel').isVisible())await page.locator('#closeLayers').click();};
 const rename=async name=>{await options();await page.locator('#layerName').fill(name);await page.locator('#layerName').press('Enter');};
 const select=async name=>{await layers();if(await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();await page.getByRole('button',{name:new RegExp('^Paint on '+name+'(?:, selected)?$')}).click();await hide();};
 await rename('Smudge source');if(await page.locator('#layerOptions').evaluate(e=>e.open))await page.locator('#layerOptions summary').click();await page.locator('#addLayer').click();await rename('Green guide');await page.locator('#layerDown').click();await hide();
 const colour=async(name,tab)=>{if(!await page.locator('[data-target="'+tab+'"]').isVisible())await page.locator('#paletteToggle').click();await page.locator('[data-target="'+tab+'"]').click();await page.getByRole('button',{name,exact:true}).click();if(await page.locator('#paletteToggle').getAttribute('aria-expanded')==='true')await page.locator('#paletteToggle').click();};
 const click=async source=>{const r=await page.locator('#view').boundingBox(),point={x:r.x+source[0]/320*r.width,y:r.y+source[1]/240*r.height};assert.equal(await page.evaluate(p=>document.elementFromPoint(p.x,p.y)?.id,point),'view');await page.mouse.click(point.x,point.y);await frames(page);};
 await colour('Green','tray-solids');await page.locator('[data-tool="bucket"]').click();await click([10,10]);await page.waitForTimeout(200);await select('Smudge source');const settled=await pair(d,'SMUDGE-settled');await d.snapshot('SMUDGE-settled');
 await colour('water ink','tray-textures');await page.locator('[data-tool="bucket"]').click();await click([200,120]);await page.waitForTimeout(200);
 for(const time of [10000,10371,11113]){await page.evaluate(t=>window.__acceptanceRenderTime=t,time);await frames(page);await d.canvas('#view','SMUDGE-water-time-'+time);}
 await page.evaluate(()=>window.__acceptanceRenderTime=10000);await frames(page);const live=await pair(d,'SMUDGE-live');await d.snapshot('SMUDGE-live');report.render_times_ms=[10000,10371,11113];report.live_reference_time_ms=10000;
 for(const [label,file] of [['settled',settled],['live',live]]){const fresh=await create(path.join(out,'fresh-'+label));try{await fresh.page.evaluate(()=>window.__acceptanceRenderTime=10000);await fresh.d.open(file,'project');await pair(fresh.d,'reopened');await fresh.d.snapshot('reopened');}finally{await fresh.context.close();}}
 assert(!report.errors.length);report.status='Producer controls completed; independent fixture verification required';
}catch(error){report.status='Fail';report.error=String(error.stack??error);process.exitCode=1;}finally{report.finished=new Date().toISOString();await fs.copyFile(new URL(import.meta.url),path.join(out,'executed-harness.mjs'));await fs.writeFile(path.join(out,'SMUDGE-producer-ui.json'),JSON.stringify(report,null,2)+'\n');await context?.close();await browser.close();console.log('SMUDGE '+report.status);}
