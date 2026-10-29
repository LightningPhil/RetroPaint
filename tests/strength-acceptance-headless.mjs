import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];},root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/strength')),origin=option('--origin','http://127.0.0.1:8099/');await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0,'Retain earlier evidence');const plan=JSON.parse(await fs.readFile(path.join(root,'fixtures/PAINT-009-plan.json'),'utf8'));
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,plan:'fixtures/PAINT-009-plan.json',execution:'Isolated headless production, trusted mouse and actual controls/chooser/downloads. No existing browser profile or desktop access.',harness_sha256:createHash('sha256').update(await fs.readFile(new URL(import.meta.url))).digest('hex'),rows:[],errors:[]};
const create=async(width,height,folder)=>{await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,folder);page.setDefaultTimeout(30000);page.on('pageerror',e=>report.errors.push(String(e)));await page.goto(origin,{waitUntil:'domcontentloaded'});return{context,page,driver};};
const pair=async(d,label)=>{const saved=await d.download(label);await d.download(label,'png');return saved;};
try{
 for(const [width,height] of plan.viewports){
  console.log('STRENGTH '+width+'x'+height);const id=width+'x'+height,folder=path.join(out,id),{context,page,driver}=await create(width,height,folder);
  try{
   const colour=async name=>{if(!await page.locator('[data-target="tray-solids"]').isVisible())await page.locator('#paletteToggle').click();await page.locator('[data-target="tray-solids"]').click();await page.getByRole('button',{name,exact:true}).click();if(await page.locator('#paletteToggle').getAttribute('aria-expanded')==='true')await page.locator('#paletteToggle').click();};
   const size=async value=>{const range=page.locator('#brushSize');await range.press(value<49?'Home':'End');for(let i=0;i<Math.min(value-1,96-value);i++)await range.press(value<49?'ArrowRight':'ArrowLeft');assert.equal(Number(await range.inputValue()),value);};
   const strength=async value=>{await page.locator('#opacity').press(value===1?'End':'Home');assert.equal(Number(await page.locator('#opacity').inputValue()),value);await page.waitForFunction(value=>document.getElementById('workspaceToolDetail').textContent.includes(Math.round(value*100)+'%'),value);await driver.record({action:'visible-strength-and-range-agree',value,label:await page.locator('#workspaceToolDetail').innerText()});};
   await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="marker"]').click();await size(96);await strength(1);await colour('Blue');await pair(driver,'before');
   const all=[{centre:[200,440],half:100},{centre:[700,440],half:100},...plan.gestures.map(({centre})=>({centre,half:60}))],required=all.flatMap(({centre:[x,y],half})=>Array.from({length:21},(_,i)=>[x-half+2*half*i/20,y])),preparation=[];
   for(let attempt=0;attempt<4;attempt++){
    const covered=await page.locator('#view').evaluate((view,points)=>{const r=view.getBoundingClientRect();return points.map(source=>({source,hit:document.elementFromPoint(r.x+source[0]/960*r.width,r.y+source[1]/640*r.height)?.id})).filter(p=>p.hit!=='view');},required);if(!covered.length)break;assert(attempt<3,'Declared Strength paths are covered');await page.locator('#paperControls').getByRole('button',{name:'Zoom out',exact:true}).click();await page.waitForTimeout(80);preparation.push({action:'actual-paper-Zoom-out',previously_covered:covered});
   }
   await driver.record({action:'paper-view-preparation',steps:preparation});await page.locator('#view').evaluate(e=>{window.__strengthInput=[];for(const type of ['pointerdown','pointermove','pointerup'])e.addEventListener(type,event=>{const r=e.getBoundingClientRect();window.__strengthInput.push({type,trusted:event.isTrusted,pointerType:event.pointerType,timeStamp:event.timeStamp,source:[(event.clientX-r.x)*960/r.width,(event.clientY-r.y)*640/r.height]});});});
   const line=async(centre,half,label)=>{const points=Array.from({length:21},(_,i)=>[centre[0]-half+2*half*i/20,centre[1]]),rect=await page.locator('#view').boundingBox(),convert=([x,y])=>({x:rect.x+x/960*rect.width,y:rect.y+y/640*rect.height}),first=convert(points[0]);await page.mouse.move(first.x,first.y);await page.mouse.down();for(const source of points.slice(1)){const p=convert(source);assert.equal(await page.evaluate(p=>document.elementFromPoint(p.x,p.y)?.id,p),'view');await page.mouse.move(p.x,p.y);}await page.mouse.up();await driver.record({action:'native-marker-line',label,points});};
   await line([200,440],100,'blue-left');await pair(driver,'blue-left');await line([700,440],100,'blue-right');await pair(driver,'blue-right');await size(22);await colour('Red');let saved;
   for(const gesture of plan.gestures){
    await strength(gesture.strength);
    if(gesture.label==='white-weak'){
     await page.locator('[data-tool="spray"]').click();await page.locator('[data-applicator="mist"]').click();await strength(.15);await driver.download('spray-selected');await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="biro"]').click();await strength(.15);await driver.download('biro-selected');await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="marker"]').click();await strength(.15);await driver.download('marker-restored');
    }
    await line(gesture.centre,60,gesture.label);saved=await pair(driver,gesture.label);
   }
   await driver.snapshot('complete-overlaps');const labels=['blue-left','blue-right',...plan.gestures.map(g=>g.label)];for(const label of [...labels].reverse()){await page.locator('#undoBtn').click();await driver.download(label+'-undone');}for(const label of labels){await page.locator('#view').press('Control+Shift+z');await driver.download(label+'-redone');}
   const inputs=await page.evaluate(()=>window.__strengthInput);await fs.writeFile(path.join(folder,'native-input.json'),JSON.stringify(inputs,null,2)+'\n');assert.equal(inputs.filter(e=>e.type==='pointerdown').length,8);assert.equal(inputs.filter(e=>e.type==='pointerup').length,8);assert(inputs.every(e=>e.trusted&&e.pointerType==='mouse'));
   const fresh=await create(width,height,path.join(folder,'fresh'));try{await fresh.driver.open(saved,'project');await pair(fresh.driver,'reopened');}finally{await fresh.context.close();}report.rows.push({id,viewport:[width,height],paper_view_preparation:preparation,eight_native_gestures_and_history:true});
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'PAINT-009-ui.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log('STRENGTH '+report.status);if(report.status!=='Pass')process.exitCode=1;}
