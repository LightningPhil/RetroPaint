import { baseCtx, H, W } from './canvas';
import { restoreLive, snapshotLive, type LiveSnapshot } from './live';

export interface Hist {
  image: ImageData;
  live: LiveSnapshot;
}

const stack: Hist[] = [];

export function captureHistory(): Hist {
  return {
    image: baseCtx.getImageData(0, 0, W, H),
    live: snapshotLive(),
  };
}

export function restoreHistory(item: Hist): void {
  baseCtx.putImageData(item.image, 0, 0);
  restoreLive(item.live);
}

export function pushHistory(item = captureHistory()): void {
  stack.push(item);
  if (stack.length > 20) stack.shift();
}

export function undo(): void {
  const item = stack.pop();
  if (!item) {
    return;
  }
  baseCtx.putImageData(item.image, 0, 0);
  restoreLive(item.live);
}
