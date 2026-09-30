import { play } from './audio';
import { view } from './canvas';
import { paintFrame } from './paint';

export function exportPng(): void {
  paintFrame(performance.now());
  const link = document.createElement('a');
  link.download = 'retropaint.png';
  link.href = view.toDataURL('image/png');
  link.click();
  play('pop');
}
