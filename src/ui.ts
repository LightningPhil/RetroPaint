import { unlockAudio } from './audio';
import { play } from './audio';
import { bus } from './bus';
import { canvasToClient } from './canvas';
import { isHex } from './color';
import { exportGif, exportPng } from './export';
import { cancelPending, getPending } from './fill';
import { startSqueegee } from './effects';
import { undo } from './history';
import { tapCanvas } from './input';
import { GRADIENTS, patternFor, thumbFor } from './materials';
import { activeInkId } from './materials';
import { assignGear, GEARS, gearById, gearCenter, hitStator, resetKit, startMotor } from './spiro';
import { saveLevel, state } from './state';
import { customStamps, STAMP_BANKS } from './stamps';
import type { Applicator, EraserMode, ShapeKind, StatorShape, SymmetryMode, ToolId } from './types';

const TOOL_LEVEL: Record<ToolId, number> = {
  draw: 1,
  bucket: 1,
  shapes: 2,
  eraser: 2,
  stamp: 2,
  spray: 3,
  wand: 3,
  sponge: 3,
  scissors: 3,
  spiro: 4,
};

const SOLIDS: { color: string; level: number }[] = [
  { color: '#E53935', level: 1 },
  { color: '#FDD835', level: 1 },
  { color: '#1E88E5', level: 1 },
  { color: '#43A047', level: 1 },
  { color: '#1A1A1A', level: 1 },
  { color: '#EF476F', level: 2 },
  { color: '#06D6A0', level: 2 },
  { color: '#118AB2', level: 2 },
  { color: '#FFD166', level: 2 },
  { color: '#9D4EDD', level: 2 },
  { color: '#FF9F1C', level: 2 },
  { color: '#FFFFFF', level: 2 },
];

let scanTimer = 0;
let scanIndex = 0;
let stampBank = 'critters';
let beltNow = 0;

export function initUi(): void {
  document.body.dataset.level = String(state.level);
  const slider = document.getElementById('levelSlider') as HTMLInputElement;
  slider.value = String(state.level);
  buildSolids();
  buildTextures();
  buildGradients();
  buildGears();
  renderStampBank();
  renderCustomStamps();
  bindTools();
  bindSliders();
  bindConveyor();
  bindExport();
  bindSwitch();
  bindCutout();
  sync();
  document.addEventListener('pointerdown', () => unlockAudio());
  document.addEventListener('keydown', onKey);
}

export function updateBelt(now: number): void {
  beltNow = now;
  const slots = [...document.querySelectorAll<HTMLButtonElement>('.belt-slot')];
  const colors = state.conveyor;
  const shift = colors.length ? Math.floor(now * state.beltSpeed * 0.002) : 0;
  slots.forEach((slot, index) => {
    if (!colors.length || index >= colors.length) {
      slot.style.background = '#d0d0d0';
      slot.textContent = '';
      delete slot.dataset.index;
      return;
    }
    const dataIndex = ((index - shift) % colors.length + colors.length) % colors.length;
    slot.style.background = colors[dataIndex];
    slot.dataset.index = String(dataIndex);
  });
}

function buildSolids(): void {
  const tray = document.getElementById('tray-solids')!;
  for (const solid of SOLIDS) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'color-btn scan-item';
    btn.dataset.minLevel = String(solid.level);
    btn.style.background = solid.color;
    btn.draggable = true;
    if (solid.color === state.ink) btn.classList.add('selected');
    btn.addEventListener('click', () => selectInk(solid.color, btn));
    btn.addEventListener('dragstart', (event) => event.dataTransfer?.setData('text/plain', `ink:${solid.color}`));
    tray.append(btn);
  }
  addFx(tray, 'rainbow', 'linear-gradient(45deg, red, yellow, lime, cyan, magenta)');
  addFx(tray, 'neon', '#ffffff');
  addFx(tray, 'sparkle', 'radial-gradient(circle, #fff 20%, #FFE566 45%, #EF476F 80%)');
}

