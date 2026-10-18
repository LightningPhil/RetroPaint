import { bus, emit } from './bus';
import { baseCtx, cloneCanvas, H, resetPaint, useBase, view, W } from './canvas';
import { pushHistory } from './history';
import { activeLayer, activeLayerId, currentLive, layerChanged, layers, renderActive } from './layers';
import { bakeStaticStrokes, clearLive, renderLiveSnapshot, restoreLive, snapshotLive, type LiveSnapshot } from './live';
import { activeInkId, captureStrokeSpec, fillSpecFor } from './materials';
import { drawObject, multiply, objectBounds, objectCapture, setObjectCapture, type Bounds, type ObjectInk, type PaintObject, type PathObject, type RasterObject } from './object-scene';
import { invalidatePhotoCanvas } from './photo-render';
import { shapePoints } from './shapes';
import { state } from './state';
import { mirrorPoints, symmetryTransforms } from './symmetry';
import { lanePolygon } from './symmetry-mask';
import type { ShapeKind } from './types';
import { drips } from './effects';
import { trimRasterToPaper } from './selection-commit';

let sequence=0;
export const objectId=():string=>`object-${Date.now().toString(36)}-${++sequence}`;
let selected=new Set<string>(),selectionLayer=0;
const editedSelection=new Set<string>();
let clipboard:PaintObject[]=[];
let capture:{layer:number;live:LiveSnapshot;name:string;blend?:'destination-out';index?:number}|null=null;
const surface=(width=W,height=H)=>{const c=document.createElement('canvas');c.width=width;c.height=height;return c;};
export function editableObjects():boolean { return state.drawingMode==='vector'||Boolean(activeLayer().objects?.length); }
export function selectedObjects():PaintObject[] { return selectionLayer===activeLayerId?(activeLayer().objects??[]).filter(object=>selected.has(object.id)):[]; }
export function hasObjectSelection():boolean { return selectedObjects().length>0; }
export function objectSelectionBounds():Bounds|null {
  const bounds=selectedObjects().map(objectBounds);if(!bounds.length)return null;
  const x=Math.min(...bounds.map(b=>b.x)),y=Math.min(...bounds.map(b=>b.y));return {x,y,width:Math.max(...bounds.map(b=>b.x+b.width))-x,height:Math.max(...bounds.map(b=>b.y+b.height))-y};
}
export function clearObjectSelection():void { selected=new Set();editedSelection.clear();selectionLayer=activeLayerId;emit('objects'); }
function commitObjectIds(ids:Set<string>):void {
  if(selectionLayer!==activeLayerId||!ids.size)return;
  const replacements=new Map<string,PaintObject|null>();
  for(const object of activeLayer().objects??[])if(ids.has(object.id)&&object.kind==='raster'){
    const trimmed=trimRasterToPaper(object,W,H);if(trimmed!==object)replacements.set(object.id,trimmed);
  }
  if(replacements.size){
    if([...replacements.keys()].some(id=>!editedSelection.has(id)))pushHistory();
    for(const old of activeLayer().objects??[]){const replacement=replacements.get(old.id);if(old.kind!=='raster'||replacement===undefined)continue;
      for(let i=drips.length-1;i>=0;i--){const drip=drips[i];if(drip.target.canvas!==old.image)continue;if(!replacement||replacement.kind!=='raster'){drips.splice(i,1);continue;}
        const a=old.matrix,b=replacement.matrix,det=a[0]*a[3]-a[1]*a[2],dx=b[4]-a[4],dy=b[5]-a[5];drip.x-=(a[3]*dx-a[2]*dy)/det;drip.y-=(-a[1]*dx+a[0]*dy)/det;drip.target=replacement.image.getContext('2d')!;
      }
    }
    activeLayer().objects=activeLayer().objects?.flatMap(object=>{const replacement=replacements.get(object.id);return replacement===undefined?[object]:replacement?[replacement]:[];});changed();
  }
  for(const id of ids)editedSelection.delete(id);
}
export function commitObjectSelection(clear=true):void {commitObjectIds(new Set(selected));if(clear)clearObjectSelection();}
export function selectObjects(ids:string[]):void {
  commitObjectIds(new Set([...selected].filter(id=>!ids.includes(id))));selectionLayer=activeLayerId;selected=new Set(ids);emit('objects');
}
export function selectAllObjects():void { ensureObjectLayer();selectObjects((activeLayer().objects??[]).map(object=>object.id)); }
function changed():void { invalidatePhotoCanvas(activeLayer().canvas);layerChanged();emit('objects'); }
function add(object:PaintObject):void { const layer=activeLayer();layer.objects=[...(layer.objects??[]),object];selectObjects([object.id]);editedSelection.add(object.id);changed(); }
export function addPaintObject(object:PaintObject,history=true):void {commitObjectSelection();if(history)pushHistory();ensureObjectLayer();add(object); }

