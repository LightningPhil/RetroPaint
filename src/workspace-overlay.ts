import { H, view, W } from './canvas';
import { displayFrame } from './document-frame';
import { drawObject, objectAnimated } from './object-scene';
import { objectSelectionBounds, selectedObjects } from './objects';
import { photoEditing } from './photo-preview';
import { rasterSelectionPreview } from './selection';
import { state } from './state';
import { symmetryTransforms } from './symmetry';
import { bus } from './bus';

let canvas:HTMLCanvasElement|null=null;
let previous='';
for(const event of ['objects','selection','layers'])bus.addEventListener(event,()=>{previous='';});

/** A faint working copy outside the paper makes clipping and overhang visible. */
export function renderWorkspaceOverlay(now:number):void {
  if(!canvas){canvas=document.createElement('canvas');canvas.id='workspaceOverlay';canvas.setAttribute('aria-hidden','true');document.getElementById('canvasSlot')!.append(canvas);}
  const pieces=selectedObjects(),raster=rasterSelectionPreview(),bounds=objectSelectionBounds()??(raster?{x:raster.x,y:raster.y,width:raster.image.width,height:raster.image.height}:null),frame=displayFrame(W,H);
  if(state.tool!=='scissors'||photoEditing||!bounds||bounds.x>=frame.x&&bounds.y>=frame.y&&bounds.x+bounds.width<=frame.x+frame.width&&bounds.y+bounds.height<=frame.y+frame.height){
    if(!canvas.hidden){canvas.hidden=true;canvas.width=canvas.height=1;previous='';}return;
  }
  const slot=document.getElementById('canvasSlot')!,slotRect=slot.getBoundingClientRect(),paper=view.getBoundingClientRect();
  const signature=JSON.stringify([bounds,pieces.map(o=>[o.id,o.matrix,o.kind==='raster'&&o.image.width]),raster?.x,raster?.y,slotRect.width,slotRect.height,paper.x,paper.y,paper.width,paper.height]);
  if(signature===previous&&!pieces.some(object=>objectAnimated(object)||object.kind==='raster'&&object.wet))return;
  previous=signature;canvas.hidden=false;
  const ratio=Math.min(2,window.devicePixelRatio||1),width=slotRect.width,height=slotRect.height;
  if(canvas.width!==Math.ceil(width*ratio)||canvas.height!==Math.ceil(height*ratio)){canvas.width=Math.ceil(width*ratio);canvas.height=Math.ceil(height*ratio);}
  const ctx=canvas.getContext('2d')!,sx=paper.width/W,sy=paper.height/H,x=paper.left-slotRect.left,y=paper.top-slotRect.top;
  ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,width,height);ctx.save();
  ctx.beginPath();ctx.rect(0,0,width,height);ctx.rect(x+frame.x*sx,y+frame.y*sy,frame.width*sx,frame.height*sy);ctx.clip('evenodd');
  ctx.translate(x,y);ctx.scale(sx,sy);ctx.globalAlpha=.24;
  for(const piece of pieces)drawObject(ctx,piece.kind==='raster'?{...piece,blend:undefined}:piece,now);
  if(raster?.floating)for(const t of symmetryTransforms(raster.sector?.mode??'off')){
    ctx.save();ctx.translate(W/2,H/2);ctx.transform(t.a,t.c,t.b,t.d,0,0);ctx.translate(-W/2,-H/2);ctx.drawImage(raster.image,raster.x,raster.y);ctx.restore();
  }
  ctx.globalAlpha=1;ctx.strokeStyle='#fffdf7';ctx.lineWidth=4/sx;ctx.strokeRect(bounds.x,bounds.y,bounds.width,bounds.height);
  ctx.strokeStyle='#7952b8';ctx.lineWidth=1.5/sx;ctx.setLineDash([6/sx,4/sx]);ctx.strokeRect(bounds.x,bounds.y,bounds.width,bounds.height);ctx.setLineDash([]);
  ctx.fillStyle='#ffd16f';
  for(const [hx,hy] of [[bounds.x,bounds.y],[bounds.x+bounds.width/2,bounds.y],[bounds.x+bounds.width,bounds.y],[bounds.x+bounds.width,bounds.y+bounds.height/2],[bounds.x+bounds.width,bounds.y+bounds.height],[bounds.x+bounds.width/2,bounds.y+bounds.height],[bounds.x,bounds.y+bounds.height],[bounds.x,bounds.y+bounds.height/2]]){
    ctx.beginPath();ctx.roundRect(hx-5/sx,hy-5/sy,10/sx,10/sy,2/sx);ctx.fill();ctx.stroke();
  }
  ctx.restore();
}
