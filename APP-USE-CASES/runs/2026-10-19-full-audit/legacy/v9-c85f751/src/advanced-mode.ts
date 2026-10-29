import { emit } from './bus';
import { readPreference,writePreference } from './preferences-store';

let enabled=false;
export function advancedEnabled():boolean { return enabled; }
export function setAdvancedMode(value:boolean):void {
  enabled=value;
  document.body.classList.toggle('advanced-mode',value);
  (document.getElementById('advancedMode') as HTMLInputElement).checked=value;
  for(const id of ['layersToggle','photoToggle'])document.getElementById(id)!.hidden=!value;
  for(const id of ['openLayers','openPhotoLab','openSuperResolution'])(document.getElementById(id) as HTMLButtonElement).disabled=!value;
  writePreference('retropaint-advanced',String(value));
  emit('advanced-mode',value);window.dispatchEvent(new Event('resize'));
}
export function initAdvancedMode():void {
  const remembered=readPreference('retropaint-advanced')==='true';
  document.getElementById('advancedMode')!.addEventListener('change',event=>setAdvancedMode((event.target as HTMLInputElement).checked));
  setAdvancedMode(remembered);
}
