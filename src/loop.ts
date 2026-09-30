import { tickDrips, tickHole, tickSqueegee } from './effects';
import { tickSpray } from './input';
import { renderOverlay } from './overlay';
import { paintFrame } from './paint';
import { tickMotor } from './spiro';
import { updateBelt } from './ui';

export function startLoop(): void {
  let last = performance.now();
  const frame = (now: number) => {
    const dt = Math.min(50, now - last);
    last = now;
    tickSqueegee(dt);
    tickHole(dt);
    tickDrips(dt);
    tickSpray();
    tickMotor(now);
    paintFrame(now);
    renderOverlay();
    updateBelt(now);
    requestAnimationFrame(frame);
  };
  requestAnimationFrame(frame);
}