function addFx(tray: HTMLElement, id: string, background: string): void {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'color-btn square scan-item';
  btn.dataset.minLevel = '3';
  btn.style.background = background;
  btn.title = id;
  btn.addEventListener('click', () => selectInk(id, btn));
  tray.append(btn);
}

function buildTextures(): void {
  const tray = document.getElementById('tray-textures')!;
  for (const id of ['tex-brick', 'tex-dots', 'tex-weave', 'tex-grass', 'tex-stone', 'tex-water', 'tex-static']) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'color-btn square scan-item';
    btn.style.backgroundImage = `url(${thumbFor(id)})`;
    btn.addEventListener('click', () => selectInk(id, btn));
    tray.append(btn);
  }
  patternFor('tex-brick');
}

function buildGradients(): void {
  const tray = document.getElementById('gradPresets')!;
  for (const id of Object.keys(GRADIENTS)) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'color-btn square scan-item';
    const stops = GRADIENTS[id].join(', ');
    btn.style.background = `linear-gradient(90deg, ${stops})`;
    btn.addEventListener('click', () => {
      selectInk(id, btn);
      state.gradientPreset = id;
      state.gradientFrom = id;
      state.gradientTo = id;
      state.gradientDrag = true;
      (document.getElementById('gradToggle') as HTMLInputElement).checked = true;
      paintChips();
    });
    tray.append(btn);
  }
  document.getElementById('gradFrom')!.addEventListener('click', () => {
    state.gradientFrom = activeInkId();
    state.gradientPreset = null;
    paintChips();
    play('pop');
  });
  document.getElementById('gradTo')!.addEventListener('click', () => {
    state.gradientTo = activeInkId();
    state.gradientPreset = null;
    paintChips();
    play('pop');
  });
  paintChips();
}

function paintChips(): void {
  const from = document.getElementById('gradFrom') as HTMLButtonElement;
  const to = document.getElementById('gradTo') as HTMLButtonElement;
  from.style.background = chipBackground(state.gradientFrom);
  to.style.background = chipBackground(state.gradientTo);
}

function chipBackground(id: string): string {
  if (isHex(id)) return id;
  if (GRADIENTS[id]) return `linear-gradient(90deg, ${GRADIENTS[id].join(',')})`;
  if (id === 'rainbow') return 'linear-gradient(90deg, red, lime, blue)';
  if (id === 'sparkle') return '#FFE566';
  if (id === 'neon') return '#ffffff';
  return '#cccccc';
}

function buildGears(): void {
  const box = document.getElementById('gearBox')!;
  for (const gear of GEARS) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'gear-btn scan-item';
    btn.style.background = gear.color;
    btn.textContent = String(gear.teeth);
    btn.addEventListener('pointerdown', (event) => startGearDrag(event, gear.id, gear.color));
    btn.addEventListener('click', () => {
      assignGear(gear.id, state.spiro.nest);
      sync();
    });
    box.append(btn);
  }
}

function startGearDrag(event: PointerEvent, id: string, color: string): void {
  event.preventDefault();
  const ghost = document.getElementById('gearGhost')!;
  const startX = event.clientX;
  const startY = event.clientY;
  ghost.hidden = false;
  ghost.style.background = color;
  const move = (ev: PointerEvent) => {
    ghost.style.left = `${ev.clientX - 24}px`;
    ghost.style.top = `${ev.clientY - 24}px`;
  };
  const up = (ev: PointerEvent) => {
    ghost.hidden = true;
    window.removeEventListener('pointermove', move);
    window.removeEventListener('pointerup', up);
    const moved = Math.hypot(ev.clientX - startX, ev.clientY - startY);
    const pos = canvasToClientInverse(ev.clientX, ev.clientY);
    if (pos && moved > 8) {
      const center = gearCenter();
      const gear = gearById(id);
      const parent = gearById(state.spiro.gearId);
      if (center && parent && gear && gear.teeth < parent.teeth && Math.hypot(pos.x - center.x, pos.y - center.y) < center.r + 30) {
        assignGear(id, true);
      } else if (hitStator(pos.x, pos.y) || Math.hypot(pos.x - state.spiro.cx, pos.y - state.spiro.cy) < state.spiro.R + 40) {
        assignGear(id, false);
      }
    } else {
      assignGear(id, state.spiro.nest);
    }
    sync();
  };
  move(event);
  window.addEventListener('pointermove', move);
  window.addEventListener('pointerup', up);
}

