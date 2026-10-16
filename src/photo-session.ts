import { bus, emit } from './bus';
import { baseCtx, cloneCanvas, H, W } from './canvas';
import { pushHistory } from './history';
import { activeLayer, activeLayerId, layerChanged, renderActive, transformLayers } from './layers';
import { clearLive, snapshotLive } from './live';
import { drips } from './effects';
import { cropPixels, defaultPhotoSettings, type PhotoSettings } from './photo-engine';
import { clearPhotoPreview, setPhotoEditing, setPhotoPreview } from './photo-preview';

export interface PhotoSession {
  layer:number; name:string; original:HTMLCanvasElement; source:HTMLCanvasElement; small:ImageData;
  settings:PhotoSettings; preview:HTMLCanvasElement; compare:boolean; applying:boolean; rendering:boolean; revision:number; rendered:number;
}
export let photoSession:PhotoSession|null=null;
let worker:Worker|null=null, serial=0;
const jobs=new Map<number,{resolve:(image:ImageData)=>void; reject:(error:Error)=>void}>();
function processor(image:ImageData,settings:PhotoSettings):Promise<ImageData>{
  if(!worker){
    worker=new Worker(new URL('./photo-worker.ts',import.meta.url),{type:'module'});
    worker.onmessage=(event:MessageEvent<{id:number;image?:ImageData;error?:string}>)=>{
      const job=jobs.get(event.data.id);if(!job)return;jobs.delete(event.data.id);
      if(event.data.image)job.resolve(event.data.image);else job.reject(new Error(event.data.error||'Photo processing failed.'));
    };
    worker.onerror=()=>{for(const job of jobs.values())job.reject(new Error('Photo processing could not start. Close Photo lab and try again.'));jobs.clear();worker?.terminate();worker=null;};
  }
  const id=++serial;
  return new Promise((resolve,reject)=>{jobs.set(id,{resolve,reject});worker!.postMessage({id,image,settings},{transfer:[image.data.buffer]});});
}
function dispose():void{
  worker?.terminate();worker=null;for(const job of jobs.values())job.reject(new Error('Photo edit cancelled.'));jobs.clear();
}
export function beginPhoto():PhotoSession{
  cancelPhoto();
  const source=cloneCanvas(activeLayer().canvas);renderActive(source.getContext('2d')!,performance.now());
  const scale=Math.min(1,720/Math.max(W,H)),preview=document.createElement('canvas');preview.width=Math.max(1,Math.round(W*scale));preview.height=Math.max(1,Math.round(H*scale));
  const ctx=preview.getContext('2d',{willReadFrequently:true})!;ctx.drawImage(source,0,0,preview.width,preview.height);
  photoSession={layer:activeLayerId,name:activeLayer().name,original:activeLayer().canvas,source,small:ctx.getImageData(0,0,preview.width,preview.height),settings:defaultPhotoSettings(),preview,compare:false,applying:false,rendering:false,revision:0,rendered:0};
  setPhotoEditing(true);setPhotoPreview(activeLayerId,source);emit('photo-update');return photoSession;
}
export function cancelPhoto():boolean{
  if(!photoSession)return false;photoSession=null;dispose();clearPhotoPreview();setPhotoEditing(false);emit('photo-end');return true;
}
export function comparePhoto(value:boolean):void{
  const session=photoSession;if(!session)return;session.compare=value;setPhotoPreview(session.layer,value?session.source:session.preview);emit('photo-update');
}
export async function refreshPhoto():Promise<void>{
  const session=photoSession;if(!session||session.applying)return;session.compare=false;session.revision++;emit('photo-update');
  if(session.rendering)return;session.rendering=true;
  try{
    while(photoSession===session&&!session.applying&&session.rendered!==session.revision){
      const revision=session.revision,image=new ImageData(session.small.data.slice(),session.small.width,session.small.height);
      const result=await processor(image,structuredClone(session.settings));
      if(photoSession!==session)return;
      session.preview.getContext('2d')!.putImageData(result,0,0);session.rendered=revision;
      if(!session.compare)setPhotoPreview(session.layer,session.preview);emit('photo-update');
    }
  }catch(error){if(photoSession===session)emit('photo-error',error instanceof Error?error.message:String(error));}
  finally{session.rendering=false;}
}
export async function applyPhoto():Promise<boolean>{
  const session=photoSession;if(!session||session.applying)return false;
  if(JSON.stringify(session.settings)===JSON.stringify(defaultPhotoSettings())){cancelPhoto();return false;}
  session.applying=true;emit('photo-update');
  try{
    const image=session.source.getContext('2d')!.getImageData(0,0,W,H),result=await processor(image,structuredClone(session.settings));
    if(photoSession!==session)return false;
    if(activeLayerId!==session.layer||activeLayer().canvas!==session.original)throw new Error('The layer changed. Open Photo lab again.');
    const crop=cropPixels(session.settings.crop,W,H);
    // Only the completed result enters history. Preview and Cancel never touch document pixels.
    pushHistory();baseCtx.putImageData(result,0,0);clearLive();activeLayer().live=snapshotLive();
    for(let i=drips.length-1;i>=0;i--)if(drips[i].target===baseCtx)drips.splice(i,1);
    photoSession=null;dispose();clearPhotoPreview();setPhotoEditing(false);
    if(crop.x||crop.y||crop.width!==W||crop.height!==H)transformLayers(crop.width,crop.height,[1,0,0,1,-crop.x,-crop.y]);
    else layerChanged();
    emit('photo-end');return true;
  }catch(error){if(photoSession===session){session.applying=false;emit('photo-update');throw error;}return false;}
}
bus.addEventListener('layers',()=>{if(photoSession&&(activeLayerId!==photoSession.layer||activeLayer().canvas!==photoSession.original))cancelPhoto();});
document.addEventListener('canvas-size',()=>cancelPhoto());