/** Old paint is one editable piece. New strokes never share a raster surface. */
export function ensureObjectLayer():void {
  const layer=activeLayer();if(layer.objects)return;
  const live=snapshotLive(),pixels=layer.canvas.getContext('2d')!.getImageData(0,0,W,H).data;
  const paper=layer.paper?layer.paper.slice(1).match(/../g)!.map(c=>parseInt(c,16)):null;
  let hasPaint=Boolean(live.strokes.length||live.fills.length||live.sparkles.length);
  for(let i=0;!hasPaint&&i<pixels.length;i+=4)hasPaint=paper?pixels[i]!==paper[0]||pixels[i+1]!==paper[1]||pixels[i+2]!==paper[2]||pixels[i+3]!==255:pixels[i+3]!==0;
  layer.objects=hasPaint?[{id:objectId(),name:'Existing artwork',kind:'raster',image:cloneCanvas(layer.canvas),width:W,height:H,matrix:[1,0,0,1,0,0],opacity:1,liveSize:{width:W,height:H},live:live.strokes.length||live.fills.length||live.sparkles.length?live:undefined}]:[];
  resetPaint(baseCtx);baseCtx.clearRect(0,0,W,H);if(layer.paper){baseCtx.fillStyle=layer.paper;baseCtx.fillRect(0,0,W,H);}clearLive();layer.live=snapshotLive();changed();
}
export function setDrawingMode(mode:'raster'|'vector'):void {
  emit('settle-input');emit('settle-artwork');state.drawingMode=mode;
  if(mode==='vector'){pushHistory();ensureObjectLayer();}
  clearObjectSelection();document.body.classList.toggle('vector-mode',mode==='vector');
  const field=document.getElementById('drawingMode') as HTMLSelectElement|null;if(field)field.value=mode;
  emit('objects');
}
export function beginObjectStroke(name='Brush stroke',blend?:'destination-out'):boolean {
  if(capture||!editableObjects())return false;commitObjectSelection();ensureObjectLayer();
  const layer=activeLayer(),canvas=surface();capture={layer:layer.id,live:snapshotLive(),name,blend};layer.live=capture.live;
  clearLive();useBase(canvas);setObjectCapture({layer:layer.id,canvas,live:currentLive,blend});return true;
}
export function finishObjectStroke():void {
  if(!capture||!objectCapture)return;
  const saved=capture,canvas=objectCapture.canvas;bakeStaticStrokes(baseCtx);const live=snapshotLive();
  capture=null;setObjectCapture(null);const layer=layers.find(l=>l.id===saved.layer);if(!layer)return;
  useBase(layer.canvas);restoreLive(saved.live);
  // Include animated ink when finding the crop, but keep its original recipe alive.
  const preview=cloneCanvas(canvas);renderLiveSnapshot(preview.getContext('2d')!,live,performance.now());
  const pixels=preview.getContext('2d')!.getImageData(0,0,W,H).data;
  let x=W,y=H,right=0,bottom=0;
  for(let yy=0;yy<H;yy++)for(let xx=0;xx<W;xx++)if(pixels[(yy*W+xx)*4+3]){x=Math.min(x,xx);y=Math.min(y,yy);right=Math.max(right,xx+1);bottom=Math.max(bottom,yy+1);}
  const wet=drips.filter(drip=>drip.target.canvas===canvas);
  for(const drip of wet){const remaining=Math.max(0,1100-drip.age);x=Math.max(0,Math.min(x,Math.floor(drip.x-drip.r-1)));y=Math.max(0,Math.min(y,Math.floor(drip.y-drip.r-1)));right=Math.min(W,Math.max(right,Math.ceil(drip.x+drip.r+1)));bottom=Math.min(H,Math.max(bottom,Math.ceil(drip.y+remaining*(drip.vy+.002*remaining)*.08+drip.r+10)));}
  if(right>x&&bottom>y){const image=surface(right-x,bottom-y);image.getContext('2d')!.drawImage(canvas,-x,-y);for(const drip of wet){drip.target=image.getContext('2d')!;drip.x-=x;drip.y-=y;}const object:RasterObject={id:objectId(),kind:'raster',name:saved.name,image,width:image.width,height:image.height,matrix:[1,0,0,1,x,y],opacity:1,origin:{x,y},liveSize:{width:W,height:H},blend:saved.blend,wet:wet.length>0,live:live.strokes.length||live.fills.length||live.sparkles.length?live:undefined};const objects=[...(layer.objects??[])];objects.splice(saved.index??objects.length,0,object);layer.objects=objects;selectObjects([object.id]);}
  changed();
}
export function hasObjectCapture():boolean { return Boolean(capture); }
export function captureRasterAction(name:string,action:()=>void):void { const started=beginObjectStroke(name);try{action();}finally{if(started)finishObjectStroke();} }

