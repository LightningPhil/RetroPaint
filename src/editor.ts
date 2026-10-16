import { artwork } from './artwork';
import { emit } from './bus';
import { baseCtx, H, view, W } from './canvas';
import { floodMask, lockPending } from './fill';
import { pushHistory, redo } from './history';
import { activeLayer, layerChanged, layers, resetLayers, transformLayers, type Matrix } from './layers';
import { bakeLive } from './live';
import { cancelSelection, commitSelection, editSelectionPixels, flipSelection, hasClipboard, hasSelection, pasteImage, pasteSelection, resizeSelection, rotateSelection, selectionBounds, transformSelection } from './selection';
import { motorOn } from './spiro';
import { isBusy } from './effects';
import { state } from './state';
import { hasText, placeText } from './text-tool';
import { exportImage, printImage } from './export';
import { decodeTiff } from './image-codecs';
import { openProjectFile, saveProjectFile } from './project';
import { finishPath } from './input';
import { initLayersUi, refreshLayersUi } from './layer-ui';
import { photoEditing } from './photo-preview';
import { initPhotoUi } from './photo-ui';

let statusTimer = 0, inserting = false;
export function message(text: string): void {
  const status = document.getElementById('editorStatus'); if (!status) return;
  status.textContent = text; status.classList.add('visible'); clearTimeout(statusTimer);
  statusTimer = window.setTimeout(() => status.classList.remove('visible'), 5000);
}
export function settle(): void {
  emit('settle-input');
  if (state.tool === 'text' && hasText()) placeText();
  commitSelection(); lockPending(); if (state.poly.length > 1) finishPath(); else state.poly = [];
}
export function editable(): boolean {
  if (photoEditing) { message('Apply or cancel your Photo lab preview first.'); return false; }
  if (state.busy || isBusy() || motorOn()) { message('Let the current effect finish first.'); return false; }
  return true;
}
export function dimensions(width: number, height: number, layerCount = 1): void {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1 || width > 4096 || height > 4096) throw new Error('Choose a whole-pixel width and height between 1 and 4096.');
  if (width * height * layerCount > 64_000_000) throw new Error('This picture has too many pixels across its layers. Use smaller dimensions or merge some layers.');
}
export function resizePicture(width: number, height: number, paperOnly = false, smooth = true): void {
  dimensions(width, height, layers.length); settle(); pushHistory();
  transformLayers(width, height, paperOnly ? [1, 0, 0, 1, 0, 0] : [width / W, 0, 0, height / H, 0, 0], paperOnly, smooth);
}
export function cropPicture(): void {
  const bounds = selectionBounds(); if (!bounds) throw new Error('Select the part of the picture to keep first.');
  const left = Math.max(0, Math.floor(bounds.x)), top = Math.max(0, Math.floor(bounds.y));
  const width = Math.min(W, Math.ceil(bounds.x + bounds.width)) - left, height = Math.min(H, Math.ceil(bounds.y + bounds.height)) - top;
  dimensions(width, height, layers.length); settle(); pushHistory(); transformLayers(width, height, [1, 0, 0, 1, -left, -top]);
}
export function rotatePicture(degrees: number): void {
  if (!Number.isFinite(degrees)) throw new Error('Enter an angle.');
  const r = degrees * Math.PI / 180, c = Math.cos(r), s = Math.sin(r);
  const width = Math.max(1, Math.ceil(Math.abs(W * c) + Math.abs(H * s) - 1e-8)), height = Math.max(1, Math.ceil(Math.abs(W * s) + Math.abs(H * c) - 1e-8));
  dimensions(width, height, layers.length); settle(); pushHistory(); transformLayers(width, height, [c, s, -s, c, width / 2 - c * W / 2 + s * H / 2, height / 2 - s * W / 2 - c * H / 2]);
}
export function flipPicture(horizontal: boolean): void {
  settle(); pushHistory(); transformLayers(W, H, horizontal ? [-1, 0, 0, 1, W, 0] : [1, 0, 0, -1, 0, H]);
}
function skewTransform(width: number, height: number, x: number, y: number): { width: number; height: number; matrix: Matrix } {
  if (![x, y].every(n => Number.isFinite(n) && Math.abs(n) <= 80)) throw new Error('Skew angles must be between −80° and 80°.');
  const a = Math.tan(y * Math.PI / 180), b = Math.tan(x * Math.PI / 180);
  if (Math.abs(1 - a * b) < 0.01) throw new Error('Those skew angles would flatten the image. Choose smaller angles.');
  return { width: Math.ceil(width + Math.abs(b * height)), height: Math.ceil(height + Math.abs(a * width)), matrix: [1, a, b, 1, b < 0 ? -b * height : 0, a < 0 ? -a * width : 0] };
}
export function skewPicture(x: number, y: number, selection = false): void {
  const bounds = selection ? selectionBounds() : null;
  if (selection && !bounds) throw new Error('Make a selection first.');
  const transformed = skewTransform(bounds?.width ?? W, bounds?.height ?? H, x, y); dimensions(transformed.width, transformed.height, selection ? 1 : layers.length);
  if (selection) transformSelection(transformed.matrix, transformed.width, transformed.height);
  else { settle(); pushHistory(); transformLayers(transformed.width, transformed.height, transformed.matrix); }
}
export function removeEdgeBackground(): void {
  settle(); pushHistory(); bakeLive(baseCtx, performance.now());
  const image = baseCtx.getImageData(0, 0, W, H), mask = floodMask(image.data, 0, 0);
  if (mask) for (let p = 0; p < mask.length; p++) if (mask[p]) image.data[p * 4 + 3] = 0;
  baseCtx.putImageData(image, 0, 0); activeLayer().paper = null; layerChanged();
}
export async function decodeImage(file: Blob): Promise<HTMLCanvasElement> {
  if (/tiff/.test(file.type) || (file instanceof File && /\.tiff?$/i.test(file.name))) return decodeTiff(await file.arrayBuffer());
  const url = URL.createObjectURL(file);
  try {
    const image = new Image(); image.src = url;
    try { await image.decode(); } catch { throw new Error('This image could not be opened. Try PNG, JPEG, GIF, BMP, WebP, or an uncompressed TIFF.'); }
    dimensions(image.naturalWidth, image.naturalHeight);
    const canvas = document.createElement('canvas'); canvas.width = image.naturalWidth; canvas.height = image.naturalHeight; canvas.getContext('2d')!.drawImage(image, 0, 0); return canvas;
  } finally { URL.revokeObjectURL(url); }
}
export async function importImage(file: Blob, insert = false): Promise<void> {
  if (!editable()) return;
  const image = await decodeImage(file);
  if (!editable()) return;
  settle();
  if (insert) { pasteImage(image); state.tool = 'scissors'; emit('tool-request'); }
  else {
    pushHistory(); resetLayers(image.width, image.height, null); baseCtx.drawImage(image, 0, 0); artwork.markWork();
    if (file instanceof File) (document.getElementById('fileName') as HTMLInputElement).value = file.name.replace(/\.[^.]+$/, '');
  }
  emit('close-options'); message(insert ? 'Image inserted. Drag it, resize it, then Place.' : 'Image opened. Undo brings back the previous picture.');
  if(!insert)emit('image-opened');
}
export async function pasteExternal(): Promise<void> {
  if (!editable()) return;
  try {
    if (navigator.clipboard?.read) {
      const items = await navigator.clipboard.read();
      for (const item of items) {
        const type = item.types.find(type => type.startsWith('image/'));
        if (type) { await importImage(await item.getType(type), true); return; }
      }
    }
  } catch { /* Clipboard permission varies across browsers; the session clipboard is retained. */ }
  if (hasClipboard()) { pasteSelection(); state.tool = 'scissors'; emit('tool-request'); }
  else message('Press Ctrl/Cmd+V to paste an image, or use Insert image.');
}
export function requestOpen(insert = false): void { inserting = insert; (document.getElementById('imageInput') as HTMLInputElement).click(); }
const field = <T extends HTMLElement = HTMLInputElement>(id: string) => document.getElementById(id) as T;
function selectionTarget(): boolean { return field<HTMLInputElement>('editSelection').checked; }
export function refreshImageFields(): void {
  const bounds = selectionTarget() ? selectionBounds() : null, percent = field<HTMLSelectElement>('resizeUnit').value === 'percent';
  field<HTMLInputElement>('editSelection').disabled = !hasSelection();
  if (!hasSelection()) field<HTMLInputElement>('editSelection').checked = false;
  field<HTMLInputElement>('imageWidth').value = String(percent ? 100 : Math.round(bounds?.width ?? W));
  field<HTMLInputElement>('imageHeight').value = String(percent ? 100 : Math.round(bounds?.height ?? H));
  field('imageDimensions').textContent = `${W} × ${H} pixels · ${layers.length} ${layers.length === 1 ? 'layer' : 'layers'}${bounds ? ` · Selection ${Math.round(bounds.width)} × ${Math.round(bounds.height)}` : ''}`;
}
function imageSize(): [number, number] {
  const bounds = selectionTarget() ? selectionBounds() : null, percent = field<HTMLSelectElement>('resizeUnit').value === 'percent';
  const width = Number(field<HTMLInputElement>('imageWidth').value), height = Number(field<HTMLInputElement>('imageHeight').value);
  return [Math.round(percent ? (bounds?.width ?? W) * width / 100 : width), Math.round(percent ? (bounds?.height ?? H) * height / 100 : height)];
}
function bindAction(id: string, action: () => void | Promise<void>): void {
  field(id).addEventListener('click', () => {
    if (!editable()) return;
    void Promise.resolve().then(action).catch(error => message(error instanceof Error ? error.message : String(error)));
  });
}
export function updateLayersUi(): void {
  refreshLayersUi();
  refreshImageFields();
}
export function bindEditor(): void {
  initLayersUi({ editable, settle, message });
  initPhotoUi({ editable, settle, message, open:requestOpen });
  bindAction('newPicture', () => { settle(); pushHistory(); resetLayers(); artwork.reset(); message('Fresh paper! Undo brings your previous picture back.'); });
  bindAction('openPicture', () => requestOpen()); bindAction('insertPicture', () => requestOpen(true)); bindAction('pasteExternal', pasteExternal);
  bindAction('redoBtn', () => { emit('settle-input'); cancelSelection(); redo(); });
  bindAction('saveAs', async () => { settle(); await exportImage(field<HTMLSelectElement>('fileFormat').value, field<HTMLInputElement>('fileName').value); });
  bindAction('printPicture', () => { settle(); printImage(); }); bindAction('saveProject', () => { settle(); saveProjectFile(field<HTMLInputElement>('fileName').value); });
  bindAction('openProject', () => field<HTMLInputElement>('projectInput').click());
  bindAction('resizePicture', () => {
    const [width, height] = imageSize(); dimensions(width, height);
    if (selectionTarget()) resizeSelection(width, height);
    else resizePicture(width, height, false, field<HTMLInputElement>('smoothResize').checked);
    refreshImageFields();
  });
  bindAction('resizeCanvas', () => { const [width, height] = imageSize(); resizePicture(width, height, true); });
  bindAction('cropPicture', cropPicture); bindAction('cropSelection', cropPicture);
  bindAction('rotatePicture', () => { const degrees = Number(field<HTMLInputElement>('rotateAngle').value); if (selectionTarget()) rotateSelection(degrees); else rotatePicture(degrees); });
  bindAction('flipPictureH', () => selectionTarget() ? flipSelection(true) : flipPicture(true)); bindAction('flipPictureV', () => selectionTarget() ? flipSelection(false) : flipPicture(false));
  bindAction('skewPicture', () => skewPicture(Number(field<HTMLInputElement>('skewX').value), Number(field<HTMLInputElement>('skewY').value), selectionTarget()));
  bindAction('invertColours', () => {
    const invert = (image: ImageData) => { for (let i = 0; i < image.data.length; i += 4) for (let c = 0; c < 3; c++) image.data[i + c] = 255 - image.data[i + c]; };
    if (selectionTarget() && hasSelection()) editSelectionPixels(invert);
    else { settle(); pushHistory(); bakeLive(baseCtx, performance.now()); const image = baseCtx.getImageData(0, 0, W, H); invert(image); baseCtx.putImageData(image, 0, 0); }
  });
  bindAction('removeBackground', removeEdgeBackground);
  for (const id of ['editSelection', 'resizeUnit']) field(id).addEventListener('change', refreshImageFields);
  for (const dimension of ['Width', 'Height'] as const) field(`image${dimension}`).addEventListener('input', () => {
    if (!field<HTMLInputElement>('keepAspect').checked) return;
    const bounds = selectionTarget() ? selectionBounds() : null, ratio = (bounds?.width ?? W) / (bounds?.height ?? H);
    const value = Number(field<HTMLInputElement>(`image${dimension}`).value), percent = field<HTMLSelectElement>('resizeUnit').value === 'percent';
    field<HTMLInputElement>(`image${dimension === 'Width' ? 'Height' : 'Width'}`).value = String(percent ? value : Math.round(dimension === 'Width' ? value / ratio : value * ratio));
  });
  field('fillTolerance').addEventListener('input', () => { state.fillTolerance = Number(field<HTMLInputElement>('fillTolerance').value); });
  field('smoothResize').addEventListener('change', () => { state.smoothResize = field<HTMLInputElement>('smoothResize').checked; });
  for (const [id, key] of [['pixelGrid', 'pixelGrid'], ['rulers', 'rulers']] as const) field(id).addEventListener('change', () => { state[key] = field<HTMLInputElement>(id).checked; });
  bindAction('fullScreen', async () => { if (document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen(); });
  field<HTMLInputElement>('imageInput').addEventListener('change', event => {
    const input = event.target as HTMLInputElement, file = input.files?.[0]; input.value = ''; if (file) void importImage(file, inserting).catch(error => {emit('image-open-cancelled');message(error.message);});else emit('image-open-cancelled');
  });
  field('imageInput').addEventListener('cancel',()=>emit('image-open-cancelled'));
  field<HTMLInputElement>('projectInput').addEventListener('change', event => {
    const input = event.target as HTMLInputElement, file = input.files?.[0]; input.value = ''; if (file) void openProjectFile(file).then(() => emit('close-options')).catch(error => message(error.message));
  });
  view.addEventListener('dragover', event => { if (event.dataTransfer?.types.includes('Files')) event.preventDefault(); });
  view.addEventListener('drop', event => { event.preventDefault(); const file = event.dataTransfer?.files[0]; if (file) void importImage(file, true).catch(error => message(error.message)); });
  document.addEventListener('paste', event => {
    if (photoEditing) return;
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement || document.querySelector('dialog[open]')) return;
    const file = [...(event.clipboardData?.files ?? [])].find(file => file.type.startsWith('image/'));
    if (file) { event.preventDefault(); void importImage(file, true).catch(error => message(error.message)); }
    else if (hasClipboard()) { event.preventDefault(); pasteSelection(); state.tool = 'scissors'; emit('tool-request'); }
  });
  updateLayersUi();
}
