import { view } from './canvas';
import { icon } from './icons';
import { state } from './state';
import { displayFrame } from './document-frame';

export function initPaperView(compact: MediaQueryList): void {
  const slot = document.getElementById('canvasSlot')!, stage = document.getElementById('stage')!;
  const controls = document.createElement('div'); controls.id = 'paperControls'; controls.setAttribute('aria-label', 'Paper view');
  const make = (label: string, glyph: string) => {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'choice';
    button.setAttribute('aria-label', label); button.title = label; button.innerHTML = icon(glyph); controls.append(button); return button;
  };
  const smaller = make('Zoom out', 'zoomOut'), larger = make('Zoom in', 'zoomIn'), pan = make('Move paper', 'hand'), fit = make('Fit whole picture', 'fit');
  slot.append(controls);
  const readout = document.createElement('output'); readout.id = 'zoomReadout'; readout.setAttribute('aria-label', 'Picture size and zoom'); slot.append(readout);
  let zoom = 1, x = 0, y = 0, moving = false, space = false;
  let pointer: { id: number; x: number; y: number } | null = null;
  const draw = () => {
    const scaledWidth = stage.offsetWidth * zoom, scaledHeight = stage.offsetHeight * zoom;
    const left = stage.offsetLeft + (stage.offsetWidth - scaledWidth) / 2, top = stage.offsetTop + (stage.offsetHeight - scaledHeight) / 2;
    x = scaledWidth > slot.clientWidth ? Math.max(slot.clientWidth - scaledWidth - left, Math.min(-left, x)) : 0;
    y = scaledHeight > slot.clientHeight ? Math.max(slot.clientHeight - scaledHeight - top, Math.min(-top, y)) : Math.min(0, slot.clientHeight - scaledHeight - top);
    stage.style.transform = `translate(${x}px,${y}px) scale(${zoom})`;
    controls.style.top = `${Math.max(4, top + y - 56)}px`;
    const frame=displayFrame(view.width,view.height);
    state.paperScale = stage.clientWidth * zoom / frame.width;
    readout.value = `${frame.width} × ${frame.height} · ${Math.round(state.paperScale * 100)}%`;
    smaller.disabled = zoom <= 0.125; larger.disabled = zoom >= 32;
    pan.classList.toggle('active', moving); pan.setAttribute('aria-pressed', String(moving)); slot.classList.toggle('moving-paper', moving || space);
    view.style.imageRendering = state.paperScale >= 3 ? 'pixelated' : 'auto';
  };
  const scale = (factor: number) => { zoom = Math.max(0.125, Math.min(32, factor)); draw(); };
  smaller.addEventListener('click', () => scale(zoom / 1.5)); larger.addEventListener('click', () => scale(zoom * 1.5));
  pan.addEventListener('click', () => { moving = !moving; draw(); });
  const reset = () => { zoom = 1; x = y = 0; moving = false; draw(); };
  fit.addEventListener('click', reset);
  document.getElementById('viewZoomOut')!.addEventListener('click', () => smaller.click()); document.getElementById('viewZoomIn')!.addEventListener('click', () => larger.click());
  document.getElementById('viewFit')!.addEventListener('click', reset); document.getElementById('viewActual')!.addEventListener('click', () => scale(displayFrame(view.width,view.height).width / Math.max(1, stage.clientWidth)));
  slot.addEventListener('wheel', event => { if (!event.ctrlKey && !event.metaKey) return; event.preventDefault(); scale(zoom * (event.deltaY < 0 ? 1.2 : 1 / 1.2)); }, { passive: false });
  const canMove = () => moving || space;
  view.addEventListener('pointerdown', event => {
    if (!canMove()) return; event.stopImmediatePropagation(); event.preventDefault();
    if (pointer) return; pointer = { id: event.pointerId, x: event.clientX, y: event.clientY }; view.setPointerCapture(event.pointerId);
  }, true);
  view.addEventListener('pointermove', event => {
    if (!canMove()) return; event.stopImmediatePropagation(); if (!pointer || event.pointerId !== pointer.id) return;
    x += event.clientX - pointer.x; y += event.clientY - pointer.y; pointer.x = event.clientX; pointer.y = event.clientY; draw();
  }, true);
  const stop = () => { pointer = null; };
  for (const type of ['pointerup', 'pointercancel', 'lostpointercapture']) view.addEventListener(type, event => {
    if (pointer && (event as PointerEvent).pointerId === pointer.id) { event.stopImmediatePropagation(); stop(); }
  }, true);
  document.addEventListener('keydown', event => {
    if (event.code !== 'Space' || event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLSelectElement || document.querySelector('dialog[open]')) return;
    event.preventDefault(); space = true; draw();
  });
  document.addEventListener('keyup', event => { if (event.code === 'Space') { space = false; stop(); draw(); } });
  window.addEventListener('blur', () => { space = false; stop(); draw(); });
  document.getElementById('toolBin')!.addEventListener('click', () => { moving = false; stop(); draw(); });
  compact.addEventListener('change', () => { stop(); reset(); }); document.addEventListener('canvas-size', reset);
  document.addEventListener('document-frame',reset);
  const observer = new ResizeObserver(draw); observer.observe(slot); observer.observe(stage); draw();
}