function ink(id:string,stroke=false):ObjectInk {
  const spec=stroke||['rainbow','sparkle','neon'].includes(id)?captureStrokeSpec():fillSpecFor(id);
  return {color:id==='neon'?state.neonTint:id==='sparkle'?state.sparkleTint:id,spec:spec&&spec!=='sparkle'?structuredClone(spec):undefined};
}
export function makePathObject(points:{x:number;y:number}[],closed:boolean,name='Shape'):PathObject {
  const lanes=points.map(p=>mirrorPoints(p.x,p.y)),padding=state.shapeOutline==='none'?0:state.brushWidth*(state.ink==='neon'?2:1)/2;
  let left=Infinity,top=Infinity,right=-Infinity,bottom=-Infinity;for(const lane of lanes)for(const p of lane){left=Math.min(left,p.x);top=Math.min(top,p.y);right=Math.max(right,p.x);bottom=Math.max(bottom,p.y);}
  const x=left-padding,y=top-padding,width=Math.max(1,right-x+padding),height=Math.max(1,bottom-y+padding);
  const local=(p:{x:number;y:number})=>({x:p.x-x,y:p.y-y});
  return {id:objectId(),kind:'path',name,width,height,matrix:[1,0,0,1,x,y],opacity:state.opacity,lineWidth:state.brushWidth,
    paths:Array.from({length:lanes[0]?.length??0},(_,lane)=>({points:lanes.map(p=>local(p[lane])),closed,clip:lanePolygon(lane)?.map(local)})),
    fill:closed&&state.shapeFill!=='none'?ink(state.shapeFill==='secondary'?state.secondaryInk:activeInkId()):null,
    stroke:state.shapeOutline==='none'?null:ink(activeInkId(),true)};
}
export function makeVectorShape(kind:ShapeKind,x0:number,y0:number,x1:number,y1:number):PathObject {
  const object=makePathObject(shapePoints(kind,x0,y0,x1,y1),kind!=='line',kind==='line'?'Line':'Shape');
  if(kind==='ellipse'||kind==='circle'){
    const rx=kind==='circle'?Math.hypot(x1-x0,y1-y0):Math.abs(x1-x0)/2,ry=kind==='circle'?rx:Math.abs(y1-y0)/2,cx=kind==='circle'?x0:(x0+x1)/2,cy=kind==='circle'?y0:(y0+y1)/2;
    if(rx&&ry)object.paths.forEach((lane,i)=>{const t=symmetryTransforms()[i];lane.svg=`M ${cx-rx} ${cy} A ${rx} ${ry} 0 1 0 ${cx+rx} ${cy} A ${rx} ${ry} 0 1 0 ${cx-rx} ${cy} Z`;lane.transform=[t.a,t.c,t.b,t.d,W/2-t.a*W/2-t.b*H/2-object.matrix[4],H/2-t.c*W/2-t.d*H/2-object.matrix[5]];});
  }
  return object;
}
export function addVectorShape(kind:ShapeKind,x0:number,y0:number,x1:number,y1:number):void {addPaintObject(makeVectorShape(kind,x0,y0,x1,y1),false);}
let vectorPreview:{signature:string;object:PathObject}|null=null;
export function previewVectorShape(ctx:CanvasRenderingContext2D,kind:ShapeKind,x0:number,y0:number,x1:number,y1:number):void {
  const signature=JSON.stringify([kind,x0,y0,x1,y1,state.ink,state.secondaryInk,state.neonTint,state.sparkleTint,state.opacity,state.brushWidth,state.shapeFill,state.shapeOutline,state.symmetry,state.symmetryMask,state.symmetrySlice,state.liveArmed,state.conveyor,state.beltMode,state.beltSpeed]);
  if(vectorPreview?.signature!==signature)vectorPreview={signature,object:makeVectorShape(kind,x0,y0,x1,y1)};drawObject(ctx,vectorPreview.object,performance.now());
}
export function addVectorPath(points:{x:number;y:number}[],closed=false,name='Path',history=false):void { if(points.length>1)addPaintObject(makePathObject(points,closed,name),history); }
export function addRasterImage(image:HTMLCanvasElement,at={x:(W-image.width)/2,y:(H-image.height)/2},name='Image'):void {
  addPaintObject({id:objectId(),name,kind:'raster',image:cloneCanvas(image),width:image.width,height:image.height,matrix:[1,0,0,1,at.x,at.y],opacity:1});
}