function canvasToClientInverse(clientX: number, clientY: number): { x: number; y: number } | null {
  const stage = document.getElementById('view');
  if (!stage) return null;
  const rect = stage.getBoundingClientRect();
  if (clientX < rect.left || clientY < rect.top || clientX > rect.right || clientY > rect.bottom) return null;
  return {
    x: ((clientX - rect.left) * 960) / rect.width,
    y: ((clientY - rect.top) * 640) / rect.height,
  };
}

function bindTools(): void {
  document.querySelectorAll<HTMLButtonElement>('#toolBin .tool-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (btn.id === 'symBtn') {
        toggleSymmetry();
        return;
      }
      const tool = btn.dataset.tool as ToolId;
      selectTool(tool);
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-applicator]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.applicator = btn.dataset.applicator as Applicator;
      if (state.applicator === 'mist' || state.applicator === 'splatter') {
        state.tool = 'spray';
        if (state.applicator === 'mist' || state.applicator === 'splatter') play('rattle');
      } else state.tool = 'draw';
      play('clunk');
      sync();
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-shape]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.shape = btn.dataset.shape as ShapeKind;
      state.poly = [];
      play('clunk');
      sync();
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-eraser]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.eraserMode = btn.dataset.eraser as EraserMode;
      state.tool = 'eraser';
      play('clunk');
      sync();
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-sym]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.symmetry = btn.dataset.sym as SymmetryMode;
      play('clunk');
      sync();
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-drive]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.spiro.drive = btn.dataset.drive === 'auto' ? 'auto' : 'manual';
      play('clunk');
      sync();
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-stator]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.spiro.shape = btn.dataset.stator as StatorShape;
      play('clunk');
      sync();
    });
  });
  document.getElementById('nestBtn')!.addEventListener('click', () => {
    state.spiro.nest = !state.spiro.nest;
    play('clunk');
    sync();
  });
  document.getElementById('windBtn')!.addEventListener('click', () => {
    if (state.tool !== 'spiro') selectTool('spiro');
    if (!state.spiro.gearId && GEARS[0]) assignGear(GEARS[0].id, false);
    state.spiro.drive = 'auto';
    startMotor();
    sync();
  });
  document.getElementById('spiroReset')!.addEventListener('click', () => {
    resetKit();
    sync();
  });
  document.querySelectorAll<HTMLButtonElement>('.pip').forEach((btn) => {
    btn.addEventListener('click', () => setLevel(Number(btn.dataset.level)));
  });
  document.getElementById('undoBtn')!.addEventListener('click', doUndo);
  document.getElementById('clearBtn')!.addEventListener('click', () => {
    if (state.busy) return;
    startSqueegee();
  });
  document.querySelectorAll<HTMLButtonElement>('#rainbowDial .choice').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.rainbowMode = btn.dataset.rainbow === 'time' ? 'time' : 'distance';
      play('clunk');
      sync();
    });
  });
}

