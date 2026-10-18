import { enhancementSize, type EnhancementScale, type EnhancementProgress, type EnhancementRegion } from './enhancement-size';
export { enhancementSize, enhancementRegion, type EnhancementScale, type EnhancementProgress, type EnhancementRegion } from './enhancement-size';
interface EnhancementResult { image?:ImageData;png?:Blob;error?:string;progress?:EnhancementProgress }
export class SuperResolutionProcessor {
  private worker:Worker|null=null;
  private reject:((error:Error)=>void)|null=null;
  process(image:ImageData,scale:EnhancementScale,progress:(value:EnhancementProgress)=>void):Promise<ImageData>{
    return this.run(image,scale,progress,result=>{if(!result.image)throw new Error('No enhanced image was produced.');return result.image;});
  }
  processPng(image:ImageData,scale:EnhancementScale,region:EnhancementRegion,progress:(value:EnhancementProgress)=>void):Promise<{png:Blob;preview:ImageData}>{
    return this.run(image,scale,progress,result=>{if(!result.png||!result.image)throw new Error('No enhanced PNG was produced.');return {png:result.png,preview:result.image};},region);
  }
  private run<T>(image:ImageData,scale:EnhancementScale,progress:(value:EnhancementProgress)=>void,resultValue:(result:EnhancementResult)=>T,region?:EnhancementRegion):Promise<T>{
    enhancementSize(image.width,image.height,scale);
    if(this.reject)throw new Error('An enhancement is already running.');
    this.worker??=new Worker(new URL('./super-resolution-worker.ts',import.meta.url),{type:'module'});
    return new Promise((resolve,reject)=>{
      this.reject=reject;
      this.worker!.onmessage=(event:MessageEvent<EnhancementResult>)=>{
        if(event.data.progress){progress(event.data.progress);return;}
        this.reject=null;
        try{if(event.data.error)throw new Error(event.data.error);resolve(resultValue(event.data));}catch(error){reject(error);}
      };
      this.worker!.onerror=()=>this.dispose('The enhancement engine could not start. Please try again.');
      this.worker!.postMessage({image,scale,region},{transfer:[image.data.buffer]});
    });
  }
  dispose(reason='Enhancement cancelled.'):void {this.worker?.terminate();this.worker=null;this.reject?.(new Error(reason));this.reject=null;}
}
