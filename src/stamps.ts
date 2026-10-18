import { activeSector, sectorPolygon, clipPolygon } from './symmetry-mask';
import { playThrottled } from './audio';
import { baseCtx, W, H } from './canvas';
import { symmetryTransforms } from './symmetry';
import { state } from './state';
import { bakeStaticStrokes } from './live';
import { addPaintObject, makePathObject, objectId } from './objects';
import { shapePoints } from './shapes';
import { multiply } from './object-scene';

export const STAMP_BANKS: { id: string; label: string; items: string[] }[] = [
  { id: 'critters', label: '🐾 Animals', items: ['🐶', '🐱', '🐭', '🐰', '🦊', '🐸', '🐧', '🐢', '🐙', '🦋', '🦄', '🦁', '🐨', '🐼', '🐝', '🐬', '🦉', '🦕'] },
  { id: 'scenery', label: '🌿 Nature', items: ['🌳', '🌴', '🌵', '🌸', '⭐', '🌈', '⛰️', '🌊', '☀️', '🌙', '🍄', '🌻', '🍀', '❄️', '🌎', '🌺', '🍁', '🐚'] },
  { id: 'rides', label: '🚀 Rides', items: ['🚗', '🚌', '🏎️', '🚜', '✈️', '🚀', '🛸', '⛵', '🚲', '🚂', '🚁', '🚒', '🚑', '🛵', '🎈', '🛶', '🚢', '🛰️'] },
  { id: 'history', label: '🏰 Adventure', items: ['🏰', '👑', '⚔️', '🛡️', '🗿', '🏺', '🦖', '🌋', '📯', '⚓', '🧙', '🧚', '🐉', '💎', '🗺️', '🏴‍☠️', '🔮', '🦴'] },
  { id: 'cartoons', label: '🤖 Faces', items: ['🤖', '👽', '👾', '🤡', '👻', '🎃', '😀', '😎', '🤩', '💩', '🥳', '😴', '😍', '🙃', '😺', '🥸', '😇', '🤠'] },
  { id: 'treats', label: '🍓 Treats', items: ['🍓', '🍉', '🍒', '🍋', '🍎', '🍇', '🍍', '🥕', '🍕', '🍔', '🍟', '🍿', '🍩', '🍪', '🧁', '🍦', '🍭', '🎂'] },
  { id: 'play', label: '⚽ Play', items: ['⚽', '🏀', '🎾', '🏈', '🏓', '🪁', '🎸', '🥁', '🎹', '🎺', '🎨', '🧩', '🎲', '🧸', '🎁', '🏆', '🎯', '🎪'] },
  { id: 'shapes', label: '★ Shapes', items: ['vec:star', 'vec:heart', 'vec:triangle', 'vec:diamond', 'vec:blob'] },
];

