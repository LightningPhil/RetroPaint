import { activeSector, sectorPolygon, clipPolygon } from './symmetry-mask';
import { playThrottled } from './audio';
import { baseCtx, W, H } from './canvas';
import { symmetryTransforms } from './symmetry';
import { state } from './state';
import { bakeStaticStrokes } from './live';

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
  bakeStaticStrokes(baseCtx);
  const jiggle = state.stampSpin === 'auto' ? (Math.random() - 0.5) * ((28 * Math.PI) / 180) : 0;
  for (const t of symmetryTransforms()) {
    baseCtx.save();
    baseCtx.translate(W / 2, H / 2);
    baseCtx.transform(t.a, t.c, t.b, t.d, 0, 0);
    baseCtx.translate(-W / 2, -H / 2);
    const sector=activeSector();
    if (sector) clipPolygon(baseCtx,sectorPolygon(sector));
    drawStamp(x, y, jiggle);
    baseCtx.restore();
  }
  playThrottled('thwack', 42, 0.75 + Math.random() * 0.5);
}

function drawStamp(x: number, y: number, jiggle: number): void {
  const scale = state.stampScale;
  baseCtx.save();
  baseCtx.globalAlpha = state.opacity;
  baseCtx.translate(x, y);
  baseCtx.rotate(jiggle);
  baseCtx.scale(state.stampFlipH ? -scale : scale, state.stampFlipV ? -scale : scale);
  if (state.stampId.startsWith('vec:')) {
    drawVector(baseCtx, state.stampId);
  } else {
    baseCtx.font = '68px "Segoe UI Emoji", "Apple Color Emoji", sans-serif';
    baseCtx.textAlign = 'center';
    baseCtx.textBaseline = 'middle';
    baseCtx.fillText(state.stampId, 0, 0);
  }
  baseCtx.restore();
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
