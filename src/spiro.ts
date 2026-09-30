import { play, playThrottled } from './audio';
import { beginStrokeGeneration, segment } from './draw';
import { pushHistory } from './history';
import { state } from './state';
import { baseCtx } from './canvas';
import { bakeStaticStrokes } from './live';
import type { GearDef, StatorShape } from './types';

export const OUTER_CHOICES = [72, 84, 96, 105, 120];

export const GEARS: GearDef[] = [
  { id: 'pink', color: '#FF5D8F', teeth: 24, holes: 5 },
  { id: 'purple', color: '#9D4EDD', teeth: 30, holes: 6 },
  { id: 'red', color: '#EF476F', teeth: 36, holes: 7 },
  { id: 'yellow', color: '#FFD166', teeth: 42, holes: 8 },
  { id: 'green', color: '#06D6A0', teeth: 48, holes: 8 },
  { id: 'orange', color: '#FF9F1C', teeth: 54, holes: 10 },
];

interface Motor {
  start: number;
  duration: number;
  thetaMax: number;
  lastTheta: number;
}

let motor: Motor | null = null;
let crankAngle = 0;

export function gearById(id: string | null): GearDef | null {
  return GEARS.find((gear) => gear.id === id) ?? null;
}

export function motorOn(): boolean {
  return motor !== null;
}

export function resizeHandle(): { x: number; y: number } {
  return statorPoint(state.spiro.shape, state.spiro.cx, state.spiro.cy, state.spiro.R, -Math.PI / 4);
}

export function hitResizeHandle(x: number, y: number): boolean {
  const p = resizeHandle();
  return Math.hypot(x - p.x, y - p.y) < 22;
}

export function setRingRadius(radius: number): void {
  if (motor) return;
  state.spiro.R = Math.max(60, Math.min(290, radius));
  const input = document.getElementById('ringSize') as HTMLInputElement | null;
  if (input) input.value = String(Math.round(state.spiro.R));
}

function gcd(a: number, b: number): number {
  return b ? gcd(b, a % b) : Math.abs(a);
}

function statorPoint(shape: StatorShape, cx: number, cy: number, radius: number, theta: number): { x: number; y: number } {
  const c = Math.cos(theta);
  const s = Math.sin(theta);
  if (shape === 'circle') return { x: cx + radius * c, y: cy + radius * s };
  if (shape === 'oval') return { x: cx + radius * 1.28 * c, y: cy + radius * 0.72 * s };
  if (shape === 'square') {
    const m = Math.max(Math.abs(c), Math.abs(s), 0.0001);
    return { x: cx + (radius * c * 0.92) / m, y: cy + (radius * s * 0.92) / m };
  }
  const k = 0.4 + Math.abs(Math.sin(theta * 2)) * 0.9;
  return { x: cx + radius * c * k, y: cy + radius * s * k };
}

function holeOffset(index: number, holes: number, radius: number, rotation: number): { x: number; y: number } {
  const t = holes <= 1 ? 0 : index / (holes - 1);
  const ang = rotation + index * 2.2;
  const dist = radius * (0.18 + t * 0.66);
  return { x: Math.cos(ang) * dist, y: Math.sin(ang) * dist };
}

function clampInt(n: number, min: number, max: number): number {
  if (!Number.isFinite(n)) return min;
  return Math.max(min, Math.min(max, Math.round(n)));
}

function holesFor(teeth: number): number {
  return Math.max(5, Math.min(10, Math.round(teeth / 7)));
}

function outerCount(): number {
  return Math.max(24, state.spiro.outerTeeth);
}

export function innerGear(): GearDef | null {
  const base = gearById(state.spiro.gearId);
  if (!base) return null;
  const teeth = clampInt(state.spiro.innerTeeth, 8, outerCount() - 6);
  return { ...base, teeth, holes: holesFor(teeth) };
}

export function setOuterTeeth(n: number): void {
  const teeth = clampInt(n, 40, 180);
  state.spiro.outerTeeth = teeth;
  if (state.spiro.innerTeeth > teeth - 8) state.spiro.innerTeeth = Math.max(12, teeth - 12);
  play('clunk');
}

export function setInnerTeeth(n: number, colorId?: string): void {
  const teeth = clampInt(n, 10, Math.max(12, outerCount() - 8));
  state.spiro.innerTeeth = teeth;
  state.spiro.gearId = colorId ?? state.spiro.gearId ?? 'red';
  play('clunk');
}

