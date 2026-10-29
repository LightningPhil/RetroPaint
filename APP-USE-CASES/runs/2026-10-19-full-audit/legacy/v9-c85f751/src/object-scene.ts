import { resetPaint } from './canvas';
import { liveAnimated,renderLiveSnapshot, type LiveSnapshot } from './live';
import { colorFromSpec, glitterPattern, patternFor, previewColor } from './materials';
import type { LiveSpec } from './types';

export type ObjectMatrix = [number, number, number, number, number, number];
export interface Bounds { x:number; y:number; width:number; height:number }
export interface ObjectInk { color:string; spec?:LiveSpec }
export interface ObjectPath { points:{x:number;y:number}[]; clip?:{x:number;y:number}[]|null; closed:boolean; svg?:string; transform?:ObjectMatrix }
interface ObjectBase { id:string; name:string; matrix:ObjectMatrix; width:number; height:number; opacity:number }
export interface PathObject extends ObjectBase { kind:'path'; paths:ObjectPath[]; fill:ObjectInk|null; stroke:ObjectInk|null; lineWidth:number }
export interface RasterObject extends ObjectBase { kind:'raster'; image:HTMLCanvasElement; live?:LiveSnapshot; liveSize?:{width:number;height:number}; origin?:{x:number;y:number}; blend?:'destination-out'; wet?:boolean; clip?:{x:number;y:number}[] }
export interface TextObject extends ObjectBase { kind:'text'; lines:{text:string;x:number;y:number;width:number}[]; font:string; size:number; align:CanvasTextAlign; color:string; paper:string|null; underline:boolean; strike:boolean }
export interface StampObject extends ObjectBase { kind:'stamp'; emoji:string; flipH:boolean; flipV:boolean; angle:number }
export type PaintObject = PathObject|RasterObject|TextObject|StampObject;
export let objectCapture:{layer:number;canvas:HTMLCanvasElement;live:()=>LiveSnapshot;blend?:'destination-out';index?:number}|null=null;
export function setObjectCapture(value:typeof objectCapture):void { objectCapture=value; }
export function multiply(a:ObjectMatrix,b:ObjectMatrix):ObjectMatrix {
  return [a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]];
}
export function objectBounds(object:PaintObject):Bounds {
  const m=object.matrix,local=object.kind==='raster'&&object.clip?.length?object.clip:[{x:0,y:0},{x:object.width,y:0},{x:object.width,y:object.height},{x:0,y:object.height}],points=local.map(({x,y})=>({x:m[0]*x+m[2]*y+m[4],y:m[1]*x+m[3]*y+m[5]}));
  const x=Math.min(...points.map(p=>p.x)),y=Math.min(...points.map(p=>p.y));
  return {x,y,width:Math.max(...points.map(p=>p.x))-x,height:Math.max(...points.map(p=>p.y))-y};
}
export function objectAnimated(object:PaintObject):boolean { return object.kind==='raster'?Boolean(object.live&&liveAnimated(object.live)):object.kind==='path'&&[object.fill,object.stroke].some(ink=>ink?.spec&&(['conveyor','rainbow-time','texture'].includes(ink.spec.kind)||ink.spec.texture)); }
const animationBuffers=new WeakMap<LiveSnapshot,HTMLCanvasElement>();
const vectorPaths=new WeakMap<ObjectPath,Path2D>();
function inkStyle(ctx:CanvasRenderingContext2D,ink:ObjectInk,now:number,width:number):string|CanvasPattern|CanvasGradient {
  const spec=ink.spec;
  if(spec?.kind==='conveyor'||spec?.kind==='rainbow-time')return colorFromSpec(spec,now,0);
  if(spec?.kind==='rainbow') {const gradient=ctx.createLinearGradient(0,0,Math.max(1,width),0);['#ff2d55','#ff9f1c','#ffd60a','#06d6a0','#118ab2','#9d4edd'].forEach((c,i)=>gradient.addColorStop(i/5,c));return gradient;}
  if(spec?.kind==='glitter')return glitterPattern(ink.color);
  const texture=spec?.texture?`tex-${spec.texture}`:ink.color;
  return patternFor(texture,now)??previewColor(ink.color,now);
}
export function drawObject(ctx:CanvasRenderingContext2D,object:PaintObject,now:number):void {
  ctx.save();ctx.transform(...object.matrix);ctx.globalAlpha*=object.opacity;
  if(object.kind==='raster') {
    if(object.blend)ctx.globalCompositeOperation=object.blend;
    ctx.drawImage(object.image,0,0,object.width,object.height);
    if(object.live){if(object.clip){ctx.beginPath();object.clip.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.clip();}let buffer=animationBuffers.get(object.live);if(!buffer){buffer=document.createElement('canvas');buffer.width=object.liveSize?.width??object.live.fills[0]?.mask.width??Math.max(1,object.width+(object.origin?.x??0));buffer.height=object.liveSize?.height??object.live.fills[0]?.mask.height??Math.max(1,object.height+(object.origin?.y??0));animationBuffers.set(object.live,buffer);}const b=buffer.getContext('2d')!;resetPaint(b);b.clearRect(0,0,buffer.width,buffer.height);renderLiveSnapshot(b,object.live,now);ctx.drawImage(buffer,-(object.origin?.x??0),-(object.origin?.y??0));}
  } else if(object.kind==='path') {
    ctx.lineWidth=object.lineWidth;ctx.lineCap='round';ctx.lineJoin='round';
    for(const lane of object.paths){ctx.save();if(lane.clip?.length){ctx.beginPath();lane.clip.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.clip();}let path=vectorPaths.get(lane);if(!path){path=new Path2D();if(lane.svg)path.addPath(new Path2D(lane.svg),new DOMMatrix(lane.transform));else{lane.points.forEach((p,i)=>i?path!.lineTo(p.x,p.y):path!.moveTo(p.x,p.y));if(lane.closed)path.closePath();}vectorPaths.set(lane,path);}if(object.fill){ctx.fillStyle=inkStyle(ctx,object.fill,now,object.width);ctx.fill(path);}if(object.stroke){ctx.strokeStyle=inkStyle(ctx,object.stroke,now,object.width);if(object.stroke.spec?.kind==='neon'){ctx.shadowColor=object.stroke.color;ctx.shadowBlur=object.lineWidth*1.4;}ctx.stroke(path);}ctx.restore();}
  } else if(object.kind==='text') {
    if(object.paper){ctx.fillStyle=object.paper;ctx.fillRect(0,0,object.width,object.height);}ctx.font=object.font;ctx.textAlign=object.align;ctx.textBaseline='top';ctx.fillStyle=object.color;
    for(const line of object.lines){ctx.fillText(line.text,line.x,line.y);const left=line.x-(object.align==='center'?line.width/2:object.align==='right'?line.width:0);if(object.underline)ctx.fillRect(left,line.y+object.size*1.04,line.width,Math.max(1,object.size/18));if(object.strike)ctx.fillRect(left,line.y+object.size*.55,line.width,Math.max(1,object.size/18));}
  } else {
    ctx.translate(object.width/2,object.height/2);ctx.rotate(object.angle);ctx.scale(object.flipH?-1:1,object.flipV?-1:1);ctx.font=`${object.height*.82}px "Segoe UI Emoji","Apple Color Emoji",sans-serif`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(object.emoji,0,0);
  }
  ctx.restore();
}
export function drawObjects(ctx:CanvasRenderingContext2D,objects:PaintObject[]|undefined,now:number):void { for(const object of objects??[])drawObject(ctx,object,now); }
export function drawSceneObjects(ctx:CanvasRenderingContext2D,objects:PaintObject[]|undefined,layer:number,now:number):void {
  const all=objects??[],index=objectCapture?.layer===layer?(objectCapture.index??all.length):-1;
  for(let i=0;i<=all.length;i++){if(i===index)drawObjectCapture(ctx,layer,now);if(i<all.length)drawObject(ctx,all[i],now);}
}
export function drawObjectCapture(ctx:CanvasRenderingContext2D,layer:number,now:number):void {
  if(objectCapture?.layer!==layer)return;ctx.save();if(objectCapture.blend)ctx.globalCompositeOperation=objectCapture.blend;ctx.drawImage(objectCapture.canvas,0,0);renderLiveSnapshot(ctx,objectCapture.live(),now);ctx.restore();
}
