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
  const sourceScale = () => {
    const rectangle = view.getBoundingClientRect();
    return view.width >= view.height ? rectangle.width / view.width : rectangle.height / view.height;
  };
  const actualZoom = () => zoom / Math.max(0.000001, sourceScale());
  const minimumZoom = () => Math.min(0.125, actualZoom());
  const maximumZoom = () => Math.max(32, actualZoom());
  let pointer: { id: number; x: number; y: number } | null = null;
  const draw = () => {
    // Layout rounds very thin content to fractions of a CSS pixel. Correct
    // each axis so a one-pixel-high/wide picture keeps its source aspect.
    const style = getComputedStyle(view);
    const fittedX = Math.max(0.000001, parseFloat(style.width) / view.width);
    const fittedY = Math.max(0.000001, parseFloat(style.height) / view.height);
    const fitted = Math.min(fittedX, fittedY), scaleX = zoom * fitted / fittedX, scaleY = zoom * fitted / fittedY;
    const scaledWidth = stage.offsetWidth * scaleX, scaledHeight = stage.offsetHeight * scaleY;
    const left = stage.offsetLeft + (stage.offsetWidth - scaledWidth) / 2, top = stage.offsetTop + (stage.offsetHeight - scaledHeight) / 2;
    const reach = Math.max(56, (document.getElementById('workspaceBar')?.getBoundingClientRect().height ?? 0) + 8);
    const panWithin = (value: number, span: number, space: number, origin: number) => {
      const visible = Math.min(32, span, space);
      const minimum = Math.max(visible - span - origin, Math.min(0, space - span - origin) - reach);
      const maximum = Math.min(space - visible - origin, Math.max(0, -origin) + reach);
      return Math.max(minimum, Math.min(maximum, value));
    };
    x = panWithin(x, scaledWidth, slot.clientWidth, left);
    y = panWithin(y, scaledHeight, slot.clientHeight, top);
    stage.style.transform = `translate(${x}px,${y}px) scale(${scaleX},${scaleY})`;
    controls.style.top = `${Math.max(4, top + y - 56)}px`;
    const frame=displayFrame(view.width,view.height);
    state.paperScale = sourceScale();
    readout.value = `${frame.width} × ${frame.height} · ${Math.round(state.paperScale * 100)}%`;
    smaller.disabled = zoom <= minimumZoom() + 1e-9; larger.disabled = zoom >= maximumZoom() - 1e-9;
    pan.classList.toggle('active', moving); pan.setAttribute('aria-pressed', String(moving)); slot.classList.toggle('moving-paper', moving || space);
    view.style.imageRendering = state.paperScale >= 3 ? 'pixelated' : 'auto';
  };
  const scale = (factor: number) => { zoom = Math.max(minimumZoom(), Math.min(maximumZoom(), factor)); draw(); };
  smaller.addEventListener('click', () => scale(zoom / 1.5)); larger.addEventListener('click', () => scale(zoom * 1.5));
  pan.addEventListener('click', () => { moving = !moving; draw(); });
  const reset = () => { zoom = 1; x = y = 0; moving = false; draw(); };
  fit.addEventListener('click', reset);
  document.getElementById('viewZoomOut')!.addEventListener('click', () => smaller.click()); document.getElementById('viewZoomIn')!.addEventListener('click', () => larger.click());
  document.getElementById('viewFit')!.addEventListener('click', reset); document.getElementById('viewActual')!.addEventListener('click', () => scale(actualZoom()));
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
    if(state.cad.open)return;
    const typing=event.target instanceof HTMLInputElement||event.target instanceof HTMLTextAreaElement||event.target instanceof HTMLSelectElement||event.target instanceof HTMLElement&&event.target.isContentEditable;
    if(!typing&&!document.querySelector('dialog[open]')&&!event.ctrlKey&&!event.metaKey&&!event.altKey){if(['+','=','-','0'].includes(event.key)){event.preventDefault();if(event.key==='0')reset();else if(event.key==='-')smaller.click();else larger.click();return;}}
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
