export const W = 960;
export const H = 640;

export const view = document.createElement('canvas');
export const ui = document.createElement('canvas');
export const base = document.createElement('canvas');
const scratch = document.createElement('canvas');

view.width = ui.width = base.width = scratch.width = W;
view.height = ui.height = base.height = scratch.height = H;

export const viewCtx = view.getContext('2d', { willReadFrequently: true })!;
export const uiCtx = ui.getContext('2d')!;
export const baseCtx = base.getContext('2d', { willReadFrequently: true })!;
export const scratchCtx = scratch.getContext('2d')!;

export function resetPaint(ctx: CanvasRenderingContext2D): void {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
  ctx.shadowBlur = 0;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = 0;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.setLineDash([]);
  ctx.filter = 'none';
}

export function initCanvas(): void {
  resetPaint(baseCtx);
  resetPaint(viewCtx);
  resetPaint(uiCtx);
  baseCtx.fillStyle = '#ffffff';
  baseCtx.fillRect(0, 0, W, H);
  const stage = document.getElementById('stage');
  if (!stage) throw new Error('Missing #stage');
  view.id = 'view';
  ui.id = 'ui';
  stage.prepend(view);
  stage.append(ui);
}

export function eventPos(e: { clientX: number; clientY: number }): { x: number; y: number } {
  const rect = view.getBoundingClientRect();
  return {
    x: ((e.clientX - rect.left) * W) / rect.width,
    y: ((e.clientY - rect.top) * H) / rect.height,
  };
}

export function canvasToClient(x: number, y: number): { x: number; y: number } {
  const rect = view.getBoundingClientRect();
  return {
    x: rect.left + (x / W) * rect.width,
    y: rect.top + (y / H) * rect.height,
  };
}

export function clearScratch(): CanvasRenderingContext2D {
  resetPaint(scratchCtx);
  scratchCtx.clearRect(0, 0, W, H);
  return scratchCtx;
}

export function cloneCanvas(src: HTMLCanvasElement): HTMLCanvasElement {
  const copy = document.createElement('canvas');
  copy.width = src.width;
  copy.height = src.height;
  copy.getContext('2d')!.drawImage(src, 0, 0);
  return copy;
}

export function paintThroughMask(
  target: CanvasRenderingContext2D,
  mask: HTMLCanvasElement,
  draw: (ctx: CanvasRenderingContext2D) => void,
): void {
  const ctx = clearScratch();
  draw(ctx);
  ctx.globalCompositeOperation = 'destination-in';
  ctx.drawImage(mask, 0, 0);
  resetPaint(target);
  target.drawImage(scratch, 0, 0);
}
