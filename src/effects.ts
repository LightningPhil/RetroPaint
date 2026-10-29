import { artwork } from './artwork';
import { activeSector, clipSegment, paintSectorPatch } from './symmetry-mask';
import { play,playDrawing } from './audio';
import { base, baseCtx, cloneCanvas, H, W } from './canvas';
import { pushHistory } from './history';
import { bakeLive, clearLive } from './live';
import { currentWidth, state } from './state';
import { advectMany } from './smudge';
import { mirrorMotion } from './symmetry';
import { activeLayer, renderLayers, resetLayers } from './layers';
import { finishObjectStroke, hasObjectCapture } from './objects';

export interface Drip {
  x: number;
  y: number;
  vy: number;
  r: number;
  color: string;
  age: number;
  target: CanvasRenderingContext2D;
}

export const drips: Drip[] = [];

let wipe: { t: number; snap: HTMLCanvasElement } | null = null;
let hole: { x: number; y: number; r: number; life: number; src: ImageData; target: CanvasRenderingContext2D; clear: Uint8ClampedArray; held: boolean } | null = null;

export function isBusy(): boolean {
  return wipe !== null || hole !== null;
}

export function addDrip(x: number, y: number, r: number, color: string): void {
  drips.push({ x, y, vy: 0.4, r, color, age: 0, target: baseCtx });
}

export function startSqueegee(): void {
  if (isBusy()) return;
  pushHistory();
  const snapshot = cloneCanvas(base); renderLayers(snapshot.getContext('2d')!, performance.now());
  resetLayers();
  clearLive();
  wipe = { t: 0, snap: snapshot };
  artwork.reset();
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

export function startHole(x: number, y: number, history=true, held=false): void {
  if (isBusy() || x+58<=0 || y+58<=0 || x-58>=W || y-58>=H) return;
  if(history)pushHistory();
  bakeLive(baseCtx, performance.now());
  clearLive();
  const clearCanvas=document.createElement('canvas');clearCanvas.width=clearCanvas.height=1;
  const clearCtx=clearCanvas.getContext('2d')!;
  // A selected piece has a clear backing, even when its parent sheet is Paper.
  const paper=hasObjectCapture()?null:activeLayer().paper;
  if(paper){clearCtx.fillStyle=paper;clearCtx.fillRect(0,0,1,1);}
  hole = { x, y, r: 58, life: 1, src: baseCtx.getImageData(0, 0, W, H), target:baseCtx, clear:clearCtx.getImageData(0,0,1,1).data, held };
  state.busy = true;
  playDrawing('vwoop');
}

export function moveHole(x:number,y:number):void {
  if(!hole||!hole.held||hole.x===x&&hole.y===y)return;
  // Continue from committed paint at the new centre; never resurrect an earlier hole.
  hole.x=x;hole.y=y;hole.life=1;
  hole.src=hole.target.getImageData(0,0,hole.target.canvas.width,hole.target.canvas.height);
}

export function stopHole():void {
  if(!hole)return;
  hole=null;state.busy=false;finishObjectStroke();
}

export function tickHole(dt: number): void {
  if (!hole || hole.life<=0) return;
  hole.life -= dt / 680;
  const amount = 1 - Math.max(0, hole.life);
  const { x, y, r, src, target, clear } = hole;
  const x0 = Math.max(0, Math.floor(x - r));
  const y0 = Math.max(0, Math.floor(y - r));
  const x1 = Math.min(src.width, Math.ceil(x + r));
  const y1 = Math.min(src.height, Math.ceil(y + r));
  if(x1<=x0||y1<=y0){if(!hole.held&&hole.life<=0)stopHole();return;}
  const img = target.getImageData(x0, y0, x1 - x0, y1 - y0);
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
      if (sx < 0 || sy < 0 || sx >= src.width || sy >= src.height || dist < amount * r * 0.25) {
        img.data.set(clear,di);
        continue;
      }
      const si = (sy * src.width + sx) * 4;
      img.data[di] = src.data[si];
      img.data[di + 1] = src.data[si + 1];
      img.data[di + 2] = src.data[si + 2];
      img.data[di + 3] = src.data[si + 3];
    }
  }
  paintSectorPatch(target,img,x0,y0,x,y,r,true);
  if (hole.life <= 0) {
    for(let yy=y0;yy<y1;yy++)for(let xx=x0;xx<x1;xx++){
      if(Math.hypot(xx-x,yy-y)<=r*.94)img.data.set(clear,((yy-y0)*dw+xx-x0)*4);
    }
    paintSectorPatch(target,img,x0,y0,x,y,r*.94,true);
    if(!hole.held)stopHole();
  }
}

