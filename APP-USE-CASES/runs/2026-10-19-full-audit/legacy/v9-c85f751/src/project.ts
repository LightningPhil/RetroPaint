import { H, W } from './canvas';
import { activeLayerId, captureLayers, restoreLayers, type LayerSnapshot } from './layers';
import { renderLiveSnapshot, type LiveSnapshot } from './live';
import { download } from './export';
import { decodeImage, dimensions, editable, message, settle } from './editor';
import { pushHistory } from './history';
import { artwork } from './artwork';
import type { Applicator, LiveSpec } from './types';
import { documentCrop, setDocumentCrop } from './document-frame';
import { readPhotoCrop, readPhotoRecipe } from './photo-recipe';
import { state } from './state';
import type { ObjectInk, ObjectMatrix, PaintObject } from './object-scene';
import { emit } from './bus';
import { play } from './audio';
import { readCadLayer } from './cad-model';

const canvasFromImage = (image: ImageData) => { const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height; canvas.getContext('2d')!.putImageData(image, 0, 0); return canvas; };
function saveLive(value:LiveSnapshot){return {strokes:value.strokes.filter(s=>!s.rainbow),fills:value.fills.map(fill=>({...fill})),sparkles:value.sparkles};}
function saveObject(object:PaintObject):unknown {
  if(object.kind!=='raster')return object;
  const image=cloneObjectImage(object.image,object.live);return {...object,image,live:object.live?saveLive(object.live):undefined};
}
function cloneObjectImage(source:HTMLCanvasElement,snapshot?:LiveSnapshot):HTMLCanvasElement {
  const canvas=document.createElement('canvas');canvas.width=source.width;canvas.height=source.height;const ctx=canvas.getContext('2d')!;ctx.drawImage(source,0,0);
  if(snapshot?.strokes.some(s=>s.rainbow))renderLiveSnapshot(ctx,{strokes:snapshot.strokes.filter(s=>s.rainbow),fills:[],sparkles:[]},performance.now());return canvas;
}
function projectDocument() {
  const saved = captureLayers().map(layer => {
    const canvas = canvasFromImage(layer.image), rainbow = layer.live.strokes.filter(stroke => stroke.rainbow);
    if (rainbow.length) renderLiveSnapshot(canvas.getContext('2d')!, { strokes: rainbow, fills: [], sparkles: [] }, performance.now());
    return { id: layer.id, name: layer.name, visible: layer.visible, opacity: layer.opacity, paper: layer.paper, photo:layer.photo,objects:layer.objects?.map(saveObject),cad:layer.cad,
      image: canvas,live:saveLive(layer.live),
    };
  });
  return { format: 'RetroPaint', version: 9, drawingMode:state.drawingMode, width: W, height: H, crop:documentCrop(), active: activeLayerId, layers: saved };
}
export function projectData():string {return JSON.stringify(projectDocument(),(_key,value:unknown)=>value instanceof HTMLCanvasElement?value.toDataURL():value);}
function canvasDataUrl(canvas:HTMLCanvasElement):Promise<string> {
  return new Promise((resolve,reject)=>canvas.toBlob(blob=>{if(!blob){reject(new Error('Could not encode this picture.'));return;}const reader=new FileReader();reader.onload=()=>resolve(String(reader.result));reader.onerror=()=>reject(reader.error??new Error('Could not read the encoded picture.'));reader.readAsDataURL(blob);},'image/png'));
}
export async function projectDataAsync():Promise<string> {
  const snapshot=projectDocument(),canvases=new Set<HTMLCanvasElement>();
  const visit=(value:unknown):void=>{if(value instanceof HTMLCanvasElement){canvases.add(value);return;}if(value&&typeof value==='object')for(const child of Object.values(value))visit(child);};visit(snapshot);
  const urls=new Map<HTMLCanvasElement,string>(),pending=[...canvases];
  // Encoding yields between batches so large projects do not freeze the controls.
  for(let i=0;i<pending.length;i+=2)await Promise.all(pending.slice(i,i+2).map(async canvas=>urls.set(canvas,await canvasDataUrl(canvas))));
  return JSON.stringify(snapshot,(_key,value:unknown)=>value instanceof HTMLCanvasElement?urls.get(value):value);
}
export async function saveProjectFile(name = 'retropaint'):Promise<void> {
  const button=document.getElementById('saveProject') as HTMLButtonElement|null;if(button?.disabled)return;if(button)button.disabled=true;
  try{const data=await projectDataAsync(),filename=`${name.replace(/[<>:"/\\|?*]/g, '-') || 'retropaint'}.retropaint`;download(new Blob([data],{type:'application/json'}),filename);play('save');message('Project copy ready, including editable pieces, layers and photo adjustments.');}
  finally{if(button)button.disabled=false;}
}
type RecordValue = Record<string, unknown>;
function record(value: unknown): RecordValue { if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid project data.'); return value as RecordValue; }
function array(value: unknown, limit: number): unknown[] { if (!Array.isArray(value) || value.length > limit) throw new Error('Project contains too much or invalid data.'); return value; }
function number(value: unknown, min = -1e7, max = 1e7): number { if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max) throw new Error('Invalid project numbers.'); return value; }
function point(value: unknown): { x: number; y: number } { const p = record(value); return { x: number(p.x), y: number(p.y) }; }
function spec(value: unknown): LiveSpec {
  const s = record(value), kind = String(s.kind);
  if (!['conveyor', 'rainbow-time', 'texture', 'neon', 'solid', 'rainbow', 'glitter'].includes(kind) || !['snap', 'ooze'].includes(String(s.mode))) throw new Error('Unknown project ink.');
  const colors = array(s.colors, 32).map(color => { if (typeof color !== 'string' || color.length > 80) throw new Error('Invalid ink colour.'); return color; });
  return { kind: kind as LiveSpec['kind'], colors, speed: number(s.speed, -100, 100), mode: s.mode as LiveSpec['mode'], along: Boolean(s.along), texture: s.texture === 'water' || s.texture === 'static' ? s.texture : null };
}
const spark = (value: unknown) => { const p = record(value); return { ...point(p), phase: number(p.phase), size: number(p.size, 0, 10000), color: typeof p.color === 'string' ? p.color.slice(0, 80) : '#ffffff' }; };
async function image(value: unknown, width: number, height: number): Promise<HTMLCanvasElement> {
  if (typeof value !== 'string' || !value.startsWith('data:image/png;base64,') || value.length > 100_000_000) throw new Error('Invalid project image.');
  const blob = await (await fetch(value)).blob(), canvas = await decodeImage(blob);
  if (canvas.width !== width || canvas.height !== height) throw new Error('Project layer dimensions do not match.'); return canvas;
}
async function live(value: unknown, width: number, height: number): Promise<LiveSnapshot> {
  const saved = record(value);
  const applicators = ['marker', 'biro', 'callig', 'gouache', 'watercolor', 'mist', 'splatter', 'confetti', 'pencil', 'brush', 'oil', 'crayon', 'natural'];
  const strokes = array(saved.strokes, 10000).map(value => {
    const stroke = record(value); if (!applicators.includes(String(stroke.applicator))) throw new Error('Unknown project brush.');
    return { points: array(stroke.points, 100000).map(value => { const p = record(value); return { ...point(p), w: number(p.w, 0, 10000) }; }),
      opacity: number(stroke.opacity, 0, 1), applicator: stroke.applicator as Applicator, spec: spec(stroke.spec), generation: number(stroke.generation, 0), lane: number(stroke.lane, 0, 24), clip: stroke.clip ? array(stroke.clip, 1000).map(point) : null,
    };
  });
  const fills = await Promise.all(array(saved.fills, 2000).map(async value => {
    const fill = record(value), g = fill.gradient ? record(fill.gradient) : null;
    const gradient = g ? { x1: number(g.x1), y1: number(g.y1), x2: number(g.x2), y2: number(g.y2), from: String(g.from).slice(0, 80), to: String(g.to).slice(0, 80), preset: g.preset ? String(g.preset).slice(0, 80) : null } : null;
    return { mask: await image(fill.mask, width, height), opacity: number(fill.opacity, 0, 1), spec: spec(fill.spec), gradient, sparkles: array(fill.sparkles, 10000).map(spark) };
  }));
  return { strokes, fills, sparkles: array(saved.sparkles, 20000).map(spark) };
}
function objectInk(value:unknown):ObjectInk|null {if(value===null)return null;const ink=record(value);if(typeof ink.color!=='string'||ink.color.length>80)throw new Error('Invalid object ink.');return {color:ink.color,spec:ink.spec?spec(ink.spec):undefined};}
async function readObject(value:unknown,documentWidth:number,documentHeight:number):Promise<PaintObject> {
  const o=record(value),matrix=array(o.matrix,6).map(v=>number(v));if(matrix.length!==6||matrix[0]*matrix[3]-matrix[1]*matrix[2]===0)throw new Error('Invalid object transform.');
  const base={id:String(o.id).slice(0,100),name:String(o.name??'Piece').slice(0,60),width:number(o.width,.01),height:number(o.height,.01),matrix:matrix as ObjectMatrix,opacity:number(o.opacity,0,1)};
  if(o.kind==='raster'){
    const width=number(o.width,1,4096),height=number(o.height,1,4096);if(!Number.isInteger(width)||!Number.isInteger(height))throw new Error('Invalid object image size.');
    const origin=o.origin?point(o.origin):undefined;
    const liveSize=o.liveSize?{width:number(record(o.liveSize).width,1,4096),height:number(record(o.liveSize).height,1,4096)}:{width:documentWidth,height:documentHeight};
    return {...base,kind:'raster',image:await image(o.image,width,height),live:o.live?await live(o.live,liveSize.width,liveSize.height):undefined,liveSize,origin,clip:o.clip?array(o.clip,1000).map(point):undefined,blend:o.blend==='destination-out'?'destination-out':undefined};
  }
  if(o.kind==='path')return {...base,kind:'path',lineWidth:number(o.lineWidth,0,10000),fill:objectInk(o.fill),stroke:objectInk(o.stroke),paths:array(o.paths,24).map(value=>{const p=record(value);const transform=p.transform?array(p.transform,6).map(v=>number(v)):undefined;if(transform&&transform.length!==6)throw new Error('Invalid path transform.');return {points:array(p.points,1_000_000).map(point),clip:p.clip?array(p.clip,1000).map(point):undefined,closed:Boolean(p.closed),svg:typeof p.svg==='string'?p.svg.slice(0,10000):undefined,transform:transform as ObjectMatrix|undefined};})};
  if(o.kind==='text')return {...base,kind:'text',font:String(o.font).slice(0,300),size:number(o.size,1,10000),align:['left','center','right'].includes(String(o.align))?o.align as CanvasTextAlign:'left',color:String(o.color).slice(0,80),paper:o.paper?String(o.paper).slice(0,80):null,underline:Boolean(o.underline),strike:Boolean(o.strike),lines:array(o.lines,20000).map(value=>{const p=record(value);return {text:String(p.text).slice(0,20000),...point(p),width:number(p.width,0)};})};
  if(o.kind==='stamp')return {...base,kind:'stamp',emoji:String(o.emoji).slice(0,100),flipH:Boolean(o.flipH),flipV:Boolean(o.flipV),angle:number(o.angle)};
  throw new Error('Unknown project piece.');
}
export async function loadProjectData(source: string): Promise<boolean> {
  if(source.length>100_000_000)throw new Error('This project is too large to open.');
  const project = record(JSON.parse(source));
  if (project.format !== 'RetroPaint' || ![1,2,3,4,5,6,7,8,9].includes(project.version as number)) throw new Error('Choose a RetroPaint project file.');
  const width = number(project.width, 1, 4096), height = number(project.height, 1, 4096); dimensions(width, height);
  if (!Number.isInteger(width) || !Number.isInteger(height)) throw new Error('Invalid project dimensions.');
  const data = array(project.layers, 16); if (!data.length) throw new Error('This project has no layers.');
  if (width * height * data.length > 64_000_000) throw new Error('This project has too many pixels across its layers.');
  let plannedPixels=width*height*data.length;
  for(const value of data){const layer=record(value);if(layer.objects)for(const value of array(layer.objects,10000)){const object=record(value);if(object.kind==='raster')plannedPixels+=number(object.width,1,4096)*number(object.height,1,4096);}}
  if(plannedPixels>128_000_000)throw new Error('This project has too many pixels in its editable pieces.');
  const crop=project.crop===undefined?{x:0,y:0,width:1,height:1}:readPhotoCrop(project.crop);
  const snapshots: LayerSnapshot[] = await Promise.all(data.map(async value => {
    const layer = record(value), canvas = await image(layer.image, width, height);
    return { id: number(layer.id, 1), name: String(layer.name ?? 'Layer').slice(0, 60), visible: Boolean(layer.visible), opacity: number(layer.opacity, 0, 1), paper: typeof layer.paper === 'string' && /^#[\da-f]{6}$/i.test(layer.paper) ? layer.paper : null,
      image: canvas.getContext('2d')!.getImageData(0, 0, width, height), live: await live(layer.live, width, height),photo:readPhotoRecipe(layer.photo),cad:readCadLayer(layer.cad),objects:layer.objects?await Promise.all(array(layer.objects,10000).map(value=>readObject(value,width,height))):undefined };
  }));
  if (new Set(snapshots.map(layer => layer.id)).size !== snapshots.length) throw new Error('Project layer IDs must be unique.');
  const cadIds=snapshots.flatMap(layer=>layer.cad?.bodies.map(b=>b.id)??[]);if(new Set(cadIds).size!==cadIds.length)throw new Error('3D piece IDs must be unique across layers.');
  let objectPixels=width*height*snapshots.length;
  for(const layer of snapshots){if(new Set(layer.objects?.map(o=>o.id)).size!==layer.objects?.length&&layer.objects)throw new Error('Project piece IDs must be unique within a layer.');for(const object of layer.objects??[])if(object.kind==='raster')objectPixels+=object.width*object.height;}
  if(objectPixels>128_000_000)throw new Error('This project has too many pixels in its editable pieces.');
  const solids=snapshots.flatMap(layer=>layer.cad?.bodies??[]);
  if(solids.length){const{cadCompute}=await import('./cad-engine');for(const solid of solids)await cadCompute([solid]);}
  if (!editable()) return false;
  settle(); pushHistory(); restoreLayers(snapshots, number(project.active, 1), width, height); setDocumentCrop(crop);state.drawingMode=project.drawingMode==='vector'?'vector':'raster';document.body.classList.toggle('vector-mode',state.drawingMode==='vector');const mode=document.getElementById('drawingMode') as HTMLSelectElement|null;if(mode)mode.value=state.drawingMode;artwork.markWork();emit('document-opened');message('Project opened with editable pieces, layers, photo adjustments and live ink.');return true;
}
export async function openProjectFile(file: File): Promise<void> {
  if (file.size > 100_000_000) throw new Error('This project is too large to open.');
  await loadProjectData(await file.text());
}
