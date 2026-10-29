import type { TextObject } from './object-scene';

export function calloutConnection(width:number,height:number,tip:{x:number;y:number},rounded:boolean):{x:number;y:number} {
  let x=Math.max(0,Math.min(width,tip.x)),y=Math.max(0,Math.min(height,tip.y));
  const r=rounded?Math.min(8,height/4):0;
  if(r&&(x<r||x>width-r)&&(y<r||y>height-r)){
    const cx=x<r?r:width-r,cy=y<r?r:height-r,dx=tip.x-cx,dy=tip.y-cy,length=Math.hypot(dx,dy);
    if(length>r){x=cx+r*dx/length;y=cy+r*dy/length;}
  }
  return {x,y};
}

/** Auto-size to the laid-out words, retaining comfortable padding. */
export function fitCallout(object:TextObject,border=true,rounded=true,tip={x:object.width+80,y:object.height+80}):TextObject {
  const width=Math.max(32,...object.lines.map(line=>line.width+24));
  return {...object,width,height:object.height+16,lines:object.lines.map(line=>({...line,x:object.align==='center'?width/2:object.align==='right'?width-12:12,y:line.y+8})),callout:{border,rounded,tip}};
}
export function calloutHandles(object:TextObject):{x:number;y:number}[] {
  if(!object.callout)return [];
  return [object.callout.tip,{x:object.width/2,y:object.height/2}].map(({x,y})=>({x:object.matrix[0]*x+object.matrix[2]*y+object.matrix[4],y:object.matrix[1]*x+object.matrix[3]*y+object.matrix[5]}));
}
