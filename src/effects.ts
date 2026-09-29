import { play } from './audio';
import { base, baseCtx, cloneCanvas, H, W } from './canvas';
import { pushHistory } from './history';
import { bakeLive, clearLive } from './live';
import { currentWidth, state } from './state';

export interface Drip {
  x: number;
  y: number;
  vy: number;
  r: number;
  color: string;
  age: number;
}

export interface SparkParticle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
}

export const drips: Drip[] = [];
export const sparks: SparkParticle[] = [];

let wipe: { t: number; snap: HTMLCanvasElement } | null = null;
let hole: { x: number; y: number; r: number; life: number; src: ImageData } | null = null;

export function isBusy(): boolean {
  return wipe !== null || hole !== null;
}

export function addDrip(x: number, y: number, r: number, color: string): void {
  drips.push({ x, y, vy: 0.4, r, color, age: 0 });
}

export function burst(x: number, y: number): void {
  for (let i = 0; i < 26; i++) {
    sparks.push({
      x,
      y,
      vx: (Math.random() - 0.5) * 16,
      vy: (Math.random() - 0.5) * 16 - 2,
      life: 1,
    });
  }
}

export function startSqueegee(): void {
  if (isBusy()) return;
  pushHistory();
  bakeLive(baseCtx, performance.now());
  clearLive();
  wipe = { t: 0, snap: cloneCanvas(base) };
  state.busy = true;
  play('squeegee');
}

export function squeegeeX(): number | null {
  if (!wipe) return null;
  const slide = Math.min(1, wipe.t / 760);
  const eased = slide < 0.5 ? 2 * slide * slide : 1 - ((-2 * slide + 2) ** 2) / 2;
  let x = eased * (W + 30);
  if (wipe.t > 760) {
    const bounce = Math.min(1, (wipe.t - 760) / 240);
    x = W - Math.sin(bounce * Math.PI) * 42;
  }
  return x;
}

export function tickSqueegee(dt: number): void {
  if (!wipe) return;
  wipe.t += dt;
  const x = squeegeeX() ?? W;
  baseCtx.setTransform(1, 0, 0, 1, 0, 0);
  baseCtx.globalAlpha = 1;
  baseCtx.globalCompositeOperation = 'source-over';
  baseCtx.fillStyle = '#ffffff';
  baseCtx.fillRect(0, 0, W, H);
  const srcX = Math.max(0, Math.min(W, x));
  if (srcX < W) baseCtx.drawImage(wipe.snap, srcX, 0, W - srcX, H, srcX, 0, W - srcX, H);
  if (wipe.t > 1040) {
    baseCtx.fillStyle = '#ffffff';
    baseCtx.fillRect(0, 0, W, H);
    wipe = null;
    state.busy = false;
  }
}

export function startHole(x: number, y: number): void {
  if (isBusy()) return;
  pushHistory();
  bakeLive(baseCtx, performance.now());
  clearLive();
  hole = { x, y, r: 58, life: 1, src: baseCtx.getImageData(0, 0, W, H) };
  state.busy = true;
  play('vwoop');
}

export function tickHole(dt: number): void {
  if (!hole) return;
  hole.life -= dt / 680;
  const amount = 1 - Math.max(0, hole.life);
  const { x, y, r, src } = hole;
  const x0 = Math.max(0, Math.floor(x - r));
  const y0 = Math.max(0, Math.floor(y - r));
  const x1 = Math.min(W, Math.ceil(x + r));
  const y1 = Math.min(H, Math.ceil(y + r));
  const img = baseCtx.getImageData(x0, y0, x1 - x0, y1 - y0);
  const dw = x1 - x0;
  for (let yy = y0; yy < y1; yy++) {
    for (let xx = x0; xx < x1; xx++) {
      const dx = xx - x;
      const dy = yy - y;
      const dist = Math.hypot(dx, dy);
      if (dist > r) continue;
      const ang = Math.atan2(dy, dx) + amount * 3.4;
      const nd = dist * (1 - amount * 0.9);
      const sx = Math.floor(x + Math.cos(ang) * nd);
      const sy = Math.floor(y + Math.sin(ang) * nd);
      const di = ((yy - y0) * dw + (xx - x0)) * 4;
      if (sx < 0 || sy < 0 || sx >= W || sy >= H || dist < amount * r * 0.25) {
        img.data[di] = img.data[di + 1] = img.data[di + 2] = 255;
        img.data[di + 3] = 255;
        continue;
      }
      const si = (sy * W + sx) * 4;
      img.data[di] = src.data[si];
      img.data[di + 1] = src.data[si + 1];
      img.data[di + 2] = src.data[si + 2];
      img.data[di + 3] = 255;
    }
  }
  baseCtx.putImageData(img, x0, y0);
  if (hole.life <= 0) {
    baseCtx.fillStyle = '#ffffff';
    baseCtx.beginPath();
    baseCtx.arc(x, y, r * 0.94, 0, Math.PI * 2);
    baseCtx.fill();
    hole = null;
    state.busy = false;
  }
}

export function tickDrips(dt: number): void {
  if (!drips.length) return;
  baseCtx.setTransform(1, 0, 0, 1, 0, 0);
  baseCtx.globalAlpha = 0.9;
  baseCtx.globalCompositeOperation = 'source-over';
  for (let i = drips.length - 1; i >= 0; i--) {
    const drip = drips[i];
    drip.age += dt;
    drip.vy += dt * 0.004;
    drip.y += drip.vy * dt * 0.08;
    baseCtx.fillStyle = drip.color;
    baseCtx.beginPath();
    baseCtx.arc(drip.x, drip.y, drip.r, 0, Math.PI * 2);
    baseCtx.fill();
    if (drip.age > 1100 || drip.y > H + 8) drips.splice(i, 1);
  }
  baseCtx.globalAlpha = 1;
}

