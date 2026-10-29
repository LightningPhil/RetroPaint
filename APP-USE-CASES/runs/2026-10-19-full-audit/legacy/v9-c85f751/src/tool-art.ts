import type { ToolId } from './types';

export const TOOL_INFO:Record<ToolId,{label:string;hint:string;shortcut:string;accent:string}>={
  draw:{label:'Brushes',hint:'Make your mark. Try a brush, an ink, or both.',shortcut:'B',accent:'#f5bd58'},
  shapes:{label:'Shapes',hint:'Drag a shape. Hold Shift for a straight line or equal sides.',shortcut:'S',accent:'#80c8ee'},
  bucket:{label:'Bucket',hint:'Tap a space to fill it. Drag to make a gradient.',shortcut:'F',accent:'#a8dcc8'},
  spray:{label:'Spray',hint:'Hold to spray. Keep still for a puddle of colour.',shortcut:'',accent:'#efacc7'},
  sponge:{label:'Smudge',hint:'Pick a piece, then gently push the paint around.',shortcut:'',accent:'#c4b2e7'},
  scissors:{label:'Select',hint:'Pick a piece. Move it, resize it, and make it yours.',shortcut:'R',accent:'#e8c367'},
  eraser:{label:'Eraser',hint:'Rub out a little, or explore a playful pixel effect.',shortcut:'E',accent:'#f3aab7'},
  stamp:{label:'Stamps',hint:'Pick a stamp, then tap the paper. Drag to make a trail.',shortcut:'A',accent:'#b4d1c7'},
  spiro:{label:'Spiro',hint:'Pick a gear and wind the key. Big paper, big patterns.',shortcut:'G',accent:'#a9cfd8'},
  text:{label:'Text',hint:'Say something. Tap the paper to position your words.',shortcut:'T',accent:'#b8a2df'},
  picker:{label:'Pick colour',hint:'Borrow a colour from your picture.',shortcut:'I',accent:'#a7d8d4'},
};

