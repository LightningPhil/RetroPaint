import { unlockAudio } from './audio';
import { play } from './audio';
import { bus } from './bus';
import { isHex } from './color';
import { exportPng } from './export';
import { cancelPending, getPending } from './fill';
import { startSqueegee } from './effects';
import { undo } from './history';
import { GRADIENTS, glitterThumb, patternFor, thumbFor } from './materials';
import { activeInkId } from './materials';
import { assignGear, GEARS, hitStator, OUTER_CHOICES, resetKit, setInnerTeeth, setOuterTeeth, startMotor } from './spiro';
import { state } from './state';
import { STAMP_BANKS } from './stamps';
import { icon, labelIcon } from './icons';
import { finishPath } from './input';
import { setRingRadius } from './spiro';
import { cancelSelection, commitSelection, copySelection, cutSelection, deleteSelection, hasClipboard, hasSelection, pasteSelection, refreshTransparency } from './selection';
import type { Applicator, EraserMode, ShapeKind, StatorShape, SymmetryMode, ToolId } from './types';

const SOLIDS = ['#E53935', '#FDD835', '#1E88E5', '#43A047', '#1A1A1A', '#EF476F', '#06D6A0', '#118AB2', '#FFD166', '#9D4EDD', '#FF9F1C', '#FFFFFF'];

let stampBank = 'critters';
let beltNow = 0;
let openDrawer: string | null = null;

export function initUi(): void {
  buildSolids();
  buildTextures();
  buildGradients();
  buildBeltPicks();
  buildGears();
  renderStampBank();
  bindTools();
  bindSliders();
  bindConveyor();
  bindExport();
  bindSelection();
  decorateControls();
  bindLayout();
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
  const colours = document.createElement('div'); colours.className = 'solid-colours';
  const effects = document.createElement('div'); effects.className = 'ink-effects';
  tray.append(colours, effects);
  for (const color of SOLIDS) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'color-btn';
    btn.dataset.ink = color;
    btn.style.background = color;
    btn.draggable = true;
    btn.title = colourName(color);
    btn.setAttribute('aria-label', colourName(color));
    if (color === state.ink) btn.classList.add('selected');
    btn.addEventListener('click', () => selectInk(color, btn));
    btn.addEventListener('dragstart', (event) => event.dataTransfer?.setData('text/plain', `ink:${color}`));
    colours.append(btn);
  }
  addFx(effects, 'rainbow', 'linear-gradient(45deg, red, yellow, lime, cyan, magenta)');
  addFx(effects, 'neon', '#263047');
  addFx(effects, 'sparkle', 'url(' + glitterThumb() + ')');
}

function addFx(tray: HTMLElement, id: string, background: string): void {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'color-btn square';
  btn.dataset.ink = id;
  btn.style.background = background;
  const label = id === 'sparkle' ? 'Glitter' : id === 'neon' ? 'Neon' : 'Rainbow';
  btn.title = label + ' ink — pick a colour first to tint it';
  btn.setAttribute('aria-label', label + ' ink');
  btn.classList.add('ink-effect', 'ink-' + id);
  btn.innerHTML = '<span class="ink-sample" aria-hidden="true">' + (id === 'neon' ? '∿' : id === 'sparkle' ? '✦' : '🌈') + '</span><span class="ink-label">' + label + '</span>';
  btn.addEventListener('click', () => selectInk(id, btn));
  tray.append(btn);
}

function buildTextures(): void {
  const tray = document.getElementById('tray-textures')!;
  for (const id of ['tex-brick', 'tex-dots', 'tex-weave', 'tex-grass', 'tex-stone', 'tex-water', 'tex-static']) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'color-btn square';
    btn.dataset.ink = id;
    btn.title = id.replace('tex-', '').replace('grad-', '') + ' ink';
    btn.setAttribute('aria-label', btn.title);
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
    btn.className = 'color-btn square';
    btn.dataset.ink = id;
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

function buildBeltPicks(): void {
  const box = document.getElementById('beltPicks')!;
  for (const color of SOLIDS) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'belt-pick';
    btn.style.background = color;
    btn.dataset.color = color;
    btn.title = colourName(color);
    btn.setAttribute('aria-label', colourName(color) + ' for live ink');
    btn.addEventListener('click', () => {
      state.beltPick = color;
      play('pop');
      sync();
    });
    box.append(btn);
  }
}

