import { resetPaint } from './canvas';
import { darkenHex, hexToRgb, mixHex, neonColor } from './color';
import { state } from './state';
import type { Applicator } from './types';

let bloomX = -1e9;
let bloomY = -1e9;

export function resetBrushSpacing(): void {
  bloomX = -1e9;
  bloomY = -1e9;
}

function fade(color: string): string {
  const rgb = hexToRgb(color);
  if (!rgb) return 'rgba(0,0,0,0)';
  return `rgba(${rgb.r},${rgb.g},${rgb.b},0)`;
}

function strokeLine(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  color: string | CanvasPattern | CanvasGradient,
  dx = 0,
  dy = 0,
): void {
  ctx.lineWidth = width;
  ctx.strokeStyle = color;
  ctx.beginPath();
  ctx.moveTo(x0 + dx, y0 + dy);
  ctx.lineTo(x1 + dx, y1 + dy);
  ctx.stroke();
}

export function paintStroke(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  color: string | CanvasPattern | CanvasGradient,
  alpha: number,
  applicator: Applicator,
  neon: boolean,
  speed = 0,
  plain = false,
  lite = false,
): void {
  resetPaint(ctx);
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
  ctx.globalAlpha = alpha;
  if (plain) {
    strokeLine(ctx, x0, y0, x1, y1, width, color);
    resetPaint(ctx);
    return;
  }
  if (neon && typeof color === 'string') {
    paintNeon(ctx, x0, y0, x1, y1, width, alpha);
    return;
  }
  if (applicator === 'callig') paintCalligraphy(ctx, x0, y0, x1, y1, width, color, alpha);
  else if (applicator === 'biro') paintBiro(ctx, x0, y0, x1, y1, width, color, alpha, speed, lite);
  else if (applicator === 'watercolor') paintWatercolor(ctx, x0, y0, x1, y1, width, color, alpha, lite);
  else if (applicator === 'gouache') paintGouache(ctx, x0, y0, x1, y1, width, color, alpha, speed, lite);
  else paintMarker(ctx, x0, y0, x1, y1, width, color, alpha, speed, lite);
  resetPaint(ctx);
}

function paintNeon(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  alpha: number,
): void {
  paintNeonPath(ctx,[{x:x0,y:y0,w:width},{x:x1,y:y1,w:width}],state.neonTint,alpha);
}

/** A continuous fluorescent ribbon: coloured centre, gradual shading, soft spill. */
export function paintNeonPath(ctx: CanvasRenderingContext2D, points: { x: number; y: number; w: number }[], tint: string, alpha: number): void {
  if (!points.length) return;
  ctx.save(); resetPaint(ctx);
  const width = points[0].w;
  ctx.beginPath(); ctx.moveTo(points[0].x, points[0].y);
  for (const p of points.slice(1)) ctx.lineTo(p.x, p.y);
  if (points.every(p => p.x === points[0].x && p.y === points[0].y)) ctx.lineTo(points[0].x + 0.01, points[0].y);
  if (points.length > 2 && Math.hypot(points[0].x - points.at(-1)!.x, points[0].y - points.at(-1)!.y) < 0.05) ctx.closePath();
  const fluorescent=neonColor(tint);
  const pass=(w:number,color:string,blur:number,opacity:number)=>{
    ctx.lineWidth=w;ctx.strokeStyle=color;ctx.filter=blur ? 'blur('+blur+'px)' : 'none';
    ctx.globalAlpha=alpha*opacity;ctx.stroke();
  };
  pass(width*1.1,fluorescent,Math.max(3,width*0.5),0.38);
  pass(width*0.86,fluorescent,Math.max(0.7,width*0.09),0.95);
  // Fine nested contours form a smooth colour profile, with no white filament.
  // Render each as a whole path so joins and intersections keep even coverage.
  for(let i=0;i<=24;i++){
    const t=i/24,light=t*t*(3-2*t)*0.34;
    pass(width*(0.78-0.69*t),mixHex(fluorescent,'#ffffff',light),0,1);
  }
  ctx.restore();
}

