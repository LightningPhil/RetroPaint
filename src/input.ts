import { activeSector, insideSector, clipSegment, sliceAt } from './symmetry-mask';
import { bus } from './bus';
import { unlockAudio } from './audio';
import { baseCtx, eventPos, view, viewCtx } from './canvas';
import { bakeStaticStrokes } from './live';
import { beginStrokeGeneration, dot, segment, sprayCloud, useGeneration } from './draw';
import { beginBake, embossAt, invertAt, isBusy, pixelateAt, smudge, startHole } from './effects';
import { drawShape, floodAt, getPending, hitPin, lockPending, movePin, setPinDrag, setShapePainter, strokePath } from './fill';
import { pushHistory } from './history';
import { setPreview } from './preview';
import { crankMove, crankStart, hitStator, hitWindKey, hoverHole, startMotor } from './spiro';
import { currentWidth, state } from './state';
import { placeStamp } from './stamps';
import { cancelSelection, commitSelection, hitSelection, moveSelection, rectangle, selectRegion } from './selection';
import { SmudgePath } from './smudge';
import { splinePoints } from './curves';
import { hitResizeHandle, motorOn, resizeHandle, setRingRadius } from './spiro';

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
  mode: 'draw' | 'spray' | 'shape' | 'lasso' | 'grad' | 'pin' | 'ring' | 'crank' | 'stamp' | 'filter' | 'smudge' | 'ignore' | 'bucket' | 'selectionMove' | 'resize';
  smudgePath?: SmudgePath;
  lasso: { x: number; y: number }[];
  ringDx: number;
  ringDy: number;
  lastSpeed: number;
  fx: number;
  fy: number;
}

const ptrs = new Map<number, Ptr>();
let groupSaved = false;

export function initInput(): void {
  setShapePainter((x0, y0, x1, y1, width) => segment(x0, y0, x1, y1, width, 0));
  view.addEventListener('pointerdown', onDown);
  view.addEventListener('pointermove', onMove);
  view.addEventListener('pointerup', onUp);
  view.addEventListener('pointercancel', onUp);
  view.addEventListener('pointerleave', () => { state.cursor = null; });
  view.addEventListener('contextmenu', (event) => event.preventDefault());
}

export function sprayPointers(): Ptr[] {
  return [...ptrs.values()].filter((ptr) => ptr.mode === 'spray');
}

