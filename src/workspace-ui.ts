import { play } from './audio';
import { bus, emit } from './bus';
import { H, W } from './canvas';
import { editable, message } from './editor';
import { canRedo, redo, undo } from './history';
import { icon } from './icons';
import { centreObjects, duplicateObjects, hasObjectSelection, selectedObjects } from './objects';
import { photoEditing } from './photo-preview';
import { cancelSelection, commitSelection, copySelection, deleteSelection, hasSelection, moveSelection, selectionBounds } from './selection';
import { state, vectorDrawingEnabled } from './state';
import { TOOL_INFO, toolArtwork } from './tool-art';

let root:HTMLElement|null=null,signature='';
function outside():boolean {const b=selectionBounds();return Boolean(b&&(b.x<0||b.y<0||b.x+b.width>W||b.y+b.height>H));}
export function initWorkspaceUi():void {
  root=document.createElement('div');root.id='workspaceBar';root.setAttribute('aria-label','Painting controls');
  root.innerHTML=`<div id="workspaceIdle"><div class="workspace-tool"><span id="workspaceToolArt"></span><span><strong id="workspaceToolName"></strong><small id="workspaceToolDetail"></small></span></div><div id="workspaceZoom"></div><button type="button" class="choice" id="workspaceRedo" title="Redo (Ctrl/Cmd + Shift + Z)" aria-label="Redo">${icon('redo')}</button></div><div id="workspaceSelection" hidden><div class="workspace-selection-info"><strong id="workspaceSelectionType"></strong><small id="workspaceSelectionSize"></small></div><button type="button" class="choice workspace-place" id="workspacePlace">${icon('done')}<span>Place</span></button><button type="button" class="choice" id="workspaceCentre" title="Bring selection to the centre of the paper" aria-label="Bring selection to paper">${icon('centre')}</button><button type="button" class="choice" id="workspaceCopy" title="Copy selection" aria-label="Copy selection">${icon('copy')}</button><button type="button" class="choice" id="workspaceDuplicate" title="Duplicate selection (Ctrl/Cmd + D)" aria-label="Duplicate selection">${icon('plus')}</button><button type="button" class="choice" id="workspaceDelete" title="Delete selection" aria-label="Delete selection">${icon('delete')}</button><button type="button" class="choice" id="workspaceCancel" title="Cancel selection" aria-label="Cancel selection">${icon('close')}</button><button type="button" class="choice" id="workspaceMore" title="Selection options" aria-label="Selection options">${icon('settings')}</button></div>`;
  document.getElementById('canvasSlot')!.append(root);document.getElementById('workspaceZoom')!.append(document.getElementById('zoomReadout')!);document.body.classList.add('workspace-ready');
  const action=(id:string,callback:()=>void)=>document.getElementById(id)!.addEventListener('click',()=>{if(editable())callback();});
  action('workspacePlace',()=>{const wasOutside=outside(),pieces=selectedObjects(),raster=pieces.some(o=>o.kind==='raster')||!pieces.length,vector=pieces.some(o=>o.kind!=='raster');commitSelection();play('place');if(wasOutside)message(raster?`Placed. Off-paper raster pixels were trimmed.${vector?' Complete vectors are kept.':' Undo brings them back.'}`:'Placed. The whole vector is kept, ready to move back in.');});
  action('workspaceCentre',()=>{if(hasObjectSelection())centreObjects();else{const b=selectionBounds();if(b)moveSelection((W-b.width)/2-b.x,(H-b.height)/2-b.y);}});
  action('workspaceCopy',()=>{copySelection();play('clack');message('Copied. Paste makes another piece.');});
  action('workspaceDuplicate',()=>{duplicateObjects();play('place');});
  action('workspaceDelete',()=>{deleteSelection();play('delete');});
  action('workspaceCancel',()=>{if(hasObjectSelection())undo();else cancelSelection();});
  action('workspaceMore',()=>emit('open-selection-options'));
  action('workspaceRedo',()=>{commitSelection();redo();});
  bus.addEventListener('objects',()=>{signature='';});bus.addEventListener('selection',()=>{signature='';});
  updateWorkspaceUi();
}
export function updateWorkspaceUi():void {
  if(!root)return;root.hidden=photoEditing;if(photoEditing)return;
  const selected=state.tool==='scissors'&&hasSelection(),b=selectionBounds(),pieces=selectedObjects(),beyond=outside();
  const next=JSON.stringify([state.tool,state.applicator,state.brushWidth,state.stampScale,state.opacity,state.drawingMode,state.workspaceMode,selected,b,beyond,canRedo(),pieces.map(p=>[p.id,p.kind])]);if(signature===next)return;signature=next;
  document.getElementById('workspaceIdle')!.hidden=selected;document.getElementById('workspaceSelection')!.hidden=!selected;
  root.classList.toggle('selection-active',selected);root.classList.toggle('selection-outside',beyond);
  const info=TOOL_INFO[state.tool];document.getElementById('workspaceToolArt')!.innerHTML=toolArtwork(state.tool);document.getElementById('workspaceToolName')!.textContent=info.label;
  document.getElementById('workspaceToolDetail')!.textContent=`${state.tool==='stamp'?`${state.stampScale.toFixed(1)}×`:['draw','spray','eraser','sponge','shapes','spiro'].includes(state.tool)?`${state.brushWidth} px`:vectorDrawingEnabled()?'Editable pieces':'Pixels'} · ${Math.round(state.opacity*100)}%`;
  document.getElementById('workspaceIdle')!.title=info.hint;
  (document.getElementById('workspaceRedo') as HTMLButtonElement).disabled=!canRedo();
  const rasterCount=pieces.filter(p=>p.kind==='raster').length,kind=pieces.length>1?`${pieces.length} pieces`:pieces.length===1?pieces[0].kind==='raster'?'Raster piece':'Vector piece':'Raster selection';
  document.getElementById('workspaceSelectionType')!.textContent=kind;
  document.getElementById('workspaceSelectionSize')!.textContent=b?`${Math.round(b.width)} × ${Math.round(b.height)} px${beyond?(rasterCount&&rasterCount<pieces.length?' · rasters trim on Place':rasterCount||!pieces.length?' · trims on Place':' · whole shape kept'):''}`:'';
  document.getElementById('workspaceCentre')!.hidden=!beyond;document.getElementById('workspaceDuplicate')!.hidden=!pieces.length;
  document.getElementById('workspaceCancel')!.innerHTML=icon(pieces.length?'undo':'close');const cancelLabel=pieces.length?'Undo last change':'Cancel selection';document.getElementById('workspaceCancel')!.setAttribute('aria-label',cancelLabel);document.getElementById('workspaceCancel')!.title=cancelLabel;
}
