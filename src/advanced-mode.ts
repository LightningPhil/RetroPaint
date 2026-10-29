import { bus, emit } from './bus';
import { readPreference,writePreference } from './preferences-store';
import { state, vectorDrawingEnabled } from './state';
import { layers } from './layers';

export function advancedEnabled():boolean { return state.workspaceMode === 'advanced'; }
function updateArtworkHint():void {
  const hint=document.getElementById('basicArtworkHint');
  if(hint)hint.hidden=advancedEnabled()||!(layers.length>1||layers.some(layer=>layer.cad||layer.objects?.length||layer.photo));
  document.body.classList.toggle('vector-mode',vectorDrawingEnabled());
}
export function setAdvancedMode(value:boolean):void {
  if(!value&&state.cad.open){(document.getElementById('advancedMode') as HTMLInputElement).checked=true;return;}
  if(value!==advancedEnabled())emit('settle-input');
  state.workspaceMode=value?'advanced':'basic';
  document.body.classList.toggle('advanced-mode',value);
  (document.getElementById('advancedMode') as HTMLInputElement).checked=value;
  if(!value&&document.querySelector('[data-studio="layers"][aria-selected="true"]'))document.querySelector<HTMLButtonElement>('[data-studio="file"]')!.click();
  for(const element of document.querySelectorAll<HTMLElement>('[data-advanced-only]'))element.hidden=!value;
  for(const id of ['layersToggle','photoToggle'])document.getElementById(id)!.hidden=!value;
  for(const id of ['openLayers','openPhotoLab','openSuperResolution','openCad','drawingMode'])(document.getElementById(id) as HTMLButtonElement|HTMLSelectElement).disabled=!value;
  document.getElementById('workspaceModeTitle')!.textContent=value?'Advanced mode':'Basic mode';
  document.getElementById('workspaceModeDescription')!.textContent=value?'Paint plus layers, editable vectors, Photo lab, enhancement and 3D. Switching back to Basic keeps your picture intact.':'Paint, draw and play. Turn on Advanced for layers, editable vectors, Photo lab and 3D.';
  document.getElementById('studioBtn')!.title=`${value?'Advanced':'Basic'} mode · Open toolbox to change mode`;
  updateArtworkHint();
  writePreference('retropaint-advanced',String(value));
  emit('advanced-mode',value);emit('objects');window.dispatchEvent(new Event('resize'));
}
export function initAdvancedMode():void {
  const remembered=readPreference('retropaint-advanced')==='true';
  document.getElementById('advancedMode')!.addEventListener('change',event=>setAdvancedMode((event.target as HTMLInputElement).checked));
  for(const event of ['layers','document-opened','document-created'])bus.addEventListener(event,updateArtworkHint);
  setAdvancedMode(remembered);
}
