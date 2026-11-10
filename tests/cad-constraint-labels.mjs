import fs from 'node:fs/promises';
import path from 'node:path';

// Exercise SVG hit testing with real pointer clicks, including redundant dimensions.
export async function testCadConstraintLabels(browser,{origin,out}){
 const context=await browser.newContext({viewport:{width:1280,height:720}}),page=await context.newPage(),errors=[];
 page.setDefaultTimeout(15000);page.on('pageerror',e=>errors.push(String(e)));
 const result={status:'Fail',errors,layouts:[]};const assert=(v,message)=>{if(!v)throw Error(message);};
 try{
  await page.goto(origin,{waitUntil:'domcontentloaded'});await page.locator('#view').waitFor();
  for(const [width,height]of [[1280,720],[320,568],[390,844],[844,390]]){
   await page.setViewportSize({width,height});
   await page.evaluate(async()=>{
    await import('/src/cad-ui.ts');const {CadSketchEditor}=await import('/src/cad-sketch-ui.ts');document.querySelector('#dimensionLabelFixture')?.remove();
    const host=document.createElement('div');host.id='dimensionLabelFixture';host.className='cad-constraint-editor';host.style.cssText='position:fixed;z-index:10000;left:12px;top:12px;width:min(320px,calc(100vw - 24px));padding:8px;background:white;max-height:calc(100vh - 24px);overflow:auto';document.body.append(host);
    const points=[[0,0],[45,0],[45,20],[0,20]],rules=[{id:'length-a',kind:'length',edge:0,value:45},{id:'angle-a',kind:'angle',edge:0,value:0},{id:'redundant-angle-a',kind:'angle',edge:0,value:0},{id:'length-b',kind:'length',edge:1,value:20},{id:'angle-b',kind:'angle',edge:1,value:90},{id:'length-c',kind:'length',edge:2,value:45}];
    new CadSketchEditor(host,'dimensionHit',{points:()=>points,shape:()=>'polygon',constraints:()=>rules,update:()=>{throw Error('Selecting a dimension label changed the sketch');}},{changed:()=>{},guide:()=>{},notice:message=>{throw Error(message);}});
   });
   const layout={size:[width,height],hits:[]};result.layouts.push(layout);
   for(const id of ['length-a','angle-a','redundant-angle-a','length-b','angle-b','length-c']){
    const target=page.locator('#dimensionHitPlot [data-constraint="'+id+'"]'),box=await target.boundingBox();assert(box,'Missing dimension label '+id);await page.mouse.click(box.x+box.width/2,box.y+box.height/2);await page.locator('#dimensionHitSaved').waitFor();const selected=await page.locator('#dimensionHitSaved').inputValue();layout.hits.push({requested:id,selected});assert(selected===id,'Dimension label '+id+' selected '+selected);
   }
   const boxes=await page.locator('#dimensionHitPlot [data-constraint]').evaluateAll(es=>es.map(e=>{const r=e.getBoundingClientRect(),svg=e.ownerSVGElement.getBoundingClientRect();return {id:e.getAttribute('data-constraint'),x:r.x,y:r.y,right:r.right,bottom:r.bottom,inside:r.x>=svg.x&&r.right<=svg.right&&r.y>=svg.y&&r.bottom<=svg.bottom};}));
   assert(boxes.every(b=>b.inside),'A dimension label is clipped');for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i],b=boxes[j];assert(a.right<=b.x||b.right<=a.x||a.bottom<=b.y||b.bottom<=a.y,'Dimension labels still overlap');}layout.labelsUnclippedAndSeparate=true;
  }
  assert(!errors.length,errors.join('\n'));result.status='Pass';
 }catch(error){result.error=String(error.stack??error);}
 finally{await page.screenshot({path:path.join(out,'cad-constraint-labels.png')});await fs.writeFile(path.join(out,'cad-constraint-labels.json'),JSON.stringify(result,null,2)+'\n');await context.close();}
 return result;
}
