import { isHex, mixHex, rainbowCss } from './color';
import { state } from './state';
import type { BlendMode, GradientLine, LiveSpec } from './types';

export const PATTERN_IDS = ['tex-brick', 'tex-dots', 'tex-weave', 'tex-grass', 'tex-stone', 'tex-water', 'tex-static'] as const;
export type PatternId = (typeof PATTERN_IDS)[number];

export const GRADIENTS: Record<string, string[]> = {
  'grad-sunset': ['#3A0CA3', '#F72585', '#FF9E00', '#FFE066'],
  'grad-rainbow': ['#FF2D55', '#FF9F1C', '#FFD60A', '#06D6A0', '#118AB2', '#9D4EDD'],
  'grad-ocean': ['#023E8A', '#0096C7', '#90E0EF', '#CAF0F8'],
  'grad-candy': ['#FF006E', '#FB5607', '#FFBE0B', '#8338EC'],
};

const patterns = new Map<string, CanvasPattern>();
const tiles = new Map<string, HTMLCanvasElement>();

function tile(size = 64): { canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D } {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  return { canvas, ctx: canvas.getContext('2d')! };
}

function store(id: string, canvas: HTMLCanvasElement): void {
  tiles.set(id, canvas);
  const pattern = document.createElement('canvas').getContext('2d')!.createPattern(canvas, 'repeat');
  if (pattern) patterns.set(id, pattern);
}

export function initMaterials(): void {
  const brick = tile();
  brick.ctx.fillStyle = '#C4492C';
  brick.ctx.fillRect(0, 0, 64, 64);
  brick.ctx.fillStyle = '#A33B24';
  brick.ctx.fillRect(0, 0, 30, 14);
  brick.ctx.fillRect(34, 0, 30, 14);
  brick.ctx.fillRect(16, 18, 30, 14);
  brick.ctx.fillRect(50, 18, 14, 14);
  brick.ctx.fillRect(0, 18, 12, 14);
  brick.ctx.fillRect(0, 36, 30, 14);
  brick.ctx.fillRect(34, 36, 30, 14);
  brick.ctx.fillRect(16, 52, 30, 12);
  brick.ctx.strokeStyle = '#E7B8A4';
  brick.ctx.lineWidth = 2;
  brick.ctx.strokeRect(0, 0, 64, 64);
  store('tex-brick', brick.canvas);

  const dots = tile();
  dots.ctx.fillStyle = '#FFF6E8';
  dots.ctx.fillRect(0, 0, 64, 64);
  dots.ctx.fillStyle = '#EF476F';
  for (const [x, y] of [[16, 16], [48, 16], [32, 40], [8, 48], [56, 48]] as const) {
    dots.ctx.beginPath();
    dots.ctx.arc(x, y, 7, 0, Math.PI * 2);
    dots.ctx.fill();
  }
  store('tex-dots', dots.canvas);

  const weave = tile();
  weave.ctx.fillStyle = '#F3E6C8';
  weave.ctx.fillRect(0, 0, 64, 64);
  weave.ctx.strokeStyle = '#C48A4A';
  weave.ctx.lineWidth = 3;
  for (let i = 0; i < 64; i += 8) {
    weave.ctx.beginPath();
    weave.ctx.moveTo(0, i);
    weave.ctx.lineTo(64, i);
    weave.ctx.stroke();
    weave.ctx.beginPath();
    weave.ctx.moveTo(i, 0);
    weave.ctx.lineTo(i, 64);
    weave.ctx.stroke();
  }
  store('tex-weave', weave.canvas);

  const grass = tile();
  grass.ctx.fillStyle = '#2D6A4F';
  grass.ctx.fillRect(0, 0, 64, 64);
  grass.ctx.strokeStyle = '#95D5B2';
  grass.ctx.lineWidth = 2;
  for (let i = 0; i < 18; i++) {
    const x = (i * 17) % 64;
    const y = (i * 29) % 64;
    grass.ctx.beginPath();
    grass.ctx.moveTo(x, y + 10);
    grass.ctx.quadraticCurveTo(x + 4, y, x - 2, y - 8);
    grass.ctx.stroke();
  }
  store('tex-grass', grass.canvas);

  const stone = tile();
  stone.ctx.fillStyle = '#8D99AE';
  stone.ctx.fillRect(0, 0, 64, 64);
  stone.ctx.strokeStyle = '#2B2D42';
  stone.ctx.lineWidth = 3;
  stone.ctx.strokeRect(2, 2, 28, 22);
  stone.ctx.strokeRect(32, 6, 28, 18);
  stone.ctx.strokeRect(6, 28, 22, 30);
  stone.ctx.strokeRect(32, 30, 28, 26);
  stone.ctx.fillStyle = '#EDF2F4';
  stone.ctx.fillRect(10, 10, 6, 4);
  store('tex-stone', stone.canvas);

  const water = tile();
  paintWater(water.ctx, 0);
  store('tex-water', water.canvas);

  const stat = tile(48);
  paintStatic(stat.ctx, 1);
  store('tex-static', stat.canvas);
}

