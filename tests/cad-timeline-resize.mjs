import fs from 'node:fs/promises';
import path from 'node:path';

// Real viewport transitions in a disposable browser; live user audit remains separate.
export async function testCadTimelineResize(browser,{origin,out}){
 const context=await browser.newContext({viewport:{width:1280,height:720}}),page=await context.newPage(),errors=[];
 page.setDefaultTimeout(20000);page.on('pageerror',e=>errors.push(String(e)));
 const result={status:'Fail',errors,transitions:[]};
 const assert=(value,message)=>{if(!value)throw Error(message);};
 const ready=()=>page.waitForFunction(()=>!document.querySelector('#cadWorkshop')?.hasAttribute('aria-busy'));
 const hideTools=async()=>{if(await page.locator('#cadHideTools').isVisible())await page.locator('#cadHideTools').click();};
 const snapshot=()=>page.locator('[data-cad-step]').evaluateAll(es=>es.map(e=>({index:Number(e.dataset.cadStep),selected:e.getAttribute('aria-pressed')==='true',width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})));
 try{
  await page.goto(origin,{waitUntil:'domcontentloaded'});await page.locator('#view').waitFor();
  const before=await page.evaluate(async()=>{
   const {resetLayers}=await import('/src/layers.ts'),doc=await import('/src/cad-document.ts'),{primitive}=await import('/src/cad-model.ts'),{openCad}=await import('/src/cad-ui.ts');
   (await import('/src/advanced-mode.ts')).setAdvancedMode(true);resetLayers(160,120);doc.ensureCadLayer();let root=primitive('box');root.name='First cube';
   for(let i=1;i<=3;i++){const cube=primitive('box');cube.position=[i*30,0,10];cube.name='Cube '+(i+1);root=doc.combinedBody('union',[root,cube]);}
   doc.replaceBodies([root]);doc.selectBodies([root.id]);await openCad();return JSON.stringify(doc.currentBodies());
  });
  await page.locator('[data-cad-tab="history"]').click();await ready();assert((await snapshot()).length===6,'Desktop should show six of seven steps');
  await page.locator('#cadTimelineNext').click();assert((await snapshot()).map(s=>s.index).join(',')==='6','Desktop last page omitted step7');
  await page.setViewportSize({width:320,height:568});await hideTools();
  await page.waitForFunction(()=>document.querySelector('[data-cad-step="6"]')&&document.querySelector('#cadTimelinePrevious')?.disabled===false);
  result.transitions.push({size:[320,568],steps:await snapshot()});
  await page.locator('#cadTimelinePrevious').click();
  assert((await snapshot()).map(s=>s.index).join(',')==='3,4,5','Phone page does not preserve the previous visible step when regrouping');
  await page.locator('[data-cad-step="4"]').click();await ready();await hideTools();
  for(const [width,height]of [[1280,720],[390,844],[844,390],[320,568],[1280,720]]){
   await page.setViewportSize({width,height});await hideTools();
   const compact=width<=600||(width<=1000&&height<=500);
   await page.waitForFunction(compact=>{const es=[...document.querySelectorAll('[data-cad-step]')];return es.length===(compact?3:6)&&es.some(e=>e.dataset.cadStep==='4'&&e.getAttribute('aria-pressed')==='true');},compact);
   const steps=await snapshot();result.transitions.push({size:[width,height],steps});assert(steps.every(s=>s.width>=43.99&&s.height>=(compact?43.99:39.99)),'Resized timeline has undersized step targets');
  }
  await page.locator('#cadTimelineLatest').click();await ready();
  const after=await page.evaluate(async()=>JSON.stringify((await import('/src/cad-document.ts')).currentBodies()));assert(after===before,'Timeline resize or inspection changed the model');assert(!errors.length,errors.join('\n'));result.status='Pass';result.selectedStepPreserved=true;result.modelExact=true;
 }catch(error){result.error=String(error.stack??error);}
 finally{await page.screenshot({path:path.join(out,'cad-timeline-resize.png')});await fs.writeFile(path.join(out,'cad-timeline-resize.json'),JSON.stringify(result,null,2)+'\n');await context.close();}
 return result;
}
