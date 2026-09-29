import { GIFEncoder, quantize, applyPalette } from 'gifenc';
import { play } from './audio';
import { H, view, W } from './canvas';
import { paintFrame } from './paint';

export async function exportPng(): Promise<void> {
  paintFrame(performance.now());
  const link = document.createElement('a');
  link.download = 'dazzle.png';
  link.href = view.toDataURL('image/png');
  link.click();
  play('pop');
}

export async function exportGif(): Promise<void> {
  play('pop');
  const frames = 20;
  const delay = 80;
  const scale = 0.5;
  const w = Math.round(W * scale);
  const h = Math.round(H * scale);
  const small = document.createElement('canvas');
  small.width = w;
  small.height = h;
  const ctx = small.getContext('2d', { willReadFrequently: true })!;
  const gif = GIFEncoder();
  const start = performance.now();
  for (let i = 0; i < frames; i++) {
    paintFrame(start + i * delay);
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, w, h);
    ctx.drawImage(view, 0, 0, w, h);
    const raw = ctx.getImageData(0, 0, w, h).data;
    const data = new Uint8Array(raw);
    const palette = quantize(data, 64);
    const index = applyPalette(data, palette);
    gif.writeFrame(index, w, h, { palette, delay, repeat: i === 0 ? 0 : undefined });
    await new Promise((resolve) => setTimeout(resolve, 0));
  }
  gif.finish();
  const bytes = gif.bytes();
  const copy = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
  const blob = new Blob([copy], { type: 'image/gif' });
  const link = document.createElement('a');
  link.download = 'dazzle.gif';
  link.href = URL.createObjectURL(blob);
  link.click();
  paintFrame(performance.now());
}
