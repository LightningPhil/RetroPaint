import { uiCtx, W, H } from './canvas';
import { drawShape, getPending } from './fill';
import { drawSparks, drawSqueegee } from './effects';
import { getPreview } from './preview';
import { drawRig } from './spiro';
import { state } from './state';

export function renderOverlay(): void {
  uiCtx.setTransform(1, 0, 0, 1, 0, 0);
  uiCtx.clearRect(0, 0, W, H);
  uiCtx.globalAlpha = 1;
  uiCtx.shadowBlur = 0;
  uiCtx.setLineDash([]);

  if (state.symmetry !== 'off') drawGuides(uiCtx);
  if (state.tool === 'spiro') drawRig(uiCtx);

  const preview = getPreview();
  if (preview?.kind === 'shape') {
    drawShape(preview.shape, preview.x0, preview.y0, preview.x1, preview.y1, uiCtx, false);
  } else if (preview?.kind === 'lasso') {
    uiCtx.strokeStyle = '#1A1A1A';
    uiCtx.lineWidth = 3;
    uiCtx.setLineDash([6, 5]);
    uiCtx.beginPath();
    preview.points.forEach((p, i) => (i ? uiCtx.lineTo(p.x, p.y) : uiCtx.moveTo(p.x, p.y)));
    uiCtx.stroke();
    uiCtx.setLineDash([]);
  } else if (preview?.kind === 'rubber') {
    uiCtx.strokeStyle = '#1A1A1A';
    uiCtx.lineWidth = 3;
    uiCtx.setLineDash([7, 6]);
    uiCtx.beginPath();
    uiCtx.moveTo(preview.x0, preview.y0);
    uiCtx.lineTo(preview.x1, preview.y1);
    uiCtx.stroke();
    uiCtx.setLineDash([]);
    pin(uiCtx, preview.x0, preview.y0, '#ffffff');
    pin(uiCtx, preview.x1, preview.y1, '#1A1A1A');
  }

  const pending = getPending();
  if (pending) {
    uiCtx.strokeStyle = '#1A1A1A';
    uiCtx.lineWidth = 3;
    uiCtx.beginPath();
    uiCtx.moveTo(pending.x1, pending.y1);
    uiCtx.lineTo(pending.x2, pending.y2);
    uiCtx.stroke();
    pin(uiCtx, pending.x1, pending.y1, '#06D6A0');
    pin(uiCtx, pending.x2, pending.y2, '#EF476F');
  }

  if (state.tool === 'spiro') {
    /* rig already drawn */
  }
  drawSparks(uiCtx);
  drawSqueegee(uiCtx);

  if (state.poly.length > 0 && state.tool === 'shapes' && state.shape === 'poly') {
    uiCtx.strokeStyle = '#1A1A1A';
    uiCtx.lineWidth = 3;
    uiCtx.beginPath();
    state.poly.forEach((p, i) => (i ? uiCtx.lineTo(p.x, p.y) : uiCtx.moveTo(p.x, p.y)));
    uiCtx.stroke();
    uiCtx.fillStyle = '#FFD166';
    for (const p of state.poly) {
      uiCtx.beginPath();
      uiCtx.arc(p.x, p.y, 5, 0, Math.PI * 2);
      uiCtx.fill();
    }
  }
}

function drawGuides(ctx: CanvasRenderingContext2D): void {
  ctx.save();
  ctx.strokeStyle = 'rgba(0, 255, 200, 0.9)';
  ctx.shadowColor = '#00FFC8';
  ctx.shadowBlur = 10;
  ctx.lineWidth = 2;
  const cx = W / 2;
  const cy = H / 2;
  ctx.beginPath();
  if (state.symmetry === 'v' || state.symmetry === '4' || state.symmetry === '8') {
    ctx.moveTo(cx, 0);
    ctx.lineTo(cx, H);
  }
  if (state.symmetry === 'h' || state.symmetry === '4' || state.symmetry === '8') {
    ctx.moveTo(0, cy);
    ctx.lineTo(W, cy);
  }
  if (state.symmetry === '8') {
    ctx.moveTo(0, 0);
    ctx.lineTo(W, H);
    ctx.moveTo(W, 0);
    ctx.lineTo(0, H);
  }
  ctx.stroke();
  ctx.restore();
}

function pin(ctx: CanvasRenderingContext2D, x: number, y: number, fill: string): void {
  ctx.beginPath();
  ctx.arc(x, y, 11, 0, Math.PI * 2);
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.lineWidth = 4;
  ctx.strokeStyle = '#1A1A1A';
  ctx.stroke();
}
