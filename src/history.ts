import { artwork } from './artwork';
import { baseCtx, H, W } from './canvas';
import { restoreLive, snapshotLive, type LiveSnapshot } from './live';

export interface Hist {
  image: ImageData;
  startedAt: number | null;
  live: LiveSnapshot;
}

const stack: Hist[] = [];

export function captureHistory(): Hist {
  return {
    startedAt: artwork.snapshot(),
    image: baseCtx.getImageData(0, 0, W, H),
    live: snapshotLive(),
  };
}

export function restoreHistory(item: Hist): void {
  baseCtx.putImageData(item.image, 0, 0);
  restoreLive(item.live);
  artwork.restore(item.startedAt);
}

export function pushHistory(item = captureHistory()): void {
  stack.push(item);
  artwork.markWork();
  if (stack.length > 20) stack.shift();
}

export function undo(): void {
  const item = stack.pop();
  if (!item) {
    return;
  }
  baseCtx.putImageData(item.image, 0, 0);
  restoreLive(item.live);
  artwork.restore(item.startedAt);
}
