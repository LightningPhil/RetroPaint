import type { Applicator, BlendMode, Drive, EraserMode, ShapeKind, StatorShape, SymmetryMode, ToolId } from './types';

export const state = {
  workspaceMode: 'basic' as 'basic' | 'advanced',
  cad: { open: false, gesture: false, selected: [] as string[], preview: null as import('./cad-model').CadBody | null, editing: false, edgeSelection:[] as import('./cad-model').CadEdgeRef[], faceSelection:[] as import('./cad-model').CadFaceRef[], tool: 'translate' as 'translate' | 'rotate' | 'scale' | 'face' | 'rectangle' | 'circle' | 'polygon' | 'edge' | 'shellFace' | 'measure', snap: true, grid: 1, angle: 15 },
  drawingMode: 'raster' as 'raster' | 'vector',
  tool: 'draw' as ToolId,
  applicator: 'marker' as Applicator,
  brushApplicator: 'marker' as Applicator,
  sprayApplicator: 'mist' as Applicator,
  ink: '#E53935',
  secondaryInk: '#FFFFFF',
  neonTint: '#E53935',
  sparkleTint: '#FFE566',
  beltPick: '#E53935',
  brushWidth: 22,
  opacity: 1,
  shape: 'line' as ShapeKind,
  shapeFill: 'none' as 'none' | 'primary' | 'secondary',
  shapeOutline: 'brush' as 'brush' | 'solid' | 'none',
  fillTolerance: 48,
  pixelGrid: false,
  rulers: false,
  paperScale: 1,
  smoothResize: true,
  symmetry: 'off' as SymmetryMode,
  symmetryMask: false,
  symmetrySlice: 0,
  choosingSlice: false,
  eraserMode: 'scrub' as EraserMode,
  selectionMode: 'rect' as 'rect' | 'lasso' | 'wand',
  transparentSelection: false,
  stampId: '🐶',
  stampScale: 1,
  stampSpin: 'fixed' as 'fixed' | 'auto',
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
    outerTeeth: 96,
    innerTeeth: 36,
    gearId: 'red' as string | null,
    hole: 2,
    theta: 0,
    drive: 'manual' as Drive,
  },
  poly: [] as { x: number; y: number }[],
  busy: false,
  cursor: null as { x: number; y: number } | null,
};

export function currentWidth(): number {
  return state.brushWidth;
}

export function currentAlpha(): number {
  return state.opacity;
}

/** Keep the document's preferred drawing mode while Basic creates raster art. */
export function vectorDrawingEnabled(): boolean {
  return state.workspaceMode === 'advanced' && state.drawingMode === 'vector';
}

export function strokeApplicator(): Applicator {
  return ['mist', 'splatter', 'confetti'].includes(state.applicator) ? state.brushApplicator : state.applicator;
}
