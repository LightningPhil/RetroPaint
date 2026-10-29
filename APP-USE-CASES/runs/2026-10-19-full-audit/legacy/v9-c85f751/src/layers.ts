import { base, cloneCanvas, H, resetPaint, setCanvasSize, useBase, W } from './canvas';
import { emit } from './bus';
import { clearLive, fills, renderLive, renderLiveSnapshot, restoreLive, snapshotLive, sparkles, strokes, type LiveSnapshot } from './live';
import { state } from './state';
import { photoPreview } from './photo-preview';
import type { PhotoRecipe } from './photo-recipe';
import { hasPhotoAdjustments } from './photo-recipe';
import { fullPhotoPixels, renderPhotoPixels, renderPhotoSurface } from './photo-render';
import { documentCrop } from './document-frame';
import { drawObjects, drawSceneObjects, multiply, objectAnimated, objectCapture, type PaintObject } from './object-scene';
import type { CadLayer } from './cad-model';

export interface Layer {
  id: number;
  name: string;
  canvas: HTMLCanvasElement;
  live: LiveSnapshot;
  visible: boolean;
  opacity: number;
  paper: string | null;
  photo?: PhotoRecipe;
  objects?: PaintObject[];
  cad?: CadLayer;
}
export interface LayerSnapshot extends Omit<Layer, 'canvas'> { image: ImageData }
const emptyLive = (): LiveSnapshot => ({ strokes: [], fills: [], sparkles: [] });
export const layers: Layer[] = [{ id: 1, name: 'Paper', canvas: base, live: emptyLive(), visible: true, opacity: 1, paper: '#ffffff' }];
export let activeLayerId = 1;
let nextId = 2;
let composite: HTMLCanvasElement | null = null;
let thumbnailBuffer: HTMLCanvasElement | null = null;

export function activeLayer(): Layer { return layers.find(layer => layer.id === activeLayerId)!; }
function storeActive(): void { activeLayer().live = snapshotLive(); }
function activate(layer: Layer): void { activeLayerId = layer.id; useBase(layer.canvas); restoreLive(layer.live); }
export function layerChanged(): void { emit('layers'); }
export function switchLayer(id: number): void {
  const layer = layers.find(layer => layer.id === id);
  if (!layer || id === activeLayerId) return;
  storeActive(); activate(layer); layerChanged();
}
function surface(width = W, height = H): HTMLCanvasElement {
  const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height; return canvas;
}
export function addLayer(cad?: CadLayer): void {
  storeActive();
  let number = 1; while (layers.some(layer => layer.name === `Layer ${number}`)) number++;
  const layer: Layer = { id: nextId++, name: `Layer ${number}`, canvas: surface(), live: emptyLive(), visible: true, opacity: 1, paper: null, cad };
  layers.splice(layers.indexOf(activeLayer()) + 1, 0, layer);
  activate(layer); layerChanged();
}
export function duplicateLayer(): void {
  storeActive(); const original = activeLayer();
  const layer = { ...original, cad:original.cad?{units:'mm' as const,bodies:original.cad.bodies.map(b=>({...b,id:crypto.randomUUID()}))}:undefined, objects:original.objects?.map(object=>object.kind==='raster'&&object.wet?{...object,image:cloneCanvas(object.image),wet:false}:{...object}), photo:original.photo?structuredClone(original.photo):undefined, id: nextId++, name: `${original.name} copy`, canvas: cloneCanvas(original.canvas), live: snapshotLive() };
  layers.splice(layers.indexOf(original) + 1, 0, layer); activate(layer); layerChanged();
}
export function deleteLayer(id=activeLayerId): void {
  if (layers.length === 1) return;
  const index = layers.findIndex(layer=>layer.id===id);if(index<0)return;const selected=id===activeLayerId;layers.splice(index, 1);
  if(selected)activate(layers[Math.max(0, index - 1)]); layerChanged();
}
export function reorderLayer(direction: number): void {
  const index = layers.indexOf(activeLayer()), target = index + direction;
  if (target < 0 || target >= layers.length) return;
  [layers[index], layers[target]] = [layers[target], layers[index]]; layerChanged();
}
export function moveLayer(id: number, targetId: number, above: boolean): boolean {
  const original = layers.find(layer => layer.id === id), target = layers.find(layer => layer.id === targetId);
  if (!original || !target || original === target) return false;
  const reordered = layers.filter(layer => layer !== original), index = reordered.indexOf(target) + Number(above);
  reordered.splice(index, 0, original);
  if (reordered.every((layer, i) => layer === layers[i])) return false;
  layers.splice(0, layers.length, ...reordered); layerChanged(); return true;
}
export function canAddLayer(): boolean { return layers.length < 16 && W * H * (layers.length + 1) <= 64_000_000; }

