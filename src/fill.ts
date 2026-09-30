import { activeSector, insideSector, clipLane } from './symmetry-mask';
import { symmetryTransforms } from './symmetry';
import { neonColor } from './color';
import { play } from './audio';
import { renderPaintPath } from './stroke-renderer';
import { baseCtx, paintThroughMask, viewCtx, W, H } from './canvas';
import { mirrorPoints } from './draw';
import { pushHistory } from './history';
import { addFill, addSparkle, blankMask, renderLive, subtractMask } from './live';
import {
  activeInkId,
  animatedKind,
  fillSpecFor,
  isAnimatedMaterial,
  patternFor,
  glitterPattern,
  previewColor,
  sampleInk,
  stopsFor,
} from './materials';
import { currentAlpha, state, strokeApplicator } from './state';
import type { GradientLine, LiveSpec, Spark } from './types';

export interface PendingGradient {
  mask: HTMLCanvasElement;
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  from: string;
  to: string;
  preset: string | null;
  animated: boolean;
}

let pending: PendingGradient | null = null;
let dragPin: 'start' | 'end' | null = null;

export function getPending(): PendingGradient | null {
  return pending;
}

export function pinDrag(): 'start' | 'end' | null {
  return dragPin;
}

export function hitPin(x: number, y: number): 'start' | 'end' | null {
  if (!pending) return null;
  if (Math.hypot(x - pending.x1, y - pending.y1) < 22) return 'start';
  if (Math.hypot(x - pending.x2, y - pending.y2) < 22) return 'end';
  return null;
}

export function setPinDrag(pin: 'start' | 'end' | null): void {
  dragPin = pin;
}

export function movePin(x: number, y: number): void {
  if (!pending || !dragPin) return;
  if (dragPin === 'start') {
    pending.x1 = x;
    pending.y1 = y;
  } else {
    pending.x2 = x;
    pending.y2 = y;
  }
}

export function cancelPending(): void {
  pending = null;
  dragPin = null;
}

export function floodAt(x: number, y: number, line: { x1: number; y1: number; x2: number; y2: number } | null): void {
  if (!insideSector(x,y)) return;
  paintViewReady();
  const pixels = viewCtx.getImageData(0, 0, W, H).data;
  const sector=activeSector();
  const mask = floodMask(pixels, Math.floor(x), Math.floor(y), sector ? (x,y)=>insideSector(x+0.5,y+0.5,sector) : undefined);
  if (!mask) return;
  let maskCanvas = maskToCanvas(mask);
  if (sector) {
    const source=maskCanvas; maskCanvas=blankMask(); const ctx=maskCanvas.getContext('2d')!;
    for (const [lane,t] of symmetryTransforms().entries()) {
      ctx.save(); clipLane(ctx,lane); ctx.translate(W/2,H/2); ctx.transform(t.a,t.c,t.b,t.d,0,0); ctx.translate(-W/2,-H/2);
      ctx.drawImage(source,0,0); ctx.restore();
    }
  }
  if (line) {
    const from = state.gradientPreset ? state.ink : state.gradientFrom;
    const to = state.gradientPreset ? state.ink : state.gradientTo;
    const preset = state.gradientPreset ?? (state.ink.startsWith('grad-') ? state.ink : null);
    pending = {
      mask: maskCanvas,
      x1: line.x1,
      y1: line.y1,
      x2: line.x2,
      y2: line.y2,
      from: state.ink.startsWith('grad-') ? state.ink : from,
      to: state.ink.startsWith('grad-') ? state.ink : to,
      preset,
      animated: isAnimatedMaterial(state.gradientFrom) || isAnimatedMaterial(state.gradientTo) || isAnimatedMaterial(activeInkId()),
    };
    return;
  }
  commitMask(maskCanvas);
}

