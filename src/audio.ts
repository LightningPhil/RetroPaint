export type SoundName =
  | 'pop'
  | 'clunk'
  | 'thwack'
  | 'rip'
  | 'chime'
  | 'splash'
  | 'vwoop'
  | 'squeak'
  | 'rattle'
  | 'shimmer'
  | 'zip'
  | 'snick'
  | 'clack'
  | 'squeegee'
  | 'whir'
  | 'motor-stop';

let audioCtx: AudioContext | null = null;
let popped = false;
const lastAt = new Map<string, number>();

function context(): AudioContext {
  if (!audioCtx) {
    const Ctor = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    audioCtx = new Ctor();
  }
  return audioCtx;
}

export function unlockAudio(): void {
  const ctx = context();
  const go = () => {
    if (!popped && ctx.state === 'running') {
      popped = true;
      play('pop');
    }
  };
  if (ctx.state === 'suspended') void ctx.resume().then(go);
  else go();
}

export function playMarkerPop(): void {
  const ctx = context();
  if (ctx.state === 'running') {
    popped = true;
    play('pop');
  }
}

function envGain(ctx: AudioContext, start: number, peak: number, dur: number): GainNode {
  const gain = ctx.createGain();
  gain.gain.setValueAtTime(peak, start);
  gain.gain.exponentialRampToValueAtTime(0.001, start + dur);
  gain.connect(ctx.destination);
  return gain;
}

function tone(type: OscillatorType, freq: number, endFreq: number, dur: number, peak: number, ramp: 'exp' | 'lin' = 'exp'): void {
  const ctx = context();
  if (ctx.state !== 'running') return;
  const now = ctx.currentTime;
  const osc = ctx.createOscillator();
  const gain = envGain(ctx, now, peak, dur);
  osc.type = type;
  osc.frequency.setValueAtTime(freq, now);
  if (ramp === 'exp') osc.frequency.exponentialRampToValueAtTime(Math.max(1, endFreq), now + dur);
  else osc.frequency.linearRampToValueAtTime(endFreq, now + dur);
  osc.connect(gain);
  osc.start(now);
  osc.stop(now + dur + 0.02);
}

function noise(dur: number, freq: number, q: number, peak: number): void {
  const ctx = context();
  if (ctx.state !== 'running') return;
  const now = ctx.currentTime;
  const length = Math.max(1, Math.floor(ctx.sampleRate * dur));
  const buffer = ctx.createBuffer(1, length, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < length; i++) data[i] = Math.random() * 2 - 1;
  const src = ctx.createBufferSource();
  src.buffer = buffer;
  const filter = ctx.createBiquadFilter();
  filter.type = 'bandpass';
  filter.frequency.setValueAtTime(freq, now);
  filter.Q.value = q;
  const gain = envGain(ctx, now, peak, dur);
  src.connect(filter);
  filter.connect(gain);
  src.start(now);
  src.stop(now + dur);
}

export function play(name: SoundName, pitch = 1): void {
  const ctx = context();
  if (ctx.state !== 'running') return;
  const p = Math.max(0.4, pitch);
  switch (name) {
    case 'pop':
      tone('sine', 880 * p, 120, 0.1, 0.35);
      break;
    case 'clunk':
      tone('square', 160 * p, 40, 0.09, 0.22);
      break;
    case 'thwack':
      tone('triangle', 280 * p, 55, 0.14, 0.4);
      break;
    case 'rip':
      tone('sawtooth', 90, 520, 0.22, 0.18, 'lin');
      break;
    case 'chime':
      tone('sine', 660, 1320, 0.45, 0.2);
      break;
    case 'splash':
      tone('sine', 280, 860, 0.18, 0.35);
      break;
    case 'vwoop':
      tone('sine', 420, 70, 0.45, 0.3);
      break;
    case 'squeak':
      noise(0.08, 1400 * p, 8, 0.08);
      break;
    case 'rattle':
      noise(0.18, 900, 2, 0.2);
      tone('square', 90, 70, 0.16, 0.12);
      break;
    case 'shimmer':
      tone('sine', 1760 * p, 2100 * p, 0.25, 0.06);
      tone('sine', 2400 * p, 1800 * p, 0.3, 0.04);
      break;
    case 'zip':
      noise(0.05, 700 * p, 6, 0.07);
      break;
    case 'snick':
      tone('square', 900 * p, 400, 0.04, 0.12);
      break;
    case 'clack':
      tone('square', 220, 80, 0.07, 0.25);
      window.setTimeout(() => tone('square', 180, 60, 0.07, 0.22), 90);
      break;
    case 'squeegee':
      noise(0.55, 600, 1.2, 0.16);
      break;
    case 'whir':
      tone('sawtooth', 180 * p, 520 * p, 0.12, 0.05);
      break;
    case 'motor-stop':
      tone('square', 300, 90, 0.08, 0.2);
      break;
    default:
      break;
  }
}

export function playThrottled(name: SoundName, gapMs: number, pitch = 1): void {
  const now = performance.now();
  const prev = lastAt.get(name) ?? 0;
  if (now - prev < gapMs) return;
  lastAt.set(name, now);
  play(name, pitch);
}
