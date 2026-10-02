import markup from '../index.html?raw';
const parsed = new DOMParser().parseFromString(markup, 'text/html');
parsed.querySelectorAll('script').forEach(script => script.remove());
document.body.replaceChildren(...Array.from(parsed.body.childNodes));
await import('../src/main');
const { state } = await import('../src/state');
const { baseCtx, view, eventPos } = await import('../src/canvas');
const { bakeStaticStrokes } = await import('../src/live');
const results: string[] = [];
const el = <T extends HTMLElement = HTMLElement>(selector: string) => document.querySelector<T>(selector)!;
const click = (selector: string) => el(selector).click();
const frame = () => new Promise<void>(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
function assert(value: unknown, message: string): asserts value { if (!value) throw new Error(message); }
function expectInk(expected: string) { assert(state.ink === expected, `Expected ${expected}, received ${state.ink}`); }
async function check(name: string, fn: () => void | Promise<void>) {
  try { await fn(); results.push('PASS ' + name); }
  catch (error) { results.push('FAIL ' + name + ': ' + String(error)); }
}
function fits(element: HTMLElement, label: string) {
  const r = element.getBoundingClientRect();
  assert(r.left >= -1 && r.top >= -1 && r.right <= innerWidth + 1 && r.bottom <= innerHeight + 1, `${label} leaves viewport: ${JSON.stringify(r)}`);
  assert(element.scrollWidth <= element.clientWidth + 1 && element.scrollHeight <= element.clientHeight + 1, `${label} has overflow`);
}
function brightness(value: number) {
  const slider = el<HTMLInputElement>('#wheelBrightness');
  slider.value = String(value); slider.dispatchEvent(new Event('input', { bubbles: true }));
}
function pick(hue: number, saturation: number, type = 'touch') {
  const wheel = el('#colourWheel'), rect = wheel.getBoundingClientRect();
  const radius = rect.width / 2 - wheel.clientLeft * rect.width / wheel.offsetWidth;
  const radians = hue * Math.PI / 180;
  const x = rect.left + rect.width / 2 + Math.cos(radians) * radius * saturation;
  const y = rect.top + rect.height / 2 + Math.sin(radians) * radius * saturation;
  // Synthetic touches have no browser pointer to capture. Exercise the same input handlers.
  const capture = wheel.setPointerCapture; wheel.setPointerCapture = () => {};
  try {
    for (const name of ['pointerdown', 'pointermove', 'pointerup']) wheel.dispatchEvent(new PointerEvent(name, { pointerId: 80, pointerType: type, button: 0, clientX: x, clientY: y, bubbles: true }));
  } finally { wheel.setPointerCapture = capture; }
}
await frame();
await check('Wheel button is on the palette with a visible colour icon', () => {
  if (getComputedStyle(el('#paletteToggle')).display !== 'none') click('#paletteToggle');
  fits(el('#trayContents').getBoundingClientRect().width ? el('#trayContents') : el('#bottomTray'), 'Palette');
  fits(el('#colourWheelBtn'), 'Wheel button');
  assert(el('.wheel-icon').getBoundingClientRect().width >= 26, 'Wheel icon is too small');
});
await check('Wheel, brightness and actions fit without scrolling', async () => {
  click('#colourWheelBtn'); await frame();
  fits(el('#colourWheelDialog'), 'Picker');
  for (const selector of ['#colourWheel', '#wheelBrightness', '.wheel-cancel', '.wheel-use']) fits(el(selector), selector);
  assert(el('.wheel-use').getBoundingClientRect().height >= 44, 'Use colour is too short to tap');
});
await check('Cancelling a preview leaves the ink and selection untouched', () => {
  const before = state.ink, selected = el('.color-btn.selected');
  brightness(100); pick(240, 0.8); click('.wheel-cancel');
  assert(state.ink === before && el('.color-btn.selected') === selected, 'Cancel changed drawing colour');
});
await check('Touch chooses an arbitrary blue with one obvious selected swatch', () => {
  click('#colourWheelBtn'); brightness(100); pick(240, 0.8); click('.wheel-use');
  assert(state.ink === '#3333ff', `Wrong wheel colour: ${state.ink}`);
  assert(el('#colourWheelBtn').dataset.ink === state.ink, 'Wheel swatch did not store colour');
  assert(document.querySelectorAll('.color-btn.selected').length === 1 && el('#colourWheelBtn').classList.contains('selected'), 'Selected ring is ambiguous');
  assert(el('#colourWheelBtn').getAttribute('aria-pressed') === 'true', 'Selection is not accessible');
  assert(!el('#currentInk').children.length && el('#currentInk').style.background === el('#colourWheelBtn').style.background, 'Collapsed palette shows a wheel instead of chosen ink');
});
await check('Custom wheel colour paints at the touched canvas point', () => {
  if (el('#bottomTray').classList.contains('palette-open')) click('#paletteToggle');
  const r = view.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2;
  const p = eventPos({ clientX: x, clientY: y });
  const capture = view.setPointerCapture; view.setPointerCapture = () => {};
  try {
    for (const type of ['pointerdown', 'pointerup']) view.dispatchEvent(new PointerEvent(type, { pointerId: 81, pointerType: 'touch', button: 0, clientX: x, clientY: y }));
    bakeStaticStrokes(baseCtx);
    const pixel = baseCtx.getImageData(Math.round(p.x), Math.round(p.y), 1, 1).data;
    assert(pixel[0] === 51 && pixel[1] === 51 && pixel[2] === 255, `Custom ink was not painted: ${pixel}`);
  } finally { view.setPointerCapture = capture; }
});
await check('Wheel colour tints Neon and Glitter', () => {
  click('[data-ink="neon"]'); assert(state.neonTint === '#3333ff', 'Neon lost wheel colour');
  click('[data-ink="sparkle"]'); assert(state.sparkleTint === '#3333ff', 'Glitter lost wheel colour');
});
await check('Reopening and accepting preserves exact colours, including white and black', () => {
  for (const ink of ['#12ab89', '#FFFFFF', '#000000', '#E53935', '#FFD166']) {
    state.ink = ink; click('#colourWheelBtn'); click('.wheel-use');
    assert(state.ink.toLowerCase() === ink.toLowerCase(), `${ink} changed to ${state.ink}`);
  }
});
await check('Switching tools keeps one selected ring even for a preset wheel colour', () => {
  click('[data-tool="shapes"]'); click('.drawer.open .drawer-close');
  assert(document.querySelectorAll('.color-btn.selected').length === 1 && el('#colourWheelBtn').classList.contains('selected'), 'Tool change duplicated or lost the selected ring');
  click('[data-ink="#E53935"]');
  assert(document.querySelectorAll('.color-btn.selected').length === 1 && !el('#colourWheelBtn').classList.contains('selected'), 'Preset did not replace the wheel selection');
});
await check('Brightness reaches black; wheel centre reaches white; outside drags clamp', () => {
  click('#colourWheelBtn'); brightness(0); pick(60, 1); click('.wheel-use'); expectInk('#000000');
  click('#colourWheelBtn'); brightness(100); pick(0, 0); click('.wheel-use'); expectInk('#ffffff');
  click('#colourWheelBtn'); brightness(100); pick(0, 2); click('.wheel-use'); expectInk('#ff0000');
});
await check('Keyboard wheel controls work and modal keys do not alter drawing state', () => {
  click('#colourWheelBtn'); brightness(100); pick(0, 1);
  el('#colourWheel').dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', shiftKey: true, bubbles: true, cancelable: true }));
  assert(el('#colourWheel').getAttribute('aria-valuenow') === '10', 'Keyboard hue did not change');
  state.choosingSlice = true;
  el('#colourWheel').dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true, cancelable: true }));
  assert(state.choosingSlice, 'Escape leaked into canvas shortcuts');
  state.choosingSlice = false; click('.wheel-cancel');
});
const report = document.createElement('pre'); report.id = 'wheelResults';
report.style.cssText = 'position:fixed;inset:10px;z-index:100;background:white;color:#263047;overflow:auto;padding:16px;white-space:pre-wrap';
report.textContent = `${innerWidth} × ${innerHeight}\n` + results.join('\n'); document.body.append(report);
document.title = results.some(result => result.startsWith('FAIL')) ? 'FAIL — Colour wheel checks' : 'PASS — Colour wheel checks';
