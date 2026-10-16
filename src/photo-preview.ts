// Preview surfaces never replace document pixels or enter project/history snapshots.
let preview: { layer:number; canvas:HTMLCanvasElement } | null = null;
export let photoEditing = false;
export function setPhotoEditing(value:boolean):void { photoEditing=value; }
export function setPhotoPreview(layer:number,canvas:HTMLCanvasElement):void { preview={layer,canvas}; }
export function clearPhotoPreview():void { preview=null; }
export function photoPreview(layer:number):HTMLCanvasElement|null { return preview?.layer===layer?preview.canvas:null; }