export function tapCanvas(x: number, y: number): void {
  if (isBusy() || state.busy || chooseSource(x,y)) return;
  if (state.tool === 'bucket') {
    floodAt(x, y, null);
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
  if (isBusy() || state.busy || event.button !== 0) return;
  if (ptrs.size && (state.tool === 'sponge' || state.tool === 'scissors')) return;
  view.setPointerCapture(event.pointerId);
  const pos = eventPos(event);
  if (chooseSource(pos.x,pos.y)) return;
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

  if (state.tool === 'scissors') {
    if (hitSelection(pos.x, pos.y)) {
      ptrs.set(event.pointerId, blank(event.pointerId, pos, 'selectionMove'));
      return;
    }
    commitSelection();
  }
  if (state.tool === 'spiro') {
    if (motorOn()) return;
    if (hitResizeHandle(pos.x, pos.y)) {
      const ptr = blank(event.pointerId, pos, 'resize');
      const handle = resizeHandle();
      ptr.ringDx = state.spiro.R / Math.hypot(handle.x - state.spiro.cx, handle.y - state.spiro.cy);
      ptrs.set(event.pointerId, ptr);
      return;
    }
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

  if (state.tool === 'shapes' && (state.shape === 'poly' || state.shape === 'spline')) {
    addPolyPoint(pos.x, pos.y, event.detail);
    return;
  }

  if (state.tool === 'eraser' && state.eraserMode === 'blackhole') {
    startHole(pos.x, pos.y);
    return;
  }

  if (state.tool === 'bucket') {
    const gradient = state.gradientDrag || state.ink.startsWith('grad-');
    if (!gradient) {
      if (insideSector(pos.x,pos.y)) floodAt(pos.x, pos.y, null);
      else ptrs.set(event.pointerId, blank(event.pointerId, pos, 'bucket'));
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
    if (ptr.mode === 'smudge' || ptr.mode === 'filter' || (activeSector() && state.tool === 'eraser')) beginBake();
    else pushHistory();
    groupSaved = true;
  }

  ptrs.set(event.pointerId, ptr);
  useGeneration(ptr.gen);

  if (ptr.mode === 'draw') dot(pos.x, pos.y, widthFor(ptr, 0, 0, 0));
  if (ptr.mode === 'stamp') placeStamp(pos.x, pos.y);
  if (ptr.mode === 'filter') applyFilter(pos.x, pos.y);
  if (ptr.mode === 'smudge') {
    const radius = Math.max(12, currentWidth());
    ptr.smudgePath = new SmudgePath(pos.x, pos.y, radius, (x, y, dx, dy) => smudge(x, y, dx, dy, radius));
  }
  if (ptr.mode === 'lasso') ptr.lasso.push(pos);
}

function onMove(event: PointerEvent): void {
  state.cursor = eventPos(event);
  view.style.cursor = 'crosshair';
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

  if (ptr.mode === 'bucket' && insideSector(pos.x,pos.y)) { floodAt(pos.x,pos.y,null); ptr.mode='ignore'; }
  else if (ptr.mode === 'selectionMove') moveSelection(pos.x - ptr.x, pos.y - ptr.y);
  else if (ptr.mode === 'resize') setRingRadius(Math.hypot(pos.x - state.spiro.cx, pos.y - state.spiro.cy) * ptr.ringDx);
  else if (ptr.mode === 'pin') movePin(pos.x, pos.y);
  else if (ptr.mode === 'ring') {
    state.spiro.cx = pos.x - ptr.ringDx;
    state.spiro.cy = pos.y - ptr.ringDy;
  } else if (ptr.mode === 'crank') crankMove(pos.x, pos.y);
  else if (ptr.mode === 'shape') setPreview({ kind: 'shape', shape: state.shape === 'poly' || state.shape === 'spline' ? 'line' : state.shape, x0: ptr.sx, y0: ptr.sy, x1: pos.x, y1: pos.y });
  else if (ptr.mode === 'lasso') {
    if (state.selectionMode === 'rect') ptr.lasso = rectangle(ptr.sx, ptr.sy, pos.x, pos.y);
    else if (dist >= 2) ptr.lasso.push(pos);
    setPreview({ kind: 'lasso', points: ptr.lasso });
  } else if (ptr.mode === 'grad') setPreview({ kind: 'rubber', x0: ptr.sx, y0: ptr.sy, x1: pos.x, y1: pos.y });
  else if (ptr.mode === 'stamp') {
    if (dist > Math.max(18, 34 * state.stampScale)) {
      placeStamp(pos.x, pos.y);
      ptr.x = pos.x;
      ptr.y = pos.y;
    }
  } else if (ptr.mode === 'smudge') {
    const samples = event.getCoalescedEvents?.() ?? [];
    for (const sample of samples.length ? samples : [event]) {
      const p = eventPos(sample);
      ptr.smudgePath?.move(p.x, p.y);
    }
  }
  else if (ptr.mode === 'filter' && dist > 6) applyFilter(pos.x, pos.y);
  else if (ptr.mode === 'draw' && state.tool === 'draw' && state.applicator === 'callig') {
    layCalligraphy(ptr, pos.x, pos.y, speed);
  } else if (ptr.mode === 'draw' && dist > 0.6) {
    useGeneration(ptr.gen);
    const x1 = (ptr.x + pos.x) / 2;
    const y1 = (ptr.y + pos.y) / 2;
    strokeCurve(ptr.lx, ptr.ly, ptr.x, ptr.y, x1, y1, widthFor(ptr, pos.x - ptr.x, pos.y - ptr.y, speed), speed, ptr.gen);
    ptr.lx = x1;
    ptr.ly = y1;
    ptr.x = pos.x;
    ptr.y = pos.y;
  }

  if (ptr.mode !== 'draw' && ptr.mode !== 'stamp') {
    ptr.x = pos.x;
    ptr.y = pos.y;
    ptr.lx = pos.x;
    ptr.ly = pos.y;
  }
  ptr.t = now;
}

function onUp(event: PointerEvent): void {
  const ptr = ptrs.get(event.pointerId);
  ptrs.delete(event.pointerId);
  if (!ptr) return;
  const pos = eventPos(event);
  if (event.type === 'pointercancel') {
    setPreview(null);
    if (ptr.mode === 'selectionMove') cancelSelection();
    if (ptr.mode === 'pin') setPinDrag(null);
    if (!ptrs.size) groupSaved = false;
    return;
  }
  if (ptr.mode === 'smudge') ptr.smudgePath?.move(pos.x, pos.y, true);
  if (ptr.mode === 'selectionMove') moveSelection(pos.x - ptr.x, pos.y - ptr.y);
  if (ptr.mode === 'pin') setPinDrag(null);
  if (ptr.mode === 'shape' && state.shape !== 'poly' && state.shape !== 'spline') {
    setPreview(null);
    useGeneration(ptr.gen);
    const kind = state.shape === 'line' || state.shape === 'rect' || state.shape === 'circle' ? state.shape : 'line';
    drawShape(kind, ptr.sx, ptr.sy, pos.x, pos.y, viewCtx, true);
  }
  if (ptr.mode === 'lasso') {
    setPreview(null);
    selectRegion(state.selectionMode === 'rect' ? rectangle(ptr.sx, ptr.sy, pos.x, pos.y) : [...ptr.lasso, pos]);
  }
  if (ptr.mode === 'grad') {
    setPreview(null);
    const dist = Math.hypot(pos.x - ptr.sx, pos.y - ptr.sy);
    const clipped = clipSegment({x:ptr.sx,y:ptr.sy},pos);
    if (clipped) {
      const [entry,end] = clipped;
      const length = Math.hypot(end.x-entry.x,end.y-entry.y);
      const nudge = insideSector(ptr.sx,ptr.sy) ? 0 : Math.min(1,1/Math.max(length,0.001));
      const seed = {x:entry.x+(end.x-entry.x)*nudge,y:entry.y+(end.y-entry.y)*nudge};
      floodAt(seed.x,seed.y,dist<8 ? null : {x1:ptr.sx,y1:ptr.sy,x2:pos.x,y2:pos.y});
    }
  }
  if (ptr.mode === 'draw' && state.tool === 'draw' && state.applicator === 'callig') {
    for (let i = 0; i < 10; i++) layCalligraphy(ptr, pos.x, pos.y, ptr.lastSpeed);
    if (Math.hypot(pos.x - ptr.lx, pos.y - ptr.ly) > 0.5) {
      useGeneration(ptr.gen);
      strokeCurve(ptr.lx, ptr.ly, ptr.x, ptr.y, pos.x, pos.y, widthFor(ptr, pos.x - ptr.x, pos.y - ptr.y, ptr.lastSpeed), ptr.lastSpeed, ptr.gen, 3);
    }
  } else if (ptr.mode === 'draw' && Math.hypot(pos.x - ptr.lx, pos.y - ptr.ly) > 0.5) {
    useGeneration(ptr.gen);
    strokeCurve(ptr.lx, ptr.ly, ptr.x, ptr.y, pos.x, pos.y, widthFor(ptr, pos.x - ptr.x, pos.y - ptr.y, ptr.lastSpeed), ptr.lastSpeed, ptr.gen);
  }
  if (ptrs.size === 0) {
    groupSaved = false;
    bakeStaticStrokes(baseCtx);
  }
}

function addPolyPoint(x: number, y: number, detail: number): void {
  const nearStart = state.poly.length > 2 && Math.hypot(x - state.poly[0].x, y - state.poly[0].y) < 18;
  if (detail >= 2 || nearStart) {
    finishPath(nearStart);
    return;
  }
  state.poly.push({ x, y });
}

export function finishPath(close = false): void {
  if (state.poly.length > 1) {
    pushHistory();
    useGeneration(beginStrokeGeneration());
    const points = state.shape === 'spline' ? splinePoints(state.poly, close) : state.poly;
    strokePath(points, viewCtx, true, close && state.shape !== 'spline');
    bakeStaticStrokes(baseCtx);
  }
  state.poly = [];
}

function applyFilter(x: number, y: number): void {
  if (state.eraserMode === 'pixelate') pixelateAt(x, y);
  else if (state.eraserMode === 'invert') invertAt(x, y);
  else embossAt(x, y);
}

function widthFor(_ptr: Ptr, _dx: number, _dy: number, _speed: number): number {
  if (state.tool === 'draw' && state.applicator === 'callig') return currentWidth() * 1.12;
  if (state.tool === 'eraser') return Math.max(18, currentWidth() * 1.4);
  if (state.tool === 'draw' && state.applicator === 'marker') {
    return currentWidth();
  }
  if (state.tool === 'draw' && state.applicator === 'watercolor') return currentWidth() * 1.2;
  return currentWidth();
}

function layCalligraphy(ptr: Ptr, x: number, y: number, speed: number): void {
  const jump = Math.hypot(x - ptr.fx, y - ptr.fy);
  const follow = jump > 28 ? 0.55 : 0.28;
  ptr.fx += (x - ptr.fx) * follow;
  ptr.fy += (y - ptr.fy) * follow;
  if (Math.hypot(ptr.fx - ptr.x, ptr.fy - ptr.y) < 2.2) return;
  useGeneration(ptr.gen);
  const x1 = (ptr.x + ptr.fx) / 2;
  const y1 = (ptr.y + ptr.fy) / 2;
  strokeCurve(ptr.lx, ptr.ly, ptr.x, ptr.y, x1, y1, widthFor(ptr, ptr.fx - ptr.x, ptr.fy - ptr.y, speed), speed, ptr.gen, 3);
  ptr.lx = x1;
  ptr.ly = y1;
  ptr.x = ptr.fx;
  ptr.y = ptr.fy;
}

function strokeCurve(x0: number, y0: number, cx: number, cy: number, x1: number, y1: number, width: number, speed: number, gen: number, step = 2): void {
  const approx = Math.hypot(x0 - cx, y0 - cy) + Math.hypot(cx - x1, cy - y1);
  const steps = Math.max(1, Math.ceil(approx / step));
  let px = x0;
  let py = y0;
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const u = 1 - t;
    const x = u * u * x0 + 2 * u * t * cx + t * t * x1;
    const y = u * u * y0 + 2 * u * t * cy + t * t * y1;
    segment(px, py, x, y, width, speed, gen);
    px = x;
    py = y;
  }
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
    fx: pos.x,
    fy: pos.y,
  };
}

export function tickSpray(): void {
  for (const ptr of sprayPointers()) {
    useGeneration(ptr.gen);
    sprayCloud(ptr.x, ptr.y, ptr.still);
  }
}

function chooseSource(x: number, y: number): boolean {
  if (!state.choosingSlice || !activeSector()) return false;
  commitSelection();
  state.symmetrySlice=sliceAt(x,y); state.choosingSlice=false;
  state.poly=[]; setPreview(null);
  bus.dispatchEvent(new Event('symmetry-mask'));
  return true;
}
