import { bindClearConfirmation } from './clear-confirmation';
import { bindColourWheel } from './colour-wheel';
import { initPaperView } from './paper-view';
import { sliceCount } from './symmetry-mask';
import { unlockAudio } from './audio';
import { play } from './audio';
import { bus } from './bus';
import { isHex, mixHex, neonColor } from './color';
import { exportPng } from './export';
import { cancelPending, getPending } from './fill';
import { startSqueegee } from './effects';
import { canRedo, redo, undo } from './history';
import { GRADIENTS, glitterThumb, patternFor, thumbFor } from './materials';
import { activeInkId } from './materials';
import { assignGear, GEARS, hitStator, OUTER_CHOICES, resetKit, setInnerTeeth, setOuterTeeth, startMotor } from './spiro';
import { state } from './state';
import { STAMP_BANKS } from './stamps';
import { icon, labelIcon } from './icons';
import { finishPath } from './input';
import { setRingRadius } from './spiro';
import { cancelSelection, commitSelection, copySelection, cutSelection, deleteSelection, flipSelection, hasClipboard, hasSelection, invertSelection, moveSelection,pasteSelection, refreshTransparency, rotateSelection, selectAll } from './selection';
import type { Applicator, EraserMode, ShapeKind, StatorShape, SymmetryMode, ToolId } from './types';
import { H, W, view, ui } from './canvas';
import { displayFrame } from './document-frame';
import { bindEditor, editable, message, pasteExternal, refreshImageFields, requestOpen, settle, updateLayersUi } from './editor';
import { bindText, cancelText, hasText, placeText } from './text-tool';
import { printImage } from './export';
import { motorOn } from './spiro';
import { initAdvancedMode } from './advanced-mode';
import { initSuperResolution } from './super-resolution-ui';
import { duplicateObjects, hasObjectSelection, moveObjects } from './objects';
import { initObjectUi } from './object-ui';
import { decorateToolArtwork } from './tool-art';
import { initPreferencesUi } from './preferences-ui';
import { initShortcutsUi } from './shortcuts-ui';
import { initWorkspaceUi } from './workspace-ui';
import { initRecoveryUi } from './recovery-ui';
import { updateBrushPreviews } from './brush-previews';
import { initAccessibleTabs } from './accessible-tabs';
import { initCadLaunch } from './cad-launch';

const SOLIDS = ['#E53935', '#FDD835', '#1E88E5', '#43A047', '#1A1A1A', '#EF476F', '#06D6A0', '#118AB2', '#FFD166', '#9D4EDD', '#FF9F1C', '#FFFFFF'];

let stampBank = 'critters';
let beltNow = 0;
let openDrawer: string | null = null;
const phoneLayout = matchMedia('(max-width: 600px), (max-height: 500px) and (max-width: 1000px)');

function closePalette(): void {
  document.getElementById('bottomTray')!.classList.remove('palette-open');
  document.getElementById('paletteToggle')!.setAttribute('aria-expanded', 'false');
}

function updateInkPreview(): void {
  const selected = document.querySelector<HTMLElement>('.color-btn.selected');
  const preview = document.getElementById('currentInk')!;
  document.documentElement.style.setProperty('--paint-ink',isHex(state.ink)?state.ink:state.ink==='neon'?state.neonTint:state.ink==='sparkle'?state.sparkleTint:'#bb79db');
  preview.style.background = state.liveArmed
    ? `linear-gradient(135deg,${(state.conveyor.length > 1 ? state.conveyor : ['#ef476f','#ffd166','#06d6a0']).join(',')})`
    : selected?.style.background || chipBackground(activeInkId());
  preview.innerHTML = state.liveArmed || selected?.id === 'colourWheelBtn' ? '' : selected?.querySelector('.ink-sample')?.outerHTML || '';
  updateBrushPreviews();
}

function bindMobilePalette(): void {
  const tray = document.getElementById('bottomTray')!;
  const toggle = document.getElementById('paletteToggle')!;
  toggle.addEventListener('click', () => {
    const open = !tray.classList.contains('palette-open');
    openDrawer = null;
    sync();
    tray.classList.toggle('palette-open', open);
    toggle.setAttribute('aria-expanded', String(open));
  });
  document.getElementById('toolBin')!.addEventListener('click', closePalette);
  document.getElementById('view')!.addEventListener('pointerdown', closePalette);
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !document.querySelector('dialog[open]') && tray.classList.contains('palette-open')) {
      closePalette(); toggle.focus();
    }
  });
  phoneLayout.addEventListener('change', closePalette);
  updateInkPreview();
}