export function drawLayerThumbnail(ctx: CanvasRenderingContext2D, layer: Layer, now: number): void {
  const live = layer.id === activeLayerId && objectCapture?.layer!==layer.id ? currentLive() : layer.live;
  let source = layer.canvas;
  if (live.strokes.length || live.fills.length || live.sparkles.length || layer.objects?.length) {
    thumbnailBuffer ??= surface();
    if (thumbnailBuffer.width !== W || thumbnailBuffer.height !== H) { thumbnailBuffer.width = W; thumbnailBuffer.height = H; }
    const buffer = thumbnailBuffer.getContext('2d')!;
    resetPaint(buffer); buffer.clearRect(0, 0, W, H); buffer.drawImage(layer.canvas, 0, 0);
    renderLiveSnapshot(buffer, live, now); drawSceneObjects(buffer,layer.objects,layer.id,now); source = thumbnailBuffer;
  }
  if(layer.photo&&hasPhotoAdjustments(layer.photo.settings))source=renderPhotoSurface(layer.photo,layer.canvas,source,now,Boolean(live.fills.length||live.strokes.length||live.sparkles.length));
  resetPaint(ctx); ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  const scale = Math.min(ctx.canvas.width / W, ctx.canvas.height / H), width = W * scale, height = H * scale;
  ctx.globalAlpha = layer.opacity; ctx.drawImage(source, (ctx.canvas.width - width) / 2, (ctx.canvas.height - height) / 2, width, height); resetPaint(ctx);
}
export function mergeLayerDown(now = performance.now()): void {
  const index = layers.indexOf(activeLayer()); if (!index) return;
  if (layers[index].cad || layers[index - 1].cad) return;
  storeActive();
  const lower = layers[index - 1], upper = layers[index], canvas = surface();
  const ctx = canvas.getContext('2d')!;
  for (const layer of [lower, upper]) {
    if (!layer.visible) continue;
    const image = cloneCanvas(layer.canvas); renderLiveSnapshot(image.getContext('2d')!, layer.live, now); drawObjects(image.getContext('2d')!,layer.objects,now);
    if(layer.photo)image.getContext('2d')!.putImageData(renderPhotoPixels(layer.photo,image),0,0);
    ctx.globalAlpha = layer.opacity; ctx.drawImage(image, 0, 0);
  }
  lower.canvas = canvas; lower.objects=undefined; lower.photo=undefined; lower.live = emptyLive(); lower.opacity = 1; lower.visible = true;
  layers.splice(index, 1); activate(lower); layerChanged();
}
export function resetLayers(width = W, height = H, paper: string | null = '#ffffff'): void {
  state.spiro.cx = width / 2; state.spiro.cy = height / 2; state.spiro.R = Math.max(1, Math.min(width,height) / 3);
  setCanvasSize(width, height); clearLive();
  const canvas = surface();
  if (paper) { const ctx = canvas.getContext('2d')!; ctx.fillStyle = paper; ctx.fillRect(0, 0, W, H); }
  const layer: Layer = { id: nextId++, name: paper ? 'Paper' : 'Layer 1', canvas, live: emptyLive(), visible: true, opacity: 1, paper };
  layers.splice(0, layers.length, layer); activate(layer); layerChanged();
  emit('document-created');
}
export function captureLayers(): LayerSnapshot[] {
  return layers.map(layer => {
    const { canvas, ...metadata } = layer;
    return { ...metadata,
    objects:layer.objects?.map(object=>object.kind==='raster'&&object.wet?{...object,image:cloneCanvas(object.image)}:object),
    image: canvas.getContext('2d')!.getImageData(0, 0, W, H),
    live: layer.id === activeLayerId && objectCapture?.layer!==layer.id ? snapshotLive() : cloneLive(layer.live),
  }; });
}
function cloneLive(snap: LiveSnapshot): LiveSnapshot {
  // Inactive snapshots are never mutated; transforms and restore create replacements.
  return snap;
}
export function restoreLayers(snapshots: LayerSnapshot[], active: number, width: number, height: number): void {
  setCanvasSize(width, height);
  layers.splice(0, layers.length, ...snapshots.map(snapshot => {
    const canvas = surface(); canvas.getContext('2d')!.putImageData(snapshot.image, 0, 0);
    return { ...snapshot, canvas };
  }));
  nextId = Math.max(nextId, ...layers.map(layer => layer.id + 1));
  activate(layers.find(layer => layer.id === active) ?? layers[0]); layerChanged();
}
export function renderLayers(ctx: CanvasRenderingContext2D, now: number, activeOverlay?: (ctx: CanvasRenderingContext2D) => void): void {
  composite ??= surface();
  if (composite.width !== W || composite.height !== H) { composite.width = W; composite.height = H; }
  const buffer = composite.getContext('2d')!;
  resetPaint(ctx); ctx.clearRect(0, 0, W, H);
  for (const layer of layers) {
    if (!layer.visible) continue;
    const preview=photoPreview(layer.id);
    resetPaint(buffer); buffer.clearRect(0, 0, W, H); buffer.drawImage(preview??layer.canvas, 0, 0, W, H);
    if (!preview) {
      if (layer.id === activeLayerId && objectCapture?.layer!==layer.id) renderLive(buffer, now);
      else renderLiveSnapshot(buffer, layer.live, now);
      drawSceneObjects(buffer,layer.objects,layer.id,now);
      if(layer.id===activeLayerId)activeOverlay?.(buffer);
    }
    const live=layer.id===activeLayerId?currentLive():layer.live;
    const adjusted=!preview&&layer.photo&&hasPhotoAdjustments(layer.photo.settings)?renderPhotoSurface(layer.photo,layer.canvas,composite,now,Boolean(live.fills.length||live.strokes.length||live.sparkles.length||layer.objects?.some(objectAnimated)||objectCapture?.layer===layer.id)):composite;
    ctx.globalAlpha = layer.opacity; ctx.drawImage(adjusted, 0, 0, W, H);
  }
  resetPaint(ctx);
}
export function renderActive(ctx: CanvasRenderingContext2D, now: number): void {
  const layer=activeLayer();resetPaint(ctx); ctx.clearRect(0, 0, W, H); ctx.drawImage(layer.canvas, 0, 0);
  if(objectCapture?.layer===layer.id)renderLiveSnapshot(ctx,layer.live,now);else renderLive(ctx, now);
  drawSceneObjects(ctx,layer.objects,layer.id,now);
}
export async function renderFullPicture(now:number):Promise<HTMLCanvasElement> {
  const output=surface(),crop=documentCrop(),pending=layers.filter(layer=>layer.visible).map(layer=>{
    const canvas=cloneCanvas(layer.canvas);renderLiveSnapshot(canvas.getContext('2d')!,layer.id===activeLayerId?currentLive():layer.live,now);drawObjects(canvas.getContext('2d')!,layer.objects,now);
    return {canvas,opacity:layer.opacity,photo:layer.photo};
  });
  const ctx=output.getContext('2d')!;
  for(const layer of pending){if(layer.photo)layer.canvas.getContext('2d')!.putImageData(await fullPhotoPixels(layer.photo,layer.canvas.getContext('2d')!.getImageData(0,0,layer.canvas.width,layer.canvas.height),crop),0,0);ctx.globalAlpha=layer.opacity;ctx.drawImage(layer.canvas,0,0);}
  return output;
}
export function allLayersEditable(): void { activeLayer().visible = true; layerChanged(); }
export function eraseRegion(ctx: CanvasRenderingContext2D, draw: () => void): void {
  ctx.save();
  const paper = activeLayer().paper;
  ctx.globalCompositeOperation = paper ? 'source-over' : 'destination-out'; ctx.fillStyle = paper ?? '#000000';
  draw(); ctx.restore();
}
export type Matrix = [number, number, number, number, number, number];
export function transformLayers(width: number, height: number, matrix: Matrix, extendPaper = false, smooth = true): void {
  storeActive();
  const point = (p: { x: number; y: number }) => ({ x: matrix[0] * p.x + matrix[2] * p.y + matrix[4], y: matrix[1] * p.x + matrix[3] * p.y + matrix[5] });
  const scale = Math.sqrt(Math.abs(matrix[0] * matrix[3] - matrix[1] * matrix[2]));
  const kit = point({ x: state.spiro.cx, y: state.spiro.cy });
  state.spiro.cx = Math.max(0, Math.min(width, kit.x)); state.spiro.cy = Math.max(0, Math.min(height, kit.y)); state.spiro.R = Math.max(8, state.spiro.R * scale);
  for (const layer of layers) {
    layer.objects=layer.objects?.map(object=>({...object,matrix:multiply(matrix,object.matrix)}));
    const canvas = surface(width, height), ctx = canvas.getContext('2d')!;
    ctx.imageSmoothingEnabled = smooth;
    if (extendPaper && layer.paper) { ctx.fillStyle = layer.paper; ctx.fillRect(0, 0, width, height); }
    ctx.setTransform(...matrix); ctx.drawImage(layer.canvas, 0, 0); resetPaint(ctx);
    const mapSpark = (s: LiveSnapshot['sparkles'][number]) => ({ ...s, ...point(s), size: s.size * scale });
    layer.live = {
      strokes: layer.live.strokes.map(stroke => ({ ...stroke, points: stroke.points.map(p => ({ ...point(p), w: p.w * scale })), clip: stroke.clip?.map(point) })),
      fills: layer.live.fills.map(fill => {
        const mask = surface(width, height), maskCtx = mask.getContext('2d')!;
        maskCtx.setTransform(...matrix); maskCtx.drawImage(fill.mask, 0, 0);
        const g = fill.gradient, a = g ? point({ x: g.x1, y: g.y1 }) : null, b = g ? point({ x: g.x2, y: g.y2 }) : null;
        return { ...fill, mask, gradient: g ? { ...g, x1: a!.x, y1: a!.y, x2: b!.x, y2: b!.y } : null, sparkles: fill.sparkles.map(mapSpark) };
      }), sparkles: layer.live.sparkles.map(mapSpark),
    };
    layer.canvas = canvas;
  }
  setCanvasSize(width, height); activate(activeLayer()); layerChanged();
}
export function currentLive(): LiveSnapshot { return { strokes, fills, sparkles }; }
