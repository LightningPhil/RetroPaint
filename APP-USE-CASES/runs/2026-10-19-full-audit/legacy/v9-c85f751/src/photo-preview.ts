// Preview surfaces never replace document pixels or enter project/history snapshots.
import { invalidatePicture } from './render-state';
let preview: { layer:number; canvas:HTMLCanvasElement } | null = null;
export let photoEditing = false;
export function setPhotoEditing(value:boolean):void { photoEditing=value;invalidatePicture(); }
export function setPhotoPreview(layer:number,canvas:HTMLCanvasElement):void { preview={layer,canvas};invalidatePicture(); }
export function clearPhotoPreview():void { preview=null;invalidatePicture(); }
export function photoPreview(layer:number):HTMLCanvasElement|null { return preview?.layer===layer?preview.canvas:null; }
