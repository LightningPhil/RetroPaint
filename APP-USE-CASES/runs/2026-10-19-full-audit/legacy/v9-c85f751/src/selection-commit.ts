import { multiply, objectBounds, type RasterObject } from './object-scene';

type Point = { x: number; y: number };
const EPSILON = 1e-7;

function clipPlane(polygon: Point[], distance: (point: Point) => number): Point[] {
  const output: Point[] = [];
  for (let i = 0; i < polygon.length; i++) {
    const a = polygon[i], b = polygon[(i + 1) % polygon.length];
    const da = distance(a), db = distance(b), insideA = da >= -EPSILON, insideB = db >= -EPSILON;
    if (insideA) output.push(a);
    if (insideA !== insideB) {
      const t = da / (da - db);
      output.push({ x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t });
    }
  }
  return output;
}

export function rasterOutsidePaper(object: RasterObject, width: number, height: number): boolean {
  const bounds = objectBounds(object);
  return bounds.x < -EPSILON || bounds.y < -EPSILON || bounds.x + bounds.width > width + EPSILON || bounds.y + bounds.height > height + EPSILON;
}

/** Trim in the bitmap's own coordinates: keep its resolution, position and transform. */
export function trimRasterToPaper(object: RasterObject, width: number, height: number): RasterObject | null {
  if (!rasterOutsidePaper(object, width, height)) return object;
  const m = object.matrix;
  const rectangle=[{ x: 0, y: 0 }, { x: object.width, y: 0 }, { x: object.width, y: object.height }, { x: 0, y: object.height }],original=object.clip??rectangle;
  const planes:((point:Point)=>number)[]=[p=>m[0]*p.x+m[2]*p.y+m[4],p=>width-m[0]*p.x-m[2]*p.y-m[4],p=>m[1]*p.x+m[3]*p.y+m[5],p=>height-m[1]*p.x-m[3]*p.y-m[5]];
  let polygon=original,mask=rectangle;
  for(const plane of planes){polygon=clipPlane(polygon,plane);if(original.some(point=>plane(point)<-EPSILON))mask=clipPlane(mask,plane);}
  if (polygon.length < 3||Math.abs(polygon.reduce((sum,p,i)=>{const q=polygon[(i+1)%polygon.length];return sum+p.x*q.y-q.x*p.y;},0))<EPSILON) return null;
  const left = Math.max(0, Math.floor(Math.min(...polygon.map(p => p.x)) + EPSILON));
  const top = Math.max(0, Math.floor(Math.min(...polygon.map(p => p.y)) + EPSILON));
  const right = Math.min(object.image.width, Math.ceil(Math.max(...polygon.map(p => p.x)) - EPSILON));
  const bottom = Math.min(object.image.height, Math.ceil(Math.max(...polygon.map(p => p.y)) - EPSILON));
  if (right <= left || bottom <= top) return null;
  const image = document.createElement('canvas'); image.width = right - left; image.height = bottom - top;
  const clip = polygon.map(p => ({ x: p.x - left, y: p.y - top }));
  const ctx = image.getContext('2d')!;
  // Clip only newly cut edges. Reapplying an old antialiased edge would fade it.
  ctx.beginPath(); mask.forEach((p,i)=>i?ctx.lineTo(p.x-left,p.y-top):ctx.moveTo(p.x-left,p.y-top)); ctx.closePath(); ctx.clip();
  ctx.drawImage(object.image, -left, -top);
  return { ...object, image, clip, width: image.width, height: image.height,
    matrix: multiply(m, [1, 0, 0, 1, left, top]),
    origin: object.live ? { x: (object.origin?.x ?? 0) + left, y: (object.origin?.y ?? 0) + top } : undefined,
  };
}
