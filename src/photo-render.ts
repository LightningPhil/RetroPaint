import { bus } from './bus';
import { documentCrop } from './document-frame';
import { processPhoto } from './photo-engine';
import type { CropBox } from './photo-engine';
import { PhotoProcessor } from './photo-processor';
import type { PhotoRecipe } from './photo-recipe';

interface RenderCache { canvas:HTMLCanvasElement; source:HTMLCanvasElement; stamp:string; busy:boolean; time:number }
const cache=new WeakMap<PhotoRecipe,RenderCache>(),versions=new WeakMap<HTMLCanvasElement,number>();
const processor=new PhotoProcessor();let epoch=0;
export function invalidatePhotoCanvas(canvas:HTMLCanvasElement):void { versions.set(canvas,(versions.get(canvas)||0)+1); }
export function invalidatePhotoRenders():void { epoch++; }
export function seedPhotoRender(recipe:PhotoRecipe,source:HTMLCanvasElement,image:ImageData):void {
  const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;canvas.getContext('2d')!.putImageData(image,0,0);
  cache.set(recipe,{canvas,source,stamp:`${epoch}:${versions.get(source)||0}:${JSON.stringify(documentCrop())}`,busy:false,time:performance.now()});
}
export function cachedPhotoRender(recipe:PhotoRecipe,source?:HTMLCanvasElement):HTMLCanvasElement|undefined {
  const entry=cache.get(recipe);
  return entry&&(!source||entry.source===source)?entry.canvas:undefined;
}
// Paint/live data remains the source. This cache is disposable, never an edited original.
export function renderPhotoSurface(recipe:PhotoRecipe,source:HTMLCanvasElement,composite:HTMLCanvasElement,now:number,animated:boolean):HTMLCanvasElement {
  const stamp=`${epoch}:${versions.get(source)||0}:${JSON.stringify(documentCrop())}`;
  let entry=cache.get(recipe);
  if(!entry||entry.source!==source){
    const canvas=document.createElement('canvas'),scale=Math.min(1,360/Math.max(composite.width,composite.height));
    canvas.width=Math.max(1,Math.round(composite.width*scale));canvas.height=Math.max(1,Math.round(composite.height*scale));
    const ctx=canvas.getContext('2d')!;
    ctx.drawImage(composite,0,0,canvas.width,canvas.height);
    ctx.putImageData(processPhoto(ctx.getImageData(0,0,canvas.width,canvas.height),{...recipe.settings,crop:documentCrop()}),0,0);
    entry={canvas,source,stamp:'',busy:false,time:0};cache.set(recipe,entry);
  }
  if(!entry.busy&&(entry.stamp!==stamp||animated&&now-entry.time>100)){
    entry.busy=true;const pending=entry,scale=animated?Math.min(1,640/Math.max(composite.width,composite.height)):1,sample=document.createElement('canvas');
    sample.width=Math.max(1,Math.round(composite.width*scale));sample.height=Math.max(1,Math.round(composite.height*scale));sample.getContext('2d')!.drawImage(composite,0,0,sample.width,sample.height);
    void processor.process(sample.getContext('2d')!.getImageData(0,0,sample.width,sample.height),{...recipe.settings,crop:documentCrop()}).then(image=>{
      pending.canvas.width=image.width;pending.canvas.height=image.height;pending.canvas.getContext('2d')!.putImageData(image,0,0);pending.source=source;pending.stamp=stamp;pending.time=now;
    }).catch(()=>{pending.stamp=stamp;pending.time=now;}).finally(()=>{pending.busy=false;});
  }
  return entry.canvas;
}
export function renderPhotoPixels(recipe:PhotoRecipe,canvas:HTMLCanvasElement):ImageData {
  return processPhoto(canvas.getContext('2d')!.getImageData(0,0,canvas.width,canvas.height),{...recipe.settings,crop:documentCrop()});
}
export async function fullPhotoPixels(recipe:PhotoRecipe,image:ImageData,crop:CropBox=documentCrop()):Promise<ImageData> { return processor.process(image,{...recipe.settings,crop}); }
bus.addEventListener('history',invalidatePhotoRenders);
document.addEventListener('document-frame',invalidatePhotoRenders);