export function paintWater(ctx: CanvasRenderingContext2D, now: number): void {
  const shift = (now * 0.04) % 64;
  ctx.fillStyle = '#0077B6';
  ctx.fillRect(0, 0, 64, 64);
  for (let y = 0; y < 64; y += 8) {
    ctx.strokeStyle = y % 16 === 0 ? '#CAF0F8' : '#48CAE4';
    ctx.lineWidth = 3;
    ctx.beginPath();
    for (let x = 0; x <= 64; x += 4) {
      const yy = y + Math.sin((x + shift) * 0.2) * 3;
      if (x === 0) ctx.moveTo(x, yy);
      else ctx.lineTo(x, yy);
    }
    ctx.stroke();
  }
}

export function paintStatic(ctx: CanvasRenderingContext2D, frame: number): void {
  const size = 48;
  const img = ctx.createImageData(size, size);
  let seed = (frame * 9973) >>> 0;
  const rand = () => {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  for (let i = 0; i < img.data.length; i += 4) {
    const v = rand() > 0.5 ? 255 : 20;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
    img.data[i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
}

export function patternFor(id: string, now = 0): CanvasPattern | null {
  if (id === 'tex-water') {
    const canvas = tiles.get(id);
    if (!canvas) return null;
    paintWater(canvas.getContext('2d')!, now);
    return canvas.getContext('2d')!.createPattern(canvas, 'repeat');
  }
  if (id === 'tex-static') {
    const canvas = tiles.get(id);
    if (!canvas) return null;
    paintStatic(canvas.getContext('2d')!, Math.floor(now / 90));
    return canvas.getContext('2d')!.createPattern(canvas, 'repeat');
  }
  return patterns.get(id) ?? null;
}

export function thumbFor(id: string): string {
  const canvas = tiles.get(id);
  return canvas ? canvas.toDataURL() : '';
}

export function previewColor(id: string, _now = 0): string {
  if (isHex(id)) return id;
  if (id === 'neon') return state.neonTint;
  if (id === 'rainbow') return rainbowCss(0);
  if (id === 'sparkle') return state.sparkleTint;
  if (id === 'tex-brick') return '#C4492C';
  if (id === 'tex-dots') return '#EF476F';
  if (id === 'tex-weave') return '#C48A4A';
  if (id === 'tex-grass') return '#2D6A4F';
  if (id === 'tex-stone') return '#8D99AE';
  if (id === 'tex-water') return '#48CAE4';
  if (id === 'tex-static') return '#AAAAAA';
  if (id === 'live') return state.conveyor[0] ?? state.ink;
  const preset = GRADIENTS[id];
  if (preset) return preset[0];
  return state.neonTint;
}

export function stopsFor(line: GradientLine, now: number): { t: number; color: string }[] {
  if (line.preset && GRADIENTS[line.preset]) {
    const colors = GRADIENTS[line.preset];
    return colors.map((color, i) => ({ t: colors.length === 1 ? 0 : i / (colors.length - 1), color }));
  }
  return [
    { t: 0, color: sampleInk(line.from, now, 0) },
    { t: 1, color: sampleInk(line.to, now, 80) },
  ];
}

export function sampleInk(id: string, now: number, distance: number): string {
  if (id === 'live') return sampleConveyor(state.conveyor, state.beltSpeed, state.beltMode, now, distance);
  if (id === 'rainbow') return rainbowCss(distance * 0.55);
  if (id === 'neon') return state.neonTint;
  if (id === 'sparkle') return state.sparkleTint;
  return previewColor(id, now);
}

export function sampleConveyor(colors: string[], speed: number, mode: BlendMode, now: number, distance: number): string {
  if (colors.length === 0) return '#888888';
  if (colors.length === 1) return colors[0];
  const phase = now * speed * 0.0015 + distance * 0.02;
  const span = colors.length;
  const wrapped = ((phase % span) + span) % span;
  const index = Math.floor(wrapped);
  const frac = wrapped - index;
  const a = colors[index % span];
  const b = colors[(index + 1) % span];
  if (mode === 'snap') return a;
  return mixHex(a, b, frac);
}

export function animatedKind(id: string): 'sparkle' | 'texture' | 'time' | null {
  if (id === 'tex-water' || id === 'tex-static') return 'texture';
  if (id === 'live' && state.conveyor.length >= 2) return 'time';
  return null;
}

export function captureStrokeSpec(): LiveSpec | 'sparkle' | null {
  if (state.liveArmed && state.conveyor.length >= 2) {
    return {
      kind: 'conveyor',
      colors: [...state.conveyor],
      speed: state.beltSpeed,
      mode: state.beltMode,
      along: true,
      texture: null,
    };
  }
  if (state.ink === 'neon') return { kind: 'neon', colors: [state.neonTint], speed: 0, mode: 'snap', along: false, texture: null };
  if (state.ink === 'tex-water' || state.ink === 'tex-static') {
    return {
      kind: 'texture',
      colors: [],
      speed: 1,
      mode: 'snap',
      along: false,
      texture: state.ink === 'tex-water' ? 'water' : 'static',
    };
  }
  return { kind: state.ink === 'sparkle' ? 'glitter' : state.ink === 'rainbow' ? 'rainbow' : 'solid', colors: [state.ink === 'sparkle' ? state.sparkleTint : state.ink], speed: 0, mode: 'snap', along: true, texture: null };
}

export function fillSpecFor(id: string): LiveSpec | 'sparkle' | null {
  if (id === 'live' || (state.liveArmed && id === state.ink)) {
    if (state.conveyor.length >= 2) {
      return {
        kind: 'conveyor',
        colors: [...state.conveyor],
        speed: state.beltSpeed,
        mode: state.beltMode,
        along: false,
        texture: null,
      };
    }
  }
  // Glitter is rendered as a static material.
  if (id === 'tex-water' || id === 'tex-static') {
    return {
      kind: 'texture',
      colors: [],
      speed: 1,
      mode: 'snap',
      along: false,
      texture: id === 'tex-water' ? 'water' : 'static',
    };
  }
  return null;
}

export function specKey(spec: LiveSpec): string {
  return JSON.stringify(spec);
}

export function colorFromSpec(spec: LiveSpec, now: number, distance: number): string {
  if (spec.kind === 'conveyor') return sampleConveyor(spec.colors, spec.speed, spec.mode, now, spec.along ? distance : 0);
  if (spec.kind === 'rainbow-time') return rainbowCss(now * 0.12 + (spec.along ? distance * 0.4 : 0));
  if (spec.texture === 'water') return '#48CAE4';
  return '#CCCCCC';
}

export function activeInkId(): string {
  if (state.liveArmed && state.conveyor.length >= 2) return 'live';
  return state.ink;
}

export function isAnimatedMaterial(id: string): boolean {
  return animatedKind(id) !== null;
}

/** A stationary metallic pigment tile shared by swatches, strokes and fills. */
export function glitterPattern(color = state.sparkleTint): CanvasPattern {
  const id = 'glitter:' + color;
  if (!patterns.has(id)) {
    const { canvas, ctx } = tile(192);
    let seed = 74291;
    const random = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
    const image = ctx.createImageData(192, 192);
    const rgb = (hex: string) => [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
    const base = rgb(color);
    for (let y = 0; y < 192; y++) for (let x = 0; x < 192; x++) {
      const grain = random();
      const sheen = 0.5 + 0.5 * Math.sin((x + y) * Math.PI * 2 / 96);
      const light = grain > 0.955 ? 0.82 : 0.08 + sheen * 0.22 + grain * 0.12;
      const dark = grain < 0.15 ? 0.48 : 0.78;
      const i = (y * 192 + x) * 4;
      for (let c = 0; c < 3; c++) image.data[i + c] = base[c] * dark * (1 - light) + 255 * light;
      image.data[i + 3] = 255;
    }
    ctx.putImageData(image, 0, 0);
    for (let i = 0; i < 540; i++) {
      const x = Math.floor(random() * 192), y = Math.floor(random() * 192);
      ctx.fillStyle = mixHex(color, '#ffffff', 0.88);
      ctx.fillRect(x, y, 1 + Math.floor(random() * 2), 1);
      ctx.fillStyle = mixHex(color, '#151525', 0.5);
      ctx.fillRect(x, y + 1, 1, 1);
    }
    store(id, canvas);
  }
  return patterns.get(id)!;
}
export function glitterThumb(): string {
  glitterPattern();
  return tiles.get('glitter:' + state.sparkleTint)!.toDataURL();
}
