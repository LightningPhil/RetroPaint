import { base, baseCtx, cloneCanvas, H, resetPaint, W } from './canvas';
import { emit } from './bus';
import { captureHistory, pushHistory, restoreHistory, type Hist } from './history';
import { bakeLive, renderLive } from './live';
import { state } from './state';
import { activeSector, clipPolygon, clipToSector, insideSector, sectorPolygon, type Sector } from './symmetry-mask';
import { symmetryTransforms } from './symmetry';
import { activeLayer, eraseRegion } from './layers';

type Point = { x: number; y: number };
interface Selection {
  sector: Sector | null;
  original: HTMLCanvasElement;
  image: HTMLCanvasElement;
  points: Point[];
  excluded?: Point[];
  mask?: HTMLCanvasElement;
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
function selectionPath(ctx: CanvasRenderingContext2D, selection: Selection): void {
  trace(ctx, selection.points);
  if (selection.excluded) {
    selection.excluded.forEach((p, i) => i ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y)); ctx.closePath();
  }
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
  if (w < 1 || h < 1) return;
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
  if (selected.mask) {
    const px = Math.floor(x - selected.x), py = Math.floor(y - selected.y);
    return px >= 0 && py >= 0 && px < selected.mask.width && py < selected.mask.height && selected.mask.getContext('2d')!.getImageData(px, py, 1, 1).data[3] > 20;
  }
  selectionPath(ctx, selected);
  return ctx.isPointInPath(x - selected.x, y - selected.y, 'evenodd');
}
function lift(): void {
  if (!selected || selected.floating) return;
  selected.before = captureHistory();
  bakeLive(baseCtx, performance.now());
  const selection = selected;
  eachLane(baseCtx, selection.sector, () => {
    baseCtx.translate(selection.sourceX, selection.sourceY);
    if (selection.mask) {
      baseCtx.save(); baseCtx.globalCompositeOperation = 'destination-out'; baseCtx.drawImage(selection.mask, 0, 0); baseCtx.restore();
      if (activeLayer().paper) {
        const fill = cloneCanvas(selection.mask), ctx = fill.getContext('2d')!;
        ctx.globalCompositeOperation = 'source-in'; ctx.fillStyle = activeLayer().paper!; ctx.fillRect(0, 0, fill.width, fill.height); baseCtx.drawImage(fill, 0, 0);
      }
      return;
    }
    selectionPath(baseCtx, selection);
    eraseRegion(baseCtx, () => baseCtx.fill('evenodd'));
  });
  selected.floating = true;
}
export function moveSelection(dx: number, dy: number): void {
  if (!selected || (!dx && !dy)) return;
  lift();
  const right = W - selected.image.width, bottom = H - selected.image.height;
  selected.x = Math.max(Math.min(0, right), Math.min(Math.max(0, right), selected.x + dx));
  selected.y = Math.max(Math.min(0, bottom), Math.min(Math.max(0, bottom), selected.y + dy));
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
  void writeClipboard(clipboard);
}
async function writeClipboard(image: HTMLCanvasElement): Promise<void> {
  if (!navigator.clipboard?.write || typeof ClipboardItem === 'undefined') return;
  const blob = await new Promise<Blob | null>(resolve => image.toBlob(resolve));
  if (blob) try { await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]); } catch { /* The in-app clipboard remains available. */ }
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
  pasteImage(cloneCanvas(clipboard));
}
export function pasteImage(original: HTMLCanvasElement, at?: Point): void {
  commitSelection();
  const sector = activeSector();
  // Start inside the working slice so a pasted piece is immediately visible.
  const polygon = sector ? sectorPolygon(sector) : rectangle(0, 0, W, H);
  const center = polygon.reduce((sum, p) => ({x:sum.x+p.x/polygon.length,y:sum.y+p.y/polygon.length}), {x:0,y:0});
  const x = at?.x ?? Math.round(Math.max(0, Math.min(W-original.width, center.x-original.width/2)));
  const y = at?.y ?? Math.round(Math.max(0, Math.min(H-original.height, center.y-original.height/2)));
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
      if (!selection.sector) {
        ctx.setLineDash([]); ctx.fillStyle = '#ffd16f'; ctx.strokeStyle = '#25335c'; ctx.lineWidth = 1;
        for (const p of rectangle(0, 0, selection.image.width, selection.image.height)) {
          ctx.fillRect(p.x - 5, p.y - 5, 10, 10); ctx.strokeRect(p.x - 5, p.y - 5, 10, 10);
        }
      }
    }
  });
}