export function tickSparks(dt: number): void {
  for (let i = sparks.length - 1; i >= 0; i--) {
    const spark = sparks[i];
    spark.x += spark.vx * dt * 0.06;
    spark.y += spark.vy * dt * 0.06;
    spark.vy += dt * 0.018;
    spark.life -= dt / 650;
    if (spark.life <= 0) sparks.splice(i, 1);
  }
}

export function drawSparks(ctx: CanvasRenderingContext2D): void {
  for (const spark of sparks) {
    ctx.fillStyle = `rgba(255, 214, 70, ${Math.max(0, spark.life)})`;
    ctx.beginPath();
    ctx.arc(spark.x, spark.y, Math.max(1, spark.life * 5), 0, Math.PI * 2);
    ctx.fill();
  }
}

export function beginBake(): void {
  pushHistory();
  bakeLive(baseCtx, performance.now());
  clearLive();
}

export function smudge(x: number, y: number): void {
  const r = Math.max(18, currentWidth());
  const ox = (Math.random() - 0.5) * 12;
  const oy = (Math.random() - 0.5) * 12;
  baseCtx.save();
  baseCtx.globalAlpha = 0.75;
  baseCtx.drawImage(base, x - r, y - r, r * 2, r * 2, x - r + ox, y - r + oy, r * 2, r * 2);
  baseCtx.restore();
}

export function pixelateAt(x: number, y: number): void {
  const radius = Math.max(22, currentWidth() * 1.4);
  filterDisc(x, y, radius, (data, w, h, cx, cy) => {
    const block = 8;
    const copy = new Uint8ClampedArray(data);
    for (let by = 0; by < h; by += block) {
      for (let bx = 0; bx < w; bx += block) {
        const mx = Math.min(w - 1, bx + block / 2);
        const my = Math.min(h - 1, by + block / 2);
        if ((mx - cx) ** 2 + (my - cy) ** 2 > radius * radius) continue;
        let r = 0, g = 0, b = 0, n = 0;
        for (let yy = by; yy < Math.min(h, by + block); yy++) {
          for (let xx = bx; xx < Math.min(w, bx + block); xx++) {
            const i = (yy * w + xx) * 4;
            r += copy[i];
            g += copy[i + 1];
            b += copy[i + 2];
            n++;
          }
        }
        r /= n; g /= n; b /= n;
        for (let yy = by; yy < Math.min(h, by + block); yy++) {
          for (let xx = bx; xx < Math.min(w, bx + block); xx++) {
            if ((xx - cx) ** 2 + (yy - cy) ** 2 > radius * radius) continue;
            const i = (yy * w + xx) * 4;
            data[i] = r;
            data[i + 1] = g;
            data[i + 2] = b;
          }
        }
      }
    }
  });
}

export function invertAt(x: number, y: number): void {
  const radius = Math.max(20, currentWidth() * 1.3);
  filterDisc(x, y, radius, (data, w, _h, cx, cy) => {
    for (let yy = 0; yy < _h; yy++) {
      for (let xx = 0; xx < w; xx++) {
        if ((xx - cx) ** 2 + (yy - cy) ** 2 > radius * radius) continue;
        const i = (yy * w + xx) * 4;
        data[i] = 255 - data[i];
        data[i + 1] = 255 - data[i + 1];
        data[i + 2] = 255 - data[i + 2];
      }
    }
  });
}

export function embossAt(x: number, y: number): void {
  const radius = Math.max(20, currentWidth() * 1.3);
  filterDisc(x, y, radius, (data, w, h, cx, cy) => {
    const copy = new Uint8ClampedArray(data);
    for (let yy = 1; yy < h; yy++) {
      for (let xx = 1; xx < w; xx++) {
        if ((xx - cx) ** 2 + (yy - cy) ** 2 > radius * radius) continue;
        const i = (yy * w + xx) * 4;
        const j = (yy * w + (xx - 1)) * 4;
        const mag = 128 + (copy[i] - copy[j]) * 0.9;
        const v = Math.max(0, Math.min(255, mag));
        data[i] = v * 0.7 + copy[i] * 0.3;
        data[i + 1] = v * 0.7 + copy[i + 1] * 0.3;
        data[i + 2] = v * 0.7 + copy[i + 2] * 0.3;
      }
    }
  });
}

function filterDisc(
  x: number,
  y: number,
  radius: number,
  paint: (data: Uint8ClampedArray, w: number, h: number, cx: number, cy: number) => void,
): void {
  const x0 = Math.max(0, Math.floor(x - radius));
  const y0 = Math.max(0, Math.floor(y - radius));
  const x1 = Math.min(W, Math.ceil(x + radius));
  const y1 = Math.min(H, Math.ceil(y + radius));
  const w = x1 - x0;
  const h = y1 - y0;
  if (w < 2 || h < 2) return;
  const img = baseCtx.getImageData(x0, y0, w, h);
  paint(img.data, w, h, x - x0, y - y0);
  baseCtx.putImageData(img, x0, y0);
}

export function drawSqueegee(ctx: CanvasRenderingContext2D): void {
  const x = squeegeeX();
  if (x === null) return;
  ctx.save();
  ctx.translate(Math.min(W + 10, x), H / 2);
  ctx.fillStyle = '#FFD166';
  ctx.strokeStyle = '#1A1A1A';
  ctx.lineWidth = 6;
  ctx.beginPath();
  ctx.roundRect(-18, -H * 0.42, 36, H * 0.84, 10);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = '#1A1A1A';
  ctx.fillRect(8, -16, 46, 14);
  ctx.restore();
}