function updateDrawerSettings(drawer: HTMLElement): void {
  const button = drawer.querySelector<HTMLButtonElement>('.drawer-settings');
  if (!button) return;
  const secondary = drawer.classList.contains('settings-open');
  const stamps = drawer.id === 'stampDrawer';
  button.innerHTML = icon(secondary ? 'back' : 'settings') + `<span>${secondary ? 'Back' : 'More'}</span>`;
  button.setAttribute('aria-pressed', String(secondary));
  button.setAttribute('aria-label', secondary ? (stamps ? 'Back to stamps' : 'Back to Spiro') : (stamps ? 'Stamp size and turn' : 'Spiro ring options'));
  drawer.querySelector('strong')!.textContent = phoneLayout.matches && secondary
    ? (stamps ? 'Size & turn' : 'Ring & gears')
    : (stamps ? 'Stamps' : 'Spiro kit');
}

function bindDrawerSettings(): void {
  for (const id of ['stampDrawer', 'spiroDrawer']) {
    const drawer = document.getElementById(id)!;
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'drawer-settings';
    drawer.append(button);
    button.addEventListener('click', () => {
      drawer.classList.toggle('settings-open');
      updateDrawerSettings(drawer); layoutStage();
    });
    updateDrawerSettings(drawer);
  }
  phoneLayout.addEventListener('change', () => {
    document.querySelectorAll<HTMLElement>('.settings-open').forEach(drawer => {
      drawer.classList.remove('settings-open'); updateDrawerSettings(drawer);
    });
  });
}

export function initUi(): void {
  foldExtraChoices('#penDrawer', '[data-applicator]', 5, 'Classic brushes');
  foldExtraChoices('#shapesDrawer', '[data-shape]', 5, 'More shapes');
  foldSelectionEdits();
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
  decorateToolArtwork();
  bindEditor();
  initAdvancedMode();
  initSuperResolution();
  bindText();
  initObjectUi();
  bindPaintExtras();
  bindDrawerSettings();
  bindMobilePalette();
  bindLayout();
  initPaperView(phoneLayout);
  initPreferencesUi();
  initShortcutsUi();
  initWorkspaceUi();
  initRecoveryUi();
  initCadLaunch();
  initAccessibleTabs();
  sync();
  document.addEventListener('pointerdown', () => unlockAudio());
  document.addEventListener('keydown', onKey);
}

function foldExtraChoices(drawerId: string, selector: string, keep: number, label: string): void {
  const drawer = document.querySelector<HTMLElement>(drawerId)!, buttons = [...drawer.querySelectorAll<HTMLElement>(selector)];
  const details = document.createElement('details'); details.className = 'extra-choices';
  const summary = document.createElement('summary'); summary.textContent = label;
  const row = document.createElement('div'); row.className = 'row'; buttons.slice(keep).forEach(button => row.append(button));
  details.append(summary, row); drawer.querySelector('.row')!.after(details);
  if (drawer.id === 'shapesDrawer') {
    summary.textContent = 'More shapes & fill';
    const styles = drawer.querySelector('.compact-fields'); if (styles) summary.after(styles);
  }
  details.addEventListener('toggle', layoutStage);
}
function foldSelectionEdits(): void {
  const drawer = document.getElementById('selectionDrawer')!, actions = drawer.querySelector('.selection-actions')!;
  const details = document.createElement('details'); details.className = 'extra-choices';
  const summary = document.createElement('summary'); summary.textContent = 'More edits & transforms';
  const row = document.createElement('div'); row.className = 'row selection-actions';
  for (const id of ['selectAll', 'invertSelection', 'deleteSelection']) row.append(document.getElementById(id)!);
  const transforms = drawer.querySelector('.selection-transforms')!, hint = transforms.nextElementSibling!;
  details.append(summary, row, transforms, hint); actions.after(details); details.addEventListener('toggle', layoutStage);
}