function buildGears(): void {
  const outer = document.getElementById('outerChoices')!;
  for (const teeth of OUTER_CHOICES) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'choice';
    btn.dataset.outer = String(teeth);
    btn.innerHTML = '<span aria-hidden="true">⚙</span> ' + teeth;
    btn.setAttribute('aria-label', teeth + ' outer teeth');
    btn.addEventListener('click', () => {
      setOuterTeeth(teeth);
      sync();
    });
    outer.append(btn);
  }
  const box = document.getElementById('gearBox')!;
  for (const gear of GEARS) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'gear-btn';
    btn.dataset.gear = gear.id;
    btn.style.background = gear.color;
    btn.textContent = String(gear.teeth);
    btn.setAttribute('aria-label', gear.id + ' gear, ' + gear.teeth + ' teeth');
    btn.addEventListener('pointerdown', (event) => startGearDrag(event, gear.id, gear.color));
    btn.addEventListener('click', () => {
      assignGear(gear.id);
      sync();
    });
    box.append(btn);
  }
  document.getElementById('outerTeeth')!.addEventListener('change', (event) => {
    setOuterTeeth(Number((event.target as HTMLInputElement).value));
    sync();
  });
  document.getElementById('innerTeeth')!.addEventListener('change', (event) => {
    setInnerTeeth(Number((event.target as HTMLInputElement).value));
    sync();
  });
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
      if (hitStator(pos.x, pos.y) || Math.hypot(pos.x - state.spiro.cx, pos.y - state.spiro.cy) < state.spiro.R + 40) {
        assignGear(id);
      }
    } else {
      assignGear(id);
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
      const drawer = drawerFor(tool);
      openDrawer = openDrawer === drawer ? null : drawer;
      selectTool(tool);
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-applicator]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.applicator = btn.dataset.applicator as Applicator;
      if (state.applicator === 'mist' || state.applicator === 'splatter' || state.applicator === 'confetti') {
        state.sprayApplicator = state.applicator;
        state.tool = 'spray';
        if (state.applicator === 'mist' || state.applicator === 'splatter' || state.applicator === 'confetti') play('rattle');
      } else {
        state.brushApplicator = state.applicator;
        state.tool = 'draw';
      }
      openDrawer = null;
      play('clunk');
      sync();
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-shape]').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.shape = btn.dataset.shape as ShapeKind;
      state.poly = [];
      openDrawer = null;
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
      openDrawer = null;
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
  document.getElementById('windBtn')!.addEventListener('click', () => {
    if (state.tool !== 'spiro') selectTool('spiro');
    if (!state.spiro.gearId) setInnerTeeth(36, 'red');
    state.spiro.drive = 'auto';
    startMotor();
    sync();
  });
  document.getElementById('spiroReset')!.addEventListener('click', () => {
    resetKit();
    sync();
  });
  document.getElementById('undoBtn')!.addEventListener('click', doUndo);
  document.getElementById('clearBtn')!.addEventListener('click', () => {
    if (state.busy) return;
    commitSelection();
    state.poly = [];
    startSqueegee();
  });
}