function bindSliders(): void {
  const level = document.getElementById('levelSlider') as HTMLInputElement;
  level.addEventListener('input', () => setLevel(Number(level.value)));
  const size = document.getElementById('brushSize') as HTMLInputElement;
  size.value = String(state.brushWidth);
  size.addEventListener('input', () => {
    state.brushWidth = Number(size.value);
  });
  const opacity = document.getElementById('opacity') as HTMLInputElement;
  opacity.addEventListener('input', () => {
    state.opacity = Number(opacity.value);
  });
  const scale = document.getElementById('stampScale') as HTMLInputElement;
  scale.addEventListener('input', () => {
    state.stampScale = Number(scale.value);
  });
  const rot = document.getElementById('stampRotate') as HTMLInputElement;
  rot.addEventListener('input', () => {
    state.stampRotation = Number(rot.value);
  });
  document.getElementById('flipH')!.addEventListener('click', () => {
    state.stampFlipH = !state.stampFlipH;
    play('clunk');
    sync();
  });
  document.getElementById('flipV')!.addEventListener('click', () => {
    state.stampFlipV = !state.stampFlipV;
    play('clunk');
    sync();
  });
  const grad = document.getElementById('gradToggle') as HTMLInputElement;
  grad.addEventListener('change', () => {
    state.gradientDrag = grad.checked;
  });
}

function bindConveyor(): void {
  document.getElementById('addBeltBtn')!.addEventListener('click', () => {
    if (isHex(state.ink) && state.conveyor.length < 8) {
      state.conveyor.push(state.ink);
      play('clunk');
      updateBelt(beltNow);
    }
  });
  document.getElementById('clearBeltBtn')!.addEventListener('click', () => {
    state.conveyor = [];
    play('vwoop');
    updateBelt(beltNow);
  });
  document.getElementById('beltMode')!.addEventListener('click', () => {
    state.beltMode = state.beltMode === 'ooze' ? 'snap' : 'ooze';
    play('clunk');
    sync();
  });
  const speed = document.getElementById('beltSpeed') as HTMLInputElement;
  speed.addEventListener('input', () => {
    state.beltSpeed = Number(speed.value);
  });
  document.querySelectorAll<HTMLButtonElement>('.belt-slot').forEach((slot) => {
    slot.addEventListener('click', () => {
      if (!slot.dataset.index) return;
      const index = Number(slot.dataset.index);
      if (index >= 0 && index < state.conveyor.length) {
        state.conveyor.splice(index, 1);
        play('pop');
        updateBelt(performance.now());
      }
    });
    slot.addEventListener('dragover', (event) => event.preventDefault());
    slot.addEventListener('drop', (event) => {
      event.preventDefault();
      const data = event.dataTransfer?.getData('text/plain') ?? '';
      if (!data.startsWith('ink:') || !isHex(data.slice(4))) return;
      const color = data.slice(4);
      const index = Number(slot.dataset.index ?? state.conveyor.length);
      if (state.conveyor.length >= 8) return;
      const at = Number.isFinite(index) ? Math.min(state.conveyor.length, Math.max(0, index)) : state.conveyor.length;
      state.conveyor.splice(at, 0, color);
      play('clunk');
      updateBelt(performance.now());
    });
  });
}

function bindExport(): void {
  const modal = document.getElementById('modalBg')!;
  document.getElementById('saveBtn')!.addEventListener('click', () => {
    play('clunk');
    modal.classList.add('open');
  });
  document.getElementById('closeModal')!.addEventListener('click', () => {
    play('clunk');
    modal.classList.remove('open');
  });
  document.getElementById('expPng')!.addEventListener('click', () => {
    void exportPng();
    modal.classList.remove('open');
  });
  document.getElementById('expVid')!.addEventListener('click', async () => {
    const btn = document.getElementById('expVid') as HTMLButtonElement;
    btn.disabled = true;
    btn.textContent = 'Rendering...';
    try {
      await exportGif();
    } finally {
      btn.disabled = false;
      btn.textContent = 'Movie';
      modal.classList.remove('open');
    }
  });
}