let beltSlots: HTMLButtonElement[] | null = null;
let beltSignature = '';
export function updateBelt(now: number): void {
  beltNow = now;
  const slots = beltSlots ??= [...document.querySelectorAll<HTMLButtonElement>('.belt-slot')];
  const colors = state.conveyor;
  const shift = colors.length ? Math.floor(now * state.beltSpeed * 0.002) : 0;
  const signature = colors.join(',') + ':' + (colors.length ? shift % colors.length : 0);
  if (signature === beltSignature) return;
  beltSignature = signature;
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
  const wheel = document.createElement('button');
  wheel.type = 'button'; wheel.id = 'colourWheelBtn';
  wheel.className = 'color-btn square ink-effect colour-wheel-btn';
  wheel.title = 'Choose any colour';
  wheel.setAttribute('aria-label', 'Colour wheel');
  wheel.setAttribute('aria-haspopup', 'dialog');
  wheel.style.background = state.neonTint;
  wheel.innerHTML = '<span class="wheel-icon" aria-hidden="true"></span><span class="ink-label">Wheel</span>';
  effects.append(wheel);
  bindColourWheel(wheel, () => isHex(state.ink) ? state.ink : state.neonTint, hex => {
    wheel.dataset.ink = hex; wheel.style.background = hex;
    selectInk(hex, wheel);
  });
  wheel.draggable = true;
  wheel.addEventListener('dragstart', event => event.dataTransfer?.setData('text/plain', `ink:${wheel.dataset.ink || state.neonTint}`));
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
  if (event.button !== 0) return;
  event.preventDefault();
  const target = event.currentTarget as HTMLElement;
  target.setPointerCapture(event.pointerId);
  const ghost = document.getElementById('gearGhost')!;
  const startX = event.clientX;
  const startY = event.clientY;
  ghost.hidden = false;
  ghost.style.background = color;
  const move = (ev: PointerEvent) => {
    if (ev.pointerId !== event.pointerId) return;
    ghost.style.left = `${ev.clientX - 24}px`;
    ghost.style.top = `${ev.clientY - 24}px`;
  };
  const cleanup = () => {
    ghost.hidden = true;
    window.removeEventListener('pointermove', move);
    window.removeEventListener('pointerup', up);
    window.removeEventListener('pointercancel', cancel);
    window.removeEventListener('blur', cleanup);
    target.removeEventListener('lostpointercapture', cleanup);
  };
  const cancel = (ev: PointerEvent) => { if (ev.pointerId === event.pointerId) cleanup(); };
  const up = (ev: PointerEvent) => {
    if (ev.pointerId !== event.pointerId) return;
    cleanup();
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
  window.addEventListener('pointercancel', cancel);
  window.addEventListener('blur', cleanup);
  target.addEventListener('lostpointercapture', cleanup);
}

function canvasToClientInverse(clientX: number, clientY: number): { x: number; y: number } | null {
  const stage = document.getElementById('view');
  if (!stage) return null;
  const rect = stage.getBoundingClientRect();
  if (clientX < rect.left || clientY < rect.top || clientX > rect.right || clientY > rect.bottom) return null;
  return {
    x: ((clientX - rect.left) * W) / rect.width,
    y: ((clientY - rect.top) * H) / rect.height,
  };
}

function bindTools(): void {
  document.querySelectorAll<HTMLButtonElement>('#toolBin [data-tool], #symBtn').forEach((btn) => {
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
      if (state.applicator === 'pencil') { state.brushWidth = 1; (document.getElementById('brushSize') as HTMLInputElement).value = '1'; }
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
      commitSelection();
      state.symmetry = btn.dataset.sym as SymmetryMode;
      state.symmetrySlice %= sliceCount();
      state.choosingSlice = state.symmetryMask && state.symmetry !== 'off';
      openDrawer = null;
      play('clunk');
      sync();
    });
  });
  const maskToggle = document.getElementById('symmetryMask') as HTMLButtonElement;
  maskToggle.addEventListener('click', () => {
    commitSelection();
    state.symmetryMask = !state.symmetryMask;
    state.choosingSlice = state.symmetryMask;
    openDrawer = null; sync();
  });
  bus.addEventListener('symmetry-mask', sync);
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
  bindClearConfirmation(document.getElementById('clearBtn') as HTMLButtonElement, () => {
    if (!editable()) return;
    settle();
    startSqueegee();
  }, undefined, () => !state.busy && !motorOn());
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
    if (!editable()) return;
    settle();
    void exportPng().catch(error=>message(error instanceof Error?error.message:String(error)));
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
  window.visualViewport?.addEventListener('resize', layoutStage);
  document.addEventListener('canvas-size', layoutStage);
  document.addEventListener('document-frame', layoutStage);
  bus.addEventListener('layer-panel', layoutStage);
  bus.addEventListener('photo-panel', layoutStage);
  layoutStage();
}