export function lockPending(): void {
  if (!pending) return;
  const item = pending;
  pending = null;
  dragPin = null;
  pushHistory();
  const line: GradientLine = {
    x1: item.x1,
    y1: item.y1,
    x2: item.x2,
    y2: item.y2,
    from: item.from,
    to: item.to,
    preset: item.preset,
  };
  subtractMask(item.mask);
  if (item.animated) {
    whiteOut(item.mask);
    const spec = fillSpecFor(item.from) ?? fillSpecFor(item.to);
    const sparkles = sparklesAlong(item.mask, line);
    if (spec && spec !== 'sparkle') addFill(item.mask, spec, currentAlpha(), line, sparkles);
    else if (sparkles.length) {
      const dummy: LiveSpec = { kind: 'conveyor', colors: ['#ffffff'], speed: 0, mode: 'snap', along: false, texture: null };
      addFill(item.mask, dummy, 0, null, sparkles);
      paintGradient(baseCtx, item.mask, line, performance.now());
    } else paintGradient(baseCtx, item.mask, line, performance.now());
  } else {
    paintGradient(baseCtx, item.mask, line, performance.now());
  }
  play('splash');
}

function commitMask(mask: HTMLCanvasElement): void {
  pushHistory();
  subtractMask(mask);
  const id = activeInkId();
  const spec = fillSpecFor(id);
  if (spec === 'sparkle') {
    whiteOut(mask);
    const pts = sparkleCover(mask);
    for (const p of pts) addSparkle(p.x, p.y, p.size, p.color);
  } else if (spec) {
    whiteOut(mask);
    addFill(mask, spec, currentAlpha(), null, spec.kind === 'texture' ? [] : []);
  } else {
    paintSolid(baseCtx, mask, id);
  }
  play('splash');
}

function paintSolid(ctx: CanvasRenderingContext2D, mask: HTMLCanvasElement, id: string): void {
  const neon = id === 'neon';
  paintThroughMask(ctx, mask, (sctx) => {
    sctx.globalAlpha = currentAlpha();
    if (neon) {
      sctx.fillStyle = neonColor(state.neonTint);
      sctx.shadowColor = neonColor(state.neonTint);
      sctx.shadowBlur = 24;
    } else if (id === 'sparkle') {
      sctx.fillStyle = glitterPattern();
    } else if (id.startsWith('tex-')) {
      sctx.fillStyle = patternFor(id) ?? previewColor(id);
    } else if (id.startsWith('grad-')) {
      const grad = sctx.createLinearGradient(0, 0, W, H);
      const stops = stopsFor({ x1: 0, y1: 0, x2: W, y2: H, from: id, to: id, preset: id }, performance.now());
      stops.forEach((stop) => grad.addColorStop(stop.t, stop.color));
      sctx.fillStyle = grad;
    } else {
      sctx.fillStyle = sampleInk(id, performance.now(), 0);
    }
    sctx.fillRect(0, 0, W, H);
    if (neon) {
      sctx.shadowBlur = 0;
      sctx.globalCompositeOperation = 'source-over';
      sctx.fillStyle = 'rgba(255,255,255,0.16)';
      sctx.fillRect(0, 0, W, H);
    }
  });
}

export function paintGradient(ctx: CanvasRenderingContext2D, mask: HTMLCanvasElement, line: GradientLine, now: number): void {
  paintThroughMask(ctx, mask, (sctx) => {
    const grad = sctx.createLinearGradient(line.x1, line.y1, line.x2, line.y2);
    for (const stop of stopsFor(line, now)) grad.addColorStop(Math.max(0, Math.min(1, stop.t)), stop.color);
    sctx.fillStyle = grad;
    sctx.globalAlpha = currentAlpha();
    sctx.fillRect(0, 0, W, H);
  });
}

export function drawPending(ctx: CanvasRenderingContext2D, now: number): void {
  if (!pending) return;
  const line: GradientLine = {
    x1: pending.x1,
    y1: pending.y1,
    x2: pending.x2,
    y2: pending.y2,
    from: pending.from,
    to: pending.to,
    preset: pending.preset,
  };
  paintGradient(ctx, pending.mask, line, now);
}

function whiteOut(mask: HTMLCanvasElement): void {
  paintThroughMask(baseCtx, mask, (sctx) => {
    sctx.fillStyle = '#ffffff';
    sctx.fillRect(0, 0, W, H);
  });
}