function bindSwitch(): void {
  document.getElementById('switchBtn')!.addEventListener('click', () => {
    play('clunk');
    state.switchOn = !state.switchOn;
    const quads = document.getElementById('quads')!;
    quads.innerHTML = '';
    if (scanTimer) window.clearInterval(scanTimer);
    document.querySelectorAll('.scan-focus').forEach((el) => el.classList.remove('scan-focus'));
    if (!state.switchOn) {
      sync();
      return;
    }
    const cells = state.level >= 3 ? 3 : 2;
    for (let y = 0; y < cells; y++) {
      for (let x = 0; x < cells; x++) {
        const cell = document.createElement('button');
        cell.type = 'button';
        cell.className = 'quadrant scan-item';
        cell.style.left = `${(x * 100) / cells}%`;
        cell.style.top = `${(y * 100) / cells}%`;
        cell.style.width = `${100 / cells}%`;
        cell.style.height = `${100 / cells}%`;
        cell.addEventListener('click', () => {
          tapCanvas(((x + 0.5) * 960) / cells, ((y + 0.5) * 640) / cells);
        });
        quads.append(cell);
      }
    }
    scanIndex = 0;
    scanTimer = window.setInterval(stepScan, 1500);
    stepScan();
    sync();
  });
}

function stepScan(): void {
  const items = [...document.querySelectorAll<HTMLElement>('.scan-item')].filter((el) => getComputedStyle(el).display !== 'none' && !el.hidden);
  if (!items.length) return;
  items.forEach((el) => el.classList.remove('scan-focus'));
  scanIndex = scanIndex % items.length;
  items[scanIndex].classList.add('scan-focus');
  scanIndex = (scanIndex + 1) % items.length;
}

function bindCutout(): void {
  const cutout = document.getElementById('cutout')!;
  bus.addEventListener('cutout', (event) => {
    const detail = (event as CustomEvent<{ url: string; x: number; y: number }>).detail;
    const img = cutout.querySelector('img')!;
    img.src = detail.url;
    const client = canvasToClient(detail.x, detail.y);
    cutout.hidden = false;
    cutout.style.left = `${client.x}px`;
    cutout.style.top = `${client.y}px`;
    selectTool('stamp');
    stampBank = 'custom';
    renderStampBank();
  });
  bus.addEventListener('stamps', () => renderCustomStamps());
  let dx = 0;
  let dy = 0;
  let originX = 0;
  let originY = 0;
  cutout.addEventListener('pointerdown', (event) => {
    const pointer = event as PointerEvent;
    originX = pointer.clientX;
    originY = pointer.clientY;
    dx = pointer.clientX - cutout.getBoundingClientRect().left;
    dy = pointer.clientY - cutout.getBoundingClientRect().top;
    cutout.setPointerCapture(pointer.pointerId);
  });
  cutout.addEventListener('pointermove', (event) => {
    const pointer = event as PointerEvent;
    if (!cutout.hasPointerCapture(pointer.pointerId)) return;
    cutout.style.left = `${pointer.clientX - dx}px`;
    cutout.style.top = `${pointer.clientY - dy}px`;
  });
  cutout.addEventListener('pointerup', (event) => {
    const moved = Math.hypot(event.clientX - originX, event.clientY - originY);
    cutout.style.visibility = 'hidden';
    const hit = document.elementFromPoint(event.clientX, event.clientY);
    cutout.style.visibility = '';
    if (moved < 10 || hit?.closest('#stampDrawer')) {
      cutout.hidden = true;
      play('clunk');
    }
  });
}

