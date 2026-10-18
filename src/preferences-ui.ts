import { audioSettings, play, setAudioSettings, toggleSounds,unlockAudio } from './audio';
import { bus } from './bus';
import { icon } from './icons';
import { readPreference,writePreference } from './preferences-store';

export type DeskTheme='mint'|'lavender'|'sand'|'night';
let desk:DeskTheme='mint',reducedMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
const savedDesk=readPreference('retropaint-desk');if(['mint','lavender','sand','night'].includes(savedDesk??''))desk=savedDesk as DeskTheme;const savedMotion=readPreference('retropaint-reduced-motion');if(savedMotion!==null)reducedMotion=savedMotion==='true';
export function setDeskTheme(value:DeskTheme):void {desk=value;document.body.dataset.desk=value;writePreference('retropaint-desk',value);document.querySelectorAll<HTMLElement>('[data-desk-choice]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.deskChoice===value)));}
export function setReducedMotion(value:boolean):void {reducedMotion=value;document.body.classList.toggle('reduced-motion',value);writePreference('retropaint-reduced-motion',String(value));}

export function initPreferencesUi():void {
  setDeskTheme(desk);setReducedMotion(reducedMotion);
  const dialog=document.createElement('dialog');dialog.id='preferencesDialog';dialog.setAttribute('aria-labelledby','preferencesTitle');
  dialog.innerHTML=`<header class="preferences-heading"><div>${icon('settings')}<h2 id="preferencesTitle">Sound &amp; feel</h2></div><button type="button" class="drawer-close" id="preferencesClose" aria-label="Close preferences">${icon('close')}</button></header><div class="preferences-tabs" role="tablist" aria-label="Preferences"><button type="button" class="tray-tab active" data-preference-tab="sound" role="tab" aria-selected="true">Sound</button><button type="button" class="tray-tab" data-preference-tab="desk" role="tab" aria-selected="false">Your desk</button></div><section data-preference-panel="sound"><label class="preference-toggle"><span><strong>Sound effects</strong><small>A little toy-box magic.</small></span><input id="soundEnabled" type="checkbox" role="switch"></label><label class="preference-volume">Volume <output id="soundVolumeValue"></output><input id="soundVolume" type="range" min="0" max="100" step="5" aria-label="Sound volume"></label><label class="selection-toggle"><input id="drawingSounds" type="checkbox"> Sounds while painting</label><button type="button" class="choice" id="soundPreview">${icon('soundOn')}Try a sound</button></section><section data-preference-panel="desk" hidden><div class="desk-choices" aria-label="Desk colour">${([['mint','Mint'],['lavender','Lilac'],['sand','Oat'],['night','Night']] as const).map(([value,label])=>`<button type="button" class="choice" data-desk-choice="${value}" aria-pressed="false"><span class="desk-swatch desk-${value}"></span>${label}</button>`).join('')}</div><label class="selection-toggle"><input id="reducedMotion" type="checkbox"> Reduce interface motion</label><p class="hint">Make the space comfortable. Desk colours and sound settings are remembered on this device.</p></section><footer><button type="button" class="choice" id="preferencesDone">Done</button></footer>`;
  document.body.append(dialog);
  const viewPanel=document.querySelector<HTMLElement>('[data-studio-panel="view"]')!,row=document.createElement('div');row.className='row workspace-preferences-row';
  const open=document.createElement('button');open.type='button';open.className='choice';open.id='openPreferences';open.innerHTML=icon('settings')+'Sound & feel';open.addEventListener('click',()=>dialog.showModal());row.append(open);
  const shortcut=document.createElement('button');shortcut.type='button';shortcut.className='choice';shortcut.id='openShortcuts';shortcut.innerHTML=icon('help')+'Shortcuts';row.append(shortcut);viewPanel.append(row);
  const hints=viewPanel.querySelectorAll('.hint');if(hints.length>1)hints[hints.length-1].remove();
  const quick=document.createElement('button');quick.type='button';quick.className='choice';quick.id='soundToggle';document.getElementById('paperControls')!.append(quick);
  quick.addEventListener('click',()=>{toggleSounds();unlockAudio();if(audioSettings().enabled)play('pop');});
  for(const id of ['preferencesClose','preferencesDone'])document.getElementById(id)!.addEventListener('click',()=>dialog.close());
  dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
  document.querySelectorAll<HTMLButtonElement>('[data-preference-tab]').forEach(button=>button.addEventListener('click',()=>{
    document.querySelectorAll<HTMLButtonElement>('[data-preference-tab]').forEach(tab=>{tab.classList.toggle('active',tab===button);tab.setAttribute('aria-selected',String(tab===button));});document.querySelectorAll<HTMLElement>('[data-preference-panel]').forEach(panel=>{panel.hidden=panel.dataset.preferencePanel!==button.dataset.preferenceTab;});
  }));
  const enabled=document.getElementById('soundEnabled') as HTMLInputElement,volume=document.getElementById('soundVolume') as HTMLInputElement,drawing=document.getElementById('drawingSounds') as HTMLInputElement;
  enabled.addEventListener('change',()=>{setAudioSettings({enabled:enabled.checked});unlockAudio();if(enabled.checked)play('pop');});
  volume.addEventListener('input',()=>setAudioSettings({volume:Number(volume.value)/100}));volume.addEventListener('change',()=>play('colour'));
  drawing.addEventListener('change',()=>setAudioSettings({drawing:drawing.checked}));document.getElementById('soundPreview')!.addEventListener('click',()=>{unlockAudio();play('splash');});
  const motion=document.getElementById('reducedMotion') as HTMLInputElement;motion.checked=reducedMotion;motion.addEventListener('change',()=>setReducedMotion(motion.checked));
  document.querySelectorAll<HTMLButtonElement>('[data-desk-choice]').forEach(button=>button.addEventListener('click',()=>{setDeskTheme(button.dataset.deskChoice as DeskTheme);play('colour');}));setDeskTheme(desk);
  function refresh():void {const value=audioSettings(),audible=value.enabled&&value.volume>0;enabled.checked=value.enabled;volume.value=String(Math.round(value.volume*100));drawing.checked=value.drawing;document.getElementById('soundVolumeValue')!.textContent=`${Math.round(value.volume*100)}%`;quick.innerHTML=icon(audible?'soundOn':'soundOff');quick.title=audible?'Mute sounds (M)':'Turn on sounds (M)';quick.setAttribute('aria-label','Sound effects');quick.setAttribute('aria-pressed',String(audible));(document.getElementById('soundPreview') as HTMLButtonElement).disabled=!audible;}
  bus.addEventListener('sound-settings',refresh);refresh();
  document.addEventListener('keydown',event=>{if(event.key.toLowerCase()!=='m'||event.ctrlKey||event.metaKey||event.altKey||document.querySelector('dialog[open]')||event.target instanceof HTMLInputElement||event.target instanceof HTMLTextAreaElement||event.target instanceof HTMLSelectElement)return;event.preventDefault();quick.click();});
}
