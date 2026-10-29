import type { ShapeKind } from './types';
type Point = { x: number; y: number };
const interpolate = (points: Point[], close = true): Point[] => {
  const result = [points[0]];
  for (let i = 1; i < points.length + Number(close); i++) {
    const a = points[i - 1], b = points[i % points.length], n = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / 3));
    for (let j = 1; j <= n; j++) result.push({ x: a.x + (b.x - a.x) * j / n, y: a.y + (b.y - a.y) * j / n });
  }
  return result;
};
export function shapePoints(kind: ShapeKind, x0: number, y0: number, x1: number, y1: number): Point[] {
  const x = Math.min(x0, x1), y = Math.min(y0, y1), w = Math.abs(x1 - x0), h = Math.abs(y1 - y0);
  const scaled = (points: number[][]) => interpolate(points.map(([a, b]) => ({ x: x + a * w, y: y + b * h })));
  const cx = x + w / 2, cy = y + h / 2;
  const round = (rx: number, ry: number, centerX = cx, centerY = cy, cloud = false) => {
    const steps = Math.max(32, Math.ceil(Math.max(rx, ry) * Math.PI * 2 / 3));
    return Array.from({ length: steps + 1 }, (_, i) => {
      const a = i / steps * Math.PI * 2, r = cloud ? 1 + 0.1 * Math.cos(a * 10) : 1;
      return { x: centerX + Math.cos(a) * rx * r, y: centerY + Math.sin(a) * ry * r };
    });
  };
  if (kind === 'line') return interpolate([{ x: x0, y: y0 }, { x: x1, y: y1 }], false);
  if (kind === 'circle') { const r = Math.hypot(x1 - x0, y1 - y0); return round(r, r, x0, y0); }
  if (kind === 'ellipse') return round(w / 2, h / 2);
  if (kind === 'cloud') return round(w / 2.2, h / 2.2, cx, cy, true);
  if (kind === 'rect') return scaled([[0, 0], [1, 0], [1, 1], [0, 1]]);
  if (kind === 'roundRect') {
    const r = Math.min(w, h) * 0.2, result: Point[] = [];
    for (const [corner, xx, yy] of [[0, x + w - r, y + r], [1, x + w - r, y + h - r], [2, x + r, y + h - r], [3, x + r, y + r]]) {
      for (let i = 0; i <= 12; i++) { const a = (-0.5 + corner / 2 + i / 24) * Math.PI; result.push({ x: xx + Math.cos(a) * r, y: yy + Math.sin(a) * r }); }
    }
    return interpolate(result);
  }
  if (kind === 'triangle') return scaled([[0.5, 0], [1, 1], [0, 1]]);
  if (kind === 'rightTriangle') return scaled([[0, 0], [1, 1], [0, 1]]);
  if (kind === 'diamond') return scaled([[0.5, 0], [1, 0.5], [0.5, 1], [0, 0.5]]);
  if (kind === 'pentagon' || kind === 'hexagon' || kind.startsWith('star')) {
    const star = kind.startsWith('star'), count = star ? Number(kind.slice(4)) * 2 : kind === 'pentagon' ? 5 : 6;
    return interpolate(Array.from({ length: count }, (_, i) => {
      const a = i / count * Math.PI * 2 - Math.PI / 2, r = star && i % 2 ? 0.42 : 1;
      return { x: cx + Math.cos(a) * w / 2 * r, y: cy + Math.sin(a) * h / 2 * r };
    }));
  }
  if (kind === 'heart') return interpolate(Array.from({ length: 100 }, (_, i) => {
    const a = i / 100 * Math.PI * 2, xx = 16 * Math.sin(a) ** 3, yy = 13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a);
    return { x: cx + xx / 32 * w, y: y + (12 - yy) / 29 * h };
  }));
  if (kind === 'lightning') return scaled([[0.55, 0], [0.1, 0.55], [0.45, 0.55], [0.35, 1], [0.95, 0.35], [0.6, 0.35]]);
  if (kind.startsWith('arrow')) {
    let points = [[0, 0.3], [0.6, 0.3], [0.6, 0], [1, 0.5], [0.6, 1], [0.6, 0.7], [0, 0.7]];
    if (kind === 'arrowLeft') points = points.map(([a, b]) => [1 - a, b]);
    if (kind === 'arrowUp') points = points.map(([a, b]) => [b, 1 - a]);
    if (kind === 'arrowDown') points = points.map(([a, b]) => [b, a]);
    return scaled(points);
  }
  if (kind === 'ovalCallout') {
    const pts = round(w / 2, h * 0.4, cx, y + h * 0.4);
    pts.splice(Math.floor(pts.length * 0.31), 0, { x: x + w * 0.15, y: y + h }); return interpolate(pts);
  }
  return scaled([[0, 0], [1, 0], [1, 0.75], [0.45, 0.75], [0.15, 1], [0.25, 0.75], [0, 0.75]]);
}
