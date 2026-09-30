import { initCanvas, baseCtx, viewCtx, view, W, H, cloneCanvas } from '../src/canvas';
import { initMaterials } from '../src/materials';
import { beginStrokeGeneration, segment } from '../src/draw';
import { clearLive, strokes } from '../src/live';
import { paintFrame } from '../src/paint';
import { state } from '../src/state';
initCanvas();initMaterials();
const median=(times:number[])=>times.sort((a,b)=>a-b)[Math.floor(times.length/2)].toFixed(2)+' ms';
for(const applicator of ['marker','watercolor'] as const){
  clearLive();baseCtx.fillStyle='#ffffff';baseCtx.fillRect(0,0,W,H);
  state.symmetry='off';state.symmetryMask=false;state.tool='draw';state.ink='rainbow';state.applicator=applicator;
  state.opacity=1;state.liveArmed=false;beginStrokeGeneration();
  let index=0,x=480,y=320;
  function frame():number{
    const start=performance.now();
    for(let n=0;n<8;n++){
      index++;const nx=480+Math.sin(index/73)*230,ny=320+Math.sin(index/109)*170;
      segment(x,y,nx,ny,24,0);x=nx;y=ny;
    }
    paintFrame(0);viewCtx.getImageData(0,0,1,1);
    return performance.now()-start;
  }
  for(let i=0;i<128;i++)frame();
  const early=Array.from({length:120},frame);
  while(index<60000){
    for(let i=0;i<128 && index<60000;i++)frame();
    await new Promise(resolve=>setTimeout(resolve,0));
  }
  const late=Array.from({length:120},frame);
  const row=document.createElement('tr');
  const values=[applicator==='marker'?'Squeaky marker':'Watercolour',median(early),median(late),String(strokes.reduce((sum,stroke)=>sum+stroke.points.length,0))];
  for(const value of values){const cell=document.createElement('td');cell.textContent=value;row.append(cell);}
  document.querySelector('#results')!.append(row);
}
document.querySelector('#sample')!.append(cloneCanvas(view));
document.querySelector('#status')!.textContent='Complete. Gesture history remains bounded to one point per stroke.';
document.title='Complete — Rainbow streaming benchmark';