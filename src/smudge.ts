/** Backward advection: every destination samples the same immutable source.
 * A smooth radial displacement and bilinear sampling avoid square seams and holes. */
export function advect(source: Uint8ClampedArray, width: number, height: number,
  cx: number, cy: number, dx: number, dy: number, radius: number, strength: number): Uint8ClampedArray {
  const out = new Uint8ClampedArray(source);
  for (let y = Math.max(0, Math.floor(cy - radius)); y < Math.min(height, Math.ceil(cy + radius)); y++) {
    for (let x = Math.max(0, Math.floor(cx - radius)); x < Math.min(width, Math.ceil(cx + radius)); x++) {
      const d = Math.hypot(x - cx, y - cy) / radius;
      if (d >= 1) continue;
      const t = 1 - d * d;
      const falloff = t * t * (3 - 2 * t) * strength;
      const sx = Math.max(0, Math.min(width - 1, x - dx * falloff));
      const sy = Math.max(0, Math.min(height - 1, y - dy * falloff));
      const x0 = Math.floor(sx), y0 = Math.floor(sy);
      const x1 = Math.min(width - 1, x0 + 1), y1 = Math.min(height - 1, y0 + 1);
      const fx = sx - x0, fy = sy - y0;
      const dest = (y * width + x) * 4;
      for (let c = 0; c < 4; c++) {
        const top = source[(y0 * width + x0) * 4 + c] * (1 - fx) + source[(y0 * width + x1) * 4 + c] * fx;
        const bottom = source[(y1 * width + x0) * 4 + c] * (1 - fx) + source[(y1 * width + x1) * 4 + c] * fx;
        out[dest + c] = top * (1 - fy) + bottom * fy;
      }
    }
  }
  return out;
}

/** Distance-based elastic follower: sub-pixel mouse noise never gets stamped. */
export class SmudgePath {
  private fx: number;
  private fy: number;
  private px: number;
  private py: number;
  constructor(x: number, y: number, private radius: number,
    private dab: (x: number, y: number, dx: number, dy: number) => void) {
    this.fx = this.px = x;
    this.fy = this.py = y;
  }
  move(x: number, y: number, finish = false): void {
    const distance = Math.hypot(x - this.fx, y - this.fy);
    const follow = finish ? 1 : 1 - Math.exp(-distance / Math.max(3, this.radius * 0.18));
    this.fx += (x - this.fx) * follow;
    this.fy += (y - this.fy) * follow;
    const dx = this.fx - this.px, dy = this.fy - this.py;
    const length = Math.hypot(dx, dy);
    const spacing = Math.max(1.5, this.radius * 0.1);
    if (length < (finish ? 0.25 : spacing)) return;
    const steps = finish ? Math.ceil(length / spacing) : Math.floor(length / spacing);
    const step = finish ? length / steps : spacing;
    for (let i = 0; i < steps; i++) {
      const vx = dx / length * step, vy = dy / length * step;
      this.px += vx; this.py += vy;
      this.dab(this.px, this.py, vx, vy);
    }
  }
}