function gearRadius(teeth: number): number {
  return (state.spiro.R * teeth) / outerCount();
}

function rotationFor(theta: number, teeth: number): number {
  return -((outerCount() - teeth) / teeth) * theta;
}

export function gearCenter(theta = state.spiro.theta): { x: number; y: number; r: number } | null {
  const gear = innerGear();
  if (!gear) return null;
  const r = gearRadius(gear.teeth);
  const orbit = statorPoint(state.spiro.shape, state.spiro.cx, state.spiro.cy, Math.max(12, state.spiro.R - r), theta);
  return { x: orbit.x, y: orbit.y, r };
}

export function penPosition(theta: number): { x: number; y: number } | null {
  const gear = innerGear();
  const center = gearCenter(theta);
  if (!gear || !center) return null;
  const rot = rotationFor(theta, gear.teeth);
  const hole = holeOffset(state.spiro.hole % gear.holes, gear.holes, center.r, rot);
  return { x: center.x + hole.x, y: center.y + hole.y };
}

export function hitStator(x: number, y: number): boolean {
  let best = 1e9;
  for (let i = 0; i < 90; i++) {
    const p = statorPoint(state.spiro.shape, state.spiro.cx, state.spiro.cy, state.spiro.R, (i / 90) * Math.PI * 2);
    best = Math.min(best, Math.hypot(p.x - x, p.y - y));
  }
  return best < 24;
}

export function hitWindKey(x: number, y: number): boolean {
  if (state.spiro.drive !== 'auto' || motor) return false;
  const center = gearCenter();
  return !!center && Math.hypot(x - center.x, y - center.y) < 20;
}

export function hoverHole(x: number, y: number): void {
  if (motor) return;
  const gear = innerGear();
  const center = gearCenter();
  if (!gear || !center) return;
  if (Math.hypot(x - center.x, y - center.y) > center.r + 6) return;
  const rot = rotationFor(state.spiro.theta, gear.teeth);
  let best = state.spiro.hole;
  let bestD = 1e9;
  for (let i = 0; i < gear.holes; i++) {
    const hole = holeOffset(i, gear.holes, center.r, rot);
    const d = Math.hypot(center.x + hole.x - x, center.y + hole.y - y);
    if (d < bestD) {
      bestD = d;
      best = i;
    }
  }
  if (best !== state.spiro.hole && bestD < 28) {
    state.spiro.hole = best;
    play('snick', 1.1);
  }
}

export function assignGear(id: string): boolean {
  const gear = gearById(id);
  if (!gear) return false;
  setInnerTeeth(gear.teeth, id);
  return true;
}

export function resetKit(): void {
  state.spiro.R = 200;
  state.spiro.cx = 480;
  state.spiro.cy = 320;
  state.spiro.outerTeeth = 96;
  state.spiro.innerTeeth = 36;
  state.spiro.gearId = 'red';
  state.spiro.theta = 0;
  motor = null;
  play('pop');
}

export function drawBetween(a: number, b: number): void {
  // Sample the actual gear curve in canvas space, independent of mouse speed or
  // animation frame rate. No skipped sections or long chords across the curve.
  const steps = Math.max(1, Math.ceil(Math.abs(b - a) * state.spiro.R * 2 / 1.5));
  let previous = penPosition(a);
  if (!previous) return;
  for (let i = 1; i <= steps; i++) {
    const next = penPosition(a + (b - a) * i / steps);
    if (!next) return;
    segment(previous.x, previous.y, next.x, next.y, state.brushWidth, 0);
    previous = next;
  }
}

export function crankStart(x: number, y: number): void {
  if (!state.spiro.gearId || motor) return;
  crankAngle = Math.atan2(y - state.spiro.cy, x - state.spiro.cx);
  pushHistory();
  beginStrokeGeneration();
}

export function crankMove(x: number, y: number): void {
  if (!state.spiro.gearId || motor) return;
  const ang = Math.atan2(y - state.spiro.cy, x - state.spiro.cx);
  let delta = ang - crankAngle;
  while (delta > Math.PI) delta -= Math.PI * 2;
  while (delta < -Math.PI) delta += Math.PI * 2;
  crankAngle = ang;
  delta = Math.max(-0.75, Math.min(0.75, delta));
  const next = state.spiro.theta + delta * 2.5;
  drawBetween(state.spiro.theta, next);
  state.spiro.theta = next;
  playThrottled('zip', 45, 0.65 + Math.min(1.8, Math.abs(delta) * 7));
}

