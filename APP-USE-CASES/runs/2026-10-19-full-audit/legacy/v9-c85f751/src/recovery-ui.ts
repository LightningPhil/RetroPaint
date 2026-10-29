import { artwork } from './artwork';
import { bus,emit } from './bus';
import { H,view,W } from './canvas';
import { outputFrame } from './document-frame';
import { editable,message,settle } from './editor';
import { isBusy } from './effects';
import { icon } from './icons';
import { inputActive } from './input';
import { hasObjectCapture } from './objects';
import { photoEditing } from './photo-preview';
import { loadProjectData,projectDataAsync,saveProjectFile } from './project';
import { RecoveryStore,type DraftInfo } from './recovery-store';
import { hasFloatingSelection } from './selection';
import { motorOn } from './spiro';
import { state } from './state';
import { hasText } from './text-tool';
import { layers } from './layers';

const fixture=location.pathname.includes('/tests/')||new URLSearchParams(location.search).has('layout-preview');
const store=new RecoveryStore(fixture?`RetroPaintDraftUiChecks-${innerWidth}x${innerHeight}`:undefined);
let documentId='',dirty=0,saved=0,timer=0,saving=false,page=0,entries:DraftInfo[]=[],ready=false,offered=false;
let status:HTMLButtonElement,dialog:HTMLDialogElement,banner:HTMLElement;
function freshId():string {return window.crypto?.randomUUID?.()??`picture-${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;}
function rememberId():void {try{sessionStorage.setItem('retropaint-document',documentId);}catch{/* Storage can be disabled. */}}
function statusText(label:string,detail:string):void {status.textContent=label;status.title=detail;status.setAttribute('aria-label',detail);status.dataset.project=String(label==='Save a project');}
function postpone():void {clearTimeout(timer);timer=window.setTimeout(()=>void saveDraft(),3000);}
function markDirty():void {
  dirty++;if(offered){documentId=freshId();rememberId();offered=false;banner.hidden=true;}
  rememberId();
  statusText('Draft pending','Your next draft will be saved in this browser after you finish editing.');postpone();
}
function newDocument():void {documentId=freshId();rememberId();offered=false;banner.hidden=true;markDirty();}
function thumbnail():string {
  const frame=outputFrame(view.width,view.height),canvas=document.createElement('canvas'),scale=Math.min(1,160/frame.width,100/frame.height);
  canvas.width=Math.max(1,Math.round(frame.width*scale));canvas.height=Math.max(1,Math.round(frame.height*scale));
  canvas.getContext('2d')!.drawImage(view,frame.x,frame.y,frame.width,frame.height,0,0,canvas.width,canvas.height);return canvas.toDataURL('image/png');
}
async function saveDraft():Promise<void> {
  if(!ready||saving||dirty===saved||artwork.snapshot()===null)return;
  if(state.busy||state.cad.gesture||isBusy()||motorOn()||inputActive()||hasObjectCapture()||hasFloatingSelection()||state.poly.length||state.tool==='text'&&hasText()||photoEditing){postpone();return;}
  const pixels=W*H*layers.length+layers.reduce((sum,layer)=>sum+(layer.objects??[]).reduce((count,piece)=>count+(piece.kind==='raster'?piece.width*piece.height:0),0),0);
  if(pixels>24_000_000){saved=dirty;statusText('Save a project','Use Save project for this large picture. Automatic drafts pause above 24 million stored pixels to keep drawing responsive.');return;}
  const generation=dirty,id=documentId,width=W,height=H,name=(document.getElementById('fileName') as HTMLInputElement).value.trim()||'Untitled picture',preview=thumbnail();
  saving=true;statusText('Saving draft…','Saving an editable draft in this browser.');
  try{
    const data=await projectDataAsync();if(data.length>50_000_000)throw new Error('This picture is too large for automatic drafts. Use Save project to keep an editable copy.');
    const savedAt=Date.now();await store.save({id,name,width,height,savedAt,thumbnail:preview,data,bytes:data.length*2});
    if(documentId===id){saved=generation;statusText('Draft saved',`Draft saved in this browser at ${new Date(savedAt).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}. Open recent drafts.`);}
  }catch(error){if(documentId===id){statusText('Save a project',error instanceof Error?error.message:'Draft storage is full or unavailable. Save a project to keep an editable copy.');saved=dirty;}}
  finally{saving=false;if(dirty!==saved)postpone();}
}
function renderPage():void {
  const count=innerHeight<480?2:3;page=Math.min(page,Math.max(0,Math.ceil(entries.length/count)-1));
  const list=document.getElementById('recoveryList')!;list.replaceChildren();
  for(const draft of entries.slice(page*count,page*count+count)){
    const card=document.createElement('button');card.type='button';card.className='recovery-card';
    const image=document.createElement('img');image.src=draft.thumbnail;image.alt='';
    const info=document.createElement('span'),name=document.createElement('strong'),detail=document.createElement('small'),action=document.createElement('b');
    name.textContent=draft.name;detail.textContent=`${draft.width} × ${draft.height} · ${new Date(draft.savedAt).toLocaleString([],{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})}`;action.textContent='Resume →';info.append(name,detail,action);card.append(image,info);
    card.addEventListener('click',()=>void resume(draft.id,card));list.append(card);
  }
  document.getElementById('recoveryEmpty')!.hidden=entries.length>0;document.getElementById('recoveryPagination')!.hidden=entries.length<=count;
  (document.getElementById('recoveryPrevious') as HTMLButtonElement).disabled=page===0;(document.getElementById('recoveryNext') as HTMLButtonElement).disabled=(page+1)*count>=entries.length;
  document.getElementById('recoveryPage')!.textContent=`${page+1} / ${Math.max(1,Math.ceil(entries.length/count))}`;
}
async function openRecovery():Promise<void> {
  if(!editable())return;emit('close-options');
  try{entries=await store.list();page=0;renderPage();dialog.showModal();}
  catch{message('This browser cannot access local drafts. Save project keeps an editable file on your device.');}
}
async function resume(id:string,button:HTMLButtonElement):Promise<void> {
  if(!editable())return;button.disabled=true;
  try{
    const draft=await store.read(id);if(!draft)throw new Error('This draft is no longer available.');
    if(!await loadProjectData(draft.data))return;rememberId();saved=dirty;offered=false;banner.hidden=true;
    (document.getElementById('fileName') as HTMLInputElement).value=draft.name;statusText('Draft restored','Draft restored. Further edits will be saved in this browser.');
    if(dialog.open)dialog.close();message('Draft restored, including editable pieces and photo adjustments. Undo returns to your previous picture.');
  }catch(error){message(error instanceof Error?error.message:String(error));}
  finally{button.disabled=false;}
}
export function initRecoveryUi():void {
  status=document.createElement('button');status.type='button';status.id='draftStatus';statusText('Local drafts','Recent editable drafts are kept in this browser. Save project keeps a separate copy on your device.');status.addEventListener('click',()=>{if(status.dataset.project==='true'){if(!editable())return;settle();void saveProjectFile((document.getElementById('fileName') as HTMLInputElement).value).catch(error=>message(error instanceof Error?error.message:String(error)));}else void openRecovery();});document.getElementById('workspaceIdle')!.append(status);
  const recover=document.createElement('button');recover.type='button';recover.className='choice';recover.id='openRecovery';recover.innerHTML=`${icon('undo')}<span>Recent drafts</span>`;recover.addEventListener('click',()=>void openRecovery());document.querySelector('[data-studio-panel=file]>.row')!.append(recover);
  dialog=document.createElement('dialog');dialog.id='recoveryDialog';dialog.setAttribute('aria-labelledby','recoveryTitle');
  dialog.innerHTML=`<div class="preferences-heading"><div>${icon('save')}<h2 id="recoveryTitle">Pick up your picture</h2></div><button class="drawer-close" type="button" aria-label="Close recent drafts">${icon('close')}</button></div><p class="hint">Recent drafts from this browser. Save project keeps your own editable copy.</p><div id="recoveryList"></div><p id="recoveryEmpty">Your next picture will appear here after you finish drawing.</p><div id="recoveryPagination"><button class="choice" type="button" id="recoveryPrevious" aria-label="Previous drafts">${icon('back')}</button><span id="recoveryPage"></span><button class="choice" type="button" id="recoveryNext" aria-label="Next drafts">${icon('redo')}</button></div><footer><small>Up to eight recent pictures · saved on this device</small><button class="choice" type="button" id="recoveryDone">Done</button></footer>`;
  document.body.append(dialog);dialog.querySelector('.drawer-close')!.addEventListener('click',()=>dialog.close());document.getElementById('recoveryDone')!.addEventListener('click',()=>dialog.close());dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
  document.getElementById('recoveryPrevious')!.addEventListener('click',()=>{page--;renderPage();});document.getElementById('recoveryNext')!.addEventListener('click',()=>{page++;renderPage();});
  window.addEventListener('resize',()=>{if(dialog.open)renderPage();});
  banner=document.createElement('div');banner.id='recoveryBanner';banner.hidden=true;banner.innerHTML='<span>Your last picture is here.</span><button class="choice" type="button">Resume</button><button type="button" class="recovery-dismiss" aria-label="Dismiss resume suggestion">×</button>';document.getElementById('canvasSlot')!.append(banner);
  banner.querySelector('.recovery-dismiss')!.addEventListener('click',()=>{banner.hidden=true;});
  // Regression fixtures never read or replace the person's real drafts.
  if(fixture){statusText('Test preview','Draft saving is disabled in test previews.');return;}
  let initial:string|null=null;try{initial=sessionStorage.getItem('retropaint-document');}catch{/* Optional storage. */}
  // A fresh working ID also isolates duplicated tabs, which may copy session storage.
  documentId=freshId();initial??=documentId;
  void store.read(initial).then(draft=>{
    if(draft&&dirty===0){offered=true;banner.hidden=false;banner.querySelector('button')!.addEventListener('click',event=>void resume(draft.id,event.currentTarget as HTMLButtonElement));}
    ready=true;if(dirty!==saved)postpone();
  }).catch(()=>{ready=true;statusText('Save a project','Local draft storage is unavailable. Save project keeps an editable copy on your device.');});
  bus.addEventListener('history',markDirty);bus.addEventListener('layers',markDirty);bus.addEventListener('document-created',newDocument);bus.addEventListener('document-opened',newDocument);document.addEventListener('document-frame',markDirty);
  bus.addEventListener('cad-preview',markDirty);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)void saveDraft();});
}
