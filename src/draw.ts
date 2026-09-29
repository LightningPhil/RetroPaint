import { playThrottled } from './audio';
import { baseCtx, H, resetPaint, W } from './canvas';
import { darkenHex, rainbowCss } from './color';
import { addDrip } from './effects';
import {
  addFill,
  addSparkle,
  blankMask,
  budget,
  punchDisc,
  renderStroke,
  startStroke,
} from './live';
import { activeInkId, captureStrokeSpec, patternFor, previewColor, sampleInk, specKey } from './materials';
import { currentAlpha, state } from './state';
import type { Applicator, LiveSpec } from './types';

let generation = 0;
let traveled = 0;

export function beginStrokeGeneration(): number {
  generation += 1;
  traveled = 0;
  return generation;
}

export function mirrorPoints(x: number, y: number): { x: number; y: number }[] {
  const cx = W / 2;
  const cy = H / 2;
  const dx = x - cx;
  const dy = y - cy;
  const pts = [{ x, y }];
  const mode = state.symmetry;
  if (mode === 'off') return pts;
  const push = (px: number, py: number) => pts.push({ x: cx + px, y: cy + py });
  if (mode === 'v' || mode === '4' || mode === '8') push(-dx, dy);
  if (mode === 'h' || mode === '4' || mode === '8') push(dx, -dy);
  if (mode === '4' || mode === '8') push(-dx, -dy);
  if (mode === '8') {
    push(dy, dx);
    push(-dy, dx);
    push(dy, -dx);
    push(-dy, -dx);
  }
  return pts;
}

export function useGeneration(gen: number): void {
  generation = gen;
}

export function segment(x0: number, y0: number, x1: number, y1: number, width: number, speed: number, gen = generation): void {
  const a = mirrorPoints(x0, y0);
  const b = mirrorPoints(x1, y1);
  const count = Math.min(a.length, b.length);
  for (let i = 0; i < count; i++) {
    strokeRaw(a[i].x, a[i].y, b[i].x, b[i].y, width, speed, i, gen);
  }
}

export function dot(x: number, y: number, width: number): void {
  const pts = mirrorPoints(x, y);
  pts.forEach((p, i) => strokeRaw(p.x, p.y, p.x, p.y, width, 0, i, generation));
}

export function splatterBurst(x: number, y: number, width: number): void {
  for (let i = 0; i < 5; i++) {
    const px = x + (Math.random() - 0.5) * width * 2.4;
    const py = y + (Math.random() - 0.5) * width * 2.4;
    dot(px, py, Math.random() * 3 + 1);
  }
}

export function sprayCloud(x: number, y: number, holdMs: number): void {
  const mist = state.applicator !== 'splatter';
  const spread = currentSpread();
  const count = mist ? 12 : 4;
  for (let i = 0; i < count; i++) {
    const ang = Math.random() * Math.PI * 2;
    const rad = mist ? Math.random() * spread : Math.random() ** 0.4 * spread;
    const size = mist ? Math.random() * 2.2 + 0.5 : Math.random() * 6 + 2.2;
    const px = x + Math.cos(ang) * rad;
    const py = y + Math.sin(ang) * rad;
    for (const p of mirrorPoints(px, py)) blot(p.x, p.y, size);
  }
  if (mist && holdMs > 280 && Math.random() < 0.4) {
    const ink = activeInkId();
    if (ink === 'sparkle') addSparkle(x + (Math.random() - 0.5) * 8, y, 3, state.sparkleTint);
    else addDrip(x + (Math.random() - 0.5) * 10, y, 2 + Math.random() * 2.5, sampleInk(ink, performance.now(), traveled));
  }
}

function currentSpread(): number {
  return (state.level === 1 ? 34 : state.brushWidth) * (state.applicator === 'splatter' ? 2.1 : 2.6);
}

