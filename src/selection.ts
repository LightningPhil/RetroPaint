import { base, baseCtx, cloneCanvas, H, resetPaint, W } from './canvas';
import { emit } from './bus';
import { captureHistory, pushHistory, restoreHistory, type Hist } from './history';
import { bakeLive, renderLive } from './live';
import { state } from './state';

type Point = { x: number; y: number };
interface Selection {
  original: HTMLCanvasElement;
  image: HTMLCanvasElement;
  points: Point[];
  x: number; y: number;
  sourceX: number; sourceY: number;
  floating: boolean;
  before: Hist | null;
}
let selected: Selection | null = null;
let clipboard: HTMLCanvasElement | null = null;

export function hasSelection(): boolean { return selected !== null; }
export function hasClipboard(): boolean { return clipboard !== null; }
function changed(): void { emit('selection'); }

export function rectangle(x0: number, y0: number, x1: number, y1: number): Point[] {
  return [{ x: x0, y: y0 }, { x: x1, y: y0 }, { x: x1, y: y1 }, { x: x0, y: y1 }];
}
function trace(ctx: CanvasRenderingContext2D, points: Point[]): void {
  ctx.beginPath();
  points.forEach((p, i) => i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y));
  ctx.closePath();
}
function transparent(image: HTMLCanvasElement): HTMLCanvasElement {
  const result = cloneCanvas(image);
  if (!state.transparentSelection) return result;
  const ctx = result.getContext('2d')!;
  const pixels = ctx.getImageData(0, 0, result.width, result.height);
  for (let i = 0; i < pixels.data.length; i += 4) {
    // Paint-style transparency: remove white paper, retain coloured artwork.
    if (pixels.data[i] >= 250 && pixels.data[i + 1] >= 250 && pixels.data[i + 2] >= 250) pixels.data[i + 3] = 0;
  }
  ctx.putImageData(pixels, 0, 0);
  return result;
}
export function refreshTransparency(): void {
  if (selected) selected.image = transparent(selected.original);
  changed();
}
export function selectRegion(points: Point[]): void {
  commitSelection();
  if (points.length < 3) return;
  points = points.map(p => ({ x: Math.max(0, Math.min(W, p.x)), y: Math.max(0, Math.min(H, p.y)) }));
  const x = Math.floor(Math.min(...points.map(p => p.x))), y = Math.floor(Math.min(...points.map(p => p.y)));
  const w = Math.ceil(Math.max(...points.map(p => p.x))) - x, h = Math.ceil(Math.max(...points.map(p => p.y))) - y;
  if (w < 3 || h < 3) return;
  const picture = cloneCanvas(base);
  renderLive(picture.getContext('2d')!, performance.now());
  const original = document.createElement('canvas');
  original.width = w; original.height = h;
  const ctx = original.getContext('2d')!;
  const local = points.map(p => ({ x: p.x - x, y: p.y - y }));
  trace(ctx, local); ctx.clip();
  ctx.drawImage(picture, -x, -y);
  selected = { original, image: transparent(original), points: local, x, y, sourceX: x, sourceY: y, floating: false, before: null };
  changed();
}
export function hitSelection(x: number, y: number): boolean {
  if (!selected) return false;
  const ctx = selected.image.getContext('2d')!;
  trace(ctx, selected.points);
  return ctx.isPointInPath(x - selected.x, y - selected.y);
}
function lift(): void {
  if (!selected || selected.floating) return;
  selected.before = captureHistory();
  bakeLive(baseCtx, performance.now());
  baseCtx.save();
  resetPaint(baseCtx);
  baseCtx.translate(selected.sourceX, selected.sourceY);
  trace(baseCtx, selected.points);
  baseCtx.fillStyle = '#ffffff'; baseCtx.fill();
  baseCtx.restore();
  selected.floating = true;
}
export function moveSelection(dx: number, dy: number): void {
  if (!selected || (!dx && !dy)) return;
  lift();
  selected.x = Math.max(0, Math.min(W - selected.image.width, selected.x + dx));
  selected.y = Math.max(0, Math.min(H - selected.image.height, selected.y + dy));
}
export function copySelection(): void {
  if (!selected) return;
  clipboard = cloneCanvas(selected.original);
  changed();
}
export function deleteSelection(): void {
  if (!selected) return;
  lift();
  pushHistory(selected.before!);
  selected = null;
  changed();
}
export function cutSelection(): void { copySelection(); deleteSelection(); }
export function pasteSelection(): void {
  if (!clipboard) return;
  commitSelection();
  const original = cloneCanvas(clipboard);
  const x = Math.round((W - original.width) / 2), y = Math.round((H - original.height) / 2);
  selected = { original, image: transparent(original), points: rectangle(0, 0, original.width, original.height),
    x, y, sourceX: x, sourceY: y, floating: true, before: captureHistory() };
  // Floating artwork must sit above the current live drawing after placement too.
  bakeLive(baseCtx, performance.now());
  changed();
}
export function commitSelection(): void {
  if (!selected) return;
  if (selected.floating) {
    pushHistory(selected.before!);
    resetPaint(baseCtx);
    baseCtx.drawImage(selected.image, Math.round(selected.x), Math.round(selected.y));
  }
  selected = null;
  changed();
}
export function cancelSelection(): void {
  if (!selected) return;
  if (selected.before) restoreHistory(selected.before);
  selected = null;
  changed();
}
export function renderSelection(ctx: CanvasRenderingContext2D, border = false): void {
  if (!selected) return;
  ctx.save();
  ctx.translate(Math.round(selected.x), Math.round(selected.y));
  if (!border && selected.floating) ctx.drawImage(selected.image, 0, 0);
  if (border) {
    trace(ctx, selected.points);
    ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3; ctx.stroke();
    ctx.strokeStyle = '#25335c'; ctx.lineWidth = 1.5; ctx.setLineDash([6, 5]); ctx.stroke();
  }
  ctx.restore();
}