const ink='var(--paint-ink,#df5c79)';
const illustrations:Record<string,string>={
  draw:`<path fill="#f3c66e" d="m22 38 23-31q5-5 10 0t0 10L30 43z"/><path stroke="#fff5d8" stroke-width="3" d="m33 27 15-17"/><path fill="#9cd7d8" d="m21 31 13 11-7 8-12-11z"/><path fill="${ink}" d="M19 39c-9-1-7 14-15 16 14 9 29-3 23-12z"/><path stroke="#fff" opacity=".65" d="M17 44c-3 1-2 7-5 9"/><path fill="${ink}" stroke="none" d="M42 45q-7 11 0 11t0-11z"/>`,
  shapes:'<rect x="7" y="11" width="32" height="32" rx="6" fill="#86c5e7"/><path d="M13 16h18" stroke="#d2efff" stroke-width="3"/><circle cx="39" cy="39" r="18" fill="#eb9eb9"/><path d="m37 8 4 6 7 1-5 5 1 7-7-3-6 3 1-7-5-5 7-1z" fill="#f9d371"/><path d="M43 32q5 2 6 7" stroke="#ffe2ee" stroke-width="3"/>',
  bucket:`<path fill="${ink}" stroke="none" opacity=".8" d="M10 53c-8-8 10-13 23-8s22-2 25 5-30 13-48 3"/><g transform="rotate(-22 30 27)"><path d="M15 22V11c0-10 27-10 27 0v11"/><path fill="#a6d3dc" d="M10 17h38l-4 28q-15 8-30 0z"/><ellipse fill="#ecf6f4" cx="29" cy="17" rx="19" ry="5"/><path d="M18 24v14" stroke="#e7fbff" stroke-width="4"/><path fill="${ink}" d="M40 20c-4-3-11-1-15 0v8c0 5 6 5 6 0v-3c0-4 5-3 5 0v6c0 4 5 4 5 0z"/></g><path fill="${ink}" d="M51 32q-8 13 0 13t0-13z"/>`,
  spray:`<path fill="#e1e7df" d="M21 18V8h18v10"/><path fill="#a5d1cf" d="M17 22q15-8 30 0v31q-15 9-30 0z"/><path fill="#f4f2dc" d="M17 31h30v13H17z"/><path stroke="${ink}" stroke-width="5" d="m23 38 17-1"/><path d="M23 24v5m0 17v6" stroke="#e7fffa" stroke-width="3"/><path d="M29 8V4h10v4" fill="#e0a7c3"/><path stroke="${ink}" stroke-width="2.6" d="M43 5h5m-5 5 6 2m-6 3 5 4"/><circle fill="${ink}" stroke="none" cx="55" cy="5" r="2"/><circle fill="${ink}" stroke="none" cx="57" cy="15" r="1.8"/>`,
  sponge:'<path fill="#c2b2df" stroke="none" d="M5 39c-2-15 15-27 28-19s28 10 22 26-18 15-26 8S7 55 5 39"/><path fill="#e2c3a5" d="M21 46 8 35c-5-5 1-10 5-6l8 7V10c0-7 9-7 9 0v15-5c0-6 8-6 8 0v9-4c0-6 8-6 8 0v10c0 10-5 16-14 17z"/><path stroke="#fff0df" stroke-width="3" d="M25 11v15m3 19q6 5 11-1"/><path stroke="#8b6db1" d="M8 51q7 8 14 6m-9-41 3-5m34 7 4-3"/>',
  scissors:'<rect x="7" y="9" width="45" height="39" rx="4" fill="#d8e8e7" fill-opacity=".35" stroke-dasharray="4 5"/><path fill="#fffdf7" d="m22 20 7 36 8-12 12 4z"/><path d="m36 43 8 14" stroke-width="5"/><rect fill="#f7d17b" x="3" y="5" width="9" height="9" rx="2"/><rect fill="#f7d17b" x="48" y="5" width="9" height="9" rx="2"/><rect fill="#f7d17b" x="3" y="44" width="9" height="9" rx="2"/>',
  eraser:'<path fill="#e5a1b6" d="m8 34 24-24q5-5 10 0l15 15q4 4 0 8L33 57H24z"/><path fill="#b8bfd6" d="m8 34 12-12 25 25-12 10H24z"/><path stroke="#ffe6e6" stroke-width="3" d="m34 15 13 13"/><path d="M31 57h27"/><path fill="#edbfd0" stroke="none" d="m5 50 6 2-3 5-5-3zm43 2 5-2 3 4-5 2z"/>',
  stamp:'<path fill="#b9d5cc" d="M25 30c-2-8-11-12-8-20C20 0 43 0 46 10c3 8-6 12-8 20z"/><path stroke="#effff4" stroke-width="3" d="M24 12q5-5 13-2"/><path fill="#d3ac79" d="M13 29h37l4 12H9z"/><path fill="#ecacc4" d="M9 41h45v9H9z"/><path d="M15 45h32" stroke="#ffe1ee"/><path fill="#f5cf6e" d="m31 49 3 5 6 1-4 4 1 5-6-2-5 2 1-5-4-4 6-1z" stroke-width="1.5"/>',
  symmetry:'<path fill="#8ecadf" d="M29 30C4-1 1 15 9 33 0 54 17 63 29 39z"/><path fill="#e6a5c3" d="M35 30C60-1 63 15 55 33c9 21-8 30-20 6z"/><path fill="#d5f1f8" d="M24 27 11 17q-3 11 7 16z" stroke="none"/><path fill="#ffe3e8" d="m40 27 13-10q3 11-7 16z" stroke="none"/><path d="M32 3v58" stroke-dasharray="3 5"/><path d="m28 18-5-8m13 8 5-8"/>',
  spiro:'<circle cx="32" cy="32" r="25" fill="#b7dce0"/><circle cx="32" cy="32" r="19" fill="#f9faf0"/><path stroke="#6b92a0" d="M32 8v4m12-1-2 4m10 5-4 2m9 10h-5m1 12-4-2m-5 11-2-4m-10 8v-5m-12 1 2-4m-11-5 4-2M8 32h4m-1-12 4 2m5-11 2 4"/><circle fill="#d9b9ed" cx="39" cy="26" r="10"/><path stroke="#9866b4" stroke-width="2" d="M18 35c-6-22 32 17 19-4S11 47 31 42 44 18 24 25s17 24 18 10"/><circle fill="#f4ca70" cx="40" cy="26" r="3"/>',
  text:'<path fill="#c8b3e9" d="M10 7h34l10 10v38H10z"/><path fill="#eee4fc" d="M44 7v11h10"/><path stroke="#684c8f" stroke-width="5" d="m20 42 10-23 10 23m-16-8h12"/><path d="M17 49h27" stroke="#9a7ac0"/><circle fill="#e9a0bb" cx="51" cy="48" r="10"/><path stroke="#fff6f5" d="M47 48h8m-4-4v8"/>',
  picker:'<path fill="#6a5a8b" d="m37 6 6-4 16 16-4 6-5 2-18-18z"/><path fill="#b7dcdf" d="m16 49 24-30 9 9-29 25-11 3z"/><path fill="#65bcbf" d="m18 46 16-17 6 6-20 18-9 2z" stroke="none"/><path d="m36 23 7 7m-18 9 8-10" stroke="#fff" stroke-width="2.5"/><path fill="#edacbe" d="M13 48C2 62 21 64 13 48z"/>',
};

export function toolArtwork(name:string):string {
  return `<svg class="tool-art" viewBox="0 0 64 64" fill="none" stroke="#334256" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${illustrations[name]??illustrations.draw}</svg>`;
}

export function decorateToolArtwork():void {
  for(const button of document.querySelectorAll<HTMLButtonElement>('#toolBin [data-tool]')){
    const name=button.dataset.tool as ToolId,info=TOOL_INFO[name];
    button.innerHTML=`${toolArtwork(name)}<span class="tool-label">${info.label}</span>`;button.style.setProperty('--tool-accent',info.accent);
    button.title=`${info.label}${info.shortcut?` (${info.shortcut})`:''} · ${info.hint}`;
  }
  const symmetry=document.getElementById('symBtn')!;symmetry.innerHTML=`${toolArtwork('symmetry')}<span class="tool-label">Symmetry</span>`;symmetry.style.setProperty('--tool-accent','#a5cadd');
}
