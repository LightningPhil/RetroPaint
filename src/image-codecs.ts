/** Small, local encoders for Paint's classic image formats. */
function opaque(image: ImageData, index: number, channel: number): number {
  const alpha = image.data[index + 3] / 255; return Math.round(image.data[index + channel] * alpha + 255 * (1 - alpha));
}
export function encodeBmp(image: ImageData): Blob {
  const { width, height } = image, row = (width * 3 + 3) & ~3;
  const bytes = new Uint8Array(54 + row * height), view = new DataView(bytes.buffer);
  bytes.set([66, 77]); view.setUint32(2, bytes.length, true); view.setUint32(10, 54, true); view.setUint32(14, 40, true);
  view.setInt32(18, width, true); view.setInt32(22, height, true); view.setUint16(26, 1, true); view.setUint16(28, 24, true); view.setUint32(34, row * height, true);
  for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) {
    const i = (y * width + x) * 4, out = 54 + (height - y - 1) * row + x * 3;
    bytes[out] = opaque(image, i, 2); bytes[out + 1] = opaque(image, i, 1); bytes[out + 2] = opaque(image, i, 0);
  }
  return new Blob([bytes], { type: 'image/bmp' });
}
export function encodeGif(image: ImageData): Blob {
  const bytes: number[] = [71, 73, 70, 56, 57, 97];
  const u16 = (n: number) => bytes.push(n & 255, n >> 8);
  u16(image.width); u16(image.height); bytes.push(0xf7, 0, 0);
  for (let i = 0; i < 256; i++) bytes.push(Math.round((i >> 5) / 7 * 255), Math.round(((i >> 2) & 7) / 7 * 255), Math.round((i & 3) / 3 * 255));
  bytes.push(0x21, 0xf9, 4, 1, 0, 0, 0, 0, 0x2c); u16(0); u16(0); u16(image.width); u16(image.height); bytes.push(0, 8);
  const packed: number[] = []; let buffer = 0, bits = 0;
  const code = (n: number) => { buffer |= n << bits; bits += 9; while (bits >= 8) { packed.push(buffer & 255); buffer >>>= 8; bits -= 8; } };
  // Frequent clear codes keep the dictionary below the 10-bit boundary.
  code(256);
  for (let p = 0; p < image.width * image.height; p++) {
    if (p && p % 200 === 0) code(256);
    const i = p * 4, index = ((image.data[i] >> 5) << 5) | ((image.data[i + 1] >> 5) << 2) | (image.data[i + 2] >> 6);
    code(image.data[i + 3] < 128 ? 0 : index || 1);
  }
  code(257); if (bits) packed.push(buffer & 255);
  for (let i = 0; i < packed.length; i += 255) { const chunk = packed.slice(i, i + 255); bytes.push(chunk.length, ...chunk); }
  bytes.push(0, 0x3b); return new Blob([new Uint8Array(bytes)], { type: 'image/gif' });
}
export function encodeTiff(image: ImageData): Blob {
  const count = 11, bitsOffset = 8 + 2 + count * 12 + 4, pixelsOffset = bitsOffset + 8;
  const bytes = new Uint8Array(pixelsOffset + image.data.length), view = new DataView(bytes.buffer);
  bytes.set([73, 73, 42, 0]); view.setUint32(4, 8, true); view.setUint16(8, count, true);
  const tags = [[256, 4, 1, image.width], [257, 4, 1, image.height], [258, 3, 4, bitsOffset], [259, 3, 1, 1], [262, 3, 1, 2], [273, 4, 1, pixelsOffset], [277, 3, 1, 4], [278, 4, 1, image.height], [279, 4, 1, image.data.length], [284, 3, 1, 1], [338, 3, 1, 2]];
  tags.forEach(([tag, type, size, value], i) => { const at = 10 + i * 12; view.setUint16(at, tag, true); view.setUint16(at + 2, type, true); view.setUint32(at + 4, size, true); view.setUint32(at + 8, value, true); });
  for (let i = 0; i < 4; i++) view.setUint16(bitsOffset + i * 2, 8, true);
  bytes.set(image.data, pixelsOffset); return new Blob([bytes], { type: 'image/tiff' });
}
export function decodeTiff(buffer: ArrayBuffer): HTMLCanvasElement {
  const damaged = () => new Error('This TIFF is damaged or incomplete. Try another copy or convert it to PNG.');
  const requireBytes = (offset: number, length: number) => {
    if (!Number.isSafeInteger(offset) || !Number.isSafeInteger(length) || offset < 0 || length < 0 || offset > buffer.byteLength - length) throw damaged();
  };
  requireBytes(0, 8);
  const view = new DataView(buffer), little = view.getUint16(0) === 0x4949;
  if ((!little && view.getUint16(0) !== 0x4d4d) || view.getUint16(2, little) !== 42) throw new Error('This is not a TIFF image.');
  const directory = view.getUint32(4, little); requireBytes(directory, 2);
  const count = view.getUint16(directory, little), tags = new Map<number, number[]>();
  requireBytes(directory + 2, count * 12 + 4);
  for (let i = 0; i < count; i++) {
    const at = directory + 2 + i * 12, tag = view.getUint16(at, little), type = view.getUint16(at + 2, little), length = view.getUint32(at + 4, little);
    if (type !== 3 && type !== 4) continue;
    if (length > 65536) throw new Error('TIFF directory is too large.');
    const size = type === 3 ? 2 : 4, offset = length * size <= 4 ? at + 8 : view.getUint32(at + 8, little);
    requireBytes(offset, length * size);
    tags.set(tag, Array.from({ length }, (_, j) => size === 2 ? view.getUint16(offset + j * size, little) : view.getUint32(offset + j * size, little)));
  }
  const width = tags.get(256)?.[0] ?? 0, height = tags.get(257)?.[0] ?? 0, channels = tags.get(277)?.[0] ?? 1, compression = tags.get(259)?.[0] ?? 1;
  if (width < 1 || height < 1 || width > 4096 || height > 4096) throw new Error('TIFF dimensions must be 1–4096 pixels.');
  if (compression !== 1 || (tags.get(284)?.[0] ?? 1) !== 1 || !tags.get(258)?.length || tags.get(258)!.some(n => n !== 8)) throw new Error('This TIFF uses unsupported compression or colour depth. Open an uncompressed 8-bit TIFF or convert it to PNG.');
  const photometric = tags.get(262)?.[0] ?? 2;
  if (![0, 1, 2].includes(photometric) || ![1, 3, 4].includes(channels) || (photometric === 2 && channels < 3)) throw new Error('This TIFF colour format is not supported.');
  const rows = tags.get(278)?.[0] ?? height;
  const offsets = tags.get(273) ?? [], lengths = tags.get(279) ?? [];
  if (!rows || offsets.length !== Math.ceil(height / rows) || lengths.length !== offsets.length) throw damaged();
  // Validate the complete strip table before allocating or copying any pixels.
  // A missing final strip must not turn into a successfully imported clear row.
  for (let strip = 0; strip < offsets.length; strip++) {
    const pixels = Math.min(rows, height - strip * rows) * width;
    if (lengths[strip] < pixels * channels) throw damaged();
    requireBytes(offsets[strip], lengths[strip]);
  }
  const canvas = document.createElement('canvas'); canvas.width = width; canvas.height = height;
  const ctx = canvas.getContext('2d')!, image = ctx.createImageData(width, height);
  for (let strip = 0; strip < offsets.length; strip++) {
    const startPixel = strip * rows * width, pixels = Math.min(rows * width, width * height - startPixel);
    for (let p = 0; p < pixels; p++) {
      const at = offsets[strip] + p * channels, out = (startPixel + p) * 4;
      for (let c = 0; c < 3; c++) image.data[out + c] = photometric === 2 ? view.getUint8(at + c) : photometric === 0 ? 255 - view.getUint8(at) : view.getUint8(at);
      image.data[out + 3] = channels === 4 ? view.getUint8(at + 3) : 255;
    }
  }
  ctx.putImageData(image, 0, 0); return canvas;
}