function sparkleCover(mask: HTMLCanvasElement): Spark[] {
  const data = mask.getContext('2d')!.getImageData(0, 0, W, H).data;
  const pts: Spark[] = [];
  for (let n = 0; n < 700; n++) {
    const x = Math.floor(Math.random() * W);
    const y = Math.floor(Math.random() * H);
    if (data[(y * W + x) * 4 + 3] > 20) {
      pts.push({ x, y, phase: Math.random() * 6.28, size: 2 + Math.random() * 2.5, color: state.sparkleTint });
    }
  }
  return pts;
}

function sparklesAlong(mask: HTMLCanvasElement, line: GradientLine): Spark[] {
  const wants = animatedKind(line.from) === 'sparkle' || animatedKind(line.to) === 'sparkle' || line.from === 'sparkle' || line.to === 'sparkle';
  if (!wants) return [];
  const data = mask.getContext('2d')!.getImageData(0, 0, W, H).data;
  const dx = line.x2 - line.x1;
  const dy = line.y2 - line.y1;
  const len2 = dx * dx + dy * dy || 1;
  const pts: Spark[] = [];
  for (let n = 0; n < 500; n++) {
    const x = Math.floor(Math.random() * W);
    const y = Math.floor(Math.random() * H);
    if (data[(y * W + x) * 4 + 3] < 20) continue;
    const t = ((x - line.x1) * dx + (y - line.y1) * dy) / len2;
    const fromSpark = line.from === 'sparkle' && t < 0.55;
    const toSpark = line.to === 'sparkle' && t > 0.45;
    if (fromSpark || toSpark) pts.push({ x, y, phase: Math.random() * 6.28, size: 2 + Math.random() * 2, color: state.sparkleTint });
  }
  return pts;
}

export function floodMask(pixels: Uint8ClampedArray, sx: number, sy: number, allowed?: (x:number,y:number)=>boolean): Uint8Array | null {
  if (sx < 0 || sy < 0 || sx >= W || sy >= H) return null;
  const mask = new Uint8Array(W * H);
  const start = (sy * W + sx) * 4;
  const tr = pixels[start];
  const tg = pixels[start + 1];
  const tb = pixels[start + 2];
  const ta = pixels[start + 3];
  const match = (i: number) => {
    if (allowed && !allowed(i%W,Math.floor(i/W))) return false;
    const p = i * 4;
    return Math.abs(pixels[p] - tr) + Math.abs(pixels[p + 1] - tg) + Math.abs(pixels[p + 2] - tb) + Math.abs(pixels[p + 3] - ta) <= 48;
  };
  const stack = [sx, sy];
  let filled = 0;
  while (stack.length) {
    const y = stack.pop()!;
    let x = stack.pop()!;
    while (x >= 0 && !mask[y * W + x] && match(y * W + x)) x--;
    x++;
    let spanUp = false;
    let spanDown = false;
    for (; x < W && !mask[y * W + x] && match(y * W + x); x++) {
      mask[y * W + x] = 1;
      filled++;
      if (y > 0) {
        const up = (y - 1) * W + x;
        if (!mask[up] && match(up)) {
          if (!spanUp) {
            stack.push(x, y - 1);
            spanUp = true;
          }
        } else spanUp = false;
      }
      if (y < H - 1) {
        const down = (y + 1) * W + x;
        if (!mask[down] && match(down)) {
          if (!spanDown) {
            stack.push(x, y + 1);
            spanDown = true;
          }
        } else spanDown = false;
      }
    }
  }
  return filled > 0 ? mask : null;
}