function bindPaintExtras(): void {
  const studio = document.getElementById('studioBtn')!;
  studio.addEventListener('click', () => { openDrawer = openDrawer === 'studioDrawer' ? null : 'studioDrawer'; refreshImageFields(); updateLayersUi(); sync(); });
  document.querySelectorAll<HTMLButtonElement>('[data-studio]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll<HTMLButtonElement>('[data-studio]').forEach(tab => { tab.classList.toggle('active', tab === button); tab.setAttribute('aria-selected', String(tab === button)); });
    document.querySelectorAll<HTMLElement>('[data-studio-panel]').forEach(panel => { panel.hidden = panel.dataset.studioPanel !== button.dataset.studio; });
    refreshImageFields(); updateLayersUi(); layoutStage();
  }));
  for (const [id, key] of [['shapeOutline', 'shapeOutline'], ['shapeFill', 'shapeFill']] as const) {
    (document.getElementById(id) as HTMLSelectElement).addEventListener('change', event => { state[key] = (event.target as HTMLSelectElement).value as never; });
  }
  (document.getElementById('secondaryColour') as HTMLInputElement).addEventListener('input', event => { state.secondaryInk = (event.target as HTMLInputElement).value; });
  document.getElementById('swapColours')!.addEventListener('click', () => {
    const primary = isHex(state.ink) ? state.ink : state.neonTint;
    chooseInk(state.secondaryInk); state.secondaryInk = primary; (document.getElementById('secondaryColour') as HTMLInputElement).value = primary;
  });
  bus.addEventListener('pick-colour', event => {
    const detail = (event as CustomEvent<{ colour: string; secondary: boolean }>).detail;
    if (detail.secondary) { state.secondaryInk = detail.colour; (document.getElementById('secondaryColour') as HTMLInputElement).value = detail.colour; }
    else { chooseInk(detail.colour); selectTool('draw'); }
    message(`${detail.secondary ? 'Second colour' : 'Ink'}: ${detail.colour.toUpperCase()}`);
  });
  bus.addEventListener('layers', () => { updateLayersUi(); layoutStage(); });
  bus.addEventListener('selection', refreshImageFields);
  bus.addEventListener('history', () => { (document.getElementById('redoBtn') as HTMLButtonElement).disabled = !canRedo(); });
  (document.getElementById('redoBtn') as HTMLButtonElement).disabled = !canRedo();
  bus.addEventListener('tool-request', () => { openDrawer = null; sync(); });
  bus.addEventListener('close-options', () => { openDrawer = null; sync(); });
  bus.addEventListener('open-selection-options',()=>{selectTool('scissors');openDrawer='selectionDrawer';sync();});
  bus.addEventListener('text-anchor', () => { openDrawer = 'textDrawer'; sync(); (document.getElementById('textContent') as HTMLTextAreaElement).focus(); });
}
export function chooseInk(hex: string): void {
  const wheel = document.getElementById('colourWheelBtn')!;
  const swatch = [...document.querySelectorAll<HTMLElement>('.color-btn')].find(button => button.dataset.ink?.toLowerCase() === hex.toLowerCase());
  if (!swatch) { wheel.dataset.ink = hex; wheel.style.background = hex; }
  selectInk(hex, swatch ?? wheel);
}