export function tickDrips(dt: number): void {
  if (!drips.length) return;
  for (let i = drips.length - 1; i >= 0; i--) {
    const drip = drips[i];
    const ctx = drip.target; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 0.9; ctx.globalCompositeOperation = 'source-over';
    drip.age += dt;
    drip.vy += dt * 0.004;
    drip.y += drip.vy * dt * 0.08;
    ctx.fillStyle = drip.color;
    ctx.beginPath(); ctx.arc(drip.x, drip.y, drip.r, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    if (drip.age > 1100 || drip.y > ctx.canvas.height + 8) drips.splice(i, 1);
  }
}

export function beginBake(now=performance.now()): void {
  pushHistory();
  bakeLive(baseCtx, now);
  clearLive();
}

export function smudge(x: number, y: number, dx: number, dy: number, radius: number,
  pending?: { source: CanvasRenderingContext2D; commit: () => void }): void {
  const sector=activeSector();
  const dabs=(sector ? [{x,y,dx,dy}] : mirrorMotion(x,y,dx,dy)).filter(p=>p.x+radius>0&&p.y+radius>0&&p.x-radius<W&&p.y-radius<H);
  if(!dabs.length)return;
  const pad=radius+Math.hypot(dx,dy)+2;
  const left=Math.max(0,Math.floor(Math.min(...dabs.map(p=>p.x))-pad));
  const top=Math.max(0,Math.floor(Math.min(...dabs.map(p=>p.y))-pad));
  const right=Math.min(W,Math.ceil(Math.max(...dabs.map(p=>p.x))+pad));
  const bottom=Math.min(H,Math.ceil(Math.max(...dabs.map(p=>p.y))+pad));
  if(right<=left||bottom<=top)return;
  const patch=(pending?.source??baseCtx).getImageData(left,top,right-left,bottom-top);
  const moved=advectMany(patch.data,patch.width,patch.height,dabs.map(p=>({...p,x:p.x-left,y:p.y-top})),radius,0.88*state.opacity, sector ? (px,py,sx,sy)=>{
    const line=clipSegment({x:px+left+0.5,y:py+top+0.5},{x:sx+left+0.5,y:sy+top+0.5},sector,0.5);
    return line ? {x:line[1].x-left-0.5,y:line[1].y-top-0.5} : {x:px,y:py};
  } : undefined);
  if(!moved.some((value,i)=>value!==patch.data[i]))return;
  pending?.commit();
  patch.data.set(moved);
  paintSectorPatch(baseCtx,patch,left,top,x,y,radius);
}

export interface PixelFilterStroke {
  target: CanvasRenderingContext2D;
  source: ImageData;
  covered: Uint8Array;
  strength: number;
  mode: typeof state.eraserMode;
}

/** One immutable source and one contribution per pixel for an entire gesture. */
export function beginPixelFilterStroke(): PixelFilterStroke {
  return { target: baseCtx, source: baseCtx.getImageData(0, 0, W, H), covered: new Uint8Array(W * H), strength: state.opacity, mode: state.eraserMode };
}

export function pixelateAt(x: number, y: number, stroke?: PixelFilterStroke): void {
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
  }, stroke);
}

export function invertAt(x: number, y: number, stroke?: PixelFilterStroke): void {
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
  }, stroke);
}

export function embossAt(x: number, y: number, stroke?: PixelFilterStroke): void {
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
  }, stroke);
}

function filterDisc(
  x: number,
  y: number,
  radius: number,
  paint: (data: Uint8ClampedArray, w: number, h: number, cx: number, cy: number) => void,
  stroke?: PixelFilterStroke,
): void {
  if (stroke && (stroke.target !== baseCtx || stroke.source.width !== W || stroke.source.height !== H)) return;
  const strength = Math.max(0, Math.min(1, stroke?.strength ?? state.opacity));
  if (strength === 0) return;
  const x0 = Math.max(0, Math.floor(x - radius));
  const y0 = Math.max(0, Math.floor(y - radius));
  const x1 = Math.min(W, Math.ceil(x + radius));
  const y1 = Math.min(H, Math.ceil(y + radius));
  const w = x1 - x0;
  const h = y1 - y0;
  if (w < 2 || h < 2) return;
  const img = baseCtx.getImageData(x0, y0, w, h);
  const source = new Uint8ClampedArray(img.data);
  if (stroke) for (let row = 0; row < h; row++) {
    const start = ((y0 + row) * W + x0) * 4;
    source.set(stroke.source.data.subarray(start, start + w * 4), row * w * 4);
  }
  const filtered = new Uint8ClampedArray(source);
  paint(filtered, w, h, x - x0, y - y0);
  for (let row = 0; row < h; row++) for (let col = 0; col < w; col++) {
    if ((col + x0 - x) ** 2 + (row + y0 - y) ** 2 > radius * radius) continue;
    const index = (y0 + row) * W + x0 + col;
    if (stroke?.covered[index]) continue;
    if (stroke) stroke.covered[index] = 1;
    const i = (row * w + col) * 4;
    for (let c = 0; c < 3; c++) img.data[i + c] = source[i + c] + (filtered[i + c] - source[i + c]) * strength;
    img.data[i + 3] = source[i + 3];
  }
  paintSectorPatch(baseCtx,img,x0,y0,x,y,radius);
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
