import { paintStroke, paintNeonPath } from './brush';
import { H, W } from './canvas';
import { RainbowStroke } from './rainbow-stroke';
import { glitterPattern, patternFor, previewColor } from './materials';
import type { Applicator, Pt } from './types';

export interface PathPaint {
  kind: 'solid' | 'rainbow' | 'glitter' | 'neon';
  color: string;
  applicator: Applicator;
}

function surface(w: number, h: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = w; canvas.height = h;
  return canvas;
}

function trace(ctx: CanvasRenderingContext2D, points: Pt[]): void {
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let i = 1; i < points.length; i++) ctx.lineTo(points[i].x, points[i].y);
  if (points.length === 1 || points.every(p => p.x === points[0].x && p.y === points[0].y)) {
    ctx.lineTo(points[0].x + 0.01, points[0].y);
  }
  if (points.length > 2 && Math.hypot(points[0].x - points.at(-1)!.x, points[0].y - points.at(-1)!.y) < 0.05) ctx.closePath();
}

function roundDab(ctx: CanvasRenderingContext2D, x: number, y: number): void {
  const radius = ctx.lineWidth / 2;
  if (radius <= 1) {
    // Integrate tiny circles over each pixel; native AA can greatly overstate
    // their area or discard a near-zero stroked path at fractional positions.
    const left = Math.floor(x - radius), top = Math.floor(y - radius);
    const width = Math.ceil(x + radius) - left, height = Math.ceil(y + radius) - top;
    const stamp = surface(width, height), target = stamp.getContext('2d')!;
    const pixels = target.createImageData(width, height), samples = 16;
    for (let py = 0; py < height; py++) for (let px = 0; px < width; px++) {
      let inside = 0;
      for (let sy = 0; sy < samples; sy++) for (let sx = 0; sx < samples; sx++) {
        const dx = left + px + (sx + 0.5) / samples - x, dy = top + py + (sy + 0.5) / samples - y;
        if (dx * dx + dy * dy <= radius * radius) inside++;
      }
      const i = (py * width + px) * 4;
      pixels.data[i] = pixels.data[i + 1] = pixels.data[i + 2] = 255;
      pixels.data[i + 3] = Math.round(255 * inside / (samples * samples));
    }
    target.putImageData(pixels, 0, 0);ctx.drawImage(stamp, left, top);
    return;
  }
  ctx.beginPath();ctx.arc(x, y, radius, 0, Math.PI * 2);ctx.fillStyle = '#ffffff';ctx.fill();
}

function pixelPath(ctx: CanvasRenderingContext2D, points: Pt[], width: number): void {
  const size = Math.max(1, Math.round(width)), offset = Math.floor((size - 1) / 2);
  const nib = surface(size, size), nibCtx = nib.getContext('2d')!, pixels = nibCtx.createImageData(size, size);
  for (let y = 0; y < size; y++) for (let x = 0; x < size; x++) {
    if ((x + 0.5 - size / 2) ** 2 + (y + 0.5 - size / 2) ** 2 > (size / 2) ** 2) continue;
    const i = (y * size + x) * 4;
    pixels.data[i] = pixels.data[i + 1] = pixels.data[i + 2] = pixels.data[i + 3] = 255;
  }
  nibCtx.putImageData(pixels, 0, 0);
  let lastX = NaN, lastY = NaN;
  const stamp = (x: number, y: number) => {
    if (x !== lastX || y !== lastY) ctx.drawImage(nib, x - offset, y - offset);
    lastX = x; lastY = y;
  };
  const line = (a: Pt, b: Pt) => {
    let x = Math.floor(a.x), y = Math.floor(a.y), endX = Math.floor(b.x), endY = Math.floor(b.y);
    const vx = endX - x, vy = endY - y;
    let from = 0, to = 1;
    // Bound captured drags outside the paper before visiting their grid cells.
    for (const [start, delta, limit] of [[x, vx, ctx.canvas.width], [y, vy, ctx.canvas.height]]) {
      if (!delta) { if (start < -size || start > limit + size) return; continue; }
      const t1 = (-size - start) / delta, t2 = (limit + size - start) / delta;
      from = Math.max(from, Math.min(t1, t2)); to = Math.min(to, Math.max(t1, t2));
    }
    if (from > to) return;
    endX = Math.round(x + vx * to); endY = Math.round(y + vy * to);
    x = Math.round(x + vx * from); y = Math.round(y + vy * from);
    const dx = Math.abs(endX - x), dy = -Math.abs(endY - y), sx = x < endX ? 1 : -1, sy = y < endY ? 1 : -1;
    let error = dx + dy;
    for (;;) {
      stamp(x, y); if (x === endX && y === endY) break;
      const twice = error * 2;
      if (twice >= dy) { error += dy; x += sx; }
      if (twice <= dx) { error += dx; y += sy; }
    }
  };
  line(points[0], points[0]);
  for (let i = 1; i < points.length; i++) line(points[i - 1], points[i]);
}

function grain(x: number, y: number): number {
  let n = Math.imul(x, 374761393) ^ Math.imul(y, 668265263);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  return ((n ^ (n >>> 16)) >>> 0) / 4294967296;
}

/** Static pigments use one coverage mask. Rainbow deposits colour locally:
 * extending a stroke must not recolour earlier paint outside the moving nib.
 * Cropped bitmaps avoid allocating and processing the whole canvas. */
