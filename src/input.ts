import { unlockAudio } from './audio';
import { eventPos, view, viewCtx } from './canvas';
import { beginStrokeGeneration, calligWidth, dot, segment, splatterBurst, sprayCloud, useGeneration } from './draw';
import { beginBake, burst, embossAt, invertAt, isBusy, pixelateAt, smudge, startHole } from './effects';
import { drawShape, floodAt, getPending, hitPin, lockPending, movePin, setPinDrag, setShapePainter } from './fill';
import { pushHistory } from './history';
import { setPreview } from './preview';
import { crankMove, crankStart, hitStator, hitWindKey, hoverHole, startMotor } from './spiro';
import { currentWidth, state } from './state';
import { cutSelection, placeStamp } from './stamps';

interface Ptr {
  id: number;
  x: number;
  y: number;
  lx: number;
  ly: number;
  sx: number;
  sy: number;
  t: number;
  still: number;
  gen: number;
  mode: 'draw' | 'spray' | 'shape' | 'lasso' | 'grad' | 'pin' | 'ring' | 'crank' | 'stamp' | 'filter' | 'smudge' | 'ignore';
  lasso: { x: number; y: number }[];
  ringDx: number;
  ringDy: number;
  lastSpeed: number;
}

const ptrs = new Map<number, Ptr>();
let groupSaved = false;

export function initInput(): void {
  setShapePainter((x0, y0, x1, y1, width) => segment(x0, y0, x1, y1, width, 0));
  view.addEventListener('pointerdown', onDown);
  view.addEventListener('pointermove', onMove);
  view.addEventListener('pointerup', onUp);
  view.addEventListener('pointercancel', onUp);
  view.addEventListener('contextmenu', (event) => event.preventDefault());
}

export function sprayPointers(): Ptr[] {
  return [...ptrs.values()].filter((ptr) => ptr.mode === 'spray');
}

export function tapCanvas(x: number, y: number): void {
  if (isBusy() || state.busy) return;
  if (state.tool === 'bucket' || state.tool === 'wand') {
    floodAt(x, y, state.tool === 'wand', null);
    return;
  }
  if (state.tool === 'stamp') {
    pushHistory();
    placeStamp(x, y);
    return;
  }
  const gen = beginStrokeGeneration();
  pushHistory();
  useGeneration(gen);
  dot(x, y, currentWidth());
}

function onDown(event: PointerEvent): void {
  unlockAudio();
  if (isBusy() || state.busy) return;
  view.setPointerCapture(event.pointerId);
  const pos = eventPos(event);
  const pin = hitPin(pos.x, pos.y);
  if (pin) {
    setPinDrag(pin);
    ptrs.set(event.pointerId, blank(event.pointerId, pos, 'pin'));
    return;
  }
  if (getPending()) {
    lockPending();
    ptrs.set(event.pointerId, blank(event.pointerId, pos, 'ignore'));
    return;
  }

  if (state.tool === 'spiro') {
    if (hitWindKey(pos.x, pos.y)) {
      startMotor();
      ptrs.set(event.pointerId, blank(event.pointerId, pos, 'ignore'));
      return;
    }
    if (hitStator(pos.x, pos.y)) {
      const ptr = blank(event.pointerId, pos, 'ring');
      ptr.ringDx = pos.x - state.spiro.cx;
      ptr.ringDy = pos.y - state.spiro.cy;
      ptrs.set(event.pointerId, ptr);
      return;
    }
    crankStart(pos.x, pos.y);
    ptrs.set(event.pointerId, blank(event.pointerId, pos, 'crank'));
    return;
  }

  if (state.tool === 'shapes' && state.shape === 'poly') {
    addPolyPoint(pos.x, pos.y, event.detail);
    return;
  }

  if (state.tool === 'eraser' && state.eraserMode === 'blackhole') {
    startHole(pos.x, pos.y);
    return;
  }

  if (state.tool === 'wand') {
    floodAt(pos.x, pos.y, true, null);
    burst(pos.x, pos.y);
    return;
  }

  if (state.tool === 'bucket') {
    const gradient = state.gradientDrag || state.ink.startsWith('grad-');
    if (!gradient) {
      floodAt(pos.x, pos.y, false, null);
      return;
    }
    ptrs.set(event.pointerId, blank(event.pointerId, pos, 'grad'));
    return;
  }

  if (ptrs.size === 0) groupSaved = false;
  const ptr = blank(event.pointerId, pos, 'draw');
  ptr.gen = beginStrokeGeneration();

  if (state.tool === 'scissors') ptr.mode = 'lasso';
  else if (state.tool === 'shapes') ptr.mode = 'shape';
  else if (state.tool === 'stamp') ptr.mode = 'stamp';
  else if (state.tool === 'spray') ptr.mode = 'spray';
  else if (state.tool === 'sponge') ptr.mode = 'smudge';
  else if (state.tool === 'eraser' && state.eraserMode !== 'scrub') ptr.mode = 'filter';

  if (!groupSaved && ptr.mode !== 'lasso') {
    if (ptr.mode === 'smudge' || ptr.mode === 'filter') beginBake();
    else pushHistory();
    groupSaved = true;
  }

  ptrs.set(event.pointerId, ptr);
  useGeneration(ptr.gen);

  if (ptr.mode === 'draw') dot(pos.x, pos.y, widthFor(ptr, 0, 0, 0));
  if (ptr.mode === 'stamp') placeStamp(pos.x, pos.y);
  if (ptr.mode === 'filter') applyFilter(pos.x, pos.y);
  if (ptr.mode === 'smudge') smudge(pos.x, pos.y);
  if (ptr.mode === 'lasso') ptr.lasso.push(pos);
}

