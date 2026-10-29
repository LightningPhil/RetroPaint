import { cropPixels, type CropBox } from './photo-engine';

let frame:CropBox={x:0,y:0,width:1,height:1};
let expanded=false;
export function documentCrop():CropBox { return {...frame}; }
export function setDocumentCrop(value:CropBox):void {
  const x=Math.max(0,Math.min(.999999,value.x)),y=Math.max(0,Math.min(.999999,value.y));
  frame={x,y,width:Math.max(.000001,Math.min(1-x,value.width)),height:Math.max(.000001,Math.min(1-y,value.height))};
  document.dispatchEvent(new Event('document-frame'));
}
export function resetDocumentCrop():void { frame={x:0,y:0,width:1,height:1};expanded=false; }
export function expandPhotoFrame(value:boolean):void { if(expanded!==value){expanded=value;document.dispatchEvent(new Event('document-frame'));} }
export function displayFrame(width:number,height:number):ReturnType<typeof cropPixels> { return expanded?{x:0,y:0,width,height}:cropPixels(frame,width,height); }
export function outputFrame(width:number,height:number):ReturnType<typeof cropPixels> { return cropPixels(frame,width,height); }
