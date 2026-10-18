let revision=0;
export function invalidatePicture():void {revision++;}
export function pictureRevision():number {return revision;}
