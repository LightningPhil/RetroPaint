import { renderPaintPath } from '../src/stroke-renderer';
const start=[{x:120,y:200,w:40},{x:720,y:200,w:40},{x:720,y:236,w:40},{x:660,y:236,w:40}];
const rows: {canvas:HTMLCanvasElement;applicator:'marker'|'watercolor'}[]=[];
function draw(canvas:HTMLCanvasElement,applicator:'marker'|'watercolor',progress:number){
  const ctx=canvas.getContext('2d')!;
  ctx.fillStyle='#e9edf7';ctx.fillRect(0,0,canvas.width,canvas.height);
  const points=progress>0?[...start,{x:660-500*progress,y:236,w:40}]:start;
  const result=renderPaintPath(points,{kind:'rainbow',color:'#ff0000',applicator})!;
  ctx.drawImage(result.canvas,result.x-75,result.y-140);
}
for(const applicator of ['marker','watercolor'] as const){
  const heading=document.createElement('h2');heading.textContent=applicator==='marker'?'Squeaky marker':'Watercolour';
  const pair=document.createElement('div');pair.className='pair';
  for(const label of ['Before extending','After extending']){
    const column=document.createElement('div'),title=document.createElement('h3'),canvas=document.createElement('canvas');
    title.textContent=label;canvas.width=700;canvas.height=175;
    column.append(title,canvas);pair.append(column);draw(canvas,applicator,0);
    if(label==='After extending')rows.push({canvas,applicator});
  }
  document.querySelector('#examples')!.append(heading,pair);
}
let animation=0;
document.querySelector('#extend')!.addEventListener('click',()=>{
  cancelAnimationFrame(animation);const startTime=performance.now();
  const step=(now:number)=>{
    const progress=Math.min(1,(now-startTime)/1800);
    for(const row of rows)draw(row.canvas,row.applicator,progress);
    document.querySelector('#status')!.textContent=progress<1?'Drawing…':'Complete — earlier paint stays fixed';
    if(progress<1)animation=requestAnimationFrame(step);
  };animation=requestAnimationFrame(step);
});
document.querySelector('#reset')!.addEventListener('click',()=>{
  cancelAnimationFrame(animation);for(const row of rows)draw(row.canvas,row.applicator,0);
  document.querySelector('#status')!.textContent='Ready';
});