function maskToCanvas(mask: Uint8Array): HTMLCanvasElement {
  const canvas = blankMask();
  const ctx = canvas.getContext('2d')!;
  const img = ctx.createImageData(W, H);
  for (let i = 0; i < mask.length; i++) {
    if (mask[i]) img.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  return canvas;
}

function paintViewReady(): void {
  viewCtx.setTransform(1, 0, 0, 1, 0, 0);
  viewCtx.clearRect(0, 0, W, H);
  viewCtx.drawImage(baseCtx.canvas, 0, 0);
  renderLive(viewCtx, performance.now());
}

export function drawShape(kind: 'line' | 'rect' | 'circle', x0: number, y0: number, x1: number, y1: number, ctx: CanvasRenderingContext2D, commit: boolean): void {
  layOutline(outlinePoints(kind, x0, y0, x1, y1), ctx, commit);
}

export function strokePath(points: { x: number; y: number }[], ctx: CanvasRenderingContext2D, commit: boolean, close: boolean): void {
  if (points.length < 2) return;
  const pts = [points[0]];
  for (let i = 1; i < points.length; i++) walkLine(pts, points[i - 1].x, points[i - 1].y, points[i].x, points[i].y);
  if (close) {
    const last = points[points.length - 1];
    const first = points[0];
    walkLine(pts, last.x, last.y, first.x, first.y);
  }
  layOutline(pts, ctx, commit);
}

function segmentSafe(x0: number, y0: number, x1: number, y1: number, width: number): void {
  // Imported lazily-free: shapes call the draw module through a callback set from input to avoid a cycle.
  shapePainter?.(x0, y0, x1, y1, width);
}

let shapePainter: ((x0: number, y0: number, x1: number, y1: number, width: number) => void) | null = null;

export function setShapePainter(fn: (x0: number, y0: number, x1: number, y1: number, width: number) => void): void {
  shapePainter = fn;
}

const SHAPE_STEP = 3;

function shapeWidth(): number {
  const width = state.brushWidth;
  if (strokeApplicator() === 'callig') return width * 1.12;
  if (strokeApplicator() === 'watercolor') return width * 1.2;
  return width;
}

function walkLine(pts: { x: number; y: number }[], x0: number, y0: number, x1: number, y1: number): void {
  const dist = Math.hypot(x1 - x0, y1 - y0);
  const steps = Math.max(1, Math.ceil(dist / SHAPE_STEP));
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    pts.push({ x: x0 + (x1 - x0) * t, y: y0 + (y1 - y0) * t });
  }
}

function outlinePoints(kind: 'line' | 'rect' | 'circle', x0: number, y0: number, x1: number, y1: number): { x: number; y: number }[] {
  if (kind === 'line') {
    const pts = [{ x: x0, y: y0 }];
    walkLine(pts, x0, y0, x1, y1);
    return pts;
  }
  if (kind === 'rect') {
    const pts = [{ x: x0, y: y0 }];
    walkLine(pts, x0, y0, x1, y0);
    walkLine(pts, x1, y0, x1, y1);
    walkLine(pts, x1, y1, x0, y1);
    walkLine(pts, x0, y1, x0, y0);
    return pts;
  }
  const r = Math.hypot(x1 - x0, y1 - y0);
  const sweep = Math.PI * 2;
  const steps = Math.max(16, Math.ceil((sweep * Math.max(r, 1)) / SHAPE_STEP));
  const pts: { x: number; y: number }[] = [];
  for (let i = 0; i <= steps; i++) {
    const a = (i / steps) * sweep;
    pts.push({ x: x0 + Math.cos(a) * r, y: y0 + Math.sin(a) * r });
  }
  return pts;
}

function layOutline(pts: { x: number; y: number }[], ctx: CanvasRenderingContext2D, commit: boolean): void {
  if (pts.length < 2) return;
  const width = shapeWidth();
  if (!commit) {
    const id = activeInkId();
    const paths = [pts];
    for (const points of paths) {
    const lanes = points.map(p => mirrorPoints(p.x, p.y));
    for (let lane = 0; lane < lanes[0].length; lane++) {
      const path = lanes.map(p => ({ ...p[lane], w: width }));
      const bitmap = renderPaintPath(path, {
        kind: id === 'neon' ? 'neon' : id === 'rainbow' ? 'rainbow' : id === 'sparkle' ? 'glitter' : 'solid',
        color: id === 'sparkle' ? state.sparkleTint : id === 'neon' ? state.neonTint : id.startsWith('tex-') ? id : previewColor(id),
        applicator: strokeApplicator(),
      });
      if (bitmap) { ctx.save(); clipLane(ctx,lane); ctx.globalAlpha = currentAlpha(); ctx.drawImage(bitmap.canvas, bitmap.x, bitmap.y); ctx.restore(); }
    }
    }
    return;
  }
  for (let i = 1; i < pts.length; i++) segmentSafe(pts[i - 1].x, pts[i - 1].y, pts[i].x, pts[i].y, width);
}