function onMove(event: PointerEvent): void {
  const ptr = ptrs.get(event.pointerId);
  if (!ptr) {
    if (state.tool === 'spiro') hoverHole(eventPos(event).x, eventPos(event).y);
    return;
  }
  const pos = eventPos(event);
  const now = performance.now();
  const dt = Math.max(8, now - ptr.t);
  const dist = Math.hypot(pos.x - ptr.x, pos.y - ptr.y);
  const speed = dist / dt;
  ptr.lastSpeed = speed;
  if (dist < 1.2) ptr.still += dt;
  else ptr.still = 0;

  if (ptr.mode === 'pin') movePin(pos.x, pos.y);
  else if (ptr.mode === 'ring') {
    state.spiro.cx = pos.x - ptr.ringDx;
    state.spiro.cy = pos.y - ptr.ringDy;
  } else if (ptr.mode === 'crank') crankMove(pos.x, pos.y);
  else if (ptr.mode === 'shape') setPreview({ kind: 'shape', shape: state.shape === 'poly' ? 'line' : state.shape, x0: ptr.sx, y0: ptr.sy, x1: pos.x, y1: pos.y });
  else if (ptr.mode === 'lasso') {
    ptr.lasso.push(pos);
    setPreview({ kind: 'lasso', points: ptr.lasso });
  } else if (ptr.mode === 'grad') setPreview({ kind: 'rubber', x0: ptr.sx, y0: ptr.sy, x1: pos.x, y1: pos.y });
  else if (ptr.mode === 'stamp') {
    if (dist > Math.max(18, 34 * state.stampScale)) {
      placeStamp(pos.x, pos.y);
      ptr.x = pos.x;
      ptr.y = pos.y;
    }
  } else if (ptr.mode === 'smudge' && dist > 1) smudge(pos.x, pos.y);
  else if (ptr.mode === 'filter' && dist > 6) applyFilter(pos.x, pos.y);
  else if (ptr.mode === 'draw' && dist > 0.8) {
    useGeneration(ptr.gen);
    const steps = Math.max(1, Math.ceil(dist / 3));
    for (let i = 1; i <= steps; i++) {
      const t0 = (i - 1) / steps;
      const t1 = i / steps;
      const x0 = ptr.x + (pos.x - ptr.x) * t0;
      const y0 = ptr.y + (pos.y - ptr.y) * t0;
      const x1 = ptr.x + (pos.x - ptr.x) * t1;
      const y1 = ptr.y + (pos.y - ptr.y) * t1;
      segment(x0, y0, x1, y1, widthFor(ptr, pos.x - ptr.x, pos.y - ptr.y, speed), speed, ptr.gen);
    }
    ptr.x = pos.x;
    ptr.y = pos.y;
  }

  if (ptr.mode !== 'draw') {
    ptr.x = pos.x;
    ptr.y = pos.y;
  }
  ptr.lx = pos.x;
  ptr.ly = pos.y;
  ptr.t = now;
}

