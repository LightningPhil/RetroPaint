import { cloneCanvas, paintThroughMask, W, H } from './canvas';
import { colorFromSpec, patternFor, stopsFor } from './materials';
import type { Applicator, GradientLine, LiveSpec, Spark } from './types';

export interface LiveStroke {
  points: { x: number; y: number; w: number }[];
  opacity: number;
  applicator: Applicator;
  spec: LiveSpec;
  generation: number;
  lane: number;
}

export interface LiveFill {
  mask: HTMLCanvasElement;
  opacity: number;
  spec: LiveSpec;
  gradient: GradientLine | null;
  sparkles: Spark[];
}

export interface LiveSnapshot {
  strokes: LiveStroke[];
  fills: LiveFill[];
  sparkles: Spark[];
}

export const strokes: LiveStroke[] = [];
export const fills: LiveFill[] = [];
export const sparkles: Spark[] = [];

export function hasLive(): boolean {
  return strokes.length > 0 || fills.length > 0 || sparkles.length > 0;
}

export function specMatches(a: LiveSpec, b: LiveSpec): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

export function startStroke(spec: LiveSpec, applicator: Applicator, opacity: number, generation: number, lane: number): LiveStroke {
  for (let i = strokes.length - 1; i >= Math.max(0, strokes.length - 12); i--) {
    const last = strokes[i];
    if (
      last.generation === generation &&
      last.lane === lane &&
      last.applicator === applicator &&
      last.opacity === opacity &&
      specMatches(last.spec, spec) &&
      last.points.length < 4000
    ) {
      return last;
    }
  }
  const stroke: LiveStroke = { points: [], opacity, applicator, spec, generation, lane };
  strokes.push(stroke);
  return stroke;
}

export function addSparkle(x: number, y: number, size: number, color: string): void {
  sparkles.push({ x, y, phase: Math.random() * Math.PI * 2, size, color });
  if (sparkles.length > 7000) sparkles.splice(0, sparkles.length - 7000);
}

export function addFill(mask: HTMLCanvasElement, spec: LiveSpec, opacity: number, gradient: GradientLine | null, extra: Spark[] = []): LiveFill {
  const fill: LiveFill = { mask, opacity, spec, gradient, sparkles: extra };
  fills.push(fill);
  return fill;
}

export function blankMask(): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = W;
  canvas.height = H;
  return canvas;
}

function maskData(mask: HTMLCanvasElement): Uint8ClampedArray {
  return mask.getContext('2d')!.getImageData(0, 0, W, H).data;
}

export function punchDisc(x: number, y: number, radius: number): void {
  const r2 = radius * radius;
  for (const fill of fills) {
    const ctx = fill.mask.getContext('2d')!;
    ctx.globalCompositeOperation = 'destination-out';
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalCompositeOperation = 'source-over';
    fill.sparkles = fill.sparkles.filter((p) => (p.x - x) ** 2 + (p.y - y) ** 2 > r2);
  }
  for (const stroke of strokes) {
    stroke.points = stroke.points.filter((p) => (p.x - x) ** 2 + (p.y - y) ** 2 > r2);
  }
  for (let i = sparkles.length - 1; i >= 0; i--) {
    const p = sparkles[i];
    if ((p.x - x) ** 2 + (p.y - y) ** 2 <= r2) sparkles.splice(i, 1);
  }
}

export function subtractMask(mask: HTMLCanvasElement): void {
  const data = maskData(mask);
  const inside = (x: number, y: number) => {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    if (ix < 0 || iy < 0 || ix >= W || iy >= H) return false;
    return data[(iy * W + ix) * 4 + 3] > 20;
  };
  for (const fill of fills) {
    const ctx = fill.mask.getContext('2d')!;
    ctx.globalCompositeOperation = 'destination-out';
    ctx.drawImage(mask, 0, 0);
    ctx.globalCompositeOperation = 'source-over';
    fill.sparkles = fill.sparkles.filter((p) => !inside(p.x, p.y));
  }
  for (const stroke of strokes) stroke.points = stroke.points.filter((p) => !inside(p.x, p.y));
  for (let i = sparkles.length - 1; i >= 0; i--) {
    if (inside(sparkles[i].x, sparkles[i].y)) sparkles.splice(i, 1);
  }
}

export function renderLive(ctx: CanvasRenderingContext2D, now: number): void {
  for (const fill of fills) renderFill(ctx, fill, now);
  for (const stroke of strokes) renderStroke(ctx, stroke, now);
  renderSparkleList(ctx, sparkles, now);
}