function strokeRaw(x0: number, y0: number, x1: number, y1: number, width: number, speed: number, lane: number, gen: number): void {
  const scrub = state.tool === 'eraser' && state.eraserMode === 'scrub';
  if (!scrub && state.applicator === 'biro' && speed > 1.35 && Math.random() < 0.55) return;

  const dist = Math.hypot(x1 - x0, y1 - y0);
  if (lane === 0) traveled += dist;

  if (scrub) {
    paintLine(baseCtx, x0, y0, x1, y1, width * 1.15, '#ffffff', 1, 'marker', false);
    punchDisc((x0 + x1) / 2, (y0 + y1) / 2, width * 0.65);
    return;
  }

  const spec = captureStrokeSpec();
  if (spec === 'sparkle') {
    sprinkle(x0, y0, x1, y1, width);
    if (lane === 0) playThrottled('shimmer', 140, 0.85 + Math.random() * 0.3);
    return;
  }
  if (spec && spec.kind === 'texture') {
    dabTexture(x0, y0, x1, y1, width, spec, gen);
    return;
  }
  if (spec) {
    const stroke = startStroke(spec, state.applicator, currentAlpha(), gen, lane);
    if (stroke.points.length === 0) stroke.points.push({ x: x0, y: y0, w: width });
    stroke.points.push({ x: x1, y: y1, w: width });
    budget(performance.now(), renderStroke, baseCtx);
    return;
  }

  if (lane === 0 && state.applicator === 'marker') playThrottled('squeak', 110, 0.9 + Math.random() * 0.2);
  const neon = state.ink === 'neon';
  const color = neon ? '#ffffff' : resolveStatic(traveled);
  paintLine(baseCtx, x0, y0, x1, y1, width, color, currentAlpha(), state.applicator, neon);
}

function blot(x: number, y: number, size: number): void {
  const spec = captureStrokeSpec();
  if (spec === 'sparkle') {
    addSparkle(x, y, Math.max(2, size), state.sparkleTint);
    playThrottled('shimmer', 160);
    return;
  }
  if (spec && spec.kind === 'texture') {
    dabTexture(x, y, x, y, size * 2, spec, generation);
    return;
  }
  if (spec) {
    const stroke = startStroke(spec, state.applicator === 'splatter' ? 'splatter' : 'mist', currentAlpha(), generation, 0);
    stroke.points.push({ x, y, w: size * 2 });
    return;
  }
  const neon = state.ink === 'neon';
  resetPaint(baseCtx);
  baseCtx.globalAlpha = currentAlpha();
  if (neon) {
    baseCtx.globalCompositeOperation = 'source-over';
    baseCtx.fillStyle = state.neonTint;
    baseCtx.shadowColor = state.neonTint;
    baseCtx.shadowBlur = 12;
    baseCtx.globalAlpha = currentAlpha() * 0.9;
  } else if (state.ink.startsWith('tex-') && state.ink !== 'tex-water' && state.ink !== 'tex-static') {
    baseCtx.fillStyle = patternFor(state.ink) ?? resolveStatic(traveled);
  } else {
    baseCtx.fillStyle = resolveStatic(traveled);
  }
  baseCtx.beginPath();
  baseCtx.arc(x, y, Math.max(0.6, size / 2), 0, Math.PI * 2);
  baseCtx.fill();
  if (neon) {
    baseCtx.shadowBlur = 0;
    baseCtx.globalCompositeOperation = 'source-over';
    baseCtx.globalAlpha = 1;
    baseCtx.fillStyle = '#ffffff';
    baseCtx.beginPath();
    baseCtx.arc(x, y, Math.max(0.5, size / 5), 0, Math.PI * 2);
    baseCtx.fill();
  }
  resetPaint(baseCtx);
}