function bindSliders(): void {
  const size = document.getElementById('brushSize') as HTMLInputElement;
  size.value = String(state.brushWidth);
  size.addEventListener('input', () => {
    if (state.tool === 'stamp') {
      state.stampScale = Number(size.value);
      (document.getElementById('stampScale') as HTMLInputElement).value = size.value;
    } else state.brushWidth = Number(size.value);
  });
  const opacity = document.getElementById('opacity') as HTMLInputElement;
  opacity.addEventListener('input', () => {
    state.opacity = Number(opacity.value);
  });
  const scale = document.getElementById('stampScale') as HTMLInputElement;
  scale.addEventListener('input', () => {
    state.stampScale = Number(scale.value);
    if (state.tool === 'stamp') size.value = scale.value;
  });
  document.getElementById('spinMode')!.addEventListener('click', () => {
    state.stampSpin = state.stampSpin === 'auto' ? 'fixed' : 'auto';
    play('clunk');
    sync();
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
  const ring = document.getElementById('ringSize') as HTMLInputElement;
  ring.addEventListener('input', () => setRingRadius(Number(ring.value)));
  const grad = document.getElementById('gradToggle') as HTMLInputElement;
  grad.addEventListener('change', () => {
    state.gradientDrag = grad.checked;
  });
}

function bindConveyor(): void {
  document.getElementById('addBeltBtn')!.addEventListener('click', () => {
    if (isHex(state.beltPick) && state.conveyor.length < 8) {
      state.conveyor.push(state.beltPick);
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
  document.getElementById('saveBtn')!.addEventListener('click', () => {
    play('clunk');
    commitSelection();
    exportPng();
  });
}

function bindLayout(): void {
  const watch = ['canvasSlot', 'toolBin', 'topBar', 'bottomTray']
    .map((id) => document.getElementById(id))
    .filter((el): el is HTMLElement => !!el);
  if (typeof ResizeObserver !== 'undefined') {
    const observer = new ResizeObserver(() => layoutStage());
    watch.forEach((el) => observer.observe(el));
  }
  window.addEventListener('resize', layoutStage);
  layoutStage();
}

function layoutStage(): void {
  const slot = document.getElementById('canvasSlot');
  const stage = document.getElementById('stage');
  const bin = document.getElementById('toolBin');
  if (!slot || !stage || !bin) return;
  const rect = slot.getBoundingClientRect();
  const uiScale = Number(getComputedStyle(document.documentElement).getPropertyValue('--ui-scale')) || 1;
  const pad = 12 * uiScale;
  const availW = Math.max(80, rect.width - pad * 2);
  const availH = Math.max(80, rect.height - pad * 2);
  const aspect = 960 / 640;
  let width = availW;
  let height = width / aspect;
  if (height > availH) {
    height = availH;
    width = height * aspect;
  }
  stage.style.width = `${Math.floor(width)}px`;
  stage.style.height = `${Math.floor(height)}px`;
  stage.style.left = `${Math.floor((rect.width - width) / 2)}px`;
  stage.style.top = `${Math.floor((rect.height - height) / 2)}px`;
  const tool = bin.getBoundingClientRect();
  document.querySelectorAll<HTMLElement>('.drawer').forEach((drawer) => {
    drawer.style.zoom = '1';
    const portrait = tool.width > tool.height * 2;
    const gap = 12 * uiScale;
    const anchorX = portrait ? gap : tool.right + gap;
    const roomW = window.innerWidth - anchorX - gap;
    const roomH = window.innerHeight - gap * 2;
    const width = drawer.offsetWidth || (drawer.id === 'stampDrawer' ? 470 : drawer.id === 'spiroDrawer' ? 500 : 360);
    const height = drawer.offsetHeight || 360;
    const scale = Math.max(0.4, Math.min(uiScale, roomW / width, roomH / height));
    const anchorY = portrait ? tool.bottom + gap : tool.top;
    drawer.style.zoom = String(scale);
    drawer.style.left = Math.round((portrait ? (window.innerWidth - width * scale) / 2 : anchorX) / scale) + 'px';
    drawer.style.top = Math.round(Math.max(gap, Math.min(anchorY, window.innerHeight - height * scale - gap)) / scale) + 'px';
  });
}

function bindSelection(): void {
  document.querySelectorAll<HTMLButtonElement>('[data-select]').forEach(btn => btn.addEventListener('click', () => {
    state.selectionMode = btn.dataset.select as 'rect' | 'lasso';
    commitSelection(); openDrawer = null; sync();
  }));
  const transparent = document.getElementById('transparentSelection') as HTMLInputElement;
  transparent.addEventListener('change', () => { state.transparentSelection = transparent.checked; refreshTransparency(); });
  const actions: Record<string, () => void> = {
    copySelection, cutSelection, pasteSelection, doneSelection: commitSelection, cancelSelection,
  };
  for (const [id, action] of Object.entries(actions)) document.getElementById(id)!.addEventListener('click', () => {
    action(); play('clunk'); sync();
  });
  bus.addEventListener('selection', updateSelectionButtons);
  document.getElementById('finishPath')!.addEventListener('click', () => { finishPath(); openDrawer = null; sync(); });
  updateSelectionButtons();
}
function updateSelectionButtons(): void {
  for (const id of ['copySelection', 'cutSelection', 'doneSelection', 'cancelSelection']) {
    (document.getElementById(id) as HTMLButtonElement).disabled = !hasSelection();
  }
  (document.getElementById('pasteSelection') as HTMLButtonElement).disabled = !hasClipboard();
  document.getElementById('selectionQuick')?.classList.toggle('visible', state.tool === 'scissors' && (hasSelection() || hasClipboard()));
  document.querySelectorAll<HTMLButtonElement>('[data-selection-action]').forEach(btn => {
    btn.disabled = btn.dataset.selectionAction === 'paste' ? !hasClipboard() : !hasSelection();
  });
}

function renderStampBank(): void {
  const tabs = document.getElementById('stampTabs')!;
  tabs.innerHTML = '';
  for (const bank of STAMP_BANKS) {
    const tab = document.createElement('button');
    tab.type = 'button';
    tab.className = `tray-tab${bank.id === stampBank ? ' active' : ''}`;
    tab.textContent = bank.label;
    tab.addEventListener('click', () => {
      stampBank = bank.id;
      play('clunk');
      renderStampBank();
    });
    tabs.append(tab);
  }
  const grid = document.getElementById('stampGrid')!;
  grid.style.display = 'grid';
  grid.innerHTML = '';
  {
    const bank = STAMP_BANKS.find((item) => item.id === stampBank) ?? STAMP_BANKS[0];
    for (const item of bank.items) {
      const el = document.createElement('button');
      el.type = 'button';
      el.className = `stamp-item${state.stampId === item ? ' selected' : ''}`;
      el.textContent = item.startsWith('vec:') ? vectorLabel(item) : item;
      el.setAttribute('aria-label', 'Stamp ' + (item.startsWith('vec:') ? item.slice(4) : item));
      el.addEventListener('click', () => {
        state.stampId = item;
        openDrawer = null;
        sync();
        play('pop');
        renderStampBank();
      });
      grid.append(el);
    }
  }
}

function vectorLabel(id: string): string {
  if (id.endsWith('star')) return '★';
  if (id.endsWith('heart')) return '♥';
  if (id.endsWith('triangle')) return '▲';
  if (id.endsWith('diamond')) return '◆';
  return '●';
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
  const glitter = document.querySelector<HTMLElement>('[data-ink="sparkle"]');
  if (glitter) glitter.style.backgroundImage = 'url(' + glitterThumb() + ')';
  document.documentElement.style.setProperty('--neon-tint', state.neonTint);
  updatePathControls();
}

function selectTool(tool: ToolId): void {
  play(tool === 'spray' ? 'rattle' : 'clunk');
  if (state.tool !== tool) { commitSelection(); state.poly = []; }
  state.tool = tool;
  if (tool === 'draw' || tool === 'shapes' || tool === 'spiro') state.applicator = state.brushApplicator;
  if (tool === 'spray') state.applicator = state.sprayApplicator;
  sync();
}

function toggleSymmetry(): void {
  play('clunk');
  openDrawer = openDrawer === 'symDrawer' ? null : 'symDrawer';
  sync();
}
function drawerFor(tool: ToolId): string | null {
  return ({ draw: 'penDrawer', spray: 'sprayDrawer', shapes: 'shapesDrawer', eraser: 'eraserDrawer', stamp: 'stampDrawer', spiro: 'spiroDrawer', scissors: 'selectionDrawer', sponge: null, bucket: null })[tool];
}

function sync(): void {
  const size = document.getElementById('brushSize') as HTMLInputElement;
  const stamp = state.tool === 'stamp';
  size.min = stamp ? '0.4' : '4'; size.max = stamp ? '2.6' : '48'; size.step = stamp ? '0.1' : '1';
  size.value = String(stamp ? state.stampScale : state.brushWidth);
  size.disabled = state.tool === 'scissors' || state.tool === 'bucket';
  (document.getElementById('opacity') as HTMLInputElement).disabled = state.tool === 'scissors';
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
  document.querySelectorAll<HTMLElement>('.drawer').forEach(drawer => drawer.classList.toggle('open', drawer.id === openDrawer));
  document.querySelectorAll<HTMLButtonElement>('[data-select]').forEach(btn => btn.classList.toggle('active', btn.dataset.select === state.selectionMode));
  updateSelectionButtons();
  updatePathControls();
  layoutStage();
  labelIcon(document.getElementById('beltMode')!, state.beltMode === 'ooze' ? 'blend' : 'pixelate', state.beltMode === 'ooze' ? 'Blend' : 'Jump');
  document.getElementById('flipH')!.classList.toggle('active', state.stampFlipH);
  document.getElementById('flipV')!.classList.toggle('active', state.stampFlipV);
  const spin = document.getElementById('spinMode')!;
  labelIcon(spin, 'rotate', state.stampSpin === 'auto' ? 'Random turns' : 'Keep upright');
  spin.classList.toggle('active', state.stampSpin === 'auto');
  document.querySelectorAll<HTMLButtonElement>('.belt-pick').forEach((btn) => {
    btn.classList.toggle('picked', btn.dataset.color === state.beltPick);
  });
  document.querySelectorAll<HTMLButtonElement>('[data-outer]').forEach((btn) => {
    btn.classList.toggle('active', Number(btn.dataset.outer) === state.spiro.outerTeeth);
  });
  document.querySelectorAll<HTMLButtonElement>('#gearBox .gear-btn').forEach((btn) => {
    const gear = GEARS.find((item) => item.id === btn.dataset.gear);
    btn.classList.toggle('picked', !!gear && gear.id === state.spiro.gearId && gear.teeth === state.spiro.innerTeeth);
  });
  setNumber('outerTeeth', state.spiro.outerTeeth);
  setNumber('innerTeeth', state.spiro.innerTeeth);
  setNumber('ringSize', state.spiro.R);
  const gradTab = document.querySelector<HTMLButtonElement>('[data-target="tray-gradients"]');
  if (gradTab) gradTab.hidden = state.tool !== 'bucket';
  if (state.tool !== 'bucket') {
    state.gradientDrag = false;
    const toggle = document.getElementById('gradToggle') as HTMLInputElement | null;
    if (toggle) toggle.checked = false;
    if (state.ink.startsWith('grad-')) state.ink = isHex(state.neonTint) ? state.neonTint : '#E53935';
    document.querySelectorAll<HTMLElement>('.color-btn').forEach((btn) => {
      btn.classList.toggle('selected', btn.dataset.ink === state.ink);
    });
    const panel = document.getElementById('tray-gradients');
    if (panel && panel.style.display === 'flex') showTray('tray-solids');
  }
}

function setNumber(id: string, value: number): void {
  const el = document.getElementById(id) as HTMLInputElement | null;
  if (el && document.activeElement !== el) el.value = String(value);
}

function markChoices(selector: string, value: string): void {
  document.querySelectorAll<HTMLButtonElement>(selector).forEach((btn) => {
    const marker = btn.dataset.applicator || btn.dataset.shape || btn.dataset.eraser || btn.dataset.sym || btn.dataset.drive || btn.dataset.stator || btn.dataset.rainbow;
    btn.classList.toggle('active', marker === value);
    btn.setAttribute('aria-pressed', String(marker === value));
  });
}

function doUndo(): void {
  if (state.busy) return;
  if (hasSelection()) { cancelSelection(); return; }
  if (state.poly.length) { state.poly.pop(); return; }
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
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return;
  const key = event.key.toLowerCase();
  if (event.ctrlKey || event.metaKey) {
    if (key === 'z') { event.preventDefault(); doUndo(); }
    else if (key === 'c' && hasSelection()) { event.preventDefault(); copySelection(); }
    else if (key === 'x' && hasSelection()) { event.preventDefault(); cutSelection(); }
    else if (key === 'v' && hasClipboard()) { event.preventDefault(); selectTool('scissors'); pasteSelection(); }
    return;
  }
  if (key === 'escape') { cancelSelection(); state.poly = []; cancelPending(); openDrawer = null; sync(); }
  if (key === 'enter' && !(event.target instanceof HTMLButtonElement)) { commitSelection(); finishPath(); }
  if (key === 'delete' || key === 'backspace') {
    if (hasSelection()) { event.preventDefault(); deleteSelection(); }
    else if (state.poly.length) { event.preventDefault(); state.poly.pop(); }
  }
}

function showTray(id: string): void {
  document.querySelectorAll('#materialTabs .tray-tab').forEach((btn) => {
    btn.classList.toggle('active', (btn as HTMLButtonElement).dataset.target === id);
  });
  for (const panel of ['tray-solids', 'tray-textures', 'tray-gradients', 'tray-live']) {
    document.getElementById(panel)!.style.display = panel === id ? 'flex' : 'none';
  }
  state.liveArmed = id === 'tray-live';
}

document.querySelectorAll<HTMLButtonElement>('#materialTabs .tray-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    if (tab.hidden) return;
    play('clunk');
    showTray(tab.dataset.target ?? 'tray-solids');
  });
});

function colourName(color: string): string {
  return ['Red', 'Yellow', 'Blue', 'Green', 'Black', 'Pink', 'Mint', 'Teal', 'Gold', 'Purple', 'Orange', 'White'][SOLIDS.indexOf(color)] ?? color;
}
function updatePathControls(): void {
  document.getElementById('finishQuick')!.hidden = state.tool !== 'shapes' || !['poly', 'spline'].includes(state.shape);
}
function decorateControls(): void {
  for (const attribute of ['applicator', 'shape', 'eraser', 'sym', 'drive', 'stator', 'select']) {
    document.querySelectorAll<HTMLElement>('[data-' + attribute + ']').forEach(btn => labelIcon(btn, btn.dataset[attribute]!));
  }
  const map: Record<string, string> = { undoBtn: 'undo', clearBtn: 'clear', saveBtn: 'save', copySelection: 'copy', cutSelection: 'cut', pasteSelection: 'paste', doneSelection: 'done', cancelSelection: 'close', finishPath: 'done', flipH: 'flipH', flipV: 'flipV', spiroReset: 'undo', windBtn: 'wind', addBeltBtn: 'plus', clearBeltBtn: 'clear' };
  for (const [id, name] of Object.entries(map)) labelIcon(document.getElementById(id)!, name);
  document.querySelectorAll<HTMLElement>('.drawer').forEach(drawer => {
    drawer.setAttribute('role', 'region');
    drawer.setAttribute('aria-label', drawer.querySelector('strong')?.textContent ?? 'Tool options');
    const close = document.createElement('button'); close.type = 'button'; close.className = 'drawer-close';
    close.innerHTML = icon('close'); close.setAttribute('aria-label', 'Close options');
    close.addEventListener('click', () => { openDrawer = null; sync(); }); drawer.prepend(close);
  });
  const quick = document.createElement('div'); quick.id = 'selectionQuick';
  const actions: Record<string, () => void> = { copy: copySelection, cut: cutSelection, paste: pasteSelection, done: commitSelection, close: cancelSelection };
  const labels: Record<string, string> = { copy: 'Copy', cut: 'Cut', paste: 'Paste', done: 'Place', close: 'Cancel' };
  for (const [name, action] of Object.entries(actions)) {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'choice'; button.dataset.selectionAction = name;
    labelIcon(button, name, labels[name]); button.addEventListener('click', action); quick.append(button);
  }
  document.getElementById('canvasSlot')!.append(quick);
  const finish = document.createElement('button'); finish.id = 'finishQuick'; finish.type = 'button'; finish.className = 'choice';
  labelIcon(finish, 'done', 'Finish path'); finish.addEventListener('click', () => finishPath());
  document.getElementById('canvasSlot')!.append(finish);
  document.getElementById('view')!.addEventListener('pointerdown', () => { if (openDrawer) { openDrawer = null; sync(); } });
  document.querySelectorAll<HTMLButtonElement>('.belt-slot').forEach((button, i) => button.setAttribute('aria-label', 'Remove live ink colour ' + (i + 1)));
}
