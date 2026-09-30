import { W, H } from './canvas';
import { state } from './state';
import { symmetryTransforms } from './symmetry';
import type { SymmetryMode } from './types';

export interface Point { x: number; y: number; }
export interface Sector { mode: SymmetryMode; slice: number; }
export function activeSector(): Sector | null {
  return state.symmetryMask && state.symmetry !== 'off' ? { mode: state.symmetry, slice: state.symmetrySlice } : null;
}
export function sliceCount(mode: SymmetryMode = state.symmetry): number {
  return mode === 'off' ? 1 : mode === 'h' || mode === 'v' ? 2 : Number(mode);
}
export function sliceAt(x: number, y: number, mode = state.symmetry): number {
  const offset = mode === 'v' ? -Math.PI / 2 : 0;
  const angle = ((Math.atan2(y - H / 2, x - W / 2) - offset) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2);
  return Math.min(sliceCount(mode) - 1, Math.floor(angle / (Math.PI * 2 / sliceCount(mode))));
}
const planeCache = new Map<string, Point[]>();
const polygonCache = new Map<string, Point[]>();
const laneCache = new Map<string, Point[]>();
const sectorKey = (sector: Sector) => sector.mode + ':' + sector.slice;
function planes(sector: Sector): Point[] {
  const key = sectorKey(sector), cached = planeCache.get(key);
  if (cached) return cached;
  const start = (sector.mode === 'v' ? -Math.PI / 2 : 0) + sector.slice * Math.PI * 2 / sliceCount(sector.mode);
  const end = start + Math.PI * 2 / sliceCount(sector.mode);
  const result = [{ x: -Math.sin(start), y: Math.cos(start) }, { x: Math.sin(end), y: -Math.cos(end) }];
  planeCache.set(key, result); return result;
}
export function insideSector(x: number, y: number, sector = activeSector()): boolean {
  return !sector || planes(sector).every(n => (x - W / 2) * n.x + (y - H / 2) * n.y >= -1e-6);
}
/** Clip a gesture to the convex working wedge; never project a slip into another wedge. */
export function clipSegment(a: Point, b: Point, sector = activeSector(), inset = 0): [Point, Point] | null {
  if (!sector) return [a, b];
  let lo = 0, hi = 1;
  for (const n of planes(sector)) {
    const start = (a.x - W / 2) * n.x + (a.y - H / 2) * n.y - inset * (Math.abs(n.x) + Math.abs(n.y));
    const delta = (b.x - a.x) * n.x + (b.y - a.y) * n.y;
    if (Math.abs(delta) < 1e-10) { if (start < -1e-6) return null; continue; }
    const t = -start / delta;
    if (delta > 0) lo = Math.max(lo, t); else hi = Math.min(hi, t);
    if (lo > hi + 1e-9) return null;
  }
  const at = (t: number) => ({ x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t });
  return [at(Math.max(0, lo)), at(Math.min(1, hi))];
}
/** Intersect a rectangle or lasso with the working slice. */
export function clipToSector(points: Point[], sector: Sector | null): Point[] {
  if (!sector) return points;
  for (const n of planes(sector)) {
    const output: Point[] = [];
    const distance = (p: Point) => (p.x-W/2)*n.x+(p.y-H/2)*n.y;
    for (let i=0;i<points.length;i++) {
      const a=points[i], b=points[(i+1)%points.length], da=distance(a), db=distance(b);
      if (da>=-1e-6) output.push(a);
      if ((da<0)!==(db<0)) { const t=da/(da-db); output.push({x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t}); }
    }
    points=output;
  }
  return points;
}
export function sectorPolygon(sector: Sector): Point[] {
  const key = sectorKey(sector), cached = polygonCache.get(key);
  if (cached) return cached;
  const result = clipToSector([{x:0,y:0},{x:W,y:0},{x:W,y:H},{x:0,y:H}], sector);
  polygonCache.set(key, result); return result;
}
export function lanePolygon(lane: number, sector = activeSector()): Point[] | null {
  if (!sector) return null;
  const key = sectorKey(sector) + ':' + lane, cached = laneCache.get(key);
  if (cached) return cached;
  const t = symmetryTransforms(sector.mode)[lane];
  const result = sectorPolygon(sector).map(p=>({x:W/2+t.a*(p.x-W/2)+t.b*(p.y-H/2),y:H/2+t.c*(p.x-W/2)+t.d*(p.y-H/2)}));
  laneCache.set(key, result); return result;
}
export function polygonPath(ctx: CanvasRenderingContext2D, polygon: Point[]): void {
  if (!polygon.length) return;
  ctx.moveTo(polygon[0].x,polygon[0].y);
  for (const p of polygon.slice(1)) ctx.lineTo(p.x,p.y);
  ctx.closePath();
}
export function clipPolygon(ctx: CanvasRenderingContext2D, polygon: Point[] | null): void {
  if (!polygon) return;
  ctx.beginPath(); polygonPath(ctx,polygon); ctx.clip();
}
export function clipLane(ctx: CanvasRenderingContext2D, lane: number): void { clipPolygon(ctx,lanePolygon(lane)); }

/** Apply a local pixel effect to the source slice and reflect its footprint. */
export function paintSectorPatch(ctx: CanvasRenderingContext2D, patch: ImageData, left: number, top: number, x: number, y: number, radius: number): void {
  const sector=activeSector();
  if (!sector) { ctx.putImageData(patch,left,top); return; }
  const tile=document.createElement('canvas'); tile.width=patch.width; tile.height=patch.height;
  tile.getContext('2d')!.putImageData(patch,0,0);
  for (const t of symmetryTransforms(sector.mode)) {
    ctx.save(); ctx.translate(W/2,H/2); ctx.transform(t.a,t.c,t.b,t.d,0,0); ctx.translate(-W/2,-H/2);
    clipPolygon(ctx,sectorPolygon(sector));
    ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.clip();
    ctx.drawImage(tile,left,top);ctx.restore();
  }
}
