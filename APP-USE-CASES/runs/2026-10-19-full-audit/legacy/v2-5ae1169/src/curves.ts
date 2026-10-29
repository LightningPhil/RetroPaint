type Point = { x: number; y: number };

/** Chord-length tangents keep closely spaced knots from making large loops. */
export function splinePoints(points: Point[], closed = false): Point[] {
  if (points.length < 3) return points.slice();
  const result: Point[] = [points[0]];
  const n = points.length;
  const at = (i: number) => points[closed ? (i + n) % n : Math.max(0, Math.min(n - 1, i))];
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const a = at(i - 1), b = at(i), c = at(i + 1), d = at(i + 2);
    const length = Math.hypot(c.x - b.x, c.y - b.y);
    const scaleB = length / Math.max(1, Math.hypot(c.x - a.x, c.y - a.y)) * 0.7;
    const scaleC = length / Math.max(1, Math.hypot(d.x - b.x, d.y - b.y)) * 0.7;
    const steps = Math.max(2, Math.ceil(length / 2));
    for (let j = 1; j <= steps; j++) {
      const t = j / steps, t2 = t * t, t3 = t2 * t;
      const h0 = 2 * t3 - 3 * t2 + 1, h1 = t3 - 2 * t2 + t;
      const h2 = -2 * t3 + 3 * t2, h3 = t3 - t2;
      result.push({
        x: h0 * b.x + h1 * (c.x - a.x) * scaleB + h2 * c.x + h3 * (d.x - b.x) * scaleC,
        y: h0 * b.y + h1 * (c.y - a.y) * scaleB + h2 * c.y + h3 * (d.y - b.y) * scaleC,
      });
    }
  }
  return result;
}
