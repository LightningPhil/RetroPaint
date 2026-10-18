import { superResolvePixels, superResolvePng } from './super-resolution-engine';
import type { EnhancementScale, EnhancementRegion } from './enhancement-size';
self.onmessage=async(event:MessageEvent<{image:ImageData;scale:EnhancementScale;region?:EnhancementRegion}>)=>{
  try{
    const {image:source,scale,region}=event.data,progress=(value:unknown)=>self.postMessage({progress:value});
    if(region){const result=await superResolvePng(source,scale,region,progress);self.postMessage({image:result.preview,png:result.png},{transfer:[result.preview.data.buffer]});}
    else{const image=await superResolvePixels(source,scale,progress);self.postMessage({image},{transfer:[image.data.buffer]});}
  }catch(error){self.postMessage({error:error instanceof Error?error.message:String(error)});}
};
