import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {AcceptanceDriver} from './acceptance-driver.mjs';
const args=process.argv.slice(2),option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];},root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.resolve(option('--out','test-results/size')),origin=option('--origin','http://127.0.0.1:8099/');await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0);const plan=JSON.parse(await fs.readFile(path.join(root,'fixtures/PAINT-008-plan.json'),'utf8'));
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin,plan:'fixtures/PAINT-008-plan.json',harness_sha256:createHash('sha256').update(await fs.readFile(new URL(import.meta.url))).digest('hex'),execution:'Isolated headless production, trusted mouse/keys and real controls/chooser/downloads; existing user sessions and desktop unaccessed.',rows:[],errors:[]};
const create=async(width,height,folder)=>{await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width,height},acceptDownloads:true}),page=await context.newPage(),driver=new AcceptanceDriver(page,folder);page.setDefaultTimeout(30000);page.on('pageerror',e=>report.errors.push(String(e)));await page.goto(origin,{waitUntil:'domcontentloaded'});return{context,page,driver};};const pair=async(d,label)=>{const saved=await d.download(label);await d.download(label,'png');return saved;};
try{
 for(const [width,height] of plan.viewports){
  console.log('SIZE '+width+'x'+height);const id=width+'x'+height,folder=path.join(out,id),{context,page,driver}=await create(width,height,folder);
  try{
   await page.locator('[data-tool="draw"]').click();await page.locator('[data-applicator="marker"]').click();await page.locator('#opacity').press('End');if(!await page.locator('[data-target="tray-solids"]').isVisible())await page.locator('#paletteToggle').click();await page.locator('[data-target="tray-solids"]').click();await page.getByRole('button',{name:'Red',exact:true}).click();if(await page.locator('#paletteToggle').getAttribute('aria-expanded')==='true')await page.locator('#paletteToggle').click();await pair(driver,'before');
   const size=async value=>{const range=page.locator('#brushSize');await range.press(value<49?'Home':'End');for(let i=0;i<Math.min(value-1,96-value);i++)await range.press(value<49?'ArrowRight':'ArrowLeft');assert.equal(Number(await range.inputValue()),value);await page.waitForFunction(value=>document.getElementById('workspaceToolDetail').textContent.includes(value+' px'),value);};
   const required=[...plan.taps.map(t=>t.point),[800,200]],preparation=[];
   for(let attempt=0;attempt<4;attempt++){
    const covered=await page.locator('#view').evaluate((view,points)=>{const r=view.getBoundingClientRect();return points.map(source=>({source,hit:document.elementFromPoint(r.x+source[0]/960*r.width,r.y+source[1]/640*r.height)?.id})).filter(p=>p.hit!=='view');},required);if(!covered.length)break;assert(attempt<3,'Size/cursor points covered');await page.locator('#paperControls').getByRole('button',{name:'Zoom out',exact:true}).click();await page.waitForTimeout(80);preparation.push({action:'actual-paper-Zoom-out',previously_covered:covered});
   }
   const point=async source=>{const r=await page.locator('#view').boundingBox(),p={x:r.x+source[0]/960*r.width,y:r.y+source[1]/640*r.height};assert.equal(await page.evaluate(p=>document.elementFromPoint(p.x,p.y)?.id,p),'view');return p;};
   await page.locator('#view').evaluate(e=>{window.__sizeInput=[];for(const type of ['pointerdown','pointerup'])e.addEventListener(type,event=>{const r=e.getBoundingClientRect();window.__sizeInput.push({type,trusted:event.isTrusted,pointerType:event.pointerType,source:[(event.clientX-r.x)*960/r.width,(event.clientY-r.y)*640/r.height]});});});let saved;
   for(const tap of plan.taps){await size(tap.size);const p=await point(tap.point);await page.mouse.click(p.x,p.y);await driver.record({action:'native-size-tap',...tap});saved=await pair(driver,'size-'+tap.size);}
   const cursors=[];
   for(let zoom=0;zoom<2;zoom++){
    if(zoom){await page.locator('#paperControls').getByRole('button',{name:'Zoom out',exact:true}).click();await page.waitForTimeout(100);}
    for(const value of [1,22,96]){await size(value);const p=await point([800,200]);await page.mouse.move(p.x,p.y);await page.waitForTimeout(80);const label='cursor-z'+zoom+'-s'+value;await driver.canvas('#ui',label);const rectangle=await page.locator('#view').boundingBox();cursors.push({size:value,zoom,label,view_rectangle:rectangle,public_size_label:await page.locator('#workspaceToolDetail').innerText(),value:Number(await page.locator('#brushSize').inputValue())});}
   }
   await driver.download('view-controls');const p=await point([800,200]);await page.mouse.move(p.x,p.y);for(let i=0;i<20;i++)await page.locator('#brushSize').press(i%2?'End':'Home');await page.waitForFunction(()=>document.getElementById('workspaceToolDetail').textContent.includes('96 px'));assert.equal(Number(await page.locator('#brushSize').inputValue()),96);await driver.record({action:'rapid-size-controls',keys:20,last_value:96,pointer_down:false});await driver.download('rapid-controls');await driver.snapshot('three-sizes-and-rapid-controls');
   for(const value of [96,22,1]){await page.locator('#undoBtn').click();await driver.download('size-'+value+'-undone');}for(const value of [1,22,96]){await page.locator('#view').press('Control+Shift+z');await driver.download('size-'+value+'-redone');}
   const inputs=await page.evaluate(()=>window.__sizeInput);await fs.writeFile(path.join(folder,'native-input.json'),JSON.stringify(inputs,null,2)+'\n');assert.equal(inputs.filter(e=>e.type==='pointerdown').length,3);assert.equal(inputs.filter(e=>e.type==='pointerup').length,3);assert(inputs.every(e=>e.trusted&&e.pointerType==='mouse'));
   const fresh=await create(width,height,path.join(folder,'fresh'));try{await fresh.driver.open(saved,'project');await pair(fresh.driver,'reopened');}finally{await fresh.context.close();}report.rows.push({id,viewport:[width,height],cursors,paper_view_preparation:preparation});
  }catch(error){await driver.snapshot('failure').catch(()=>{});throw error;}finally{await context.close();}
 }
 report.status=report.errors.length?'Fail':'Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);}
finally{report.finished=new Date().toISOString();await fs.writeFile(path.join(out,'PAINT-008-ui.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log('SIZE '+report.status);if(report.status!=='Pass')process.exitCode=1;}
