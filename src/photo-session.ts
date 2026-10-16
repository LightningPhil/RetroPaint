import { bus, emit } from './bus';
import { cloneCanvas, H, W } from './canvas';
import { pushHistory } from './history';
import { activeLayer, activeLayerId, layerChanged, renderActive } from './layers';
import { clearPhotoPreview, setPhotoEditing, setPhotoPreview } from './photo-preview';
import { documentCrop, expandPhotoFrame, setDocumentCrop } from './document-frame';
import { newPhotoRecipe, type PhotoRecipe } from './photo-recipe';
import { PhotoProcessor } from './photo-processor';
import { cachedPhotoRender, seedPhotoRender } from './photo-render';

export interface PhotoSession extends PhotoRecipe {
  layer:number; name:string; original:HTMLCanvasElement; source:HTMLCanvasElement; small:ImageData;
  preview:HTMLCanvasElement; compare:boolean; applying:boolean; rendering:boolean; revision:number; rendered:number; initial:string;
}
export let photoSession:PhotoSession|null=null;
const processor=new PhotoProcessor();
function recipeOf(session:PhotoSession):PhotoRecipe { return {settings:session.settings,normal:session.normal,look:session.look,lookActive:session.lookActive}; }
export function beginPhoto():PhotoSession {
  cancelPhoto();
  const layer=activeLayer(),source=cloneCanvas(layer.canvas);renderActive(source.getContext('2d')!,performance.now());
  const recipe=layer.photo?structuredClone(layer.photo):newPhotoRecipe();recipe.settings.crop=documentCrop();
  if(!recipe.lookActive)recipe.normal.crop=documentCrop();
  const scale=Math.min(1,720/Math.max(W,H)),preview=document.createElement('canvas');preview.width=Math.max(1,Math.round(W*scale));preview.height=Math.max(1,Math.round(H*scale));
  const ctx=preview.getContext('2d',{willReadFrequently:true})!;ctx.drawImage(source,0,0,preview.width,preview.height);const small=ctx.getImageData(0,0,preview.width,preview.height);
  const rendered=layer.photo?cachedPhotoRender(layer.photo,layer.canvas):undefined;
  if(rendered){ctx.clearRect(0,0,preview.width,preview.height);ctx.drawImage(rendered,0,0,preview.width,preview.height);}
  photoSession={...recipe,layer:activeLayerId,name:layer.name,original:layer.canvas,source,small,preview,compare:false,applying:false,rendering:false,revision:0,rendered:0,initial:JSON.stringify(recipe)};
  setPhotoEditing(true);if(rendered||!layer.photo)setPhotoPreview(activeLayerId,rendered||source);
  emit('photo-update');if(layer.photo)void refreshPhoto();return photoSession;
}
export function cancelPhoto():boolean {
  if(!photoSession)return false;photoSession=null;processor.dispose();clearPhotoPreview();setPhotoEditing(false);expandPhotoFrame(false);emit('photo-end');return true;
}
export function comparePhoto(value:boolean):void {
  const session=photoSession;if(!session)return;session.compare=value;setPhotoPreview(session.layer,value?session.source:session.preview);emit('photo-update');
}
export async function refreshPhoto():Promise<void> {
  const session=photoSession;if(!session||session.applying)return;session.compare=false;session.revision++;emit('photo-update');
  if(session.rendering)return;session.rendering=true;
  try {
    while(photoSession===session&&!session.applying&&session.rendered!==session.revision){
      const revision=session.revision,image=new ImageData(session.small.data.slice(),session.small.width,session.small.height);
      const result=await processor.process(image,structuredClone(session.settings));
      if(photoSession!==session)return;
      session.preview.getContext('2d')!.putImageData(result,0,0);session.rendered=revision;
      if(!session.compare)setPhotoPreview(session.layer,session.preview);emit('photo-update');
    }
  }catch(error){if(photoSession===session)emit('photo-error',error instanceof Error?error.message:String(error));}
  finally{session.rendering=false;}
}
export async function applyPhoto():Promise<boolean> {
  const session=photoSession;if(!session||session.applying)return false;
  if(JSON.stringify(recipeOf(session))===session.initial){cancelPhoto();return false;}
  session.applying=true;emit('photo-update');
  try {
    const image=session.source.getContext('2d')!.getImageData(0,0,W,H),result=await processor.process(image,structuredClone(session.settings));
    if(photoSession!==session)return false;
    if(activeLayerId!==session.layer||activeLayer().canvas!==session.original)throw new Error('The layer changed. Open Photo lab again.');
    // Save only the recipe and frame. Raw pixels, live ink and cropped margins remain intact.
    pushHistory();const recipe=structuredClone(recipeOf(session));activeLayer().photo=recipe;
    setDocumentCrop(session.settings.crop);seedPhotoRender(recipe,session.original,result);
    photoSession=null;processor.dispose();clearPhotoPreview();setPhotoEditing(false);expandPhotoFrame(false);layerChanged();emit('photo-end');return true;
  }catch(error){if(photoSession===session){session.applying=false;emit('photo-update');throw error;}return false;}
}
bus.addEventListener('layers',()=>{if(photoSession&&(activeLayerId!==photoSession.layer||activeLayer().canvas!==photoSession.original))cancelPhoto();});
document.addEventListener('canvas-size',()=>cancelPhoto());