const hitCanvas=surface(1,1),hitCtx=hitCanvas.getContext('2d',{willReadFrequently:true})!;
export function hitObject(x:number,y:number,cycle=false):PaintObject|null {
  const hits=(activeLayer().objects??[]).filter(object=>{const b=objectBounds(object),t=6/Math.max(.01,state.paperScale);if(x<b.x-t||x>b.x+b.width+t||y<b.y-t||y>b.y+b.height+t)return false;
    resetPaint(hitCtx);hitCtx.clearRect(0,0,1,1);hitCtx.translate(.5-x,.5-y);drawObject(hitCtx,{...object,blend:undefined} as PaintObject,performance.now());return hitCtx.getImageData(0,0,1,1).data[3]>8;
  }).reverse();
  if(!hits.length)return null;if(cycle){const index=hits.findIndex(o=>selected.has(o.id));return hits[(index+1)%hits.length];}return hits[0];
}
export function selectObjectAt(x:number,y:number,additive=false,cycle=false):boolean {
  ensureObjectLayer();const object=hitObject(x,y,cycle);if(!object){if(!additive)commitObjectSelection();return false;}
  const ids=additive?new Set(selected):new Set<string>();if(additive&&ids.has(object.id))ids.delete(object.id);else ids.add(object.id);selectObjects([...ids]);return true;
}
export function selectObjectsIn(rect:Bounds,additive=false):void {
  const ids=additive?new Set(selected):new Set<string>();for(const object of activeLayer().objects??[]){const b=objectBounds(object);if(b.x<=rect.x+rect.width&&b.x+b.width>=rect.x&&b.y<=rect.y+rect.height&&b.y+b.height>=rect.y)ids.add(object.id);}selectObjects([...ids]);
}
function transformSelected(matrix:Parameters<typeof multiply>[0],original=selectedObjects()):void {
  for(const object of original)editedSelection.add(object.id);
  const replacement=new Map(original.map(object=>[object.id,{...object,matrix:multiply(matrix,object.matrix)}]));activeLayer().objects=(activeLayer().objects??[]).map(object=>replacement.get(object.id)??object);changed();
}
export function moveObjects(dx:number,dy:number,history=true):void { if(!hasObjectSelection()||(!dx&&!dy))return;if(history)pushHistory();transformSelected([1,0,0,1,dx,dy]); }
export function centreObjects():void {const b=objectSelectionBounds();if(b)moveObjects((W-b.width)/2-b.x,(H-b.height)/2-b.y);}
export function resizeObjects(width:number,height:number):void {
  const b=objectSelectionBounds();if(!b)return;if(![width,height].every(n=>Number.isFinite(n)&&n>0&&n<=1e7))throw new Error('Enter a positive width and height.');pushHistory();const sx=width/b.width,sy=height/b.height;transformSelected([sx,0,0,sy,b.x*(1-sx),b.y*(1-sy)]);
}
export function rotateObjects(degrees:number):void {
  const b=objectSelectionBounds();if(!b)return;if(!Number.isFinite(degrees))throw new Error('Enter a turn angle.');pushHistory();const x=b.x+b.width/2,y=b.y+b.height/2,r=degrees*Math.PI/180,c=Math.cos(r),s=Math.sin(r);transformSelected([c,s,-s,c,x-c*x+s*y,y-s*x-c*y]);
}
export function transformObjects(matrix:Parameters<typeof multiply>[0]):void {if(!hasObjectSelection())return;pushHistory();transformSelected(matrix);}
export function editObjectPixels(edit:(image:ImageData)=>void,history=true):void {
  if(!hasObjectSelection())return;
  const edited=new Map<string,PaintObject>();
  for(const object of selectedObjects()){
    if(object.width>4096||object.height>4096)throw new Error('Resize this piece below 4096 pixels before using a pixel effect.');
    const canvas=surface(Math.max(1,Math.ceil(object.width)),Math.max(1,Math.ceil(object.height))),ctx=canvas.getContext('2d')!;drawObject(ctx,{...object,matrix:[1,0,0,1,0,0]},performance.now());const image=ctx.getImageData(0,0,canvas.width,canvas.height);edit(image);ctx.putImageData(image,0,0);edited.set(object.id,{id:object.id,name:object.name,kind:'raster',matrix:object.matrix,width:canvas.width,height:canvas.height,image:canvas,opacity:1});
  }
  if(history)pushHistory();activeLayer().objects=activeLayer().objects?.map(o=>edited.get(o.id)??o);changed();
}
export function flipObjects(horizontal:boolean):void {const b=objectSelectionBounds();if(!b)return;pushHistory();transformSelected(horizontal?[-1,0,0,1,b.x*2+b.width,0]:[1,0,0,-1,0,b.y*2+b.height]);}
export function deleteObjects():void { if(!hasObjectSelection())return;pushHistory();activeLayer().objects=activeLayer().objects?.filter(o=>!selected.has(o.id));clearObjectSelection();changed(); }
export function copyObjects():void { clipboard=selectedObjects().map(object=>object.kind==='raster'&&object.wet?{...object,image:cloneCanvas(object.image),wet:false}:object);emit('objects'); }
export function hasObjectClipboard():boolean { return clipboard.length>0; }
export function pasteObjects():void { if(!clipboard.length)return;pushHistory();ensureObjectLayer();const copies=clipboard.map(o=>({...o,id:objectId(),matrix:multiply([1,0,0,1,20,20],o.matrix)}));activeLayer().objects=[...(activeLayer().objects??[]),...copies];selectObjects(copies.map(o=>o.id));changed(); }
export function duplicateObjects():void {copyObjects();pasteObjects();}
export function reorderObjects(direction:number):void {if(!hasObjectSelection())return;pushHistory();const all=activeLayer().objects??[],picked=all.filter(o=>selected.has(o.id)),rest=all.filter(o=>!selected.has(o.id));activeLayer().objects=direction>0?[...rest,...picked]:[...picked,...rest];changed();}

