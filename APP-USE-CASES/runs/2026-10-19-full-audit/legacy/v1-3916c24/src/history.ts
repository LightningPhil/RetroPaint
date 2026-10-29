import { artwork } from './artwork';
import { H, W } from './canvas';
import { restoreLive, type LiveSnapshot } from './live';
import { activeLayerId, captureLayers, restoreLayers, type LayerSnapshot } from './layers';
import { emit } from './bus';

export interface Hist {
  image: ImageData;
  startedAt: number | null;
  live: LiveSnapshot;
  layers: LayerSnapshot[];
  active: number;
  width: number;
  height: number;
}

const stack: Hist[] = [];
const future: Hist[] = [];

export function captureHistory(): Hist {
  const layers = captureLayers();
  return {
    startedAt: artwork.snapshot(),
    image: layers.find(layer => layer.id === activeLayerId)!.image,
    live: layers.find(layer => layer.id === activeLayerId)!.live,
    layers, active: activeLayerId, width: W, height: H,
  };
}

export function restoreHistory(item: Hist): void {
  restoreLayers(item.layers, item.active, item.width, item.height);
  restoreLive(item.live);
  artwork.restore(item.startedAt);
}

export function pushHistory(item = captureHistory()): void {
  stack.push(item);
  future.length = 0;
  artwork.markWork();
  if (stack.length > 20) stack.shift();
  // Keep large multilayer documents within a predictable memory budget.
  while (stack.length > 1 && stack.reduce((sum, entry) => sum + entry.width * entry.height * entry.layers.length * 4, 0) > 192_000_000) stack.shift();
  emit('history');
}

export function undo(): void {
  const item = stack.pop();
  if (!item) {
    return;
  }
  future.push(captureHistory());
  restoreHistory(item);
  emit('history');
}

export function redo(): void {
  const item = future.pop(); if (!item) return;
  stack.push(captureHistory()); restoreHistory(item); emit('history');
}
export function canUndo(): boolean { return stack.length > 0; }
export function canRedo(): boolean { return future.length > 0; }
