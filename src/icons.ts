const paths: Record<string, string> = {
  settings: '<path fill="#d9b5f6" d="m10 2 4 0 1 4 4-1 2 4-3 3 3 3-2 4-4-1-1 4h-4l-1-4-4 1-2-4 3-3-3-3 2-4 4 1z"/><circle fill="#fffdf7" cx="12" cy="12" r="4"/>',
  back: '<path d="M21 12H3m7-7-7 7 7 7"/>',
  zoomIn: '<circle cx="10" cy="10" r="7"/><path d="m15 15 7 7M6 10h8m-4-4v8"/>',
  zoomOut: '<circle cx="10" cy="10" r="7"/><path d="m15 15 7 7M6 10h8"/>',
  fit: '<path d="M3 9V3h6m6 0h6v6m0 6v6h-6M9 21H3v-6"/><rect x="7" y="8" width="10" height="8" rx="1"/>',
  hand: '<path fill="#ffd16f" d="M8 12V5a2 2 0 0 1 4 0v6-8a2 2 0 0 1 4 0v8-6a2 2 0 0 1 4 0v11c0 5-4 7-8 7-3 0-5-2-7-5l-3-5c-1-2 1-4 3-2l3 3z"/>',
  clock: '<circle fill="#a8d9f7" cx="12" cy="12" r="10"/><path d="M12 5v7l5 3M12 2v1m10 9h-1M12 22v-1M2 12h1"/>',
  slice: '<circle cx="12" cy="12" r="10"/><path fill="#ffd16f" d="M12 12V2a10 10 0 0 1 8.66 15z"/>',
  plus: '<circle fill="#93dfbd" cx="12" cy="12" r="10"/><path d="M6 12h12M12 6v12"/>',
  blend: '<circle fill="#f7aa76" cx="8" cy="12" r="7"/><circle fill="#b9a4e8" fill-opacity=".7" cx="16" cy="12" r="7"/>',
  marker: '<path fill="#ffcc5c" d="m6 16 8-12 5 4-8 12-6 1z"/><path d="m12 7 5 4M6 16l5 4M4 22l3-3"/>',
  biro: '<path fill="#77c8fa" d="m5 17 11-14 4 3L9 20l-5 1z"/><path d="m14 6 3 3M5 17l4 3"/>',
  callig: '<path fill="#bd9bff" d="m12 2 8 9-7 9-9-7z"/><path d="m4 13 8-1 1 8M12 12l4-6"/><circle cx="12" cy="12" r="1"/>',
  gouache: '<path fill="#ef7696" d="m9 3 10 5-4 8-10-5z"/><path fill="#ffc85d" d="m8 13 5 3-4 7-4-2z"/><path d="m11 5-3 6m6-5-3 6m6-4-3 6"/>',
  watercolor: '<path fill="#77cfed" d="M12 2C10 7 4 12 4 16a8 8 0 0 0 16 0c0-4-6-9-8-14z"/><path d="M8 15c-1 3 1 4 3 4"/>',
  mist: '<path fill="#9cd9c5" d="M4 9h7v13H4z"/><path d="M6 9V5h5v4m2-3 2-1m-2 3h3m-3 2 2 1m4-9h.1m2 5h.1m-2 6h.1"/>',
  splatter: '<path fill="#f499b6" d="m11 2 3 6 7-2-4 7 5 5-8-1-3 6-3-7-6 1 4-6-3-6 7 3z"/>',
  confetti: '<path fill="#ffc65b" d="m3 12 8 8-10 3z"/><path stroke="#e84c8b" d="m13 4 3 3m2 7 3-1M7 4l1 3"/><path stroke="#7284e9" d="m15 18 2 3M13 10l3-2m4-6 1 3"/>',
  line: '<path d="m3 20 18-16"/><circle fill="#ffc85d" cx="3" cy="20" r="2"/><circle fill="#ffc85d" cx="21" cy="4" r="2"/>',
  rect: '<rect fill="#a8d9f7" x="3" y="5" width="18" height="14" rx="1"/>',
  circle: '<circle fill="#d9b5f6" cx="12" cy="12" r="9"/>',
  poly: '<path d="m2 18 6-13 7 14 7-12"/><path fill="#ffc85d" d="M6 3h4v4H6zm7 14h4v4h-4z"/>',
  spline: '<path stroke="#8060be" stroke-width="3" d="M2 18C5-9 17 33 22 6"/><circle fill="#ffc85d" cx="2" cy="18" r="2"/><circle fill="#ffc85d" cx="22" cy="6" r="2"/>',
  lasso: '<path d="M5 17c-7-9 6-17 14-11s-1 15-11 11c-5-2-5 6 1 5"/>',
  copy: '<rect fill="#aad8f0" x="3" y="3" width="13" height="14" rx="2"/><rect fill="#fffdf8" x="8" y="8" width="13" height="14" rx="2"/>',
  cut: '<circle cx="5" cy="18" r="3"/><circle cx="18" cy="18" r="3"/><path d="m7 16 12-14M16 16 4 2"/>',
  paste: '<rect fill="#ffd16f" x="5" y="5" width="15" height="17" rx="2"/><rect fill="#fffdf8" x="9" y="2" width="7" height="6" rx="2"/><path d="M9 13h7m-7 4h7"/>',
  done: '<path stroke="#288567" stroke-width="4" d="m3 12 6 6L21 5"/>',
  close: '<path d="m6 6 12 12M18 6 6 18"/>',
  undo: '<path d="m9 3-6 6 6 6M3 9h11a7 7 0 0 1 0 14"/>',
  clear: '<path fill="#ffd16f" d="m8 11 8 4-3 8-12-6z"/><path d="m12 13 6-11M6 16l-2 3m5-2-2 3"/>',
  save: '<path fill="#8cdbc4" d="M3 2h15l4 4v16H3z"/><path fill="#fff" d="M7 2h9v7H7zm0 12h11v8H7z"/>',
  scrub: '<path fill="#f9a8c2" d="m3 14 11-11 8 8-11 11H7z"/><path d="m7 10 8 8M11 22h11"/>',
  blackhole: '<ellipse fill="#9173b9" cx="12" cy="12" rx="11" ry="6" transform="rotate(-30 12 12)"/><circle fill="#29304c" cx="12" cy="12" r="5"/>',
  pixelate: '<path fill="#a7d3f1" d="M2 2h8v8H2zm12 0h8v8h-8zM2 14h8v8H2z"/><path fill="#cfb7ec" d="M14 14h8v8h-8z"/>',
  invert: '<circle fill="#fff" cx="12" cy="12" r="10"/><path fill="#29304c" d="M12 2a10 10 0 0 1 0 20z"/>',
  emboss: '<path fill="#c0c8d5" d="m12 2 10 7v13H2V9z"/><path d="m12 7 6 5v6H6v-6z"/>',
  v: '<path stroke-dasharray="2 3" d="M12 1v22"/><path fill="#a8d9f7" d="m3 5 6 7-6 7zm18 0-6 7 6 7z"/>',
  h: '<path stroke-dasharray="2 3" d="M1 12h22"/><path fill="#a8d9f7" d="m5 3 7 6 7-6zm0 18 7-6 7 6z"/>',
  off: '<circle cx="12" cy="12" r="9"/><path d="m5 5 14 14"/>',
  manual: '<path fill="#ffd16f" d="M6 21 2 12q0-3 3-1l2 2V5q2-4 3 0v6-8q3-3 3 1v7-6q3-2 3 1v6-4q3-1 3 2v7l-3 5z"/>',
  auto: '<path fill="#8cdbc4" d="m6 3 15 9-15 9z"/>',
  oval: '<ellipse fill="#a8d9f7" cx="12" cy="12" rx="10" ry="6"/>',
  square: '<rect fill="#cfb7ec" x="3" y="3" width="18" height="18" rx="1"/>',
  cross: '<path fill="#f9c477" d="M8 2h8v6h6v8h-6v6H8v-6H2V8h6z"/>',
  wind: '<circle fill="#ffd16f" cx="6" cy="8" r="5"/><path d="m10 12 10 10m-5-5 3-3m0 6 3-3"/>',
  flipH: '<path d="M12 2v20M3 6l6 6-6 6zm18 0-6 6 6 6z"/>',
  flipV: '<path d="M2 12h20M6 3l6 6 6-6zm0 18 6-6 6 6z"/>',
  rotate: '<path d="M4 8a9 9 0 1 1-1 8M4 2v6h6"/>',
};
export function icon(name: string): string {
  const numeric = Number(name);
  const radial = Number.isFinite(numeric) && numeric > 0 ? Array.from({ length: numeric }, (_, i) => {
    const a = i * Math.PI * 2 / numeric;
    return `<path d="M12 12L${12 + Math.cos(a) * 10} ${12 + Math.sin(a) * 10}"/>`;
  }).join('') : '';
  return `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || radial || paths.circle}</svg>`;
}
export function labelIcon(button: HTMLElement, name: string, label = button.textContent ?? ''): void {
  button.innerHTML = `${icon(name)}<span>${label}</span>`;
}
