import { play } from './audio';
import { view } from './canvas';
import { paintFrame } from './paint';
import { cloneCanvas } from './canvas';
import { encodeBmp, encodeGif, encodeTiff } from './image-codecs';

export function download(blob: Blob, filename: string): void {
  const link = document.createElement('a'), url = URL.createObjectURL(blob);
  link.download = filename; link.href = url; link.click(); window.setTimeout(() => URL.revokeObjectURL(url), 30000);
}
export async function imageBlob(format: string): Promise<Blob> {
  paintFrame(performance.now());
  const canvas = cloneCanvas(view), ctx = canvas.getContext('2d')!;
  if (format === 'jpeg' || format === 'bmp') { ctx.globalCompositeOperation = 'destination-over'; ctx.fillStyle = '#ffffff'; ctx.fillRect(0, 0, canvas.width, canvas.height); }
  if (['bmp', 'gif', 'tiff'].includes(format)) {
    const image = ctx.getImageData(0, 0, canvas.width, canvas.height);
    return format === 'bmp' ? encodeBmp(image) : format === 'gif' ? encodeGif(image) : encodeTiff(image);
  }
  const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, `image/${format}`, 0.95));
  if (!blob || blob.type !== `image/${format}`) throw new Error(`Your browser cannot save ${format.toUpperCase()}. Choose PNG.`);
  return blob;
}
export async function exportImage(format = 'png', name = 'retropaint'): Promise<void> {
  const extension = format === 'jpeg' ? 'jpg' : format === 'tiff' ? 'tif' : format;
  download(await imageBlob(format), `${name.replace(/[<>:"/\\|?*]/g, '-').replace(/\.(png|jpg|jpeg|bmp|gif|tiff?|webp)$/i, '') || 'retropaint'}.${extension}`); play('pop');
}
export function printImage(): void {
  paintFrame(performance.now());
  const frame = document.createElement('iframe'); frame.hidden = true;
  frame.srcdoc = `<html><head><title>RetroPaint picture</title><style>@page{margin:12mm}body{margin:0}img{display:block;max-width:100%;max-height:95vh;object-fit:contain}</style></head><body><img src="${view.toDataURL()}" alt="RetroPaint picture"></body></html>`;
  frame.addEventListener('load', () => {
    const window = frame.contentWindow!; window.addEventListener('afterprint', () => frame.remove(), { once: true }); window.focus(); window.print();
  }); document.body.append(frame);
}

export function exportPng(): void {
  paintFrame(performance.now());
  const link = document.createElement('a');
  link.download = 'retropaint.png';
  link.href = view.toDataURL('image/png');
  link.click();
  play('pop');
}