function onUp(event: PointerEvent): void {
  const ptr = ptrs.get(event.pointerId);
  ptrs.delete(event.pointerId);
  if (!ptr) return;
  const pos = eventPos(event);

  if (ptr.mode === 'pin') setPinDrag(null);
  if (ptr.mode === 'shape' && state.shape !== 'poly') {
    setPreview(null);
    useGeneration(ptr.gen);
    const kind = state.shape === 'line' || state.shape === 'rect' || state.shape === 'circle' ? state.shape : 'line';
    drawShape(kind, ptr.sx, ptr.sy, pos.x, pos.y, viewCtx, true);
  }
  if (ptr.mode === 'lasso') {
    setPreview(null);
    cutSelection(ptr.lasso);
  }
  if (ptr.mode === 'grad') {
    setPreview(null);
    const dist = Math.hypot(pos.x - ptr.sx, pos.y - ptr.sy);
    if (dist < 8) floodAt(ptr.sx, ptr.sy, false, null);
    else floodAt(ptr.sx, ptr.sy, false, { x1: ptr.sx, y1: ptr.sy, x2: pos.x, y2: pos.y });
  }
  if (ptr.mode === 'draw' && state.applicator === 'callig' && ptr.lastSpeed > 1.15) {
    useGeneration(ptr.gen);
    splatterBurst(pos.x, pos.y, currentWidth());
  }
  if (ptrs.size === 0) groupSaved = false;
}

function addPolyPoint(x: number, y: number, detail: number): void {
  const nearStart = state.poly.length > 2 && Math.hypot(x - state.poly[0].x, y - state.poly[0].y) < 18;
  if (detail >= 2 || nearStart) {
    if (state.poly.length > 1) {
      pushHistory();
      const gen = beginStrokeGeneration();
      useGeneration(gen);
      const width = currentWidth();
      const pts = state.poly;
      for (let i = 1; i < pts.length; i++) segment(pts[i - 1].x, pts[i - 1].y, pts[i].x, pts[i].y, width, 0, gen);
      if (nearStart) segment(pts[pts.length - 1].x, pts[pts.length - 1].y, pts[0].x, pts[0].y, width, 0, gen);
    }
    state.poly = [];
    return;
  }
  state.poly.push({ x, y });
}

function applyFilter(x: number, y: number): void {
  if (state.eraserMode === 'pixelate') pixelateAt(x, y);
  else if (state.eraserMode === 'invert') invertAt(x, y);
  else embossAt(x, y);
}

function widthFor(_ptr: Ptr, dx: number, dy: number, speed: number): number {
  if (state.tool === 'draw' && state.applicator === 'callig') return calligWidth(dx, dy, speed);
  if (state.tool === 'eraser') return Math.max(18, currentWidth() * 1.4);
  return currentWidth();
}

function blank(id: number, pos: { x: number; y: number }, mode: Ptr['mode']): Ptr {
  return {
    id,
    x: pos.x,
    y: pos.y,
    lx: pos.x,
    ly: pos.y,
    sx: pos.x,
    sy: pos.y,
    t: performance.now(),
    still: 0,
    gen: 0,
    mode,
    lasso: [],
    ringDx: 0,
    ringDy: 0,
    lastSpeed: 0,
  };
}

export function tickSpray(): void {
  for (const ptr of sprayPointers()) {
    useGeneration(ptr.gen);
    sprayCloud(ptr.x, ptr.y, ptr.still);
  }
}