export function renderPaintPath(points: Pt[], paint: PathPaint,extent={width:W,height:H}): { canvas: HTMLCanvasElement; x: number; y: number } | null {
  if (!points.length) return null;
  const width = Math.max(1, points[0].w);
  const pad = width * 2.5 + 8;
  let left = extent.width, top = extent.height, right = 0, bottom = 0;
  for (const p of points) {
    left = Math.min(left, p.x); top = Math.min(top, p.y);
    right = Math.max(right, p.x); bottom = Math.max(bottom, p.y);
  }
  const x = Math.max(0, Math.floor(left - pad)), y = Math.max(0, Math.floor(top - pad));
  const w = Math.min(extent.width, Math.ceil(right + pad)) - x, h = Math.min(extent.height, Math.ceil(bottom + pad)) - y;
  if (w <= 0 || h <= 0) return null;
  const local = points.map(p => ({ x: p.x - x, y: p.y - y, w: p.w }));
  const canvas = surface(w, h);
  const ctx = canvas.getContext('2d')!;
  const nibWidth = paint.applicator === 'biro' ? Math.max(1.2, width * 0.16) : width;
  if (paint.kind === 'neon') {
    paintNeonPath(ctx, local.map(p => ({ ...p, w: nibWidth })), paint.color, 1);
    return { canvas, x, y };
  }

  if (paint.kind === 'rainbow') {
    // Keep rasterisation in paper coordinates, matching the streaming layer.
    // Translating tiny segments before rasterisation can change edge coverage.
    const stroke=new RainbowStroke(paint.applicator,width,extent.width,extent.height);
    for(const point of points)stroke.append(point);
    ctx.translate(-x,-y);stroke.render(ctx,1);ctx.setTransform(1,0,0,1,0,0);
    return {canvas,x,y};
  }

  const mask = surface(w, h);
  const coverage = mask.getContext('2d', { willReadFrequently: paint.kind === 'glitter' })!;
  coverage.strokeStyle = '#ffffff'; coverage.lineCap = 'round'; coverage.lineJoin = 'round';
  coverage.lineWidth = nibWidth;
  if (paint.applicator === 'pencil') {
    pixelPath(coverage, local, width);
  } else if (paint.applicator === 'callig') {
    if (local.length === 1) paintStroke(coverage, local[0].x, local[0].y, local[0].x, local[0].y, width, '#ffffff', 1, 'callig', false);
    for (let i = 1; i < local.length; i++) {
      paintStroke(coverage, local[i - 1].x, local[i - 1].y, local[i].x, local[i].y, width, '#ffffff', 1, 'callig', false);
    }
  } else {
    if (paint.applicator === 'watercolor') {
      coverage.lineWidth = width * 1.15;
      coverage.filter = `blur(${Math.max(1, width * 0.12)}px)`;
      coverage.globalAlpha = 0.62;
    }
    const first = local[0];
    if (local.every(point => Math.hypot(point.x - first.x, point.y - first.y) < 0.05)) {
      // A near-zero stroked line can lose its round caps at a one-pixel nib.
      // Fill the requested nib once, retaining the same coverage/filter/alpha.
      roundDab(coverage, first.x, first.y);
    } else { trace(coverage, local); coverage.stroke(); }
    coverage.filter = 'none'; coverage.globalAlpha = 1;
  }

  if (paint.kind === 'glitter') {
    const feather = surface(w, h), fctx = feather.getContext('2d', { willReadFrequently: true })!;
    fctx.filter = `blur(${Math.max(0.8, nibWidth * 0.085)}px)`;
    fctx.drawImage(mask, 0, 0);
    const pixels = fctx.getImageData(0, 0, w, h);
    for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) {
      const i = (yy * w + xx) * 4 + 3;
      const a = pixels.data[i] / 255;
      if (a > 0 && a < 0.99) {
        // Fixed pigment islands, with a little translucent binder between them.
        const fleck = grain(xx + x, yy + y);
        const pigment = grain(xx + x + 137, yy + y + 419);
        pixels.data[i] = 255 * a * (fleck < a ? 0.72 + pigment * 0.28 : 0.05 + pigment * 0.12);
      }
    }
    fctx.putImageData(pixels, 0, 0);
    coverage.clearRect(0, 0, w, h); coverage.drawImage(feather, 0, 0);
  }
  if (paint.applicator === 'crayon' || paint.applicator === 'natural') {
    const pixels = coverage.getImageData(0, 0, w, h);
    for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) {
      const i = (yy * w + xx) * 4 + 3, texture = grain(xx + x, yy + y);
      pixels.data[i] *= paint.applicator === 'crayon' ? (texture < 0.2 ? 0.15 : 0.55 + texture * 0.45) : 0.35 + texture * 0.55;
    }
    coverage.putImageData(pixels, 0, 0);
  }

  {
    // Anchor pigment to paper coordinates, including during cropped rendering.
    ctx.translate(-x, -y);
    ctx.fillStyle = paint.kind === 'glitter' ? glitterPattern(paint.color) : paint.color.startsWith('tex-') ? patternFor(paint.color) ?? previewColor(paint.color) : paint.color;
    ctx.fillRect(x, y, w, h);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }
  if ((paint.applicator === 'gouache' || paint.applicator === 'oil') && paint.kind !== 'glitter') {
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    for (let i = 0; i < 13; i++) {
      const offset = (i / 12 - 0.5) * width * 0.88;
      ctx.save(); ctx.translate(offset * 0.8, offset * 0.6);
      trace(ctx, local); ctx.lineWidth = Math.max(0.5, width / 28);
      ctx.strokeStyle = i % 4 === 0 ? '#ffffff' : '#20202a';
      ctx.globalAlpha = i % 4 === 0 ? 0.12 : 0.055; ctx.stroke(); ctx.restore();
    }
  }
  ctx.globalCompositeOperation = 'destination-in'; ctx.drawImage(mask, 0, 0);
  ctx.globalCompositeOperation = 'source-over';
  return { canvas, x, y };
}
