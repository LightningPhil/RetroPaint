export interface Pt {
  x: number;
  y: number;
  w: number;
}

export type ToolId =
  | 'draw'
  | 'spray'
  | 'shapes'
  | 'bucket'
  | 'wand'
  | 'sponge'
  | 'scissors'
  | 'eraser'
  | 'stamp'
  | 'spiro';

export type Applicator =
  | 'marker'
  | 'biro'
  | 'callig'
  | 'gouache'
  | 'watercolor'
  | 'mist'
  | 'splatter';

export type SymmetryMode = 'off' | 'v' | 'h' | '4' | '8';
export type ShapeKind = 'line' | 'rect' | 'circle' | 'poly';
export type EraserMode = 'scrub' | 'blackhole' | 'pixelate' | 'invert' | 'emboss';
export type StatorShape = 'circle' | 'oval' | 'square' | 'cross';
export type Drive = 'manual' | 'auto';
export type BlendMode = 'snap' | 'ooze';

export interface LiveSpec {
  kind: 'conveyor' | 'rainbow-time' | 'texture';
  colors: string[];
  speed: number;
  mode: BlendMode;
  along: boolean;
  texture: 'water' | 'static' | null;
}

export interface Spark {
  x: number;
  y: number;
  phase: number;
  size: number;
  color: string;
}

export interface GradientLine {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  from: string;
  to: string;
  preset: string | null;
}

export interface GearDef {
  id: string;
  color: string;
  teeth: number;
  holes: number;
}
