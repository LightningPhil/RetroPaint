import { initCanvas, baseCtx } from '../src/canvas';
import { initMaterials } from '../src/materials';
import { renderPaintPath } from '../src/stroke-renderer';
import { symmetryTransforms } from '../src/symmetry';
import { insideSector } from '../src/symmetry-mask';
import { state } from '../src/state';
import { beginStrokeGeneration, segment } from '../src/draw';
import { clearLive } from '../src/live';
initCanvas();initMaterials();
const results:Record<string,number>={};
function measure(name:string,run:()=>void){run();const times=[];for(let i=0;i<5;i++){const start=performance.now();run();times.push(performance.now()-start);}times.sort((a,b)=>a-b);results[name]=Math.round(times[2]*100)/100;}
const path=Array.from({length:601},(_,i)=>({x:100+i*1.1,y:240+Math.sin(i/55)*65,w:36}));
measure('rainbowWatercolourMs',()=>{const b=renderPaintPath(path,{kind:'rainbow',color:'#E53935',applicator:'watercolor'})!;b.canvas.getContext('2d')!.getImageData(0,0,1,1);});
measure('symmetryGeometry100kMs',()=>{for(let i=0;i<100000;i++){symmetryTransforms('12');insideSector(600+i%50,330,{mode:'12',slice:0});}});
state.symmetry='12';state.symmetryMask=true;state.symmetrySlice=0;state.ink='#E53935';state.applicator='marker';
measure('prepare12WayStrokeMs',()=>{clearLive();beginStrokeGeneration();for(let i=0;i<400;i++)segment(600+i*.2,340+Math.sin(i/30)*10,600+(i+1)*.2,340+Math.sin((i+1)/30)*10,12,0);});
clearLive();baseCtx.clearRect(0,0,960,640);
document.querySelector('#results')!.textContent=JSON.stringify(results,null,2);document.title='Complete — RetroPaint performance';
