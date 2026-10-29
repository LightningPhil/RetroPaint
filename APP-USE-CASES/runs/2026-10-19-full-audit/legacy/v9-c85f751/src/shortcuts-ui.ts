import { icon } from './icons';
import { TOOL_INFO } from './tool-art';
import { state } from './state';

export function initShortcutsUi():void {
  const dialog=document.createElement('dialog');dialog.id='shortcutsDialog';dialog.setAttribute('aria-labelledby','shortcutsTitle');
  const modifier=navigator.platform.includes('Mac')?'⌘':'Ctrl';
  const groups:Record<string,[string,string][]>= {
    tools:[...Object.values(TOOL_INFO).filter(info=>info.shortcut).map(info=>[info.shortcut,info.label] as [string,string]),['M','Mute / unmute']],
    edit:[[`${modifier} Z`,'Undo'],[`${modifier} ⇧ Z`,'Redo'],[`${modifier} A`,'Select all'],[`${modifier} C / X / V`,'Copy / cut / paste'],[`${modifier} D`,'Duplicate piece'],['Delete','Delete selection'],['Enter','Place selection'],['Esc','Cancel / close'],['↑ ↓ ← →','Nudge a piece'],['⇧ arrows','Nudge by 10 pixels']],
    view:[['Space + drag','Move the paper'],['+ / −','Zoom in / out'],['0','Fit the picture'],[`${modifier} + wheel`,'Zoom with the wheel'],['Shift + drag','Constrain a size or move'],['Shift + click','Add or remove a piece'],['Alt + click','Reach a piece behind'],[`${modifier} S`,'Download PNG'],[`${modifier} O`,'Open image'],['?','Show these shortcuts']],
  };
  dialog.innerHTML=`<header class="preferences-heading"><div>${icon('help')}<h2 id="shortcutsTitle">A few handy shortcuts</h2></div><button type="button" class="drawer-close" id="shortcutsClose" aria-label="Close shortcuts">${icon('close')}</button></header><div class="shortcut-tabs" role="tablist" aria-label="Shortcut group">${[['tools','Tools'],['edit','Editing'],['view','Paper & more']].map(([id,label])=>`<button type="button" class="tray-tab ${id==='tools'?'active':''}" data-shortcut-tab="${id}" role="tab" aria-selected="${id==='tools'}">${label}</button>`).join('')}</div>${Object.entries(groups).map(([id,keys])=>`<div class="shortcut-grid" data-shortcut-panel="${id}" ${id==='tools'?'':'hidden'}>${keys.map(([key,label])=>`<div><kbd>${key}</kbd><span>${label}</span></div>`).join('')}</div>`).join('')}<footer><span class="hint">Your picture stays right where you left it.</span><button type="button" class="choice" id="shortcutsDone">Got it</button></footer>`;
  document.body.append(dialog);document.getElementById('openShortcuts')!.addEventListener('click',()=>dialog.showModal());
  for(const id of ['shortcutsClose','shortcutsDone'])document.getElementById(id)!.addEventListener('click',()=>dialog.close());
  document.querySelectorAll<HTMLButtonElement>('[data-shortcut-tab]').forEach(button=>button.addEventListener('click',()=>{
    document.querySelectorAll<HTMLElement>('[data-shortcut-tab]').forEach(tab=>{tab.classList.toggle('active',tab===button);tab.setAttribute('aria-selected',String(tab===button));});document.querySelectorAll<HTMLElement>('[data-shortcut-panel]').forEach(panel=>{panel.hidden=panel.dataset.shortcutPanel!==button.dataset.shortcutTab;});
  }));
  document.addEventListener('keydown',event=>{
    if(state.cad.open)return;
    if(event.target instanceof HTMLInputElement||event.target instanceof HTMLTextAreaElement||event.target instanceof HTMLSelectElement||event.target instanceof HTMLElement&&event.target.isContentEditable||document.querySelector('dialog[open]'))return;
    if(event.key==='?'||(event.ctrlKey||event.metaKey)&&event.key==='/'){event.preventDefault();dialog.showModal();}
  });
}
