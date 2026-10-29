import { bus, emit } from './bus';
import { pushHistory } from './history';
import { activeLayer, activeLayerId, addLayer, canAddLayer, deleteLayer, drawLayerThumbnail, duplicateLayer, layerChanged, layers, mergeLayerDown, moveLayer, reorderLayer, switchLayer } from './layers';
import { icon } from './icons';
import { state } from './state';

interface LayerActions { editable: () => boolean; settle: () => void; message: (text: string) => void }
interface Row { element: HTMLDivElement; pick: HTMLButtonElement; eye: HTMLButtonElement; grip: HTMLButtonElement; name: HTMLSpanElement; status: HTMLSpanElement; thumbnail: HTMLCanvasElement }
interface Drag { pointerId: number; id: number; startY: number; moved: boolean; target: number | null; above: boolean }
const compact = matchMedia('(max-width:1000px), (max-height:550px)');
const rows = new Map<number, Row>();
const field = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
let actions: LayerActions | null = null, drag: Drag | null = null, opacityGesture: number | null = null, thumbnailTime = 0;

function showLayers(open: boolean, focus = false): void {
  const panel = field('layersPanel'); panel.hidden = !open;
  field('layersToggle').setAttribute('aria-expanded', String(open));
  if (open) { emit('close-options'); refreshLayersUi(); }
  emit('layer-panel');
  if (focus) (open ? field('addLayer') : field('layersToggle')).focus({ preventScroll: true });
}
function change(action: () => void, notice?: () => string): void {
  if (!actions?.editable()) return;
  actions.settle(); pushHistory(); action(); if (notice) actions.message(notice());
}
function selectLayer(id: number, keepOpen = false): void {
  if (!actions?.editable()) return;
  actions.settle(); switchLayer(id);
  if (compact.matches && !keepOpen) showLayers(false, true);
}
function makeRow(id: number): Row {
  const element = document.createElement('div'); element.className = 'layer-row'; element.dataset.layerId = String(id);
  const eye = document.createElement('button'); eye.type = 'button'; eye.className = 'layer-icon-button layer-eye';
  const pick = document.createElement('button'); pick.type = 'button'; pick.className = 'layer-pick';
  const thumbnail = document.createElement('canvas'); thumbnail.width = 64; thumbnail.height = 48; thumbnail.setAttribute('aria-hidden', 'true');
  const label = document.createElement('span'); label.className = 'layer-row-label';
  const name = document.createElement('span'), status = document.createElement('span'); name.className = 'layer-name'; status.className = 'layer-state'; label.append(name, status); pick.append(thumbnail, label);
  const grip = document.createElement('button'); grip.type = 'button'; grip.className = 'layer-icon-button layer-grip'; grip.innerHTML = icon('grip');
  element.append(eye, pick, grip);
  pick.addEventListener('click', () => selectLayer(id));
  eye.addEventListener('click', () => change(() => { const layer = layers.find(layer => layer.id === id); if (layer) { layer.visible = !layer.visible; layerChanged(); } }));
  grip.addEventListener('pointerdown', event => {
    if (event.button !== 0 || !actions?.editable()) return;
    event.preventDefault(); selectLayer(id, true);
    drag = { pointerId: event.pointerId, id, startY: event.clientY, moved: false, target: null, above: false };
    field('layersPanel').setPointerCapture(event.pointerId);
  });
  for (const button of [pick, grip]) button.addEventListener('keydown', event => {
    if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown') return;
    event.preventDefault(); event.stopPropagation();
    if (event.altKey) {
      selectLayer(id, true); const index = layers.findIndex(layer => layer.id === id), direction = event.key === 'ArrowUp' ? 1 : -1;
      if (layers[index + direction]) change(() => reorderLayer(direction));
    } else {
      const displayed = [...layers].reverse(), index = displayed.findIndex(layer => layer.id === id), next = displayed[index + (event.key === 'ArrowUp' ? -1 : 1)];
      if (next) { selectLayer(next.id, true); rows.get(next.id)?.pick.focus({ preventScroll: true }); }
    }
  });
  return { element, eye, pick, grip, name, status, thumbnail };
}
export function refreshLayersUi(): void {
  if (!actions) return;
  const list = field('layerList'), active = activeLayer(), index = layers.indexOf(active);
  const focused = list.contains(document.activeElement) ? document.activeElement as HTMLElement : null;
  if (opacityGesture !== null && opacityGesture !== active.id) opacityGesture = null;
  for (const [id, row] of rows) if (!layers.some(layer => layer.id === id)) { row.element.remove(); rows.delete(id); }
  [...layers].reverse().forEach((layer, i) => {
    let row = rows.get(layer.id); if (!row) { row = makeRow(layer.id); rows.set(layer.id, row); }
    if (list.children[i] !== row.element) list.insertBefore(row.element, list.children[i] ?? null);
    const selected = layer.id === activeLayerId;
    row.element.classList.toggle('active', selected); row.element.classList.toggle('layer-hidden', !layer.visible);
    row.name.textContent = layer.name;
    row.status.textContent = !layer.visible ? 'Hidden' : selected ? 'Painting here' : `${Math.round(layer.opacity * 100)}% visible`;
    row.pick.setAttribute('aria-pressed', String(selected)); row.pick.setAttribute('aria-label', `Paint on ${layer.name}${selected ? ', selected' : ''}${!layer.visible ? ', hidden' : ''}`);
    row.eye.innerHTML = icon(layer.visible ? 'eye' : 'eyeOff'); row.eye.setAttribute('aria-label', `${layer.visible ? 'Hide' : 'Show'} ${layer.name}`); row.eye.setAttribute('aria-pressed', String(layer.visible)); row.eye.title = `${layer.visible ? 'Hide' : 'Show'} layer`;
    row.grip.setAttribute('aria-label', `Reorder ${layer.name}`); row.grip.title = 'Drag to reorder. Alt + ↑ / ↓ also works.';
    row.grip.disabled = layers.length < 2;
  });
  if (focused?.isConnected && document.activeElement !== focused) focused.focus({ preventScroll: true });
  const setValue = (id: string, value: string) => { const input = field<HTMLInputElement>(id); if (document.activeElement !== input) input.value = value; };
  setValue('layerName', active.name); field<HTMLInputElement>('layerOpacity').value = String(active.opacity);
  field<HTMLOutputElement>('layerOpacityValue').value = `${Math.round(active.opacity * 100)}%`;
  field<HTMLInputElement>('transparentLayer').checked = active.paper === null;
  field<HTMLButtonElement>('deleteLayer').disabled = layers.length < 2; field<HTMLButtonElement>('mergeLayer').disabled = index === 0;
  field<HTMLButtonElement>('layerDown').disabled = index === 0; field<HTMLButtonElement>('layerUp').disabled = index === layers.length - 1;
  field<HTMLButtonElement>('addLayer').disabled = field<HTMLButtonElement>('duplicateLayer').disabled = !canAddLayer();
  field('activeLayerName').textContent = active.name; field('layerCount').textContent = String(layers.length);
  field('layersToggle').setAttribute('aria-label', `Layers: ${layers.length}, painting on ${active.name}${!active.visible ? ', hidden' : ''}`);
  field('layersHint').textContent = !active.visible ? `${active.name} is hidden. Tap its eye to see your paint.` : layers.length === 1 ? 'Add a clear sheet to draw on top of your picture.' : `Painting on ${active.name}. Tap another sheet to switch.`;
  refreshThumbnails(performance.now(), true);
}
function refreshThumbnails(now: number, force = false): void {
  if (!actions || field('layersPanel').hidden || (!force && now - thumbnailTime < 250)) return;
  thumbnailTime = now;
  for (const layer of layers) { const row = rows.get(layer.id); if (row) drawLayerThumbnail(row.thumbnail.getContext('2d')!, layer, now); }
}
export function updateLayerThumbnails(now: number): void { refreshThumbnails(now); }
function clearDrag(): void {
  drag = null; field('layersPanel').classList.remove('dragging-layer');
  for (const row of rows.values()) row.element.classList.remove('layer-dragging', 'drop-above', 'drop-below');
}
export function initLayersUi(callbacks: LayerActions): void {
  actions = callbacks;
  field('layersToggle').addEventListener('click', () => showLayers(field('layersPanel').hidden));
  field('closeLayers').addEventListener('click', () => showLayers(false, true));
  field('openLayers').addEventListener('click', () => showLayers(true, true));
  field('addLayer').addEventListener('click', () => {
    if (!canAddLayer()) { actions?.message('Your layer stack is full. Combine some sheets to make room.'); return; }
    change(addLayer, () => `New clear sheet: ${activeLayer().name}. You’re ready to paint.`);
    if (compact.matches) showLayers(false, true);
  });
  const commands: Record<string, () => void> = { duplicateLayer, deleteLayer, mergeLayer: mergeLayerDown, layerUp: () => reorderLayer(1), layerDown: () => reorderLayer(-1) };
  for (const [id, command] of Object.entries(commands)) field(id).addEventListener('click', () => {
    if ((field(id) as HTMLButtonElement).disabled) return;
    const previousName = activeLayer().name;
    change(command, id === 'deleteLayer' ? () => `Removed ${previousName}. Undo brings it back.` : undefined);
  });
  const name = field<HTMLInputElement>('layerName');
  const rename = () => {
    const value = name.value.trim() || 'Layer';
    if (value !== activeLayer().name) change(() => { activeLayer().name = value; layerChanged(); });
    name.value = activeLayer().name;
  };
  name.addEventListener('change', rename);
  name.addEventListener('keydown', event => {
    if (event.key === 'Enter') { event.preventDefault(); rename(); name.blur(); }
    if (event.key === 'Escape') { event.preventDefault(); name.value = activeLayer().name; name.blur(); }
  });
  const opacity = field<HTMLInputElement>('layerOpacity');
  opacity.addEventListener('input', () => {
    if (!actions?.editable()) return;
    const value = Number(opacity.value);
    if (opacityGesture !== activeLayerId) { actions.settle(); pushHistory(); opacityGesture = activeLayerId; }
    activeLayer().opacity = value; layerChanged();
  });
  for (const type of ['change', 'blur', 'pointercancel']) opacity.addEventListener(type, () => { opacityGesture = null; });
  const transparent = field<HTMLInputElement>('transparentLayer');
  transparent.addEventListener('change', () => { const value = transparent.checked; change(() => { activeLayer().paper = value ? null : state.secondaryInk; layerChanged(); }); });
  const panel = field('layersPanel');
  document.addEventListener('pointerdown', event => {
    if (compact.matches && !panel.hidden && event.target instanceof Node && !panel.contains(event.target) && !field('layersToggle').contains(event.target)) showLayers(false);
  });
  const options = field<HTMLDetailsElement>('layerOptions');
  options.addEventListener('toggle', () => {
    panel.classList.toggle('layer-options-open', options.open);
    options.querySelector('summary')!.textContent = options.open ? '← Back to layers' : 'Layer options';
  });
  panel.addEventListener('pointermove', event => {
    if (!drag || event.pointerId !== drag.pointerId || Math.abs(event.clientY - drag.startY) < 5 && !drag.moved) return;
    drag.moved = true; panel.classList.add('dragging-layer');
    const list = field('layerList'), listBounds = list.getBoundingClientRect();
    if (event.clientY < listBounds.top + 24) list.scrollTop -= 8;
    else if (event.clientY > listBounds.bottom - 24) list.scrollTop += 8;
    let candidate: Row | null = null;
    const ordered = [...layers].reverse().map(layer => rows.get(layer.id)!);
    for (const row of ordered) {
      row.element.classList.toggle('layer-dragging', Number(row.element.dataset.layerId) === drag.id);
      row.element.classList.remove('drop-above', 'drop-below');
      const bounds = row.element.getBoundingClientRect();
      if (event.clientY >= bounds.top && event.clientY <= bounds.bottom) candidate = row;
    }
    if (!candidate) candidate = event.clientY < listBounds.top ? ordered[0] : ordered.at(-1)!;
    drag.target = Number(candidate.element.dataset.layerId); drag.above = event.clientY < candidate.element.getBoundingClientRect().top + candidate.element.offsetHeight / 2;
    if (drag.target !== drag.id) candidate.element.classList.add(drag.above ? 'drop-above' : 'drop-below');
  });
  panel.addEventListener('pointerup', event => {
    if (!drag || event.pointerId !== drag.pointerId) return;
    const drop = drag; clearDrag();
    if (drop.moved && drop.target !== null && drop.target !== drop.id) {
      const order = layers.map(layer => layer.id).join(',');
      // Compute whether this is a real move before creating an undo step.
      const next = layers.filter(layer => layer.id !== drop.id), target = next.findIndex(layer => layer.id === drop.target);
      next.splice(target + Number(drop.above), 0, layers.find(layer => layer.id === drop.id)!);
      if (next.map(layer => layer.id).join(',') !== order) change(() => { moveLayer(drop.id, drop.target!, drop.above); });
    }
    if (panel.hasPointerCapture(event.pointerId)) panel.releasePointerCapture(event.pointerId);
  });
  for (const type of ['pointercancel', 'lostpointercapture']) panel.addEventListener(type, clearDrag);
  window.addEventListener('blur', () => { if (drag) clearDrag(); });
  document.addEventListener('keydown', event => {
    if (document.querySelector('dialog[open]') || event.target instanceof HTMLInputElement && !['range', 'checkbox', 'color'].includes(event.target.type) || event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLSelectElement) return;
    if (event.key.toLowerCase() === 'l' && !event.ctrlKey && !event.metaKey && !event.altKey) { event.preventDefault(); showLayers(panel.hidden, true); }
    if (event.key === 'Escape' && !panel.hidden) { event.preventDefault(); showLayers(false, true); }
  });
  compact.addEventListener('change', () => showLayers(!compact.matches));
  field('layersToggle').querySelector('span')!.innerHTML = icon('layers');
  refreshLayersUi(); showLayers(!compact.matches);
  bus.addEventListener('layers', () => { if (drag && !layers.some(layer => layer.id === drag!.id)) clearDrag(); });
  bus.addEventListener('history', () => { opacityGesture = null; });
  bus.addEventListener('photo-panel', event => { if ((event as CustomEvent<boolean>).detail) showLayers(false); });
  bus.addEventListener('restore-layers',event=>showLayers((event as CustomEvent<boolean>).detail));
}
