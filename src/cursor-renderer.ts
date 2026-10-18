import { H,view,viewCtx,W } from './canvas';
import { rgbToHex } from './color';
import { displayFrame } from './document-frame';
import { mirrorPoints } from './symmetry';
import { state } from './state';
import { drawStampPreview } from './stamps';
import { activeSector } from './symmetry-mask';

function footprint(ctx:CanvasRenderingContext2D,x:number,y:number,radius:number,scale:number,dashed:boolean):void {
  ctx.beginPath();ctx.arc(x,y,Math.max(2.5*scale,radius),0,Math.PI*2);ctx.lineWidth=3*scale;ctx.strokeStyle='#ffffffd9';ctx.stroke();
  ctx.lineWidth=scale;ctx.strokeStyle='#344654b8';ctx.setLineDash(dashed?[4*scale,4*scale]:[]);ctx.stroke();ctx.setLineDash([]);
}
export function renderToolCursor(ctx:CanvasRenderingContext2D):void {
  const point=state.cursor;if(!point||state.choosingSlice||document.getElementById('canvasSlot')?.classList.contains('moving-paper'))return;
  const scale=W/Math.max(1,view.getBoundingClientRect().width);ctx.save();
  if(['draw','eraser','sponge','spray'].includes(state.tool)){
    let radius=state.brushWidth*(state.applicator==='biro'?.08:state.applicator==='watercolor'?.69:state.applicator==='callig'?.56:.5);
    if(state.tool==='sponge')radius=Math.max(12,state.brushWidth);
    else if(state.tool==='spray')radius=state.brushWidth*(state.applicator==='splatter'?2.1:2.6);
    else if(state.tool==='eraser')radius=state.eraserMode==='blackhole'?58:state.eraserMode==='pixelate'?Math.max(22,state.brushWidth*1.4):state.eraserMode==='scrub'?(state.brushWidth<=4?state.brushWidth:Math.max(18,state.brushWidth*1.4))*.575:Math.max(20,state.brushWidth*1.3);
    const points=state.tool==='eraser'&&state.eraserMode!=='scrub'&&!activeSector()?[point]:mirrorPoints(point.x,point.y);for(const p of points)footprint(ctx,p.x,p.y,radius,scale,state.tool==='spray');
    if(radius>8*scale){ctx.beginPath();ctx.moveTo(point.x-2*scale,point.y);ctx.lineTo(point.x+2*scale,point.y);ctx.moveTo(point.x,point.y-2*scale);ctx.lineTo(point.x,point.y+2*scale);ctx.strokeStyle='#34465470';ctx.lineWidth=scale;ctx.stroke();}
  }else if(state.tool==='stamp')drawStampPreview(ctx,point.x,point.y);
  else if(state.tool==='picker')drawPicker(ctx,point.x,point.y,scale);
  ctx.restore();
}
function drawPicker(ctx:CanvasRenderingContext2D,x:number,y:number,scale:number):void {
  if(x<0||y<0||x>=W||y>=H)return;
  const frame=displayFrame(W,H);if(frame.width/scale<105||frame.height/scale<100)return;
  const size=58*scale,pad=8*scale,px=Math.min(frame.x+frame.width-size-pad,Math.max(frame.x+pad,x+19*scale)),py=Math.min(frame.y+frame.height-size-23*scale-pad,Math.max(frame.y+pad,y-size-20*scale));
  ctx.save();ctx.shadowColor='#253b4a50';ctx.shadowBlur=9*scale;ctx.shadowOffsetY=2*scale;ctx.fillStyle='#fffdf7';ctx.beginPath();ctx.roundRect(px-3*scale,py-3*scale,size+6*scale,size+27*scale,10*scale);ctx.fill();ctx.shadowBlur=ctx.shadowOffsetY=0;
  ctx.save();ctx.beginPath();ctx.roundRect(px,py,size,size,7*scale);ctx.clip();ctx.fillStyle='#d8dfda';ctx.fillRect(px,py,size,size);ctx.imageSmoothingEnabled=false;ctx.drawImage(view,Math.floor(x)-3,Math.floor(y)-3,7,7,px,py,size,size);ctx.restore();
  const cell=size/7;ctx.lineWidth=scale;ctx.strokeStyle='#ffffffb3';ctx.strokeRect(px+cell*3,py+cell*3,cell,cell);ctx.strokeStyle='#2f4052';ctx.strokeRect(px+cell*3-scale,py+cell*3-scale,cell+2*scale,cell+2*scale);
  const pixel=viewCtx.getImageData(Math.floor(x),Math.floor(y),1,1).data,color=rgbToHex(pixel[0],pixel[1],pixel[2]);
  ctx.fillStyle=pixel[3]?color:'#d8dfda';ctx.fillRect(px+2*scale,py+size+7*scale,9*scale,9*scale);ctx.font=`700 ${9*scale}px "Trebuchet MS",sans-serif`;ctx.fillStyle='#2f4052';ctx.textAlign='left';ctx.textBaseline='middle';ctx.fillText(pixel[3]?color.toUpperCase():'CLEAR',px+15*scale,py+size+12*scale);ctx.restore();
  footprint(ctx,Math.floor(x)+.5,Math.floor(y)+.5,2*scale,scale,false);
}