let drag:{objects:PaintObject[];bounds:Bounds;x:number;y:number;handle:number;history:boolean}|null=null;
export function objectHandle(x:number,y:number):number {
  const b=objectSelectionBounds();if(!b)return -1;const points=[[b.x,b.y],[b.x+b.width/2,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height/2],[b.x+b.width,b.y+b.height],[b.x+b.width/2,b.y+b.height],[b.x,b.y+b.height],[b.x,b.y+b.height/2]],radius=12*W/Math.max(1,view.getBoundingClientRect().width);
  return points.findIndex(([px,py])=>Math.hypot(px-x,py-y)<=radius);
}
export function beginObjectDrag(x:number,y:number,handle=-1):void {const b=objectSelectionBounds();if(b)drag={objects:selectedObjects(),bounds:b,x,y,handle,history:false};}
export function dragObjects(x:number,y:number,shift=false):void {
  if(!drag)return;const d=drag,dx=x-d.x,dy=y-d.y;if(Math.abs(dx)+Math.abs(dy)<.01)return;if(!d.history){pushHistory();d.history=true;}
  if(d.handle<0){transformSelected([1,0,0,1,shift&&Math.abs(dy)>Math.abs(dx)?0:dx,shift&&Math.abs(dx)>=Math.abs(dy)?0:dy],d.objects);return;}
  const b=d.bounds,left=[0,6,7].includes(d.handle),right=[2,3,4].includes(d.handle),top=[0,1,2].includes(d.handle),bottom=[4,5,6].includes(d.handle);
  let sx=left?Math.max(1,b.width-dx)/b.width:right?Math.max(1,b.width+dx)/b.width:1,sy=top?Math.max(1,b.height-dy)/b.height:bottom?Math.max(1,b.height+dy)/b.height:1;
  if(shift){const scale=left||right?(top||bottom?Math.max(sx,sy):sx):sy;sx=sy=scale;}
  const fx=left?b.x+b.width:b.x,fy=top?b.y+b.height:b.y;transformSelected([sx,0,0,sy,fx*(1-sx),fy*(1-sy)],d.objects);
}
export function endObjectDrag(cancel=false):void {if(cancel&&drag?.history){const originals=new Map(drag.objects.map(o=>[o.id,o]));activeLayer().objects=activeLayer().objects?.map(o=>originals.get(o.id)??o);changed();}drag=null;}
export function renderObjectSelection(ctx:CanvasRenderingContext2D):void {
  if(state.tool!=='scissors')return;const b=objectSelectionBounds();if(!b)return;const scale=W/Math.max(1,view.getBoundingClientRect().width);
  ctx.save();ctx.lineWidth=3*scale;ctx.strokeStyle='#fff';ctx.strokeRect(b.x,b.y,b.width,b.height);ctx.lineWidth=1.5*scale;ctx.strokeStyle='#7952b8';ctx.setLineDash([6*scale,4*scale]);ctx.strokeRect(b.x,b.y,b.width,b.height);ctx.setLineDash([]);ctx.fillStyle='#ffd16f';
  for(const [x,y] of [[b.x,b.y],[b.x+b.width/2,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height/2],[b.x+b.width,b.y+b.height],[b.x+b.width/2,b.y+b.height],[b.x,b.y+b.height],[b.x,b.y+b.height/2]]){ctx.fillRect(x-5*scale,y-5*scale,10*scale,10*scale);ctx.strokeRect(x-5*scale,y-5*scale,10*scale,10*scale);}ctx.restore();
}

/** Pixel tools edit a selected piece while retaining every neighbouring object. */
export function beginObjectPixelEdit(group=false):boolean {
  if(!editableObjects())return false;ensureObjectLayer();const picked=selectedObjects();if(!picked.length||!group&&picked.length!==1)return false;
  const canvas=surface();for(const object of picked)drawObject(canvas.getContext('2d')!,object,performance.now());
  pushHistory();const layer=activeLayer(),index=layer.objects?.findIndex(o=>selected.has(o.id));layer.objects=layer.objects?.filter(o=>!selected.has(o.id));capture={layer:layer.id,live:snapshotLive(),name:picked.length===1?picked[0].name:'Edited objects',index};clearLive();useBase(canvas);setObjectCapture({layer:layer.id,canvas,live:currentLive,index});return true;
}
export function renderObjectArtwork(ctx:CanvasRenderingContext2D,now=performance.now()):void {renderActive(ctx,now);}
bus.addEventListener('layers',()=>{if(selectionLayer!==activeLayerId){selected=new Set();editedSelection.clear();selectionLayer=activeLayerId;emit('objects');}});
document.addEventListener('canvas-size',()=>{selected=new Set();editedSelection.clear();drag=null;emit('objects');});
