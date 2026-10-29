import { H, W } from './canvas';
import { activeLayerId, captureLayers, restoreLayers, type LayerSnapshot } from './layers';
import { renderLiveSnapshot, type LiveSnapshot } from './live';
import { download } from './export';
import { decodeImage, dimensions, editable, message, settle } from './editor';
import { pushHistory } from './history';
import { artwork } from './artwork';
import type { Applicator, LiveSpec } from './types';
import { documentCrop, setDocumentCrop } from './document-frame';
import { readPhotoCrop, readPhotoRecipe } from './photo-recipe';

const canvasFromImage = (image: ImageData) => { const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height; canvas.getContext('2d')!.putImageData(image, 0, 0); return canvas; };
export function projectData(): string {
  const saved = captureLayers().map(layer => {
    const canvas = canvasFromImage(layer.image), rainbow = layer.live.strokes.filter(stroke => stroke.rainbow);
    if (rainbow.length) renderLiveSnapshot(canvas.getContext('2d')!, { strokes: rainbow, fills: [], sparkles: [] }, performance.now());
    return { id: layer.id, name: layer.name, visible: layer.visible, opacity: layer.opacity, paper: layer.paper, photo:layer.photo,
      image: canvas.toDataURL(), live: {
        strokes: layer.live.strokes.filter(stroke => !stroke.rainbow),
        fills: layer.live.fills.map(fill => ({ ...fill, mask: fill.mask.toDataURL() })), sparkles: layer.live.sparkles,
      },
    };
  });
  return JSON.stringify({ format: 'RetroPaint', version: 2, width: W, height: H, crop:documentCrop(), active: activeLayerId, layers: saved });
}
export function saveProjectFile(name = 'retropaint'): void {
  download(new Blob([projectData()], { type: 'application/json' }), `${name.replace(/[<>:"/\\|?*]/g, '-') || 'retropaint'}.retropaint`);
  message('Project saved with layers and live ink.');
}
type RecordValue = Record<string, unknown>;
function record(value: unknown): RecordValue { if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid project data.'); return value as RecordValue; }
function array(value: unknown, limit: number): unknown[] { if (!Array.isArray(value) || value.length > limit) throw new Error('Project contains too much or invalid data.'); return value; }
function number(value: unknown, min = -1e7, max = 1e7): number { if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max) throw new Error('Invalid project numbers.'); return value; }
function point(value: unknown): { x: number; y: number } { const p = record(value); return { x: number(p.x), y: number(p.y) }; }
function spec(value: unknown): LiveSpec {
  const s = record(value), kind = String(s.kind);
  if (!['conveyor', 'rainbow-time', 'texture', 'neon', 'solid', 'rainbow', 'glitter'].includes(kind) || !['snap', 'ooze'].includes(String(s.mode))) throw new Error('Unknown project ink.');
  const colors = array(s.colors, 32).map(color => { if (typeof color !== 'string' || color.length > 80) throw new Error('Invalid ink colour.'); return color; });
  return { kind: kind as LiveSpec['kind'], colors, speed: number(s.speed, -100, 100), mode: s.mode as LiveSpec['mode'], along: Boolean(s.along), texture: s.texture === 'water' || s.texture === 'static' ? s.texture : null };
}
const spark = (value: unknown) => { const p = record(value); return { ...point(p), phase: number(p.phase), size: number(p.size, 0, 10000), color: typeof p.color === 'string' ? p.color.slice(0, 80) : '#ffffff' }; };
async function image(value: unknown, width: number, height: number): Promise<HTMLCanvasElement> {
  if (typeof value !== 'string' || !value.startsWith('data:image/png;base64,') || value.length > 100_000_000) throw new Error('Invalid project image.');
  const blob = await (await fetch(value)).blob(), canvas = await decodeImage(blob);
  if (canvas.width !== width || canvas.height !== height) throw new Error('Project layer dimensions do not match.'); return canvas;
}
async function live(value: unknown, width: number, height: number): Promise<LiveSnapshot> {
  const saved = record(value);
  const applicators = ['marker', 'biro', 'callig', 'gouache', 'watercolor', 'mist', 'splatter', 'confetti', 'pencil', 'brush', 'oil', 'crayon', 'natural'];
  const strokes = array(saved.strokes, 10000).map(value => {
    const stroke = record(value); if (!applicators.includes(String(stroke.applicator))) throw new Error('Unknown project brush.');
    return { points: array(stroke.points, 100000).map(value => { const p = record(value); return { ...point(p), w: number(p.w, 0, 10000) }; }),
      opacity: number(stroke.opacity, 0, 1), applicator: stroke.applicator as Applicator, spec: spec(stroke.spec), generation: number(stroke.generation, 0), lane: number(stroke.lane, 0, 24), clip: stroke.clip ? array(stroke.clip, 1000).map(point) : null,
    };
  });
  const fills = await Promise.all(array(saved.fills, 2000).map(async value => {
    const fill = record(value), g = fill.gradient ? record(fill.gradient) : null;
    const gradient = g ? { x1: number(g.x1), y1: number(g.y1), x2: number(g.x2), y2: number(g.y2), from: String(g.from).slice(0, 80), to: String(g.to).slice(0, 80), preset: g.preset ? String(g.preset).slice(0, 80) : null } : null;
    return { mask: await image(fill.mask, width, height), opacity: number(fill.opacity, 0, 1), spec: spec(fill.spec), gradient, sparkles: array(fill.sparkles, 10000).map(spark) };
  }));
  return { strokes, fills, sparkles: array(saved.sparkles, 20000).map(spark) };
}
export async function loadProjectData(source: string): Promise<void> {
  const project = record(JSON.parse(source));
  if (project.format !== 'RetroPaint' || ![1,2].includes(project.version as number)) throw new Error('Choose a RetroPaint project file.');
  const width = number(project.width, 1, 4096), height = number(project.height, 1, 4096); dimensions(width, height);
  if (!Number.isInteger(width) || !Number.isInteger(height)) throw new Error('Invalid project dimensions.');
  const data = array(project.layers, 16); if (!data.length) throw new Error('This project has no layers.');
  if (width * height * data.length > 64_000_000) throw new Error('This project has too many pixels across its layers.');
  const crop=project.crop===undefined?{x:0,y:0,width:1,height:1}:readPhotoCrop(project.crop);
  const snapshots: LayerSnapshot[] = await Promise.all(data.map(async value => {
    const layer = record(value), canvas = await image(layer.image, width, height);
    return { id: number(layer.id, 1), name: String(layer.name ?? 'Layer').slice(0, 60), visible: Boolean(layer.visible), opacity: number(layer.opacity, 0, 1), paper: typeof layer.paper === 'string' && /^#[\da-f]{6}$/i.test(layer.paper) ? layer.paper : null,
      image: canvas.getContext('2d')!.getImageData(0, 0, width, height), live: await live(layer.live, width, height),photo:readPhotoRecipe(layer.photo) };
  }));
  if (new Set(snapshots.map(layer => layer.id)).size !== snapshots.length) throw new Error('Project layer IDs must be unique.');
  if (!editable()) return;
  settle(); pushHistory(); restoreLayers(snapshots, number(project.active, 1), width, height); setDocumentCrop(crop);artwork.markWork(); message('Project opened with layers, editable photo adjustments and live ink.');
}
export async function openProjectFile(file: File): Promise<void> {
  if (file.size > 100_000_000) throw new Error('This project is too large to open.');
  await loadProjectData(await file.text());
}