function paintMarker(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  color: string | CanvasPattern | CanvasGradient,
  alpha: number,
  speed: number,
  lite: boolean,
): void {
  const pace = speed > 1.4 ? 0.9 : speed < 0.25 ? 1.06 : 1;
  const w = width * pace;
  const ink = typeof color === 'string' ? darkenHex(color, 0.2) : color;
  ctx.globalAlpha = alpha * 0.18;
  strokeLine(ctx, x0, y0, x1, y1, w * 1.2, color);
  ctx.globalAlpha = alpha;
  strokeLine(ctx, x0, y0, x1, y1, w * 0.86, color);
  if (lite) return;
  ctx.globalAlpha = alpha * 0.22;
  strokeLine(ctx, x0, y0, x1, y1, Math.max(1.2, w * 0.34), ink, -0.6, 0.4);
}

function paintBiro(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  color: string | CanvasPattern | CanvasGradient,
  alpha: number,
  speed: number,
  lite: boolean,
): void {
  const thin = speed > 2 ? 0.62 : speed > 1 ? 0.82 : 1;
  const w = Math.max(1.05, width * 0.15 * thin);
  const ang = Math.atan2(y1 - y0, x1 - x0);
  const px = Math.cos(ang + Math.PI / 2);
  const py = Math.sin(ang + Math.PI / 2);
  const body = typeof color === 'string' ? darkenHex(color, 0.12) : color;
  const sheen = typeof color === 'string' ? mixHex(color, '#ffffff', 0.62) : color;
  if (lite) {
    ctx.globalAlpha = alpha;
    strokeLine(ctx, x0, y0, x1, y1, w, body);
    return;
  }
  ctx.globalAlpha = alpha;
  ctx.lineWidth = w;
  ctx.strokeStyle = body;
  ctx.beginPath();
  const dist = Math.max(1, Math.hypot(x1 - x0, y1 - y0));
  const steps = Math.max(1, Math.ceil(dist / 2.5));
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = x0 + (x1 - x0) * t;
    const y = y0 + (y1 - y0) * t;
    const o = Math.sin(x * 0.45 + y * 0.28 + t * 5) * 0.28;
    const X = x + px * o;
    const Y = y + py * o;
    if (i === 0) ctx.moveTo(X, Y);
    else ctx.lineTo(X, Y);
  }
  ctx.stroke();
  ctx.globalAlpha = alpha * 0.7;
  ctx.lineWidth = Math.max(0.6, w * 0.35);
  ctx.strokeStyle = sheen;
  ctx.beginPath();
  ctx.moveTo(x0 - px * 0.45, y0 - py * 0.45);
  ctx.lineTo(x1 - px * 0.45, y1 - py * 0.45);
  ctx.stroke();
}

function paintCalligraphy(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  color: string | CanvasPattern | CanvasGradient,
  alpha: number,
): void {
  const w = Math.max(1.4, width);
  const dx = x1 - x0;
  const dy = y1 - y0;
  const len = Math.hypot(dx, dy);
  ctx.globalAlpha = alpha;
  ctx.fillStyle = color;
  if (len < 0.35) {
    stampNib(ctx, x1, y1, w);
    return;
  }
  const ang = -Math.PI / 4;
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  const ux = dx / len;
  const uy = dy / len;
  const px = -uy;
  const py = ux;
  const span = w / 2;
  const pad = 0.6;
  const overlap = 0.7;
  const nibAt = (x: number, y: number) => ({
    ax: x - c * span + px * pad,
    ay: y - s * span + py * pad,
    bx: x + c * span - px * pad,
    by: y + s * span - py * pad,
  });
  const a = nibAt(x0 - ux * overlap, y0 - uy * overlap);
  const b = nibAt(x1 + ux * overlap, y1 + uy * overlap);
  ctx.beginPath();
  ctx.moveTo(a.ax, a.ay);
  ctx.lineTo(a.bx, a.by);
  ctx.lineTo(b.bx, b.by);
  ctx.lineTo(b.ax, b.ay);
  ctx.closePath();
  ctx.fill();
}