function sprinkle(x0: number, y0: number, x1: number, y1: number, width: number): void {
  const dist = Math.max(1, Math.hypot(x1 - x0, y1 - y0));
  const steps = Math.max(1, Math.floor(dist / 4));
  const soft = state.applicator === 'watercolor' || state.applicator === 'mist';
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = x0 + (x1 - x0) * t + (Math.random() - 0.5) * width * 0.45;
    const y = y0 + (y1 - y0) * t + (Math.random() - 0.5) * width * 0.45;
    addSparkle(x, y, soft ? 2 + Math.random() * 3 : 2 + Math.random() * 2, state.sparkleTint);
  }
}

let textureMask: HTMLCanvasElement | null = null;
let textureKey = '';

function dabTexture(x0: number, y0: number, x1: number, y1: number, width: number, spec: LiveSpec, gen: number): void {
  const key = `${gen}:${specKey(spec)}`;
  if (!textureMask || textureKey !== key) {
    textureMask = blankMask();
    textureKey = key;
    addFill(textureMask, spec, currentAlpha(), null);
  }
  const ctx = textureMask.getContext('2d')!;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.strokeStyle = '#ffffff';
  ctx.fillStyle = '#ffffff';
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(x0, y0);
  ctx.lineTo(x1, y1);
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(x1, y1, width / 2, 0, Math.PI * 2);
  ctx.fill();
}

function resolveStatic(distance: number): string | CanvasPattern {
  if (state.ink === 'rainbow') return rainbowCss(distance * 0.55);
  if (state.ink.startsWith('tex-')) return patternFor(state.ink) ?? previewColor(state.ink);
  return previewColor(state.ink);
}

export function paintLine(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  color: string | CanvasPattern,
  alpha: number,
  applicator: Applicator,
  neon: boolean,
): void {
  resetPaint(ctx);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.globalAlpha = alpha;
  const draw = (lw: number, style: string | CanvasPattern, dx = 0, dy = 0) => {
    ctx.lineWidth = lw;
    ctx.strokeStyle = style;
    ctx.beginPath();
    ctx.moveTo(x0 + dx, y0 + dy);
    ctx.lineTo(x1 + dx, y1 + dy);
    ctx.stroke();
  };
  if (neon) {
    ctx.globalCompositeOperation = 'source-over';
    ctx.shadowColor = state.neonTint;
    ctx.shadowBlur = 18;
    ctx.globalAlpha = alpha * 0.9;
    draw(width, state.neonTint);
    ctx.shadowBlur = 0;
    ctx.globalAlpha = alpha;
    draw(Math.max(1.5, width * 0.28), '#ffffff');
    ctx.globalCompositeOperation = 'lighter';
    ctx.globalAlpha = alpha * 0.55;
    draw(Math.max(2, width * 0.7), state.neonTint);
    resetPaint(ctx);
    return;
  }
  if (applicator === 'watercolor') {
    ctx.globalAlpha = alpha * 0.2;
    draw(width * 1.55, color);
    const edge = typeof color === 'string' ? darkenHex(color, 0.35) : color;
    ctx.globalAlpha = alpha * 0.45;
    draw(Math.max(1, width * 0.28), edge);
    resetPaint(ctx);
    return;
  }
  if (applicator === 'gouache') {
    const shade = typeof color === 'string' ? darkenHex(color, 0.4) : color;
    draw(width, shade, 1.4, 1.6);
    draw(width * 0.92, color);
    ctx.globalAlpha = alpha * 0.28;
    draw(Math.max(1, width * 0.22), '#ffffff', -1, -1);
    resetPaint(ctx);
    return;
  }
  if (applicator === 'biro') draw(Math.max(1.15, width * 0.18), color);
  else draw(width, color);
  resetPaint(ctx);
}

export function calligWidth(dx: number, dy: number, speed: number): number {
  const base = state.level === 1 ? 34 : state.brushWidth;
  const angle = Math.atan2(dy, dx);
  const nib = Math.abs(Math.sin(angle - Math.PI / 4));
  const pace = speed < 0.35 ? 1.35 : Math.max(0.18, 1 - speed * 0.22);
  return Math.max(1, base * (0.22 + 0.9 * nib) * pace);
}
