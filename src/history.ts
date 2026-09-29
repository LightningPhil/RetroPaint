import { baseCtx, H, W } from './canvas';
import { clearLive, restoreLive, snapshotLive, type LiveSnapshot } from './live';

interface Hist {
  image: ImageData;
  live: LiveSnapshot;
}

const stack: Hist[] = [];

export function pushHistory(): void {
  stack.push({
    image: baseCtx.getImageData(0, 0, W, H),
    live: snapshotLive(),
  });
  if (stack.length > 20) stack.shift();
}

export function undo(): void {
  const item = stack.pop();
  if (!item) {
    baseCtx.fillStyle = '#ffffff';
    baseCtx.fillRect(0, 0, W, H);
    clearLive();
    return;
  }
  baseCtx.putImageData(item.image, 0, 0);
  restoreLive(item.live);
}
