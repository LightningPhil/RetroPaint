import { processPhoto, type PhotoSettings } from './photo-engine';
self.onmessage = (event: MessageEvent<{ id:number; image:ImageData; settings:PhotoSettings }>) => {
  const { id,image,settings }=event.data;
  try { const result=processPhoto(image,settings); self.postMessage({ id,image:result },{ transfer:[result.data.buffer] }); }
  catch(error){ self.postMessage({ id,error:error instanceof Error?error.message:String(error) }); }
};
