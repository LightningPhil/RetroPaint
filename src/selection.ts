import { base, baseCtx, cloneCanvas, H, resetPaint, W } from './canvas';
import { emit } from './bus';
import { captureHistory, pushHistory, restoreHistory, type Hist } from './history';
import { bakeLive, renderLive } from './live';
import { state } from './state';
import { activeSector, clipPolygon, clipToSector, insideSector, sectorPolygon, type Sector } from './symmetry-mask';
import { symmetryTransforms } from './symmetry';

type Point = { x: number; y: number };
interface Selection {
  sector: Sector | null;
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
  const sector = activeSector();
  points = clipToSector(points, sector);
  if (points.length < 3) return;
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
  selected = { sector, original, image: transparent(original), points: local, x, y, sourceX: x, sourceY: y, floating: false, before: null };
  changed();
}
export function hitSelection(x: number, y: number): boolean {
  if (!selected || !insideSector(x, y, selected.sector)) return false;
  const ctx = selected.image.getContext('2d')!;
  trace(ctx, selected.points);
  return ctx.isPointInPath(x - selected.x, y - selected.y);
}
function lift(): void {
  if (!selected || selected.floating) return;
  selected.before = captureHistory();
  bakeLive(baseCtx, performance.now());
  const selection = selected;
  eachLane(baseCtx, selection.sector, () => {
    baseCtx.translate(selection.sourceX, selection.sourceY);
    trace(baseCtx, selection.points);
    baseCtx.fillStyle = '#ffffff'; baseCtx.fill();
  });
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
  if (selected.sector) {
    const ctx = clipboard.getContext('2d')!;
    ctx.clearRect(0, 0, clipboard.width, clipboard.height);
    ctx.translate(-Math.round(selected.x), -Math.round(selected.y));
    clipPolygon(ctx, sectorPolygon(selected.sector));
    ctx.drawImage(selected.original, Math.round(selected.x), Math.round(selected.y));
  }
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
  const sector = activeSector();
  // Start inside the working slice so a pasted piece is immediately visible.
  const polygon = sector ? sectorPolygon(sector) : rectangle(0, 0, W, H);
  const center = polygon.reduce((sum, p) => ({x:sum.x+p.x/polygon.length,y:sum.y+p.y/polygon.length}), {x:0,y:0});
  const x = Math.round(Math.max(0, Math.min(W-original.width, center.x-original.width/2)));
  const y = Math.round(Math.max(0, Math.min(H-original.height, center.y-original.height/2)));
  selected = { sector, original, image: transparent(original), points: rectangle(0, 0, original.width, original.height),
    x, y, sourceX: x, sourceY: y, floating: true, before: captureHistory() };
  // Floating artwork must sit above the current live drawing after placement too.
  bakeLive(baseCtx, performance.now());
  changed();
}
export function commitSelection(): void {
  if (!selected) return;
  if (selected.floating) {
    pushHistory(selected.before!);
    renderSelection(baseCtx);
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
/** Use the captured slice for preview, removal and final placement. */
function eachLane(ctx: CanvasRenderingContext2D, sector: Sector | null, draw: () => void): void {
  for (const t of symmetryTransforms(sector?.mode ?? 'off')) {
    ctx.save();
    resetPaint(ctx);
    ctx.translate(W/2,H/2); ctx.transform(t.a,t.c,t.b,t.d,0,0); ctx.translate(-W/2,-H/2);
    if (sector) clipPolygon(ctx, sectorPolygon(sector));
    draw(); ctx.restore();
  }
}
export function renderSelection(ctx: CanvasRenderingContext2D, border = false): void {
  if (!selected) return;
  const selection = selected;
  eachLane(ctx, selection.sector, () => {
    ctx.translate(Math.round(selection.x), Math.round(selection.y));
    if (!border && selection.floating) ctx.drawImage(selection.image, 0, 0);
    if (border) {
      trace(ctx, selection.points);
      ctx.strokeStyle = '#ffffff'; ctx.lineWidth = 3; ctx.stroke();
      ctx.strokeStyle = '#25335c'; ctx.lineWidth = 1.5; ctx.setLineDash([6, 5]); ctx.stroke();
    }
  });
}
