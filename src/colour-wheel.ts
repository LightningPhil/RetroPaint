import { hexToRgb, rgbToHex } from './color';
import { icon } from './icons';

interface WheelColour { hue: number; saturation: number; value: number }

function fromHex(hex: string): WheelColour {
  const rgb = hexToRgb(hex) ?? { r: 229, g: 57, b: 53 };
  const r = rgb.r / 255, g = rgb.g / 255, b = rgb.b / 255;
  const high = Math.max(r, g, b), low = Math.min(r, g, b), range = high - low;
  const hue = !range ? 0 : high === r ? (g - b) / range : high === g ? (b - r) / range + 2 : (r - g) / range + 4;
  return { hue: (hue * 60 + 360) % 360, saturation: high ? range / high : 0, value: high };
}

function toHex({ hue, saturation, value }: WheelColour): string {
  const channel = (offset: number) => {
    const k = (offset + hue / 60) % 6;
    return 255 * value * (1 - saturation * Math.max(0, Math.min(k, 4 - k, 1)));
  };
  return rgbToHex(channel(5), channel(3), channel(1));
}

/** A CSS colour disk stays sharp at every display size, without rebuilding a bitmap on each drag. */
export function bindColourWheel(trigger: HTMLButtonElement, currentColour: () => string, choose: (hex: string) => void): HTMLDialogElement {
  const dialog = document.createElement('dialog');
  dialog.id = 'colourWheelDialog';
  dialog.setAttribute('aria-labelledby', 'colourWheelTitle');
  dialog.innerHTML = `<h2 id="colourWheelTitle">Choose a colour</h2>
    <div class="colour-wheel-body">
      <div id="colourWheel" class="colour-wheel" role="slider" tabindex="0" autofocus aria-label="Colour wheel" aria-valuemin="0" aria-valuemax="360" aria-describedby="colourWheelKeys">
        <span class="wheel-shade" aria-hidden="true"></span><span class="wheel-marker" aria-hidden="true"></span>
      </div>
      <div class="colour-wheel-options">
        <div class="wheel-preview"><span id="wheelPreview" aria-hidden="true"></span><strong>Your colour</strong></div>
        <label class="wheel-light-label" for="wheelBrightness">Light &amp; dark</label>
        <div class="wheel-light-control"><span class="wheel-dark" aria-hidden="true"></span><input id="wheelBrightness" type="range" min="0" max="100" step="1"><span class="wheel-light" aria-hidden="true"></span></div>
        <div class="wheel-actions"><button type="button" class="action-btn wheel-cancel">Cancel</button><button type="button" class="action-btn wheel-use">${icon('done')}<span>Use colour</span></button></div>
      </div>
    </div>
    <p id="colourWheelKeys" class="visually-hidden">Use left and right arrows to change hue, up and down arrows to change paleness. Use the Light and dark slider to change brightness.</p>`;
  const wheel = dialog.querySelector<HTMLElement>('#colourWheel')!;
  const marker = dialog.querySelector<HTMLElement>('.wheel-marker')!;
  const shade = dialog.querySelector<HTMLElement>('.wheel-shade')!;
  const preview = dialog.querySelector<HTMLElement>('#wheelPreview')!;
  const brightness = dialog.querySelector<HTMLInputElement>('#wheelBrightness')!;
  let colour = fromHex(currentColour());
  let pointer: number | null = null;

  function refresh(): void {
    const radians = colour.hue * Math.PI / 180;
    marker.style.left = `${50 + Math.cos(radians) * colour.saturation * 50}%`;
    marker.style.top = `${50 + Math.sin(radians) * colour.saturation * 50}%`;
    marker.style.background = preview.style.background = toHex(colour);
    shade.style.opacity = String(1 - colour.value);
    brightness.value = String(Math.round(colour.value * 100));
    brightness.style.setProperty('--wheel-bright', toHex({ ...colour, value: 1 }));
    wheel.setAttribute('aria-valuenow', String(Math.round(colour.hue)));
    wheel.setAttribute('aria-valuetext', `${Math.round(colour.hue)} degrees, ${Math.round(colour.saturation * 100)}% saturation, ${Math.round(colour.value * 100)}% brightness`);
  }

  function pick(event: PointerEvent): void {
    const rect = wheel.getBoundingClientRect();
    // The wheel's border is outside the colour disk, including when the UI is zoomed on 4K screens.
    const scale = rect.width / wheel.offsetWidth;
    const radius = rect.width / 2 - wheel.clientLeft * scale;
    const x = event.clientX - rect.left - rect.width / 2;
    const y = event.clientY - rect.top - rect.height / 2;
    const distance = Math.hypot(x, y);
    if (distance > 0.01) colour.hue = (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
    colour.saturation = Math.min(1, distance / radius);
    refresh();
  }

  wheel.addEventListener('pointerdown', event => {
    if (pointer !== null || event.button !== 0) return;
    event.preventDefault();
    pointer = event.pointerId;
    wheel.focus(); wheel.setPointerCapture(pointer); pick(event);
  });
  wheel.addEventListener('pointermove', event => { if (event.pointerId === pointer) pick(event); });
  wheel.addEventListener('pointerup', event => {
    if (event.pointerId !== pointer) return;
    pick(event); pointer = null;
    if (wheel.hasPointerCapture(event.pointerId)) wheel.releasePointerCapture(event.pointerId);
  });
  wheel.addEventListener('lostpointercapture', () => { pointer = null; });
  wheel.addEventListener('pointercancel', () => { pointer = null; });
  wheel.addEventListener('keydown', event => {
    const step = event.shiftKey ? 10 : 2;
    if (event.key === 'ArrowLeft') colour.hue = (colour.hue - step + 360) % 360;
    else if (event.key === 'ArrowRight') colour.hue = (colour.hue + step) % 360;
    else if (event.key === 'ArrowUp') colour.saturation = Math.min(1, colour.saturation + step / 100);
    else if (event.key === 'ArrowDown') colour.saturation = Math.max(0, colour.saturation - step / 100);
    else return;
    event.preventDefault(); refresh();
  });
  brightness.addEventListener('input', () => { colour.value = Number(brightness.value) / 100; refresh(); });
  dialog.querySelector('.wheel-cancel')!.addEventListener('click', () => dialog.close());
  dialog.querySelector('.wheel-use')!.addEventListener('click', () => { choose(toHex(colour)); dialog.close(); });
  dialog.addEventListener('close', () => {
    if (pointer !== null && wheel.hasPointerCapture(pointer)) wheel.releasePointerCapture(pointer);
    pointer = null;
  });
  trigger.addEventListener('click', () => {
    colour = fromHex(currentColour()); refresh();
    if (!dialog.open) dialog.showModal();
  });
  document.body.append(dialog);
  return dialog;
}
