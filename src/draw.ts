import { playThrottled } from './audio';
import { paintSprayDot, paintStroke, resetBrushSpacing } from './brush';
import { baseCtx, H, W } from './canvas';
import { rainbowCss } from './color';
import { addDrip } from './effects';
import {
  addFill,
  addSparkle,
  blankMask,
  budget,
  bakeStaticStrokes,
  isStaticStroke,
  punchDisc,
  renderStroke,
  startStroke,
} from './live';
import { activeInkId, captureStrokeSpec, glitterPattern, patternFor, previewColor, sampleInk, specKey } from './materials';
import { currentAlpha, state, strokeApplicator } from './state';
import type { LiveSpec } from './types';

let generation = 0;
let traveled = 0;

export function beginStrokeGeneration(): number {
  bakeStaticStrokes(baseCtx);
  generation += 1;
  traveled = 0;
  resetBrushSpacing();
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
  if (mode === '6' || mode === '10' || mode === '12') {
    for (let i = 1; i < Number(mode); i++) {
      const angle = i * Math.PI * 2 / Number(mode);
      pts.push({ x: cx + dx * Math.cos(angle) - dy * Math.sin(angle), y: cy + dx * Math.sin(angle) + dy * Math.cos(angle) });
    }
    return pts;
  }
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

export function sprayCloud(x: number, y: number, holdMs: number): void {
  if (state.applicator === 'confetti') {
    const spread = currentSpread();
    for (let i = 0; i < 4; i++) {
      const angle = Math.random() * Math.PI * 2;
      const radius = Math.sqrt(Math.random()) * spread;
      const px = x + Math.cos(angle) * radius, py = y + Math.sin(angle) * radius;
      for (const p of mirrorPoints(px, py)) {
        baseCtx.save();
        baseCtx.translate(p.x, p.y);
        baseCtx.rotate(Math.random() * Math.PI);
        baseCtx.globalAlpha = currentAlpha();
        const ink = activeInkId();
        baseCtx.fillStyle = ink === 'sparkle' ? glitterPattern() : ink.startsWith('tex-') ? patternFor(ink) ?? previewColor(ink) : ink === 'rainbow' ? rainbowCss(Math.random() * 360) : sampleInk(ink, performance.now(), traveled);
        if (ink === 'neon') { baseCtx.shadowColor = state.neonTint; baseCtx.shadowBlur = 8; }
        const size = Math.max(3, state.brushWidth * (0.1 + Math.random() * 0.16));
        baseCtx.fillRect(-size / 2, -size / 4, size, size / 2);
        baseCtx.restore();
      }
    }
    return;
  }
  const splatter = state.applicator === 'splatter';
  const spread = currentSpread();
  if (!splatter) {
    const count = 24 + Math.min(18, Math.floor(holdMs / 70));
    for (let i = 0; i < count; i++) {
      const ang = Math.random() * Math.PI * 2;
      const u = Math.max(1e-4, Math.random());
      const rad = Math.min(spread, spread * Math.sqrt(-Math.log(u)) * 0.58);
      const fall = 1 - rad / Math.max(1, spread);
      const size = 0.8 + Math.random() * 2.1 * (0.3 + fall);
      const px = x + Math.cos(ang) * rad;
      const py = y + Math.sin(ang) * rad;
      for (const p of mirrorPoints(px, py)) blot(p.x, p.y, size, 'mist');
    }
    if (holdMs > 320 && Math.random() < 0.35) {
      const ink = activeInkId();
      if (ink === 'sparkle') blot(x + (Math.random() - 0.5) * 8, y, 2, 'fleck');
      else addDrip(x + (Math.random() - 0.5) * 10, y, 2 + Math.random() * 2.5, sampleInk(ink, performance.now(), traveled));
    }
    return;
  }
  const count = 5 + (Math.random() < 0.35 ? 3 : 0);
  for (let i = 0; i < count; i++) {
    const ang = Math.random() * Math.PI * 2;
    const rad = Math.random() ** 1.65 * spread;
    const size = 2.2 + Math.random() ** 0.5 * (8 + spread * 0.06);
    const px = x + Math.cos(ang) * rad;
    const py = y + Math.sin(ang) * rad;
    for (const p of mirrorPoints(px, py)) blot(p.x, p.y, size, 'splatter');
  }
}

function currentSpread(): number {
  return state.brushWidth * (state.applicator === 'splatter' ? 2.1 : 2.6);
}

function strokeRaw(x0: number, y0: number, x1: number, y1: number, width: number, speed: number, lane: number, gen: number): void {
  const scrub = state.tool === 'eraser' && state.eraserMode === 'scrub';
  const dist = Math.hypot(x1 - x0, y1 - y0);
  if (lane === 0) traveled += dist;

  if (scrub) {
    paintStroke(baseCtx, x0, y0, x1, y1, width * 1.15, '#ffffff', 1, 'marker', false, 0, true);
    punchDisc((x0 + x1) / 2, (y0 + y1) / 2, width * 0.65);
    return;
  }

  if (lane === 0 && state.tool === 'draw' && state.applicator === 'marker' && dist > 1.5) {
    playThrottled('squeak', 280, 0.84 + Math.min(0.5, speed * 0.2));
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
    const stroke = startStroke(spec, strokeApplicator(), currentAlpha(), gen, lane);
    if (stroke.points.length === 0) stroke.points.push({ x: x0, y: y0, w: width });
    stroke.points.push({ x: x1, y: y1, w: width });
    budget(performance.now(), renderStroke, baseCtx);
    return;
  }

  const neon = state.ink === 'neon';
  const color = neon ? '#ffffff' : resolveStatic(traveled);
  paintStroke(baseCtx, x0, y0, x1, y1, width, color, currentAlpha(), state.applicator, neon, speed);
}

function blot(x: number, y: number, size: number, kind: 'mist' | 'splatter' | 'fleck' = 'mist'): void {
  const spec = captureStrokeSpec();
  if (spec && spec !== 'sparkle' && isStaticStroke(spec)) {
    paintSprayDot(baseCtx, x, y, kind === 'splatter' ? size * 0.55 : size, spec.kind === 'neon' ? state.neonTint : resolveStatic(traveled), currentAlpha(), kind, spec.kind === 'neon');
    return;
  }
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
    const radius = kind === 'splatter' ? size * 0.55 : size;
    const stroke = startStroke(spec, state.applicator === 'splatter' ? 'splatter' : 'mist', currentAlpha(), generation, 0);
    stroke.points.push({ x, y, w: radius * 2 });
    return;
  }
  const neon = state.ink === 'neon';
  const color = neon ? state.neonTint : resolveStatic(traveled);
  const radius = kind === 'mist' ? size : kind === 'fleck' ? size : size * 0.55;
  const alpha = kind === 'mist' ? currentAlpha() * 0.55 : currentAlpha();
  paintSprayDot(baseCtx, x, y, radius, color, alpha, kind, neon);
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
  if (state.ink === 'sparkle') return glitterPattern();
  if (state.ink === 'rainbow') return rainbowCss(distance * 0.55);
  if (state.ink.startsWith('tex-')) return patternFor(state.ink) ?? previewColor(state.ink);
  return previewColor(state.ink);
}
