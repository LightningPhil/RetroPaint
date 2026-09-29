import type { Applicator, BlendMode, Drive, EraserMode, ShapeKind, StatorShape, SymmetryMode, ToolId } from './types';

export const LEVEL_KEY = 'retropaint-level';

export const state = {
  level: 1 as 1 | 2 | 3 | 4,
  tool: 'draw' as ToolId,
  applicator: 'marker' as Applicator,
  ink: '#E53935',
  neonTint: '#E53935',
  sparkleTint: '#FFE566',
  rainbowMode: 'distance' as 'distance' | 'time',
  brushWidth: 22,
  opacity: 1,
  shape: 'line' as ShapeKind,
  symmetry: 'off' as SymmetryMode,
  eraserMode: 'scrub' as EraserMode,
  stampId: '🤖',
  stampScale: 1,
  stampRotation: 0,
  stampFlipH: false,
  stampFlipV: false,
  conveyor: ['#E53935', '#FFD166'] as string[],
  beltSpeed: 3,
  beltMode: 'ooze' as BlendMode,
  liveArmed: false,
  gradientDrag: false,
  gradientFrom: '#118AB2',
  gradientTo: '#FFD166',
  gradientPreset: null as string | null,
  spiro: {
    cx: 480,
    cy: 320,
    R: 200,
    shape: 'circle' as StatorShape,
    gearId: null as string | null,
    childId: null as string | null,
    hole: 2,
    childHole: 1,
    theta: 0,
    drive: 'manual' as Drive,
    nest: false,
  },
  poly: [] as { x: number; y: number }[],
  switchOn: false,
  busy: false,
};

export function currentWidth(): number {
  return state.level === 1 ? 34 : state.brushWidth;
}

export function currentAlpha(): number {
  return state.level >= 4 ? state.opacity : 1;
}

export function loadLevel(): void {
  try {
    const raw = localStorage.getItem(LEVEL_KEY);
    const n = raw ? Number(raw) : 1;
    if (n >= 1 && n <= 4) state.level = n as 1 | 2 | 3 | 4;
  } catch {
    state.level = 1;
  }
}

export function saveLevel(): void {
  try {
    localStorage.setItem(LEVEL_KEY, String(state.level));
  } catch {
    /* private mode */
  }
}