export function startMotor(): void {
  const gear = innerGear();
  if (!gear || motor) {
    play('clunk', 0.7);
    return;
  }
  const outer = Math.max(1, gear.teeth / gcd(outerCount(), gear.teeth));
  const cycles = outer;
  pushHistory();
  beginStrokeGeneration();
  state.spiro.theta = 0;
  motor = {
    start: performance.now(),
    duration: 1000 + Math.min(1, cycles / 40) * 1000,
    thetaMax: Math.PI * 2 * cycles,
    lastTheta: 0,
  };
  play('whir', 0.7);
}

export function tickMotor(now: number): void {
  if (!motor) return;
  const t = Math.min(1, (now - motor.start) / motor.duration);
  const eased = t < 0.5 ? 2 * t * t : 1 - ((-2 * t + 2) ** 2) / 2;
  const theta = eased * motor.thetaMax;
  drawBetween(motor.lastTheta, theta);
  state.spiro.theta = theta;
  motor.lastTheta = theta;
  playThrottled('whir', 80, 0.55 + t * 1.5);
  if (t >= 1) {
    motor = null;
    bakeStaticStrokes(baseCtx);
    play('motor-stop');
  }
}

export function drawRig(ctx: CanvasRenderingContext2D): void {
  const { cx, cy, R, shape } = state.spiro;
  ctx.save();
  ctx.lineCap = 'round';
  ctx.strokeStyle = 'rgba(17, 138, 178, 0.9)';
  ctx.lineWidth = 16;
  ctx.beginPath();
  for (let i = 0; i <= 80; i++) {
    const p = statorPoint(shape, cx, cy, R, (i / 80) * Math.PI * 2);
    if (i === 0) ctx.moveTo(p.x, p.y);
    else ctx.lineTo(p.x, p.y);
  }
  ctx.stroke();
  ctx.setLineDash([7, 7]);
  ctx.lineWidth = 3;
  ctx.strokeStyle = 'rgba(8, 70, 110, 0.7)';
  ctx.stroke();
  ctx.setLineDash([]);

  const handle = resizeHandle();
  ctx.beginPath();
  ctx.arc(handle.x, handle.y, 14, 0, Math.PI * 2);
  ctx.fillStyle = '#FFD166'; ctx.fill();
  ctx.strokeStyle = '#1A1A1A'; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = '#1A1A1A'; ctx.font = 'bold 19px sans-serif';
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('↗', handle.x, handle.y);

  const gear = innerGear();
  const center = gearCenter();
  if (gear && center) {
    drawGear(ctx, gear, center.x, center.y, center.r, rotationFor(state.spiro.theta, gear.teeth), state.spiro.hole);
    if (state.spiro.drive === 'auto' && !motor) {
      ctx.save();
      ctx.translate(center.x, center.y);
      ctx.rotate(0.6);
      ctx.fillStyle = '#FFD166';
      ctx.strokeStyle = '#1A1A1A';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.roundRect(-6, -6, 28, 12, 3);
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }
  }
  ctx.restore();
}

function drawGear(ctx: CanvasRenderingContext2D, gear: GearDef, x: number, y: number, r: number, rot: number, holeIndex: number): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(rot);
  ctx.fillStyle = gear.color;
  ctx.globalAlpha = 0.72;
  ctx.strokeStyle = '#1A1A1A';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(0, 0, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1;
  ctx.stroke();
  for (let i = 0; i < gear.teeth; i += 1) {
    if (i % 2) continue;
    const a = (i / gear.teeth) * Math.PI * 2;
    ctx.beginPath();
    ctx.arc(Math.cos(a) * (r + 4), Math.sin(a) * (r + 4), 3.2, 0, Math.PI * 2);
    ctx.fillStyle = gear.color;
    ctx.fill();
    ctx.stroke();
  }
  for (let i = 0; i < gear.holes; i++) {
    const hole = holeOffset(i, gear.holes, r, 0);
    ctx.beginPath();
    ctx.arc(hole.x, hole.y, i === holeIndex % gear.holes ? 5 : 3, 0, Math.PI * 2);
    ctx.fillStyle = i === holeIndex % gear.holes ? '#1A1A1A' : 'rgba(255,255,255,0.85)';
    ctx.fill();
  }
  ctx.restore();
}