function renderStampBank(): void {
  const tabs = document.getElementById('stampTabs')!;
  tabs.innerHTML = '';
  for (const bank of [...STAMP_BANKS, { id: 'custom', label: 'My Cuts', items: [] }]) {
    const tab = document.createElement('button');
    tab.type = 'button';
    tab.className = `tray-tab scan-item${bank.id === stampBank ? ' active' : ''}`;
    tab.textContent = bank.label;
    tab.addEventListener('click', () => {
      stampBank = bank.id;
      play('clunk');
      renderStampBank();
    });
    tabs.append(tab);
  }
  const grid = document.getElementById('stampGrid')!;
  const custom = document.getElementById('customGrid')!;
  const showCustom = stampBank === 'custom';
  grid.style.display = showCustom ? 'none' : 'grid';
  custom.style.display = showCustom ? 'grid' : 'none';
  grid.innerHTML = '';
  if (!showCustom) {
    const bank = STAMP_BANKS.find((item) => item.id === stampBank) ?? STAMP_BANKS[0];
    for (const item of bank.items) {
      const el = document.createElement('button');
      el.type = 'button';
      el.className = `stamp-item scan-item${state.stampId === item ? ' selected' : ''}`;
      el.textContent = item.startsWith('vec:') ? vectorLabel(item) : item;
      el.addEventListener('click', () => {
        state.stampId = item;
        play('pop');
        renderStampBank();
      });
      grid.append(el);
    }
  }
  renderCustomStamps();
}

function vectorLabel(id: string): string {
  if (id.endsWith('star')) return '★';
  if (id.endsWith('heart')) return '♥';
  if (id.endsWith('triangle')) return '▲';
  if (id.endsWith('diamond')) return '◆';
  return '●';
}

function renderCustomStamps(): void {
  const grid = document.getElementById('customGrid');
  if (!grid) return;
  grid.innerHTML = '';
  customStamps.forEach((stamp, index) => {
    const el = document.createElement('button');
    el.type = 'button';
    el.className = `stamp-item scan-item${state.stampId === `custom:${index}` ? ' selected' : ''}`;
    el.style.backgroundImage = `url(${stamp.url})`;
    el.addEventListener('click', () => {
      state.stampId = `custom:${index}`;
      play('pop');
      renderCustomStamps();
    });
    grid.append(el);
  });
  for (let i = customStamps.length; i < 4; i++) {
    const empty = document.createElement('div');
    empty.className = 'stamp-item empty';
    empty.textContent = '+';
    grid.append(empty);
  }
}

function selectInk(id: string, el: HTMLElement): void {
  play('pop');
  state.liveArmed = false;
  state.ink = id;
  if (isHex(id)) {
    state.neonTint = id;
    if (id !== '#FFFFFF') state.sparkleTint = id === '#1A1A1A' ? '#FFE566' : id;
  }
  document.querySelectorAll('.color-btn').forEach((btn) => btn.classList.remove('selected'));
  el.classList.add('selected');
}

function selectTool(tool: ToolId): void {
  if (TOOL_LEVEL[tool] > state.level) return;
  play(tool === 'spray' ? 'rattle' : 'clunk');
  state.tool = tool;
  if (tool === 'draw' && (state.applicator === 'mist' || state.applicator === 'splatter')) state.applicator = 'marker';
  if (tool === 'spray' && state.applicator !== 'splatter') state.applicator = 'mist';
  sync();
}

function toggleSymmetry(): void {
  play('clunk');
  if (state.symmetry === 'off') {
    state.symmetry = '8';
    if (state.tool === 'spiro' || state.tool === 'bucket') state.tool = 'draw';
  } else state.symmetry = 'off';
  sync();
}

function setLevel(level: number): void {
  const next = Math.max(1, Math.min(4, Math.round(level))) as 1 | 2 | 3 | 4;
  if (next === state.level) return;
  state.level = next;
  saveLevel();
  document.body.dataset.level = String(next);
  (document.getElementById('levelSlider') as HTMLInputElement).value = String(next);
  play('clack');
  if (TOOL_LEVEL[state.tool] > next) state.tool = 'draw';
  if (next < 3 && state.symmetry !== 'off') state.symmetry = 'off';
  if (next < 3 && state.eraserMode === 'blackhole') state.eraserMode = 'scrub';
  if (next < 4 && (state.eraserMode === 'pixelate' || state.eraserMode === 'invert' || state.eraserMode === 'emboss')) state.eraserMode = 'scrub';
  if (next < 4) state.liveArmed = false;
  if (next < 4 && state.applicator === 'splatter') state.applicator = 'mist';
  document.body.classList.add('level-pop');
  window.setTimeout(() => document.body.classList.remove('level-pop'), 280);
  sync();
}

