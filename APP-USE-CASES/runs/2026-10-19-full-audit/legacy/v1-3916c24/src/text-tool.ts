import { bus, emit } from './bus';
import { H, W } from './canvas';
import { previewColor } from './materials';
import { pasteImage } from './selection';
import { state } from './state';

export interface TextOptions {
  text: string; font: string; size: number; width: number;
  bold: boolean; italic: boolean; underline: boolean; strike: boolean;
  align: CanvasTextAlign; opaque: boolean;
}
export const textOptions: TextOptions = { text: '', font: 'Trebuchet MS', size: 36, width: 360, bold: false, italic: false, underline: false, strike: false, align: 'left', opaque: false };
let anchor: { x: number; y: number } | null = null;
let cached: HTMLCanvasElement | null = null, signature = '';

export function makeTextBitmap(options: TextOptions, ink = previewColor(state.ink), paper = state.secondaryInk): HTMLCanvasElement {
  const canvas = document.createElement('canvas'), ctx = canvas.getContext('2d')!;
  const size = Math.max(6, Math.min(300, options.size)), width = Math.max(20, Math.min(4096, options.width));
  const font = `${options.italic ? 'italic ' : ''}${options.bold ? 'bold ' : ''}${size}px "${options.font.replace(/["\\]/g, '')}"`;
  ctx.font = font;
  const lines: string[] = [];
  for (const paragraph of options.text.slice(0, 20000).split('\n')) {
    let line = '';
    for (const word of paragraph.split(/(\s+)/)) {
      if (ctx.measureText(line + word).width <= width - 8) { line += word; continue; }
      if (line.trim()) { lines.push(line.trimEnd()); line = ''; }
      for (const character of word) {
        if (ctx.measureText(line + character).width > width - 8 && line) { lines.push(line); line = ''; }
        line += character;
      }
    }
    lines.push(line.trimEnd());
  }
  canvas.width = width; canvas.height = Math.min(4096, Math.max(size * 1.35 + 8, lines.length * size * 1.35 + 8));
  if (options.opaque) { ctx.fillStyle = paper; ctx.fillRect(0, 0, canvas.width, canvas.height); }
  ctx.font = font; ctx.textBaseline = 'top'; ctx.textAlign = options.align; ctx.fillStyle = ink;
  const x = options.align === 'center' ? width / 2 : options.align === 'right' ? width - 4 : 4;
  lines.forEach((line, i) => {
    const y = 4 + i * size * 1.35;
    ctx.fillText(line, x, y);
    const measured = ctx.measureText(line).width, left = x - (options.align === 'center' ? measured / 2 : options.align === 'right' ? measured : 0);
    if (options.underline) ctx.fillRect(left, y + size * 1.04, measured, Math.max(1, size / 18));
    if (options.strike) ctx.fillRect(left, y + size * 0.55, measured, Math.max(1, size / 18));
  });
  return canvas;
}
function bitmap(): HTMLCanvasElement {
  const key = JSON.stringify([textOptions, state.ink, state.secondaryInk]);
  if (!cached || signature !== key) { cached = makeTextBitmap(textOptions); signature = key; }
  return cached;
}
export function beginText(x: number, y: number): void { anchor = { x, y }; emit('text-anchor'); }
export function hasText(): boolean { return Boolean(textOptions.text.trim()); }
export function cancelText(): void { anchor = null; textOptions.text = ''; cached = null; emit('text'); }
export function placeText(): void {
  if (!hasText()) return;
  let image = bitmap();
  if (state.opacity < 1) {
    const faded = document.createElement('canvas'); faded.width = image.width; faded.height = image.height;
    const ctx = faded.getContext('2d')!; ctx.globalAlpha = state.opacity; ctx.drawImage(image, 0, 0); image = faded;
  }
  pasteImage(image, anchor ?? { x: Math.max(0, (W - image.width) / 2), y: Math.max(0, (H - image.height) / 2) });
  anchor = null; textOptions.text = ''; cached = null; emit('text');
  state.tool = 'scissors'; emit('tool-request');
}
export function renderTextPreview(ctx: CanvasRenderingContext2D): void {
  if (state.tool !== 'text' || !hasText()) return;
  const image = bitmap(), p = anchor ?? { x: Math.max(0, (W - image.width) / 2), y: Math.max(0, (H - image.height) / 2) };
  ctx.save(); ctx.globalAlpha = state.opacity; ctx.drawImage(image, p.x, p.y); ctx.restore();
}
export function bindText(): void {
  const content = document.getElementById('textContent') as HTMLTextAreaElement;
  content.addEventListener('input', () => { textOptions.text = content.value; });
  for (const [id, key] of [['textFont', 'font'], ['textSize', 'size'], ['textWidth', 'width'], ['textAlign', 'align']] as const) {
    const field = document.getElementById(id) as HTMLInputElement | HTMLSelectElement;
    field.addEventListener('input', () => {
      if (key === 'size' || key === 'width') textOptions[key] = Number(field.value) || (key === 'size' ? 36 : 360);
      else if (key === 'align') textOptions.align = field.value as CanvasTextAlign;
      else textOptions.font = field.value;
    });
  }
  document.querySelectorAll<HTMLButtonElement>('[data-text-style]').forEach(button => button.addEventListener('click', () => {
    const key = button.dataset.textStyle as 'bold' | 'italic' | 'underline' | 'strike';
    textOptions[key] = !textOptions[key]; button.classList.toggle('active', textOptions[key]); button.setAttribute('aria-pressed', String(textOptions[key]));
  }));
  const opaque = document.getElementById('textOpaque') as HTMLInputElement;
  opaque.addEventListener('change', () => { textOptions.opaque = opaque.checked; });
  document.getElementById('placeText')!.addEventListener('click', placeText);
  document.getElementById('cancelText')!.addEventListener('click', cancelText);
  document.addEventListener('keydown', event => {
    if (event.ctrlKey && event.key === 'Enter' && state.tool === 'text') { event.preventDefault(); placeText(); }
  });
  bus.addEventListener('text', () => { content.value = textOptions.text; });
}