function layoutStage(): void {
  const slot = document.getElementById('canvasSlot');
  const stage = document.getElementById('stage');
  const bin = document.getElementById('toolBin');
  if (!slot || !stage || !bin) return;
  const rect = slot.getBoundingClientRect();
  // The compact layer list must leave the toolbar's Save/Open entry reachable.
  slot.style.setProperty('--layers-top', `${Math.ceil(document.getElementById('topBar')!.getBoundingClientRect().bottom) + 8}px`);
  const uiScale = Number(getComputedStyle(document.documentElement).getPropertyValue('--ui-scale')) || 1;
  const pad = phoneLayout.matches ? 0 : 12 * uiScale;
  const photoPanel = document.getElementById('photoPanel');
  const layerPanel = photoPanel && !photoPanel.hidden ? photoPanel : document.getElementById('layersPanel');
  const layerSpace = window.innerWidth > 1000 && window.innerHeight > 550 && layerPanel && !layerPanel.hidden && rect.width >= 700 ? layerPanel.offsetWidth + 16 : 0;
  slot.classList.toggle('layer-space', layerSpace > 0);
  slot.style.setProperty('--dock-space', `${layerSpace + 4}px`);
  const drawingWidth = rect.width - layerSpace;
  const availW = Math.max(80, drawingWidth - pad * 2);
  const availH = Math.max(80, rect.height - pad * 2);
  const frame=displayFrame(W,H),aspect=frame.width/frame.height;
  for(const canvas of [view,ui]){
    canvas.style.left=`${-frame.x/frame.width*100}%`;canvas.style.top=`${-frame.y/frame.height*100}%`;
    canvas.style.width=`${W/frame.width*100}%`;canvas.style.height=`${H/frame.height*100}%`;
  }
  const stageStyle = getComputedStyle(stage);
  const borderX = parseFloat(stageStyle.borderLeftWidth) + parseFloat(stageStyle.borderRightWidth);
  const borderY = parseFloat(stageStyle.borderTopWidth) + parseFloat(stageStyle.borderBottomWidth);
  let contentWidth = Math.max(1, availW - borderX);
  let contentHeight = contentWidth / aspect;
  if (contentHeight > availH - borderY) {
    contentHeight = Math.max(1, availH - borderY);
    contentWidth = contentHeight * aspect;
  }
  const width = contentWidth + borderX, height = contentHeight + borderY;
  stage.style.width = `${width}px`;
  stage.style.height = `${height}px`;
  const compact = phoneLayout.matches;
  const landscape = compact && window.innerWidth > window.innerHeight;
  stage.style.left = `${Math.floor(landscape ? drawingWidth - width : (drawingWidth - width) / 2)}px`;
  const paperTop = compact ? rect.height - height : (rect.height - height) / 2;
  stage.style.top = `${Math.floor(paperTop)}px`;
  const tool = bin.getBoundingClientRect();
  document.querySelectorAll<HTMLElement>('.drawer').forEach((drawer) => {
    drawer.style.zoom = '1';
    if (compact) {
      if (landscape) drawer.style.left = `${Math.max(8, tool.left)}px`;
      else drawer.style.removeProperty('left');
      // Put options above the fitted paper where space permits. Opening a menu
      // never resizes or moves the artwork underneath the child's finger.
      if (drawer.id === openDrawer) {
        const gap = 8;
        const edge = Math.max(gap, document.getElementById('topBar')!.getBoundingClientRect().top);
        const preferred = Math.min(tool.top, rect.top + paperTop - drawer.offsetHeight - gap);
        const top = Math.max(edge, Math.min(preferred, window.innerHeight - drawer.offsetHeight - gap));
        drawer.style.top = `${Math.floor(top)}px`;
      }
      return;
    }
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
    state.selectionMode = btn.dataset.select as 'rect' | 'lasso' | 'wand';
    commitSelection(); openDrawer = null; sync();
  }));
  const transparent = document.getElementById('transparentSelection') as HTMLInputElement;
  transparent.addEventListener('change', () => { state.transparentSelection = transparent.checked; refreshTransparency(); });
  const actions: Record<string, () => void> = {
    copySelection, cutSelection, pasteSelection: () => { void pasteExternal(); }, doneSelection: commitSelection, cancelSelection,
    selectAll, invertSelection, deleteSelection, selectionFlipH: () => flipSelection(true), selectionFlipV: () => flipSelection(false), selectionRotate: () => rotateSelection(90),
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
  (document.getElementById('pasteSelection') as HTMLButtonElement).disabled = false;
  for (const id of ['invertSelection', 'deleteSelection', 'selectionFlipH', 'selectionFlipV', 'selectionRotate', 'cropSelection']) (document.getElementById(id) as HTMLButtonElement).disabled = !hasSelection();
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
      layoutStage();
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
  play('colour');
  state.liveArmed = false;
  state.ink = id;
  if (isHex(id)) {
    state.neonTint = id;
    if (id.toUpperCase() !== '#FFFFFF') state.sparkleTint = id.toUpperCase() === '#1A1A1A' ? '#FFE566' : id;
  }
  markInkSelection(el);
  const glitter = document.querySelector<HTMLElement>('[data-ink="sparkle"]');
  if (glitter) glitter.style.backgroundImage = 'url(' + glitterThumb() + ')';
  document.documentElement.style.setProperty('--neon-tint', neonColor(state.neonTint));
  document.documentElement.style.setProperty('--neon-core', mixHex(neonColor(state.neonTint), '#ffffff', 0.34));
  updatePathControls();
  updateInkPreview();
}