export function placeStamp(x: number, y: number): void {
  if(state.drawingMode==='vector'){
    const size=82*state.stampScale,angle=state.stampSpin==='auto'?(Math.random()-.5)*28*Math.PI/180:0;
    if(state.stampId.startsWith('vec:')){
      const names:Record<string,Parameters<typeof shapePoints>[0]>={'vec:star':'star5','vec:heart':'heart','vec:triangle':'triangle','vec:diamond':'diamond','vec:blob':'ellipse'};
      const fill=state.shapeFill,outline=state.shapeOutline;state.shapeFill='primary';state.shapeOutline='solid';
      const points=shapePoints(names[state.stampId]??'ellipse',x-size/2,y-size/2,x+size/2,y+size/2).map(p=>{const dx=(p.x-x)*(state.stampFlipH?-1:1),dy=(p.y-y)*(state.stampFlipV?-1:1);return {x:x+Math.cos(angle)*dx-Math.sin(angle)*dy,y:y+Math.sin(angle)*dx+Math.cos(angle)*dy};});
      const object=makePathObject(points,true,'Stamp');object.lineWidth=4*state.stampScale;object.stroke={color:'#1A1A1A'};state.shapeFill=fill;state.shapeOutline=outline;addPaintObject(object,false);
    } else for(const t of symmetryTransforms()){
      const m:[number,number,number,number,number,number]=[t.a,t.c,t.b,t.d,W/2-t.a*W/2-t.b*H/2,H/2-t.c*W/2-t.d*H/2];
      addPaintObject({id:objectId(),name:'Stamp',kind:'stamp',emoji:state.stampId,width:size,height:size,matrix:multiply(m,[1,0,0,1,x-size/2,y-size/2]),opacity:state.opacity,angle,flipH:state.stampFlipH,flipV:state.stampFlipV},false);
    }
    playThrottled('thwack',42);return;
  }
  bakeStaticStrokes(baseCtx);
  const jiggle = state.stampSpin === 'auto' ? (Math.random() - 0.5) * ((28 * Math.PI) / 180) : 0;
  for (const t of symmetryTransforms()) {
    baseCtx.save();
    baseCtx.translate(W / 2, H / 2);
    baseCtx.transform(t.a, t.c, t.b, t.d, 0, 0);
    baseCtx.translate(-W / 2, -H / 2);
    const sector=activeSector();
    if (sector) clipPolygon(baseCtx,sectorPolygon(sector));
    drawStamp(baseCtx,x,y,jiggle);
    baseCtx.restore();
  }
  playThrottled('thwack', 42, 0.75 + Math.random() * 0.5);
}

export function drawStampPreview(ctx:CanvasRenderingContext2D,x:number,y:number):void {
  ctx.save();ctx.globalAlpha=.4;
  for(const t of symmetryTransforms()){
    ctx.save();ctx.translate(W/2,H/2);ctx.transform(t.a,t.c,t.b,t.d,0,0);ctx.translate(-W/2,-H/2);
    const sector=activeSector();if(sector)clipPolygon(ctx,sectorPolygon(sector));drawStamp(ctx,x,y,0);ctx.restore();
  }
  ctx.restore();
}
function drawStamp(ctx:CanvasRenderingContext2D,x: number, y: number, jiggle: number): void {
  const scale = state.stampScale;
  ctx.save();
  ctx.globalAlpha *= state.opacity;
  ctx.translate(x, y);
  ctx.rotate(jiggle);
  ctx.scale(state.stampFlipH ? -scale : scale, state.stampFlipV ? -scale : scale);
  if (state.stampId.startsWith('vec:')) {
    drawVector(ctx, state.stampId);
  } else {
    ctx.font = '68px "Segoe UI Emoji", "Apple Color Emoji", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(state.stampId, 0, 0);
  }
  ctx.restore();
}

function drawVector(ctx: CanvasRenderingContext2D, id: string): void {
  ctx.fillStyle = state.ink.startsWith('#') ? state.ink : '#EF476F';
  ctx.strokeStyle = '#1A1A1A';
  ctx.lineWidth = 4;
  ctx.beginPath();
  if (id === 'vec:star') {
    for (let i = 0; i < 10; i++) {
      const r = i % 2 === 0 ? 36 : 16;
      const a = -Math.PI / 2 + (i * Math.PI) / 5;
      const x = Math.cos(a) * r;
      const y = Math.sin(a) * r;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
  } else if (id === 'vec:heart') {
    ctx.moveTo(0, 16);
    ctx.bezierCurveTo(-40, -10, -20, -36, 0, -16);
    ctx.bezierCurveTo(20, -36, 40, -10, 0, 16);
  } else if (id === 'vec:triangle') {
    ctx.moveTo(0, -34);
    ctx.lineTo(32, 28);
    ctx.lineTo(-32, 28);
    ctx.closePath();
  } else if (id === 'vec:diamond') {
    ctx.moveTo(0, -36);
    ctx.lineTo(28, 0);
    ctx.lineTo(0, 36);
    ctx.lineTo(-28, 0);
    ctx.closePath();
  } else {
    ctx.arc(0, 0, 30, 0, Math.PI * 2);
  }
  ctx.fill();
  ctx.stroke();
}
