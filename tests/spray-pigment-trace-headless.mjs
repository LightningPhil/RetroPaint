import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const root=path.resolve('APP-USE-CASES/runs/2026-10-19-full-audit'),out=path.join(root,'headless/SPRAY-pigment-trace');await fs.mkdir(out,{recursive:true});assert.equal((await fs.readdir(out)).length,0);
const browser=await chromium.launch({headless:true,channel:'chrome'}),report={started:new Date().toISOString(),origin:'http://127.0.0.1:8101/',browser:browser.version(),harness_sha256:createHash('sha256').update(await fs.readFile(new URL(import.meta.url))).digest('hex'),scope:'Observational delegates around native Canvas2D fills/gradient stops only. Actual public controls and trusted mouse. Every original positive-row size/Strength/layout repeated for each named style. Original native methods called unchanged; no app kernel, clock or RNG override. Existing actual file/history/fresh/geometry evidence remains separate.',rows:[],errors:[]};
const frames=page=>page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
try{
 for(const [kind,caseId] of [['mist','PAINT-010'],['splatter','PAINT-011'],['confetti','PAINT-012']])for(const row of JSON.parse(await fs.readFile(path.join(root,'fixtures/'+caseId+'-plan.json'),'utf8')).rows){
  console.log('PIGMENT '+kind+' '+row.id);const folder=path.join(out,kind,row.id);await fs.mkdir(folder,{recursive:true});const context=await browser.newContext({viewport:{width:row.viewport[0],height:row.viewport[1]}});await context.addInitScript(()=>{
   const gradients=new WeakMap(),ids=new WeakMap();let serial=0;window.__pigmentTrace=[];window.__pigmentPhase='setup';const p=CanvasRenderingContext2D.prototype,g=CanvasGradient.prototype,create=p.createRadialGradient,stop=g.addColorStop;
   p.createRadialGradient=function(...args){const result=create.apply(this,args);gradients.set(result,{kind:'radial',args,stops:[]});return result;};
   g.addColorStop=function(...args){const result=stop.apply(this,args);const meta=gradients.get(this);if(meta)meta.stops.push(args);return result;};
   for(const method of ['fill','fillRect']){const original=p[method];p[method]=function(...args){
    if(window.__pigmentPhase!=='setup'&&this.canvas.width===960&&this.canvas.height===640&&!this.canvas.isConnected){const style=this.fillStyle;if(style!=='#ffffff'&&style!=='#fff'){if(!ids.has(this))ids.set(this,++serial);window.__pigmentTrace.push({phase:window.__pigmentPhase,context:ids.get(this),method,style:typeof style==='string'?style:JSON.parse(JSON.stringify(gradients.get(style)??{kind:'unobserved-style'})),alpha:this.globalAlpha,composition:this.globalCompositeOperation,time:performance.now()});}}
    return original.apply(this,args);
   };}
  });
  const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));try{
   await page.goto(report.origin);await page.bringToFront();await page.locator('[data-tool="spray"]').click();await page.locator('[data-applicator="'+kind+'"]').click();const size=page.locator('#brushSize');await size.press(row.size<49?'Home':'End');for(let i=0;i<Math.min(row.size-1,96-row.size);i++)await size.press(row.size<49?'ArrowRight':'ArrowLeft');assert.equal(Number(await size.inputValue()),row.size);await page.locator('#opacity').press(row.strength===1?'End':'Home');
   const colour=async name=>{if(!await page.locator('[data-target="tray-solids"]').isVisible())await page.locator('#paletteToggle').click();await page.locator('[data-target="tray-solids"]').click();await page.getByRole('button',{name,exact:true}).click();if(await page.locator('#paletteToggle').getAttribute('aria-expanded')==='true')await page.locator('#paletteToggle').click();};
   const burst=async phase=>{await page.evaluate(phase=>window.__pigmentPhase=phase,phase);const r=await page.locator('#view').boundingBox(),point={x:r.x+r.width/2,y:r.y+r.height/2};assert.equal(await page.evaluate(p=>document.elementFromPoint(p.x,p.y)?.id,point),'view');await page.mouse.move(point.x,point.y);await page.mouse.down();await frames(page);await page.waitForTimeout(150);await page.mouse.up();await frames(page);await page.evaluate(()=>window.__pigmentPhase='setup');const url=await page.locator('#view').evaluate(e=>e.toDataURL('image/png'));await fs.writeFile(path.join(folder,phase+'-public.png'),Buffer.from(url.split(',')[1],'base64'));};
   if(kind==='confetti'){await colour('Rainbow ink');await burst('rainbow');}await colour('Red');await burst('red');const trace=await page.evaluate(()=>window.__pigmentTrace);assert(trace.length>0);await fs.writeFile(path.join(folder,'native-canvas-deposits.json'),JSON.stringify(trace,null,2)+'\n');report.rows.push({case:caseId,applicator:kind,...row,trace:'headless/SPRAY-pigment-trace/'+kind+'/'+row.id+'/native-canvas-deposits.json',native_deposit_count:trace.length,actual_size:Number(await size.inputValue()),actual_strength:Number(await page.locator('#opacity').inputValue())});
  }finally{await context.close();}
 }
 assert.equal(report.rows.length,36);assert.equal(report.errors.length,0);report.status='Pass';
}catch(error){report.status='Fail';report.error=String(error.stack??error);process.exitCode=1;}finally{report.finished=new Date().toISOString();await fs.copyFile(new URL(import.meta.url),path.join(out,'executed-harness.mjs'));await fs.writeFile(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');await browser.close();console.log('PIGMENT '+report.status);}