function renderFill(ctx: CanvasRenderingContext2D, fill: LiveFill, now: number): void {
  paintThroughMask(ctx, fill.mask, (sctx) => {
    sctx.globalAlpha = fill.opacity;
    if (fill.spec.kind === 'texture' && fill.spec.texture) {
      const id = fill.spec.texture === 'water' ? 'tex-water' : 'tex-static';
      const pattern = patternFor(id, now);
      sctx.fillStyle = pattern ?? '#48CAE4';
      sctx.fillRect(0, 0, W, H);
      return;
    }
    if (fill.gradient) {
      const { x1, y1, x2, y2 } = fill.gradient;
      const grad = sctx.createLinearGradient(x1, y1, x2, y2);
      for (const stop of stopsFor(fill.gradient, now)) grad.addColorStop(stop.t, stop.color);
      sctx.fillStyle = grad;
      sctx.fillRect(0, 0, W, H);
      return;
    }
    sctx.fillStyle = colorFromSpec(fill.spec, now, 0);
    sctx.fillRect(0, 0, W, H);
  });
  if (fill.sparkles.length) renderSparkleList(ctx, fill.sparkles, now);
}

export function renderStroke(ctx: CanvasRenderingContext2D, stroke: LiveStroke, now: number): void {
  if (stroke.points.length === 0) return;
  ctx.save();
  ctx.globalAlpha = stroke.opacity;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  let dist = 0;
  const pts = stroke.points;
  const mist = stroke.applicator === 'mist' || stroke.applicator === 'splatter';
  if (pts.length === 1 || mist) {
    for (const p of pts) {
      ctx.fillStyle = colorFromSpec(stroke.spec, now, dist);
      ctx.beginPath();
      ctx.arc(p.x, p.y, Math.max(0.8, p.w / 2), 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
    return;
  }
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1];
    const b = pts[i];
    const seg = Math.hypot(b.x - a.x, b.y - a.y);
    ctx.strokeStyle = colorFromSpec(stroke.spec, now, dist);
    ctx.lineWidth = Math.max(1, (a.w + b.w) / 2);
    if (stroke.applicator === 'watercolor') ctx.globalAlpha = stroke.opacity * 0.28;
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.stroke();
    dist += seg;
  }
  ctx.restore();
}

export function renderSparkleList(ctx: CanvasRenderingContext2D, list: Spark[], now: number): void {
  for (const p of list) {
    const tw = 0.5 + 0.5 * Math.sin(now * 0.012 + p.phase);
    if (tw < 0.35) continue;
    ctx.globalAlpha = 1;
    ctx.fillStyle = tw > 0.72 ? '#ffffff' : p.color;
    const s = p.size * (tw > 0.72 ? 1.4 : 1);
    ctx.fillRect(p.x - s / 2, p.y - s / 2, s, s);
  }
  ctx.globalAlpha = 1;
}

export function budget(now: number, paintStroke: (ctx: CanvasRenderingContext2D, stroke: LiveStroke, now: number) => void, target: CanvasRenderingContext2D): void {
  let count = sparkles.length;
  for (const stroke of strokes) count += stroke.points.length;
  while (count > 9000 && strokes.length > 1) {
    const oldest = strokes.shift();
    if (!oldest) break;
    paintStroke(target, oldest, now);
    count -= oldest.points.length;
  }
}

export function clearLive(): void {
  strokes.length = 0;
  fills.length = 0;
  sparkles.length = 0;
}

export function snapshotLive(): LiveSnapshot {
  return {
    strokes: strokes.map((stroke) => ({
      points: stroke.points.map((p) => ({ ...p })),
      opacity: stroke.opacity,
      applicator: stroke.applicator,
      spec: { ...stroke.spec, colors: [...stroke.spec.colors] },
      generation: stroke.generation,
      lane: stroke.lane,
    })),
    fills: fills.map((fill) => ({
      mask: cloneCanvas(fill.mask),
      opacity: fill.opacity,
      spec: { ...fill.spec, colors: [...fill.spec.colors] },
      gradient: fill.gradient ? { ...fill.gradient } : null,
      sparkles: fill.sparkles.map((p) => ({ ...p })),
    })),
    sparkles: sparkles.map((p) => ({ ...p })),
  };
}

export function restoreLive(snap: LiveSnapshot): void {
  strokes.length = 0;
  fills.length = 0;
  sparkles.length = 0;
  for (const stroke of snap.strokes) {
    strokes.push({
      points: stroke.points.map((p) => ({ ...p })),
      opacity: stroke.opacity,
      applicator: stroke.applicator,
      spec: { ...stroke.spec, colors: [...stroke.spec.colors] },
      generation: stroke.generation,
      lane: stroke.lane,
    });
  }
  for (const fill of snap.fills) {
    fills.push({
      mask: cloneCanvas(fill.mask),
      opacity: fill.opacity,
      spec: { ...fill.spec, colors: [...fill.spec.colors] },
      gradient: fill.gradient ? { ...fill.gradient } : null,
      sparkles: fill.sparkles.map((p) => ({ ...p })),
    });
  }
  sparkles.push(...snap.sparkles.map((p) => ({ ...p })));
}

export function bakeLive(ctx: CanvasRenderingContext2D, now: number): void {
  if (!hasLive()) return;
  renderLive(ctx, now);
  clearLive();
}
