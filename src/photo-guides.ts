import { H, W } from './canvas';
import { state } from './state';
import type { CropBox } from './photo-engine';
let crop:CropBox|null=null,line:{x:number;y:number;xx:number;yy:number}|null=null;
export function setPhotoGuides(box:CropBox|null,horizon:typeof line=null):void{crop=box;line=horizon;}
export function drawPhotoGuides(ctx:CanvasRenderingContext2D):void{
  ctx.save();ctx.lineWidth=1.5/Math.max(0.05,state.paperScale);ctx.strokeStyle='#ffffff';
  if(crop){
    const x=crop.x*W,y=crop.y*H,w=crop.width*W,h=crop.height*H;
    ctx.fillStyle='#18223799';ctx.beginPath();ctx.rect(0,0,W,H);ctx.rect(x,y,w,h);ctx.fill('evenodd');
    ctx.strokeRect(x,y,w,h);ctx.globalAlpha=.6;
    for(let i=1;i<3;i++){ctx.beginPath();ctx.moveTo(x+w*i/3,y);ctx.lineTo(x+w*i/3,y+h);ctx.moveTo(x,y+h*i/3);ctx.lineTo(x+w,y+h*i/3);ctx.stroke();}
    ctx.globalAlpha=1;ctx.fillStyle='#ffd16f';const r=5/Math.max(.05,state.paperScale);
    for(const [xx,yy] of [[x,y],[x+w,y],[x,y+h],[x+w,y+h]]){ctx.fillRect(xx-r,yy-r,r*2,r*2);ctx.strokeRect(xx-r,yy-r,r*2,r*2);}
  }
  if(line){ctx.strokeStyle='#ffd16f';ctx.beginPath();ctx.moveTo(line.x,line.y);ctx.lineTo(line.xx,line.yy);ctx.stroke();}
  ctx.restore();
}
