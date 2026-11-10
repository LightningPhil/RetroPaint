import { activeInkId, previewColor } from './materials';
import { renderPaintPath } from './stroke-renderer';
import { state } from './state';
import type { Applicator } from './types';

let last='';
export function updateBrushPreviews():void {
  const ink=activeInkId(),color=ink==='neon'?state.neonTint:ink==='sparkle'?state.sparkleTint:ink.startsWith('#')?ink:previewColor(ink,0),signature=`${color}:${ink}`;
  if(last===signature)return;last=signature;
  for(const button of document.querySelectorAll<HTMLButtonElement>('#penDrawer [data-applicator]')){
    let canvas=button.querySelector<HTMLCanvasElement>('.brush-preview');if(!canvas){canvas=document.createElement('canvas');canvas.className='brush-preview';canvas.setAttribute('aria-hidden','true');button.prepend(canvas);}
    canvas.width=160;canvas.height=60;const ctx=canvas.getContext('2d')!;
    const points=Array.from({length:70},(_,i)=>({x:15+i*1.85,y:30+Math.sin(i/69*Math.PI*2)*9,w:button.dataset.applicator==='biro'?18:15}));
    const stroke=renderPaintPath(points,{kind:ink==='neon'?'neon':ink==='sparkle'?'glitter':ink==='rainbow'?'rainbow':'solid',color,applicator:button.dataset.applicator as Applicator},{width:160,height:60});
    if(stroke)ctx.drawImage(stroke.canvas,stroke.x,stroke.y);
  }
}