function markInkSelection(selected: HTMLElement | null): void {
  document.querySelectorAll<HTMLElement>('.color-btn').forEach(btn => {
    btn.classList.toggle('selected', btn === selected);
    btn.setAttribute('aria-pressed', String(btn === selected));
  });
}

export function selectTool(tool: ToolId): void {
  if (!editable()) return;
  play(tool === 'spray' ? 'rattle' : 'clunk');
  if (state.tool !== tool) {
    bus.dispatchEvent(new Event('settle-input'));
    if (state.tool === 'text' && hasText()) placeText();
    commitSelection(false); state.poly = [];
  }
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
  return ({ draw: 'penDrawer', spray: 'sprayDrawer', shapes: 'shapesDrawer', eraser: 'eraserDrawer', stamp: 'stampDrawer', spiro: 'spiroDrawer', scissors: 'selectionDrawer', sponge: null, bucket: null, text: 'textDrawer', picker: 'pickerDrawer' })[tool];
}

function sync(): void {
  document.getElementById('studioBtn')!.setAttribute('aria-expanded', String(openDrawer === 'studioDrawer'));
  const size = document.getElementById('brushSize') as HTMLInputElement;
  const stamp = state.tool === 'stamp';
  size.min = stamp ? '0.4' : '1'; size.max = stamp ? '2.6' : '96'; size.step = stamp ? '0.1' : '1';
  size.value = String(stamp ? state.stampScale : state.brushWidth);
  size.disabled = ['scissors', 'bucket', 'text', 'picker'].includes(state.tool);
  (document.getElementById('opacity') as HTMLInputElement).disabled = state.tool === 'scissors';
  document.querySelectorAll<HTMLButtonElement>('#toolBin [data-tool], #symBtn').forEach((btn) => {
    const tool = btn.dataset.tool as ToolId | undefined;
    btn.classList.toggle('active', tool === state.tool || (btn.id === 'symBtn' && state.symmetry !== 'off'));
  });
  markChoices('[data-applicator]', state.applicator);
  markChoices('[data-shape]', state.shape);
  markChoices('[data-eraser]', state.eraserMode);
  markChoices('[data-sym]', state.symmetry);
  const maskToggle = document.getElementById('symmetryMask') as HTMLButtonElement;
  const masked = state.symmetryMask && state.symmetry !== 'off';
  maskToggle.classList.toggle('active', masked);
  maskToggle.setAttribute('aria-pressed', String(masked));
  maskToggle.disabled = state.symmetry === 'off';
  markChoices('[data-drive]', state.spiro.drive);
  markChoices('[data-stator]', state.spiro.shape);
  document.querySelectorAll<HTMLElement>('.drawer').forEach(drawer => {
    drawer.classList.toggle('open', drawer.id === openDrawer);
    if (drawer.id !== openDrawer && drawer.classList.contains('settings-open')) {
      drawer.classList.remove('settings-open'); updateDrawerSettings(drawer);
    }
  });
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
    const selected = document.querySelector<HTMLElement>('.color-btn.selected');
    markInkSelection(selected?.dataset.ink?.toLowerCase() === state.ink.toLowerCase() ? selected
      : [...document.querySelectorAll<HTMLElement>('.color-btn')].find(btn => btn.dataset.ink?.toLowerCase() === state.ink.toLowerCase()) ?? null);
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
  if (state.busy || motorOn()) return;
  if (!bus.dispatchEvent(new Event('photo-undo', { cancelable:true }))) return;
  if (state.tool === 'text' && hasText()) { cancelText(); return; }
  if (hasSelection()&&!hasObjectSelection()) { cancelSelection(); return; }
  if (state.poly.length) { state.poly.pop(); return; }
  bus.dispatchEvent(new Event('settle-input'));
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
  if(state.cad.open)return;
  if(event.defaultPrevented)return;
  if (document.querySelector('dialog[open]')) return;
  if (event.target instanceof HTMLInputElement && !['range', 'checkbox', 'color'].includes(event.target.type) || event.target instanceof HTMLTextAreaElement || event.target instanceof HTMLSelectElement || (event.target instanceof HTMLElement && event.target.isContentEditable)) return;
  const key = event.key.toLowerCase();
  if(hasSelection()&&['arrowleft','arrowright','arrowup','arrowdown'].includes(key)&&!(event.target instanceof HTMLInputElement)){event.preventDefault();const step=event.shiftKey?10:1,dx=key==='arrowleft'?-step:key==='arrowright'?step:0,dy=key==='arrowup'?-step:key==='arrowdown'?step:0;if(hasObjectSelection())moveObjects(dx,dy);else moveSelection(dx,dy);return;}
  if (event.ctrlKey || event.metaKey) {
    if (key === 'z') { event.preventDefault(); if (event.shiftKey && editable()) { cancelSelection(); redo(); } else doUndo(); }
    else if (key === 'y') { event.preventDefault(); if (editable()) { cancelSelection(); redo(); } }
    else if (key === 'a') { event.preventDefault(); selectTool('scissors'); selectAll(); }
    else if(key==='d'&&hasObjectSelection()){event.preventDefault();duplicateObjects();}
    else if (key === 's') { event.preventDefault(); settle(); void exportPng().catch(error=>message(error instanceof Error?error.message:String(error))); }
    else if (key === 'o') { event.preventDefault(); requestOpen(); }
    else if (key === 'p') { event.preventDefault(); settle(); printImage(); }
    else if (key === 'c' && hasSelection()) { event.preventDefault(); copySelection(); }
    else if (key === 'x' && hasSelection()) { event.preventDefault(); cutSelection(); }
    return;
  }
  if (key === 'escape') { state.choosingSlice=false; if(hasObjectSelection())commitSelection();else cancelSelection(); cancelText(); state.poly = []; cancelPending(); openDrawer = null; sync(); }
  if (key === 'enter' && !(event.target instanceof HTMLButtonElement)) { commitSelection(); finishPath(); }
  if (key === 'delete' || key === 'backspace') {
    if (hasSelection()) { event.preventDefault(); deleteSelection(); }
    else if (state.poly.length) { event.preventDefault(); state.poly.pop(); }
  }
  if (!event.altKey && key.length === 1) {
    const shortcuts: Record<string, ToolId> = { b: 'draw', s:'shapes', a:'stamp', g:'spiro', e: 'eraser', f: 'bucket', i: 'picker', t: 'text', r: 'scissors' };
    if (shortcuts[key]) { selectTool(shortcuts[key]); openDrawer = drawerFor(shortcuts[key]); sync(); }
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
  updateInkPreview();
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
  document.getElementById('finishQuick')!.hidden = state.tool !== 'shapes' || !['poly', 'spline', 'polygon'].includes(state.shape);
}
function decorateControls(): void {
  for (const attribute of ['applicator', 'shape', 'eraser', 'sym', 'drive', 'stator', 'select']) {
    document.querySelectorAll<HTMLElement>('[data-' + attribute + ']').forEach(btn => labelIcon(btn, btn.dataset[attribute]!));
  }
  const map: Record<string, string> = { symmetryMask: 'slice', undoBtn: 'undo', clearBtn: 'clear', saveBtn: 'save', copySelection: 'copy', cutSelection: 'cut', pasteSelection: 'paste', doneSelection: 'done', cancelSelection: 'close', finishPath: 'done', flipH: 'flipH', flipV: 'flipV', spiroReset: 'undo', windBtn: 'wind', addBeltBtn: 'plus', clearBeltBtn: 'clear' };
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
  document.getElementById('view')!.addEventListener('pointerdown', event => {
    if (!openDrawer) return;
    const dismissOnly = openDrawer === 'studioDrawer';
    openDrawer = null; sync();
    // More is navigation; tool gestures still position text, pick colour or draw.
    if (dismissOnly) { event.preventDefault(); event.stopImmediatePropagation(); }
  });
  document.querySelectorAll<HTMLButtonElement>('.belt-slot').forEach((button, i) => button.setAttribute('aria-label', 'Remove live ink colour ' + (i + 1)));
}