function stampNib(ctx: CanvasRenderingContext2D, x: number, y: number, w: number): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(-Math.PI / 4);
  ctx.scale(1, 0.2);
  ctx.beginPath();
  ctx.arc(0, 0, w / 2, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function paintGouache(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  color: string | CanvasPattern | CanvasGradient,
  alpha: number,
  speed: number,
  lite: boolean,
): void {
  // A fixed, broad bristle fan, with restrained pigment variation. Fixed offsets
  // prevent the striped joints produced by rotating the nib at every mouse sample.
  const body = width * 0.94;
  ctx.globalAlpha = alpha;
  strokeLine(ctx, x0, y0, x1, y1, body, color);
  if (typeof color !== 'string' || lite) return;
  const bristles = 13;
  for (let i = 0; i < bristles; i++) {
    const offset = (i / (bristles - 1) - 0.5) * body * 0.94;
    const tint = i % 4 === 0 ? mixHex(color, '#ffffff', 0.12) : darkenHex(color, 0.025 + (i % 3) * 0.018);
    const thickness = Math.max(0.5, body / bristles * (speed > 1.5 ? 0.34 : 0.55));
    strokeLine(ctx, x0, y0, x1, y1, thickness, tint, offset * 0.8, offset * 0.6);
  }
}

function paintWatercolor(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  x1: number,
  y1: number,
  width: number,
  color: string | CanvasPattern | CanvasGradient,
  alpha: number,
  lite: boolean,
): void {
  const step = Math.max(3, width * 0.12);
  const distFromBloom = Math.hypot(x1 - bloomX, y1 - bloomY);
  if (distFromBloom < step) return;
  bloomX = x1;
  bloomY = y1;
  if (typeof color === 'string' && !lite) {
    const r = width * 0.78;
    const grad = ctx.createRadialGradient(x1, y1, r * 0.2, x1, y1, r);
    grad.addColorStop(0, color);
    grad.addColorStop(0.7, color);
    grad.addColorStop(1, fade(color));
    ctx.globalAlpha = alpha * 0.55;
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(x1, y1, r, 0, Math.PI * 2);
    ctx.fill();
    return;
  }
  ctx.globalAlpha = alpha * 0.16;
  strokeLine(ctx, x0, y0, x1, y1, width * 1.5, color);
  const rim = typeof color === 'string' ? darkenHex(color, 0.38) : color;
  ctx.globalAlpha = alpha * 0.34;
  strokeLine(ctx, x0, y0, x1, y1, Math.max(1.2, width * 0.22), rim);
}

export function paintSprayDot(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  color: string | CanvasPattern | CanvasGradient,
  alpha: number,
  kind: 'mist' | 'splatter' | 'fleck',
  neon: boolean,
): void {
  resetPaint(ctx);
  const r = Math.max(0.4, radius);
  if (neon) {
    const tint=neonColor(typeof color==='string'?color:state.neonTint);
    ctx.shadowColor=tint;ctx.shadowBlur=kind==='mist'?8:14;ctx.globalAlpha=alpha;
    const glow=ctx.createRadialGradient(x,y,0,x,y,r);
    glow.addColorStop(0,mixHex(tint,'#ffffff',0.34));
    glow.addColorStop(0.45,mixHex(tint,'#ffffff',0.15));
    glow.addColorStop(0.78,tint);glow.addColorStop(1,fade(tint));
    ctx.fillStyle=glow;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
    resetPaint(ctx);
    return;
  }
  ctx.fillStyle = color;
  if (kind === 'splatter') {
    const spin = Math.sin(x * 12.1 + y * 4.7) * Math.PI;
    const stretch = 0.45 + (Math.sin(x * 3.1 + y) * 0.5 + 0.5) * 0.7;
    ctx.globalAlpha = alpha * (0.72 + (Math.sin(y * 2.2) * 0.5 + 0.5) * 0.28);
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(spin);
    ctx.scale(1, stretch);
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, Math.PI * 2);
    ctx.fill();
    if (r > 3.2) {
      ctx.globalAlpha = alpha * 0.8;
      ctx.beginPath();
      ctx.ellipse(r * 0.85, 0, r * 0.95, r * 0.22, 0, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
    resetPaint(ctx);
    return;
  }
  if (typeof color === 'string' && kind === 'mist') {
    const grad = ctx.createRadialGradient(x, y, 0, x, y, r);
    grad.addColorStop(0, color);
    grad.addColorStop(0.4, color);
    grad.addColorStop(1, fade(color));
    ctx.globalAlpha = alpha;
    ctx.fillStyle = grad;
  } else {
    ctx.globalAlpha = alpha * (kind === 'fleck' ? 0.85 : 0.55);
  }
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
  resetPaint(ctx);
}
