export type Preview =
  | null
  | { kind: 'shape'; shape: 'line' | 'rect' | 'circle'; x0: number; y0: number; x1: number; y1: number }
  | { kind: 'lasso'; points: { x: number; y: number }[] }
  | { kind: 'rubber'; x0: number; y0: number; x1: number; y1: number };

let preview: Preview = null;

export function setPreview(next: Preview): void {
  preview = next;
}

export function getPreview(): Preview {
  return preview;
}
