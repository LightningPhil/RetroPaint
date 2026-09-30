export interface Rgb {
  r: number;
  g: number;
  b: number;
}

export function hexToRgb(hex: string): Rgb | null {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex.trim());
  if (!m) return null;
  return { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) };
}

export function rgbToHex(r: number, g: number, b: number): string {
  const h = (n: number) => Math.max(0, Math.min(255, Math.round(n))).toString(16).padStart(2, '0');
  return `#${h(r)}${h(g)}${h(b)}`;
}

export function mixHex(a: string, b: string, t: number): string {
  const ca = hexToRgb(a);
  const cb = hexToRgb(b);
  if (!ca || !cb) return a;
  return rgbToHex(ca.r + (cb.r - ca.r) * t, ca.g + (cb.g - ca.g) * t, ca.b + (cb.b - ca.b) * t);
}

export function darkenHex(hex: string, amount: number): string {
  const c = hexToRgb(hex);
  if (!c) return hex;
  const f = 1 - amount;
  return rgbToHex(c.r * f, c.g * f, c.b * f);
}

export function rainbowCss(turns: number): string {
  const hue = ((turns % 360) + 360) % 360;
  // Return real RGB pigment so watercolor transparency and colour mixing work
  // just as they do for the solid swatches (their helpers expect hex colours).
  const chroma = 0.88 * 0.98;
  const second = chroma * (1 - Math.abs((hue / 60) % 2 - 1));
  const m = 0.49 - chroma / 2;
  const [r, g, b] = hue < 60 ? [chroma, second, 0] : hue < 120 ? [second, chroma, 0] : hue < 180 ? [0, chroma, second] : hue < 240 ? [0, second, chroma] : hue < 300 ? [second, 0, chroma] : [chroma, 0, second];
  return rgbToHex((r + m) * 255, (g + m) * 255, (b + m) * 255);
}

export function isHex(value: string): boolean {
  return /^#[0-9a-f]{6}$/i.test(value);
}
