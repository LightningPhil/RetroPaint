import { setDim, viewCtx, base, W, H } from './canvas';
import { drawPending } from './fill';
import { renderLive } from './live';
import { state } from './state';

export function paintFrame(now: number): void {
  viewCtx.setTransform(1, 0, 0, 1, 0, 0);
  viewCtx.globalAlpha = 1;
  viewCtx.globalCompositeOperation = 'source-over';
  viewCtx.clearRect(0, 0, W, H);
  viewCtx.drawImage(base, 0, 0);
  renderLive(viewCtx, now);
  drawPending(viewCtx, now);
  setDim(state.symmetry !== 'off' || state.tool === 'spiro');
}