export function selectionBounds(): { x: number; y: number; width: number; height: number } | null {
  return selected ? { x: selected.x, y: selected.y, width: selected.image.width, height: selected.image.height } : null;
}
export function selectAll(): void { selectRegion(rectangle(0, 0, W, H)); }
export function invertSelection(): void {
  if (!selected || selected.sector) return;
  const previous = selected, mask = document.createElement('canvas'); mask.width = W; mask.height = H;
  const ctx = mask.getContext('2d')!; ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, W, H);
  ctx.translate(previous.x, previous.y); ctx.globalCompositeOperation = 'destination-out';
  if (previous.mask) ctx.drawImage(previous.mask, 0, 0);
  else { selectionPath(ctx, previous); ctx.fill('evenodd'); }
  const data = ctx.getImageData(0, 0, W, H).data, pixels = new Uint8Array(W * H);
  for (let i = 0; i < pixels.length; i++) pixels[i] = data[i * 4 + 3] > 127 ? 1 : 0;
  selectPixelMask(pixels);
}
export function transformSelection(matrix: [number, number, number, number, number, number], width: number, height: number): void {
  if (!selected) return;
  if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1 || width > 4096 || height > 4096 || matrix.some(n => !Number.isFinite(n))) throw new Error('The transformed selection must fit within 4096 × 4096 pixels.');
  lift(); const selection = selected, original = document.createElement('canvas');
  original.width = width; original.height = height;
  original.getContext('2d')!.imageSmoothingEnabled = state.smoothResize;
  original.getContext('2d')!.setTransform(...matrix); original.getContext('2d')!.drawImage(selection.original, 0, 0);
  const map = (p: Point) => ({ x: p.x * matrix[0] + p.y * matrix[2] + matrix[4], y: p.x * matrix[1] + p.y * matrix[3] + matrix[5] });
  selection.points = selection.points.map(map); selection.excluded = selection.excluded?.map(map);
  selection.original = original; selection.image = transparent(original); changed();
  if (selection.mask) {
    const mask = document.createElement('canvas'); mask.width = width; mask.height = height;
    const ctx = mask.getContext('2d')!; ctx.setTransform(...matrix); ctx.drawImage(selection.mask, 0, 0); selection.mask = mask;
  }
}
export function resizeSelection(width: number, height: number): void {
  if (!selected) return;
  transformSelection([width / selected.original.width, 0, 0, height / selected.original.height, 0, 0], width, height);
}
export function flipSelection(horizontal: boolean): void {
  if (!selected) return;
  const { width, height } = selected.original;
  transformSelection(horizontal ? [-1, 0, 0, 1, width, 0] : [1, 0, 0, -1, 0, height], width, height);
}
export function editSelectionPixels(edit: (image: ImageData) => void): void {
  if (!selected) return;
  lift(); selected.original = cloneCanvas(selected.original);
  const ctx = selected.original.getContext('2d')!, image = ctx.getImageData(0, 0, selected.original.width, selected.original.height);
  edit(image); ctx.putImageData(image, 0, 0); selected.image = transparent(selected.original); changed();
}
export function rotateSelection(degrees: number): void {
  if (!selected) return;
  const { width: w, height: h } = selected.original, r = degrees * Math.PI / 180, c = Math.cos(r), s = Math.sin(r);
  const width = Math.max(1, Math.ceil(Math.abs(w * c) + Math.abs(h * s) - 1e-8)), height = Math.max(1, Math.ceil(Math.abs(w * s) + Math.abs(h * c) - 1e-8));
  transformSelection([c, s, -s, c, width / 2 - c * w / 2 + s * h / 2, height / 2 - s * w / 2 - c * h / 2], width, height);
}
let resizing: { image: HTMLCanvasElement; points: Point[]; excluded?: Point[]; mask?: HTMLCanvasElement; x: number; y: number; corner: number } | null = null;
export function hitSelectionHandle(x: number, y: number): number | null {
  if (!selected || selected.sector) return null;
  const corners = rectangle(selected.x, selected.y, selected.x + selected.image.width, selected.y + selected.image.height);
  const radius = Math.max(9, W / Math.max(1, document.getElementById('view')?.getBoundingClientRect().width ?? W) * 10);
  const index = corners.findIndex(p => Math.hypot(p.x - x, p.y - y) <= radius); return index < 0 ? null : index;
}
export function beginSelectionResize(corner: number): void {
  if (!selected) return; lift(); resizing = { image: selected.original, points: selected.points, excluded: selected.excluded, mask: selected.mask, x: selected.x, y: selected.y, corner };
}
export function dragSelectionResize(x: number, y: number, proportional: boolean): void {
  if (!selected || !resizing) return;
  const r = resizing, left = r.corner === 0 || r.corner === 3, top = r.corner < 2;
  const fixedX = r.x + (left ? r.image.width : 0), fixedY = r.y + (top ? r.image.height : 0);
  let width = Math.max(1, Math.min(4096, Math.round(left ? fixedX - x : x - fixedX)));
  let height = Math.max(1, Math.min(4096, Math.round(top ? fixedY - y : y - fixedY)));
  if (proportional) { const scale = Math.min(width / r.image.width, height / r.image.height); width = Math.max(1, Math.round(r.image.width * scale)); height = Math.max(1, Math.round(r.image.height * scale)); }
  selected.original = r.image; selected.points = r.points; selected.excluded = r.excluded; selected.mask = r.mask;
  resizeSelection(width, height); selected.x = left ? fixedX - width : fixedX; selected.y = top ? fixedY - height : fixedY;
}
export function endSelectionResize(): void { resizing = null; }

export function selectPixelMask(pixels: Uint8Array): void {
  commitSelection();
  let left = W, top = H, right = 0, bottom = 0;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (pixels[y * W + x]) { left = Math.min(left, x); top = Math.min(top, y); right = Math.max(right, x + 1); bottom = Math.max(bottom, y + 1); }
  if (right <= left || bottom <= top) return;
  const mask = document.createElement('canvas'); mask.width = right - left; mask.height = bottom - top;
  const ctx = mask.getContext('2d')!, data = ctx.createImageData(mask.width, mask.height);
  for (let y = 0; y < mask.height; y++) for (let x = 0; x < mask.width; x++) if (pixels[(y + top) * W + x + left]) data.data.set([255, 255, 255, 255], (y * mask.width + x) * 4);
  ctx.putImageData(data, 0, 0);
  const picture = cloneCanvas(base); renderLive(picture.getContext('2d')!, performance.now());
  const original = cloneCanvas(mask), originalCtx = original.getContext('2d')!;
  originalCtx.globalCompositeOperation = 'source-in'; originalCtx.drawImage(picture, -left, -top); resetPaint(originalCtx);
  selected = { original, image: transparent(original), mask, points: rectangle(0, 0, mask.width, mask.height), sector: activeSector(), x: left, y: top, sourceX: left, sourceY: top, floating: false, before: null }; changed();
}
