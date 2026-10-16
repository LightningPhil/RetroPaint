import type { PhotoSettings } from './photo-engine';

export class PhotoProcessor {
  private worker:Worker|null=null;
  private serial=0;
  private jobs=new Map<number,{resolve:(image:ImageData)=>void;reject:(error:Error)=>void}>();
  process(image:ImageData,settings:PhotoSettings):Promise<ImageData>{
    if(!this.worker){
      this.worker=new Worker(new URL('./photo-worker.ts',import.meta.url),{type:'module'});
      this.worker.onmessage=(event:MessageEvent<{id:number;image?:ImageData;error?:string}>)=>{
        const job=this.jobs.get(event.data.id);if(!job)return;this.jobs.delete(event.data.id);
        if(event.data.image)job.resolve(event.data.image);else job.reject(new Error(event.data.error||'Photo processing failed.'));
      };
      this.worker.onerror=()=>this.dispose('Photo processing could not start. Please try again.');
    }
    const id=++this.serial;
    return new Promise((resolve,reject)=>{this.jobs.set(id,{resolve,reject});this.worker!.postMessage({id,image,settings},{transfer:[image.data.buffer]});});
  }
  dispose(reason='Photo edit cancelled.'):void {
    this.worker?.terminate();this.worker=null;for(const job of this.jobs.values())job.reject(new Error(reason));this.jobs.clear();
  }
}
