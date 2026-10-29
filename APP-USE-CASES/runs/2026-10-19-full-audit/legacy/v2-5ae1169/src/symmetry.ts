import { W, H } from './canvas';
import { state } from './state';
import type { SymmetryMode } from './types';

type Transform = { a: number; b: number; c: number; d: number };
const transforms = new Map<SymmetryMode, Transform[]>();
/** Orthogonal transforms keep each lane continuous even across a mirror seam. */
export function symmetryTransforms(mode: SymmetryMode = state.symmetry): { a: number; b: number; c: number; d: number }[] {
  const cached = transforms.get(mode);
  if (cached) return cached;
  const result = makeTransforms(mode);
  transforms.set(mode, result); return result;
}
function makeTransforms(mode: SymmetryMode): Transform[] {
  if (mode === 'off') return [{a:1,b:0,c:0,d:1}];
  if (mode === 'v') return [{a:1,b:0,c:0,d:1},{a:-1,b:0,c:0,d:1}];
  if (mode === 'h') return [{a:1,b:0,c:0,d:1},{a:1,b:0,c:0,d:-1}];
  const count = Number(mode), sector = Math.PI * 2 / count;
  return Array.from({length:count},(_,i) => {
    const reflected = i % 2 === 1;
    const angle = (Math.floor(i / 2) + (reflected ? 1 : 0)) * sector * 2;
    const cos = Math.cos(angle), sin = Math.sin(angle);
    return reflected ? {a:cos,b:sin,c:sin,d:-cos} : {a:cos,b:-sin,c:sin,d:cos};
  });
}

export function mirrorPoints(x: number, y: number): {x:number;y:number}[] {
  const px=x-W/2, py=y-H/2;
  return symmetryTransforms().map(t=>({x:W/2+t.a*px+t.b*py,y:H/2+t.c*px+t.d*py}));
}

/** A reflected smudge must also reflect its push direction. */
export function mirrorMotion(x: number, y: number, dx: number, dy: number): {x:number;y:number;dx:number;dy:number}[] {
  const px=x-W/2, py=y-H/2;
  return symmetryTransforms().map(t=>({x:W/2+t.a*px+t.b*py,y:H/2+t.c*px+t.d*py,dx:t.a*dx+t.b*dy,dy:t.c*dx+t.d*dy}));
}
