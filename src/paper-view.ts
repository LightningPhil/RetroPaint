import { view } from './canvas';
import { icon } from './icons';

// Only the displayed paper moves. Artwork, undo snapshots and exports keep their resolution.
export function initPaperView(compact: MediaQueryList): void {
  const slot = document.getElementById('canvasSlot')!;
  const stage = document.getElementById('stage')!;
  const controls = document.createElement('div');
  controls.id = 'paperControls';
  controls.setAttribute('aria-label', 'Paper view');
  const make = (label: string, glyph: string) => {
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'choice';
    button.setAttribute('aria-label', label); button.title = label;
    button.innerHTML = icon(glyph); controls.append(button);
    return button;
  };
  const smaller = make('Zoom out', 'zoomOut');
  const larger = make('Zoom in', 'zoomIn');
  const pan = make('Move paper', 'hand');
  const fit = make('Fit whole picture', 'fit');
  slot.append(controls);
  let zoom = 1, x = 0, y = 0, moving = false;
  let pointer: { id: number; x: number; y: number } | null = null;
  const draw = () => {
    const maxX = Math.max(0, (stage.offsetWidth * zoom - slot.clientWidth) / 2);
    const maxY = Math.max(0, (stage.offsetHeight * zoom - slot.clientHeight) / 2);
    x = Math.max(-maxX, Math.min(maxX, x));
    y = Math.max(-maxY, Math.min(maxY, y));
    stage.style.transform = `translate(${x}px,${y}px) scale(${zoom})`;
    smaller.disabled = zoom === 1; larger.disabled = zoom === 4;
    pan.disabled = zoom === 1;
    if (zoom === 1) moving = false;
    pan.classList.toggle('active', moving);
    pan.setAttribute('aria-pressed', String(moving));
    slot.classList.toggle('moving-paper', moving);
  };
  smaller.addEventListener('click', () => { zoom = Math.max(1, zoom - 0.5); draw(); });
  larger.addEventListener('click', () => { zoom = Math.min(4, zoom + 0.5); draw(); });
  pan.addEventListener('click', () => { moving = !moving; draw(); });
  fit.addEventListener('click', () => { zoom = 1; x = y = 0; draw(); });
  // Capture before painting listeners, so dragging the paper never lays down pigment.
  view.addEventListener('pointerdown', event => {
    if (!moving || !compact.matches) return;
    event.stopImmediatePropagation(); event.preventDefault();
    if (pointer) return;
    pointer = { id: event.pointerId, x: event.clientX, y: event.clientY };
    view.setPointerCapture(event.pointerId);
  }, true);
  view.addEventListener('pointermove', event => {
    if (!moving || !compact.matches) return;
    event.stopImmediatePropagation();
    if (!pointer || event.pointerId !== pointer.id) return;
    x += event.clientX - pointer.x; y += event.clientY - pointer.y;
    pointer.x = event.clientX; pointer.y = event.clientY; draw();
  }, true);
  const stop = () => { pointer = null; };
  for (const type of ['pointerup', 'pointercancel', 'lostpointercapture']) view.addEventListener(type, stop);
  window.addEventListener('blur', stop);
  document.getElementById('toolBin')!.addEventListener('click', () => { moving = false; stop(); draw(); });
  compact.addEventListener('change', () => { zoom = 1; x = y = 0; stop(); draw(); });
  new ResizeObserver(draw).observe(slot);
  draw();
}
