import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/biro')),origin=option('--origin','http://127.0.0.1:8099/');
await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0,'Retain earlier evidence');const plan=JSON.parse(await fs.readFile(path.join(root,'fixtures/PAINT-002-plan.json'),'utf8'));
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,plan:'fixtures/PAINT-002-plan.json',execution:'Isolated headless production; actual controls, trusted native mouse, chooser inputs and downloads. No internal paint/serializer calls.',rows:[],errors:[]};
const create=async(width,height,folder)=>{await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,folder);page.setDefaultTimeout(30000);page.on('pageerror',e=>report.errors.push(String(e)));await page.goto(origin,{waitUntil:'domcontentloaded'});return{context,page,driver};};
const pair=async(d,label)=>{const saved=await d.download(label);await d.download(label,'png');return saved;};
const curvePoints=offset=>Array.from({length:41},(_,i)=>{const t=i/40;return[150*(1-t)**2+800*(1-t)*t+650*t*t,280*(1-t)**2+320*(1-t)*t+280*t*t+offset];});
try{
 for(const row of plan.rows.filter(r=>option('--row','all')==='all'||option('--row','all').split(',').includes(r.id))){
  console.log('BIRO '+row.id+' '+row.viewport.join('x')+' '+row.size+' '+row.strength);const [width,height]=row.viewport,folder=path.join(out,row.id),{context,page,driver}=await create(width,height,folder);
  try{
   await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="marker"]').click();if(!await page.locator('[data-target="tray-solids"]').isVisible())await page.locator('#paletteToggle').click();await page.locator('[data-target="tray-solids"]').click();await page.getByRole('button',{name:'Black',exact:true}).click();if(await page.locator('#paletteToggle').getAttribute('aria-expanded')==='true')await page.locator('#paletteToggle').click();
   const size=page.locator('#brushSize');await size.press(row.size<49?'Home':'End');for(let i=0;i<Math.min(row.size-1,96-row.size);i++)await size.press(row.size<49?'ArrowRight':'ArrowLeft');assert.equal(Number(await size.inputValue()),row.size);await page.locator('#opacity').press(row.strength===1?'End':'Home');assert.equal(Number(await page.locator('#opacity').inputValue()),row.strength);await pair(driver,'before');
   const required=[...curvePoints(0),...curvePoints(-160),...curvePoints(200),[800,200],[800,480]],preparation=[];
   for(let attempt=0;attempt<4;attempt++){
    const covered=await page.locator('#view').evaluate((view,points)=>{const r=view.getBoundingClientRect();return points.map(source=>({source,hit:document.elementFromPoint(r.x+source[0]/960*r.width,r.y+source[1]/640*r.height)?.id})).filter(p=>p.hit!=='view');},required);if(!covered.length)break;assert(attempt<3,'Unchanged declared paths cannot be reached');await page.locator('#paperControls').getByRole('button',{name:'Zoom out',exact:true}).click();await page.waitForTimeout(80);preparation.push({action:'actual-paper-Zoom-out',previously_covered:covered});
   }
   await driver.record({action:'paper-view-preparation',steps:preparation,source_geometry_unchanged:true});
   await page.locator('#view').evaluate(e=>{window.__biroInput=[];for(const type of ['pointerdown','pointermove','pointerup'])e.addEventListener(type,event=>{const r=e.getBoundingClientRect();window.__biroInput.push({type,trusted:event.isTrusted,pointerType:event.pointerType,buttons:event.buttons,timeStamp:event.timeStamp,source:[(event.clientX-r.x)*960/r.width,(event.clientY-r.y)*640/r.height]});});});
   const point=async source=>{const r=await page.locator('#view').boundingBox(),p={x:r.x+source[0]/960*r.width,y:r.y+source[1]/640*r.height};assert.equal(await page.evaluate(p=>document.elementFromPoint(p.x,p.y)?.id,p),'view');return p;};
   const curve=async(offset,delay,label)=>{const points=curvePoints(offset),first=await point(points[0]);await page.mouse.move(first.x,first.y);const started=Date.now();await page.mouse.down();for(const source of points.slice(1)){const p=await point(source);await page.mouse.move(p.x,p.y);if(delay)await page.waitForTimeout(delay);}await page.mouse.up();const elapsed=Date.now()-started;await driver.record({action:'native-curve',label,points,delay_ms:delay,elapsed_ms:elapsed});return elapsed;};
   const tap=async(source,label)=>{const p=await point(source);await page.mouse.click(p.x,p.y);await driver.record({action:'native-tap',label,source});};
   await curve(0,0,'marker');await pair(driver,'marker');await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="biro"]').click();assert.equal(await page.locator('[data-applicator="biro"]').getAttribute('aria-pressed'),'true');await driver.download('biro-selected');
   const slow=await curve(-160,15,'slow');await pair(driver,'slow');await tap([800,200],'tap');await pair(driver,'tap');const fast=await curve(200,0,'fast');assert(fast<slow);await pair(driver,'fast');
   await page.locator('[data-tool="spray"]').click();await page.locator('[data-applicator="mist"]').click();assert.equal(await page.locator('[data-applicator="mist"]').getAttribute('aria-pressed'),'true');await driver.download('spray-selected');
   await page.locator('[data-tool="draw"]').click();await page.locator('#penDrawer.open [data-applicator="biro"][aria-pressed="true"]').waitFor();await driver.snapshot('biro-returned-from-spray');const close=page.locator('#penDrawer.open .drawer-close');if(await close.isVisible())await close.click();await driver.download('biro-restored');await tap([800,480],'returned');const saved=await pair(driver,'returned');await driver.snapshot('five-gestures');
   for(const label of ['returned-undone','fast-undone','tap-undone','slow-undone','marker-undone']){await page.locator('#undoBtn').click();await driver.download(label);}for(const label of ['marker-redone','slow-redone','tap-redone','fast-redone','returned-redone']){await page.locator('#view').press('Control+Shift+z');await driver.download(label);}
   const inputs=await page.evaluate(()=>window.__biroInput);await fs.writeFile(path.join(folder,'native-input.json'),JSON.stringify(inputs,null,2)+'\n');assert.equal(inputs.filter(e=>e.type==='pointerdown').length,5);assert.equal(inputs.filter(e=>e.type==='pointerup').length,5);assert(inputs.every(e=>e.trusted&&e.pointerType==='mouse'));
   const fresh=await create(width,height,path.join(folder,'fresh'));try{await fresh.driver.open(saved,'project');await pair(fresh.driver,'reopened');}finally{await fresh.context.close();}report.rows.push({...row,slow_elapsed_ms:slow,fast_elapsed_ms:fast,paper_view_preparation:preparation,actual_five_gesture_history_and_fresh_reopen:true});
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'PAINT-002-ui.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log('BIRO '+report.status);if(report.status!=='Pass')process.exitCode=1;}
