export type EnhancementScale=2|4;
export interface EnhancementProgress { fraction:number; message:string }
export interface EnhancementRegion { x:number;y:number;width:number;height:number }
export function enhancementRegion(width:number,height:number,cx=.5,cy=.5,side=128):EnhancementRegion {
  const w=Math.min(width,side),h=Math.min(height,side);
  return {x:Math.max(0,Math.min(width-w,Math.round(cx*width-w/2))),y:Math.max(0,Math.min(height-h,Math.round(cy*height-h/2))),width:w,height:h};
}
export function enhancementSize(width:number,height:number,scale:EnhancementScale):{width:number;height:number} {
  if(![2,4].includes(scale)||!Number.isInteger(width)||!Number.isInteger(height)||width<1||height<1)throw new Error('Choose a 2× or 4× enhancement.');
  const w=width*scale,h=height*scale;
  if(w>16384||h>16384)throw new Error('Enhanced copies can be up to 16384 pixels per edge. Crop the picture or choose 2×.');
  return {width:w,height:h};
}