function sync(): void {
  document.querySelectorAll<HTMLButtonElement>('#toolBin .tool-btn').forEach((btn) => {
    const tool = btn.dataset.tool as ToolId | undefined;
    btn.classList.toggle('active', tool === state.tool || (btn.id === 'symBtn' && state.symmetry !== 'off'));
  });
  markChoices('[data-applicator]', state.applicator);
  markChoices('[data-shape]', state.shape);
  markChoices('[data-eraser]', state.eraserMode);
  markChoices('[data-sym]', state.symmetry);
  markChoices('[data-drive]', state.spiro.drive);
  markChoices('[data-stator]', state.spiro.shape);
  markChoices('[data-rainbow]', state.rainbowMode);
  document.getElementById('penDrawer')!.classList.toggle('open', state.tool === 'draw' && state.level >= 3);
  document.getElementById('sprayDrawer')!.classList.toggle('open', state.tool === 'spray');
  document.getElementById('shapesDrawer')!.classList.toggle('open', state.tool === 'shapes');
  document.getElementById('eraserDrawer')!.classList.toggle('open', state.tool === 'eraser');
  document.getElementById('stampDrawer')!.classList.toggle('open', state.tool === 'stamp');
  document.getElementById('symDrawer')!.classList.toggle('open', state.symmetry !== 'off');
  document.getElementById('spiroDrawer')!.classList.toggle('open', state.tool === 'spiro');
  document.getElementById('nestBtn')!.textContent = `Nest next gear: ${state.spiro.nest ? 'on' : 'off'}`;
  document.getElementById('beltMode')!.textContent = state.beltMode === 'ooze' ? 'OOZE' : 'SNAP';
  document.getElementById('flipH')!.classList.toggle('active', state.stampFlipH);
  document.getElementById('flipV')!.classList.toggle('active', state.stampFlipV);
  document.getElementById('switchBtn')!.textContent = state.switchOn ? 'Stop scan' : 'Switch';
  document.querySelectorAll<HTMLButtonElement>('.pip').forEach((pip) => {
    pip.classList.toggle('active', Number(pip.dataset.level) === state.level);
  });
}

function markChoices(selector: string, value: string): void {
  document.querySelectorAll<HTMLButtonElement>(selector).forEach((btn) => {
    const marker = btn.dataset.applicator || btn.dataset.shape || btn.dataset.eraser || btn.dataset.sym || btn.dataset.drive || btn.dataset.stator || btn.dataset.rainbow;
    btn.classList.toggle('active', marker === value);
  });
}

function doUndo(): void {
  if (state.busy) return;
  play('clunk');
  const btn = document.getElementById('undoBtn')!;
  btn.classList.add('winding');
  window.setTimeout(() => btn.classList.remove('winding'), 280);
  if (getPending()) {
    cancelPending();
    return;
  }
  undo();
}

function onKey(event: KeyboardEvent): void {
  if (event.code === 'Space' && state.switchOn) {
    event.preventDefault();
    play('pop');
    document.querySelector<HTMLElement>('.scan-focus')?.click();
  }
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
    event.preventDefault();
    doUndo();
  }
}

document.querySelectorAll<HTMLButtonElement>('#materialTabs .tray-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    play('clunk');
    document.querySelectorAll('#materialTabs .tray-tab').forEach((btn) => btn.classList.remove('active'));
    tab.classList.add('active');
    for (const id of ['tray-solids', 'tray-textures', 'tray-gradients', 'tray-live']) {
      document.getElementById(id)!.style.display = id === tab.dataset.target ? 'flex' : 'none';
    }
    state.liveArmed = tab.dataset.target === 'tray-live';
  });
});
