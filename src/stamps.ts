import { play, playThrottled } from './audio';
import { baseCtx, H, W } from './canvas';
import { emit } from './bus';
import { mirrorPoints } from './draw';
import { pushHistory } from './history';
import { bakeLive, clearLive } from './live';
import { state } from './state';

export interface CustomStamp {
  canvas: HTMLCanvasElement;
  url: string;
}

export const customStamps: CustomStamp[] = [];

export const STAMP_BANKS: { id: string; label: string; items: string[] }[] = [
  { id: 'critters', label: 'Critters', items: ['🐶', '🐱', '🐭', '🐰', '🦊', '🐸', '🐧', '🐢', '🐙', '🦋'] },
  { id: 'scenery', label: 'Scenery', items: ['🌳', '🌴', '🌵', '🌸', '⭐', '🌈', '⛰️', '🌊', '☀️', '🌙'] },
  { id: 'rides', label: 'Rides', items: ['🚗', '🚌', '🏎️', '🚜', '✈️', '🚀', '🛸', '⛵', '🚲', '🚂'] },
  { id: 'history', label: 'History', items: ['🏰', '👑', '⚔️', '🛡️', '🗿', '🏺', '🦖', '🌋', '📯', '⚓'] },
  { id: 'cartoons', label: 'Toons', items: ['🤖', '👽', '👾', '🤡', '👻', '🎃', '😀', '😎', '🤩', '💩'] },
  { id: 'shapes', label: 'Shapes', items: ['vec:star', 'vec:heart', 'vec:triangle', 'vec:diamond', 'vec:blob'] },
];

export function placeStamp(x: number, y: number): void {
  for (const point of mirrorPoints(x, y)) drawStamp(point.x, point.y);
  playThrottled('thwack', 42, 0.75 + Math.random() * 0.5);
}

function drawStamp(x: number, y: number): void {
  const scale = state.stampScale;
  baseCtx.save();
  baseCtx.translate(x, y);
  baseCtx.rotate((state.stampRotation * Math.PI) / 180);
  baseCtx.scale(state.stampFlipH ? -scale : scale, state.stampFlipV ? -scale : scale);
  if (state.stampId.startsWith('custom:')) {
    const index = Number(state.stampId.slice(7));
    const stamp = customStamps[index];
    if (stamp) baseCtx.drawImage(stamp.canvas, -stamp.canvas.width / 2, -stamp.canvas.height / 2);
  } else if (state.stampId.startsWith('vec:')) {
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

export function cutSelection(points: { x: number; y: number }[]): CustomStamp | null {
  if (points.length < 12) return null;
  let minX = W;
  let minY = H;
  let maxX = 0;
  let maxY = 0;
  for (const p of points) {
    minX = Math.min(minX, p.x);
    minY = Math.min(minY, p.y);
    maxX = Math.max(maxX, p.x);
    maxY = Math.max(maxY, p.y);
  }
  const bw = Math.ceil(maxX - minX);
  const bh = Math.ceil(maxY - minY);
  if (bw < 8 || bh < 8) return null;

  pushHistory();
  bakeLive(baseCtx, performance.now());
  clearLive();

  const mask = document.createElement('canvas');
  mask.width = W;
  mask.height = H;
  const mctx = mask.getContext('2d')!;
  trace(mctx, points);
  mctx.clip();
  mctx.drawImage(baseCtx.canvas, 0, 0);

  const cut = document.createElement('canvas');
  cut.width = bw;
  cut.height = bh;
  cut.getContext('2d')!.drawImage(mask, minX, minY, bw, bh, 0, 0, bw, bh);

  baseCtx.save();
  trace(baseCtx, points);
  baseCtx.clip();
  baseCtx.globalCompositeOperation = 'source-over';
  baseCtx.fillStyle = '#ffffff';
  baseCtx.fillRect(0, 0, W, H);
  baseCtx.restore();

  const url = cut.toDataURL();
  const stamp = { canvas: cut, url };
  customStamps.push(stamp);
  if (customStamps.length > 16) customStamps.shift();
  state.stampId = `custom:${customStamps.length - 1}`;
  play('rip');
  emit('stamps');
  emit('cutout', { url, x: minX, y: minY, w: bw, h: bh });
  return stamp;
}

function trace(ctx: CanvasRenderingContext2D, points: { x: number; y: number }[]): void {
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (const p of points) ctx.lineTo(p.x, p.y);
  ctx.closePath();
}
