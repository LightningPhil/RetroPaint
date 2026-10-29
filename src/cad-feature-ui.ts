import { currentBodies, replaceBodies, selectBodies, selectedBodies } from './cad-document';
import { cadCompute } from './cad-engine';
import { editFeature, featureAt, featureInputView, featureName, featureTimeline, featureTree, historyStage, prepareFeatureHistory, resizeSketch, setFeaturePlane, sketchBounds, sketchType, type FeatureEntry } from './cad-features';
import { readCadLayer, type CadBody, type V2, type V3 } from './cad-model';
import type { CadViewport } from './cad-viewport';
import { state } from './state';
import { CadFormEditor, type ProfileSource } from './cad-form-ui';
import type { CadProfile } from './cad-model';
import { CadSketchEditor } from './cad-sketch-ui';
import { solveSketch } from './cad-sketch-constraints';

interface Callbacks { viewport:()=>CadViewport|undefined; notice:(text:string)=>void; run:(action:()=>Promise<void>)=>Promise<void>; changed:()=>void; open:()=>void; pick:()=>void; sources:()=>ProfileSource[]; drawing:()=>CadProfile|undefined }
interface Draft { source:CadBody; root:CadBody; entry:FeatureEntry }
const esc=(s:string)=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
const icon=(entry:FeatureEntry)=>entry.sketch?'✎':entry.item.solid.kind==='loft'?'⋈':entry.item.solid.kind==='sweep'?'∿':entry.item.solid.kind==='shell'?'▣':entry.item.solid.kind==='finish'?(entry.item.solid.mode==='fillet'?'◜':'◩'):entry.item.solid.kind==='boolean'?'⊕':entry.item.solid.kind==='revolve'?'⟳':entry.item.solid.kind==='extrude'?'↑':'◇';
const btn=(id:string,text:string)=>`<button class="choice" type="button" id="${id}">${text}</button>`;
const field=(id:string,label:string,value:number,min=-2000,max=2000,step=.1)=>`<label>${label}<input id="${id}" type="number" min="${min}" max="${max}" step="${step}" value="${Math.round(value*10000)/10000}"></label>`;
/** The draft and rollback views never mutate document recipes or the Undo stack. */
export class CadFeaturePanel {
  private rootId='';
  private key='root';
  private page=0;
  private timelinePage=0;
  private rollback=-1;
  private signature='';
  private draft:Draft|undefined;
  private previewSource:CadBody|undefined;
  private point=0;
  private sketchMode='geometry';
  private drag:number|null=null;
  private panel:HTMLElement;
  private formEditor:CadFormEditor|undefined;
  private timeline:HTMLElement;
  constructor(private host:HTMLElement,private callbacks:Callbacks){
    this.panel=document.createElement('div');this.panel.id='cadPagehistory';this.panel.className='cad-panel-page';this.panel.dataset.cadPanel='history';this.panel.hidden=true;
    this.panel.innerHTML='<div class="cad-page-content" id="cadFeatureContent"></div>';
    host.querySelector('.cad-snap-bar')!.before(this.panel);
    this.timeline=document.createElement('section');this.timeline.id='cadTimeline';this.timeline.className='cad-timeline';this.timeline.setAttribute('aria-label','Solid feature timeline');host.querySelector('#cadView')!.append(this.timeline);
  }
  private el<T extends HTMLElement=HTMLElement>(id:string):T{return this.host.querySelector<T>('#'+id)!;}
  private root():CadBody|undefined{return currentBodies().find(b=>b.id===this.rootId);}
  private entry():FeatureEntry|undefined {const root=this.root();return root?featureTree(root).find(e=>e.key===this.key):undefined;}
  reset():void{this.draft=undefined;this.previewSource=undefined;state.cad.preview=null;state.cad.editing=false;this.rollback=-1;this.signature='';this.rootId='';this.host.classList.remove('cad-history-preview','cad-feature-editing');}
  async latest():Promise<void>{state.cad.preview=null;this.previewSource=undefined;this.rollback=-1;this.callbacks.viewport()?.clearSketch();if(['edge','shellFace'].includes(state.cad.tool)){state.cad.tool='translate';this.callbacks.viewport()?.setTool();}this.host.classList.remove('cad-history-preview');await this.callbacks.viewport()?.sync();this.callbacks.viewport()?.updatePreviews();this.renderTimeline();this.callbacks.notice('Latest solid. All current features rebuilt.');}
  async newFeature(next:CadBody):Promise<void>{
    const source=currentBodies().find(b=>b.id===next.id);if(!source||source.locked)throw new Error('Select an unlocked solid first.');
    await this.latest();this.rootId=source.id;this.key='root';this.page=0;this.draft={source,root:next,entry:featureTree(next)[0]};state.cad.editing=true;this.host.classList.add('cad-feature-editing');this.renderEditor();this.callbacks.open();await this.rebuild(false);
  }
  refresh():void{
    const chosen=selectedBodies()[0]??this.root()??currentBodies()[0];
    if(state.cad.preview&&!this.draft&&this.root()!==this.previewSource){state.cad.preview=null;this.rollback=-1;this.host.classList.remove('cad-history-preview');queueMicrotask(()=>{if(state.cad.open)void this.callbacks.viewport()?.sync();});}
    if(this.draft&&(!chosen||chosen.id!==this.rootId||this.root()!==this.draft.source)){this.draft=undefined;state.cad.editing=false;state.cad.preview=null;this.host.classList.remove('cad-feature-editing','cad-history-preview');this.signature='';}
    if(chosen?.id!==this.rootId){this.rootId=chosen?.id??'';this.key='root';this.page=0;this.timelinePage=0;this.rollback=-1;state.cad.preview=null;this.signature='';this.host.classList.remove('cad-history-preview');}
    const signature=JSON.stringify([currentBodies(),this.rootId,this.key,this.page]);
    if(signature!==this.signature&&!this.draft){this.signature=signature;this.renderTree();}
    this.renderTimeline();
  }
  private renderTree():void{
    const content=this.el('cadFeatureContent'),root=this.root();
    if(!root){content.innerHTML='<h2>A story for every solid</h2><p class="cad-hint">Add a shape or select a solid. Its original sketches and build steps stay editable here.</p>';return;}
    const entries=featureTree(root),selected=entries.find(e=>e.key===this.key)??entries[0];this.key=selected.key;
    const pages=Math.ceil(entries.length/5);this.page=Math.min(this.page,pages-1);
    content.innerHTML=`<label class="cad-full-field">Solid<select id="cadHistoryBody">${currentBodies().map(b=>`<option value="${esc(b.id)}" ${b.id===root.id?'selected':''}>${esc(b.name)}</option>`).join('')}</select></label><div class="cad-feature-heading"><h2>Feature tree</h2><span>${entries.filter(e=>!e.sketch).length} steps</span></div><div class="cad-feature-tree" role="tree" aria-label="Editable solid features">${entries.slice(this.page*5,this.page*5+5).map(e=>`<button class="choice cad-feature-row ${e.key===selected.key?'active':''} ${e.item.solid.feature?.suppressed?'suppressed':''}" type="button" role="treeitem" aria-level="${e.depth+1}" aria-selected="${e.key===selected.key}" data-feature-key="${e.key}" style="--depth:${Math.min(4,e.depth)}"><span>${icon(e)}</span><span>${esc(e.label)}</span><small>${e.item.solid.feature?.suppressed?'off':e.sketch?'mm':e.item.solid.kind}</small></button>`).join('')}</div><div class="cad-pagination">${btn('cadFeaturesPrev','←')}<span>${this.page+1} / ${pages}</span>${btn('cadFeaturesNext','→')}</div><div class="cad-feature-summary"><strong>${esc(selected.label)}</strong><p id="cadFeatureDependencies">${esc(this.description(selected))}</p></div><div class="cad-actions">${btn('cadFeatureEdit',selected.sketch?'✎ Edit sketch':'✎ Edit feature')}${btn('cadFeatureSuppress',selected.item.solid.feature?.suppressed?'◉ Enable':'◌ Suppress')}</div><p class="cad-hint">Changes rebuild the later steps. Sketches, cutters and original solids stay inside the finished piece.</p>`;
    this.el<HTMLSelectElement>('cadHistoryBody').onchange=()=>{selectBodies([this.el<HTMLSelectElement>('cadHistoryBody').value]);this.refresh();};
    this.el<HTMLButtonElement>('cadFeaturesPrev').disabled=this.page===0;this.el<HTMLButtonElement>('cadFeaturesNext').disabled=this.page===pages-1;
    this.el('cadFeaturesPrev').onclick=()=>{this.page--;this.signature='';this.refresh();this.callbacks.changed();};this.el('cadFeaturesNext').onclick=()=>{this.page++;this.signature='';this.refresh();this.callbacks.changed();};
    for(const row of content.querySelectorAll<HTMLElement>('[data-feature-key]')){row.onclick=()=>{this.key=row.dataset.featureKey!;this.signature='';this.refresh();this.callbacks.changed();};row.ondblclick=()=>void this.callbacks.run(()=>this.begin());row.onkeydown=event=>{const index=entries.findIndex(e=>e.key===row.dataset.featureKey),e=entries[index];let next=index;if(event.key==='ArrowDown')next=Math.min(entries.length-1,index+1);else if(event.key==='ArrowUp')next=Math.max(0,index-1);else if(event.key==='Home')next=0;else if(event.key==='End')next=entries.length-1;else if(event.key==='ArrowLeft')next=Math.max(0,entries.findIndex(entry=>!entry.sketch&&entry.key===(e.sketch?e.path.join('.')||'root':e.path.slice(0,-1).join('.')||'root')));else if(event.key==='ArrowRight')next=index+1<entries.length&&entries[index+1].depth>e.depth?index+1:index;else return;event.preventDefault();this.key=entries[next].key;this.page=Math.floor(next/5);this.signature='';this.refresh();this.host.querySelector<HTMLElement>(`[data-feature-key="${this.key}"]`)?.focus();this.callbacks.changed();};}
    this.el<HTMLButtonElement>('cadFeatureEdit').disabled=root.locked;
    this.el<HTMLButtonElement>('cadFeatureSuppress').disabled=root.locked||selected.sketch||(!['boolean','finish','shell'].includes(selected.item.solid.kind)&&(!selected.path.length||selected.path.at(-1)===0));
    this.el('cadFeatureEdit').onclick=()=>void this.callbacks.run(()=>this.begin());this.el('cadFeatureSuppress').onclick=()=>void this.callbacks.run(()=>this.suppress());
  }
  private description(e:FeatureEntry):string{
    const s=e.item.solid;
    if(s.kind==='mesh')return `${s.sourceName} · ${s.indices.length/3} triangles · original imported mesh preserved · editable position and size`;
    if(s.kind==='loft'||s.kind==='sweep'){
      if(e.sweepPath&&s.kind==='sweep')return `${s.path.points.length} points · ${s.path.smooth?'smooth interpolating curve':'straight segments'} · editable x, y, z in mm`;
      if(e.profile!==undefined){const p=s.kind==='loft'?s.profiles[e.profile]:s.profile,b=sketchBounds(solveSketch(p.points,p.constraints,p.shape));return `${p.shape} · ${b.width.toFixed(1)} × ${b.height.toFixed(1)} mm${p.constraints?.length?' · '+p.constraints.length+' saved dimensions / relations':''} · ${s.kind==='sweep'?'follows path tangent':'origin '+p.plane.origin.join(', ')+' mm'}`;}
      return s.kind==='loft'?`${s.profiles.length} editable sketches · ${s.ruled?'ruled sides':'smooth sides'} · sketches preserved`:`Editable profile + ${s.path.points.length}-point path · ${s.path.smooth?'smooth curve':'straight segments'} · ${s.roll}° profile turn`;
    }
    if(e.sketch&&(s.kind==='extrude'||s.kind==='revolve'))return `${s.points.length} points${s.feature?.constraints?.length?' · '+s.feature.constraints.length+' saved dimensions / relations':''} · ${s.feature?.attachment?'follows supporting face':'fixed workplane'} · editable in mm`;
    if(s.kind==='primitive')return `${s.size.join(' × ')} mm${s.shape==='tube'?` · wall ${s.wall} mm`:''}`;
    if(s.kind==='extrude')return `${s.feature?.through?'Through all':Math.abs(s.height)+' mm deep'} · taper ${s.taper}× · twist ${s.twist}°`;
    if(s.kind==='revolve')return `${s.degrees}° · ${s.points.length} profile points · editable axis`;
    if(s.kind==='shell')return `${s.thickness} mm walls · ${s.faces.length?s.faces.length+(s.faces.length===1?' open face':' open faces'):'enclosed cavity'} · original solid preserved`;
    if(s.kind==='finish')return `${s.size} mm ${s.mode==='fillet'?'radius':'setback'} · ${s.edges.length} selected edges · original solid preserved`;
    return `Uses ${s.children.map(b=>featureName(b)).join(' + ')}. ${s.feature?.suppressed?'Bypassed; inputs are preserved.':'Inputs remain editable.'}`;
  }
  private renderTimeline():void{
    const root=this.root(),entries=root?featureTimeline(root):[],size=matchMedia('(max-width:600px)').matches?3:6;
    this.timeline.hidden=!entries.length;this.host.classList.toggle('cad-has-timeline',!!entries.length);if(!entries.length)return;
    this.timelinePage=Math.min(this.timelinePage,Math.max(0,Math.ceil(entries.length/size)-1));
    const signature=JSON.stringify([root?.id,entries.map(e=>[e.key,e.label,e.item.solid.feature?.suppressed]),this.timelinePage,this.rollback,!!this.draft]);if(this.timeline.dataset.signature===signature)return;this.timeline.dataset.signature=signature;
    this.timeline.innerHTML=`<div class="cad-timeline-top">${btn('cadTimelineTree','▱ History')}<span id="cadTimelinePosition">${this.rollback<0?'Latest solid':`Viewing step ${this.rollback+1} of ${entries.length}`}</span>${btn('cadTimelineLatest','Latest ↠')}</div><div class="cad-timeline-track">${btn('cadTimelinePrevious','‹')}<div class="cad-timeline-steps">${entries.slice(this.timelinePage*size,this.timelinePage*size+size).map((e,i)=>{const index=this.timelinePage*size+i;return `<button class="choice ${this.rollback===index?'active':''} ${e.item.solid.feature?.suppressed?'suppressed':''}" type="button" data-cad-step="${index}" aria-label="View step ${index+1}: ${esc(e.label)}" aria-pressed="${this.rollback===index}" title="${esc(e.label)}"><span>${icon(e)}</span><small>${index+1}. ${esc(e.label)}</small></button>`;}).join('')}</div>${btn('cadTimelineNext','›')}</div><input type="range" id="cadHistoryPlayhead" min="0" max="${entries.length-1}" value="${this.rollback<0?entries.length-1:this.rollback}" aria-label="History playhead"></input>`;
    this.el('cadTimelineTree').onclick=()=>this.callbacks.open();
    this.el<HTMLButtonElement>('cadTimelineLatest').disabled=this.rollback<0||!!this.draft;this.el('cadTimelineLatest').onclick=()=>void this.callbacks.run(()=>this.latest());
    this.el<HTMLButtonElement>('cadTimelinePrevious').disabled=this.timelinePage===0;this.el<HTMLButtonElement>('cadTimelineNext').disabled=(this.timelinePage+1)*size>=entries.length;
    this.el('cadTimelinePrevious').onclick=()=>{this.timelinePage--;this.renderTimeline();};this.el('cadTimelineNext').onclick=()=>{this.timelinePage++;this.renderTimeline();};
    for(const b of this.timeline.querySelectorAll<HTMLElement>('[data-cad-step]')){b.onclick=()=>void this.callbacks.run(()=>this.inspect(Number(b.dataset.cadStep)));b.setAttribute('aria-disabled',String(!!this.draft));}
    this.el<HTMLInputElement>('cadHistoryPlayhead').disabled=!!this.draft;this.el('cadHistoryPlayhead').onchange=()=>void this.callbacks.run(()=>this.inspect(Number(this.el<HTMLInputElement>('cadHistoryPlayhead').value)));
  }
  private async inspect(index:number):Promise<void>{
    if(this.draft)throw new Error('Apply or cancel your feature edit before moving along the timeline.');
    const root=this.root();if(!root)return;const entries=featureTimeline(root),entry=entries[index];if(!entry)return;
    this.key=entry.key;this.page=Math.floor(featureTree(root).findIndex(e=>e.key===this.key)/5);
    if(index===entries.length-1){await this.latest();}else{const preview=historyStage(root,index);await cadCompute([preview]);this.previewSource=root;state.cad.preview=preview;this.rollback=index;this.host.classList.add('cad-history-preview');await this.callbacks.viewport()?.sync();this.callbacks.notice(`History preview: ${entry.label}. Return to Latest to keep building, or edit this feature.`);}
    this.signature='';this.refresh();this.callbacks.open();
  }
  private async begin():Promise<void>{
    const root=this.root(),entry=this.entry();if(!root||!entry||root.locked)return;
    await this.latest();const prepared=await prepareFeatureHistory(root);
    this.draft={source:root,root:prepared,entry};this.sketchMode=featureAt(prepared,entry.path).solid.feature?.constraints?.length?'constraints':'geometry';state.cad.editing=true;this.host.classList.add('cad-feature-editing');this.point=0;this.callbacks.viewport()?.selection();this.renderEditor();this.renderTimeline();this.callbacks.changed();this.callbacks.notice('Edit the original feature. Preview rebuilds the whole solid; Apply keeps it and Cancel restores it.');
  }
  private async suppress():Promise<void>{
    const root=this.root(),entry=this.entry();if(!root||!entry)return;
    const next=editFeature(root,entry.path,item=>{item.solid.feature={...item.solid.feature,suppressed:!item.solid.feature?.suppressed};});
    await cadCompute([next]);state.cad.preview=null;this.rollback=-1;this.host.classList.remove('cad-history-preview');replaceBodies(currentBodies().map(b=>b.id===root.id?next:b));await this.callbacks.viewport()?.sync();this.signature='';this.refresh();this.callbacks.notice('Feature updated. Its original inputs are preserved; Undo restores this change.');
  }
  private draftItem():CadBody{if(!this.draft)throw new Error('Select a feature to edit.');return featureAt(this.draft.root,this.draft.entry.path);}
  private number(id:string,min=-2000,max=2000):number{const input=this.el<HTMLInputElement>(id),value=Number(input.value);if(!input.value.trim()||!Number.isFinite(value)||value<min||value>max)throw new Error(`${input.closest('label')?.textContent?.trim()??'Value'} must be between ${min} and ${max}.`);return value;}
  private renderEditor():void{
    const d=this.draft!;const item=this.draftItem(),s=item.solid,sketch=d.entry.sketch&&(s.kind==='extrude'||s.kind==='revolve');
    let controls='';
    if(s.kind==='mesh')controls='<p class="cad-hint">Original imported STL mesh. Its source triangles stay intact inside later features. Use Edit to move, rotate or resize the solid; sketch cuts and boolean operations stay editable in History.</p>';
    else if(s.kind==='loft'||s.kind==='sweep')controls='<div id="cadFeatureForm"></div>';
    else if(sketch&&(s.kind==='extrude'||s.kind==='revolve')){
      const shape=sketchType(s);s.points=solveSketch(s.points,s.feature?.constraints,shape);const b=sketchBounds(s.points);
      if(this.sketchMode==='constraints')controls='<div id="cadFeatureConstraints" class="cad-constraint-editor"></div>';
      else if(shape==='rectangle'||shape==='circle')controls=`<div class="cad-fields">${field('cadFeatureSketchX',shape==='circle'?'Centre X · mm':'Start X · mm',shape==='circle'?b.x+b.width/2:b.x)}${field('cadFeatureSketchY',shape==='circle'?'Centre Y · mm':'Start Y · mm',shape==='circle'?b.y+b.height/2:b.y)}${field('cadFeatureSketchWidth',shape==='circle'?'Diameter X · mm':'Width · mm',b.width,.1)}${field('cadFeatureSketchHeight',shape==='circle'?'Diameter Y · mm':'Height · mm',b.height,.1)}</div>`;
      else controls='<svg id="cadFeatureSketch" aria-label="Editable original sketch" role="img"></svg><div class="cad-fields"><label>Point<select id="cadFeaturePoint"></select></label>'+btn('cadFeatureRemovePoint','− Remove point')+'</div><div class="cad-fields">'+field('cadFeaturePointX',s.kind==='revolve'?'Radius · mm':'X · mm',s.points[this.point]?.[0]??0,s.kind==='revolve'?0:-2000)+field('cadFeaturePointY','Y / height · mm',s.points[this.point]?.[1]??0)+'</div><label class="cad-full-field">Sketch points · x,y; x,y<textarea id="cadFeaturePoints" rows="2" spellcheck="false"></textarea></label>';
      controls=`<label class="cad-full-field">Edit sketch<select id="cadFeatureSketchMode"><option value="geometry" ${this.sketchMode==='geometry'?'selected':''}>Outline & workplane</option><option value="constraints" ${this.sketchMode==='constraints'?'selected':''}>Dimensions & constraints</option></select></label><div id="cadFeatureSketchControls">${controls}</div>`+(this.sketchMode==='geometry'?`<label class="cad-full-field">${s.kind==='revolve'?'Revolve axis / sketch plane':'Sketch support'}<select id="cadFeaturePlane"><option value="keep">${s.feature?.attachment?'Follow supporting face':'Keep current workplane'}</option><option value="xy">Fixed XY · Z axis</option><option value="xz">Fixed XZ · −Y axis</option><option value="yz">Fixed YZ · X axis</option></select></label><div id="cadFeaturePlaneOrigin" hidden><div class="cad-fields three">${s.plane.origin.map((v,i)=>field('cadFeatureOrigin'+i,['Origin X','Origin Y','Origin Z'][i],v,-10000,10000)).join('')}</div></div>`:'');
    }else if(s.kind==='primitive')controls=`<div class="cad-fields three">${s.size.map((v,i)=>field('cadFeatureSize'+i,['Width X','Depth Y','Height Z'][i],v,.1)).join('')}</div>${s.shape==='tube'?field('cadFeatureWall','Wall · mm',s.wall,.1,1000):''}`;
    else if(s.kind==='extrude')controls=`<div class="cad-fields">${field('cadFeatureDepth','Depth · mm',Math.abs(s.height),.05)}<label>Direction<select id="cadFeatureDirection"><option value="1" ${s.height>0?'selected':''}>Outwards</option><option value="-1" ${s.height<0?'selected':''}>Inwards / hole</option></select></label>${field('cadFeatureTaper','Top size ×',s.taper,.01,5,.05)}${field('cadFeatureTwist','Twist °',s.twist,-720,720,1)}</div>${s.feature?.attachment?`<label class="cad-check"><input id="cadFeatureThrough" type="checkbox" ${s.feature.through?'checked':''}> Through all · follows solid depth</label>`:''}<p class="cad-hint">To change the hole diameter or outline, edit the sketch directly below this feature in the tree.</p>`;
    else if(s.kind==='revolve')controls=field('cadFeatureDegrees','Revolve angle · °',s.degrees,1,360,1)+'<p class="cad-hint">Edit Profile sketch to change radii, wall thickness, heights or the axis.</p>';
    else if(s.kind==='shell')controls=`${field('cadFeatureThickness','Wall thickness · mm',s.thickness,.01,1000)}<p class="cad-edge-count" id="cadFeatureFaceCount">${s.faces.length} ${s.faces.length===1?'face':'faces'} left open · ${s.faces.length?'pink faces will be removed':'enclosed cavity'}</p>${btn('cadFeatureReselectFaces','▧ Reselect open faces')}<div class="cad-actions" id="cadFeatureFaceActions" hidden>${btn('cadFeatureNoFaces','Clear openings')}</div>`;
    else if(s.kind==='finish')controls=`<div class="cad-fields"><label>Finish<select id="cadFeatureFinishMode"><option value="fillet" ${s.mode==='fillet'?'selected':''}>Fillet · round</option><option value="chamfer" ${s.mode==='chamfer'?'selected':''}>Chamfer · bevel</option></select></label>${field('cadFeatureFinishSize',s.mode==='fillet'?'Radius · mm':'Setback · mm',s.size,.01,1000)}</div><p class="cad-hint" id="cadFeatureEdgeCount">${s.edges.length} selected edges · original solid preserved</p>${btn('cadFeatureReselectEdges','⌁ Reselect edges')}<div class="cad-actions" id="cadFeatureEdgeActions" hidden>${btn('cadFeatureAllEdges','Select all')}${btn('cadFeatureNoEdges','Clear')}</div>`;
    else controls=`<label class="cad-full-field">Build operation<select id="cadFeatureBoolean">${[['union','Join'],['subtract','Cut / hole'],['intersect','Keep overlap'],['hull','Convex hull']].map(([op,label])=>`<option value="${op}" ${s.operation===op?'selected':''}>${label}</option>`).join('')}</select></label><p class="cad-hint">The first input is the target. Later inputs are tools. Edit each input in the feature tree to change its original dimensions.</p>`;
    this.el('cadFeatureContent').innerHTML=`<div class="cad-feature-heading"><h2>${sketch?'✎ Edit original sketch':['finish','shell','loft','sweep'].includes(s.kind)?'✎ '+esc(d.entry.sketch?d.entry.label:featureName(item)):'✎ Edit feature'}</h2>${sketch||(['finish','shell','loft','sweep'].includes(s.kind)&&!d.entry.sketch)?btn('cadFeatureRename','Rename'):''}</div><label class="cad-full-field" id="cadFeatureNameRow" ${sketch||['finish','shell','loft','sweep'].includes(s.kind)?'hidden':''}>Feature name<input id="cadFeatureName" maxlength="60" value="${esc(sketch?(s.feature?.sketchName??d.entry.label):(s.feature?.label??featureName(item)))}"></label>${controls}<p id="cadFeatureError" class="cad-feature-error" role="alert" hidden></p>${btn('cadFeaturePreview','◈ Preview rebuilt solid')}<div class="cad-actions">${btn('cadFeatureApply','✓ Apply')}${btn('cadFeatureCancel','Cancel')}</div><small class="cad-hint">Later features rebuild automatically. Nothing changes in your project until Apply.</small>`;
    for(const [id,apply]of [['cadFeaturePreview',false],['cadFeatureApply',true]] as const)this.el(id).onclick=()=>void this.callbacks.run(()=>this.rebuild(apply));
    this.el('cadFeatureCancel').onclick=()=>void this.callbacks.run(()=>this.cancel());
    if(this.host.querySelector('#cadFeatureRename'))this.el('cadFeatureRename').onclick=()=>{const row=this.el('cadFeatureNameRow');row.hidden=!row.hidden;if(!row.hidden)this.el('cadFeatureName').focus();this.callbacks.changed();};
    this.formEditor=undefined;
    if(s.kind==='loft'||s.kind==='sweep'){
      this.el('cadFeatureNameRow').hidden=true;
      this.formEditor=new CadFormEditor(this.el('cadFeatureForm'),s,'cadFeatureForm',{changed:this.callbacks.changed,notice:this.callbacks.notice,sources:this.callbacks.sources,drawing:this.callbacks.drawing,guide:form=>this.callbacks.viewport()?.showFeatureForm(d.root,d.entry.path,form)},{profile:d.entry.profile,path:d.entry.sweepPath,settings:!d.entry.sketch});
      this.formEditor.showGuide();
    }
    if(s.kind==='shell'){this.el('cadFeatureReselectFaces').onclick=()=>void this.callbacks.run(()=>this.reselectFaces());this.el('cadFeatureNoFaces').onclick=()=>this.callbacks.viewport()?.faces.selectNone();}
    if(s.kind==='finish'){
      const nameInput=this.el<HTMLInputElement>('cadFeatureName');nameInput.dataset.automatic=String(!s.feature?.label||s.feature.label===(s.mode==='fillet'?'Fillet':'Chamfer'));nameInput.oninput=()=>{nameInput.dataset.automatic='false';};
      this.el('cadFeatureReselectEdges').onclick=()=>void this.callbacks.run(()=>this.reselectEdges());
      this.el('cadFeatureAllEdges').onclick=()=>{try{this.callbacks.viewport()?.edges.selectAll();}catch(error){this.callbacks.notice(String(error));}};this.el('cadFeatureNoEdges').onclick=()=>this.callbacks.viewport()?.edges.selectNone();
      this.el('cadFeatureFinishMode').onchange=()=>{const round=this.el<HTMLSelectElement>('cadFeatureFinishMode').value==='fillet';this.el('cadFeatureFinishSize').closest('label')!.firstChild!.textContent=round?'Radius · mm':'Setback · mm';if(nameInput.dataset.automatic==='true')nameInput.value=round?'Fillet':'Chamfer';};
    }
    if(sketch&&(s.kind==='extrude'||s.kind==='revolve')){
      this.el<HTMLSelectElement>('cadFeatureSketchMode').onchange=()=>{try{const next=this.el<HTMLSelectElement>('cadFeatureSketchMode').value;this.collect();this.sketchMode=next;this.renderEditor();}catch(error){this.callbacks.notice(String(error));this.el<HTMLSelectElement>('cadFeatureSketchMode').value=this.sketchMode;}};
      if(this.sketchMode==='constraints'){const shape=sketchType(s);new CadSketchEditor(this.el('cadFeatureConstraints'),'cadFeatureConstraint',{points:()=>s.points,shape:()=>shape,constraints:()=>s.feature?.constraints,update:(points,constraints)=>{s.points=points;s.feature={...s.feature,sketch:shape,constraints};}},{changed:this.callbacks.changed,notice:this.callbacks.notice,guide:()=>{}});}
      else{
        this.el('cadFeaturePlane').onchange=()=>{this.el('cadFeaturePlaneOrigin').hidden=this.el<HTMLSelectElement>('cadFeaturePlane').value==='keep';this.callbacks.changed();};
        if(s.feature?.constraints?.length){for(const input of this.el('cadFeatureSketchControls').querySelectorAll<HTMLInputElement|HTMLSelectElement|HTMLButtonElement|HTMLTextAreaElement>('input,select,button,textarea'))input.disabled=true;this.el('cadFeatureSketchControls').inert=true;this.el('cadFeatureSketchControls').insertAdjacentHTML('beforeend','<p class="cad-hint">This outline is driven by saved constraints. Edit them in Dimensions & constraints.</p>');}
        else if(this.host.querySelector('#cadFeatureSketch'))this.bindSketch();
      }
    }
    if(!sketch&&s.kind==='extrude'&&s.feature?.attachment){const through=this.el<HTMLInputElement>('cadFeatureThrough'),sync=()=>{this.el<HTMLInputElement>('cadFeatureDepth').disabled=through.checked;this.el<HTMLSelectElement>('cadFeatureDirection').disabled=through.checked;if(through.checked)this.el<HTMLSelectElement>('cadFeatureDirection').value='-1';};through.onchange=sync;sync();}
    this.callbacks.changed();
  }
  private collect():void{
    const d=this.draft!,item=this.draftItem(),s=item.solid;const name=this.el<HTMLInputElement>('cadFeatureName').value.trim()||featureName(item);if(!d.entry.sketch||!['loft','sweep'].includes(s.kind))s.feature={...s.feature,[d.entry.sketch?'sketchName':'label']:!d.entry.sketch&&s.kind==='finish'&&this.el<HTMLInputElement>('cadFeatureName').dataset.automatic==='true'?undefined:name};
    if(s.kind==='loft'||s.kind==='sweep')this.formEditor?.read();
    else if(d.entry.sketch&&(s.kind==='extrude'||s.kind==='revolve')){
      if(this.sketchMode==='geometry'){
        if(!s.feature?.constraints?.length){if(sketchType(s)!=='polygon')resizeSketch(s,this.number('cadFeatureSketchX'),this.number('cadFeatureSketchY'),this.number('cadFeatureSketchWidth',.1),this.number('cadFeatureSketchHeight',.1));else s.points=this.readPoints();}
        const plane=this.el<HTMLSelectElement>('cadFeaturePlane').value;if(plane!=='keep')setFeaturePlane(s,plane as 'xy'|'xz'|'yz',[0,1,2].map(i=>this.number('cadFeatureOrigin'+i,-10000,10000)) as V3);
      }
      s.points=solveSketch(s.points,s.feature?.constraints,sketchType(s));
    }else if(s.kind==='primitive'){s.size=[0,1,2].map(i=>this.number('cadFeatureSize'+i,.1)) as V3;if(s.shape==='tube')s.wall=this.number('cadFeatureWall',.1,1000);}
    else if(s.kind==='extrude'){s.height=this.number('cadFeatureDepth',.05)*this.number('cadFeatureDirection',-1,1);s.taper=this.number('cadFeatureTaper',.01,5);s.twist=this.number('cadFeatureTwist',-720,720);if(s.feature?.attachment)s.feature.through=this.el<HTMLInputElement>('cadFeatureThrough').checked;}
    else if(s.kind==='revolve')s.degrees=this.number('cadFeatureDegrees',1,360);
    else if(s.kind==='shell')s.thickness=this.number('cadFeatureThickness',.01,1000);
    else if(s.kind==='finish'){s.size=this.number('cadFeatureFinishSize',.01,1000);s.mode=this.el<HTMLSelectElement>('cadFeatureFinishMode').value as 'fillet';}
    else if(s.kind==='boolean')s.operation=this.el<HTMLSelectElement>('cadFeatureBoolean').value as 'union';
    readCadLayer({units:'mm',bodies:[d.root]});
  }
  private async reselectEdges():Promise<void>{
    const d=this.draft!,s=this.draftItem().solid;if(s.kind!=='finish')return;
    this.collect();state.cad.preview=featureInputView(d.root,d.entry.path);await this.callbacks.viewport()?.sync();
    await this.callbacks.viewport()?.pickFeatureEdges(d.root,d.entry.path,s.source,s.edges,()=>{if(this.draft!==d)return;s.edges=structuredClone(state.cad.edgeSelection);this.el('cadFeatureEdgeCount').textContent=`${s.edges.length} selected edges · tap to toggle, drag to orbit`;});
    this.el('cadFeatureEdgeActions').hidden=false;this.callbacks.changed();this.callbacks.pick();this.callbacks.notice('Pick edges on the original input. Preview rebuilds this finish and all later features.');
  }
  private async reselectFaces():Promise<void>{
    const d=this.draft!,s=this.draftItem().solid;if(s.kind!=='shell')return;
    this.collect();state.cad.preview=featureInputView(d.root,d.entry.path);await this.callbacks.viewport()?.sync();
    await this.callbacks.viewport()?.pickFeatureFaces(d.root,d.entry.path,s.source,s.faces,()=>{if(this.draft!==d)return;s.faces=structuredClone(state.cad.faceSelection);this.el('cadFeatureFaceCount').textContent=`${s.faces.length} faces left open · ${s.faces.length?'tap to toggle, drag to orbit':'enclosed cavity'}`;});
    this.el('cadFeatureFaceActions').hidden=false;this.callbacks.changed();this.callbacks.pick();this.callbacks.notice('Pick faces on the original input. Pink faces become openings. Preview rebuilds the shell and all later features.');
  }
  private async rebuild(apply:boolean):Promise<void>{
    const d=this.draft;if(!d)return;
    try{if(this.root()!==d.source)throw new Error('The solid changed. Cancel and reopen this feature.');this.collect();await cadCompute([d.root]);if(this.draft!==d||this.root()!==d.source){this.callbacks.notice('The solid changed during rebuilding. No feature edit was applied.');return;}if(['edge','shellFace'].includes(state.cad.tool)){state.cad.tool='translate';this.callbacks.viewport()?.setTool();for(const actions of this.host.querySelectorAll<HTMLElement>('#cadFeatureEdgeActions,#cadFeatureFaceActions'))actions.hidden=true;}
      if(apply){this.callbacks.viewport()?.clearSketch();const next=structuredClone(d.root);this.draft=undefined;state.cad.editing=false;state.cad.preview=null;this.host.classList.remove('cad-feature-editing','cad-history-preview');replaceBodies(currentBodies().map(b=>b.id===next.id?next:b));this.signature='';await this.callbacks.viewport()?.sync();this.refresh();this.callbacks.notice('Original feature updated. Every later feature has been rebuilt. Undo restores this edit in one step.');}
      else{state.cad.preview=structuredClone(d.root);this.el('cadFeatureError').hidden=true;await this.callbacks.viewport()?.sync();this.callbacks.notice('Preview of the rebuilt solid. Apply to keep these dimensions, or Cancel.');}
    }catch(error){const text=error instanceof Error?error.message:String(error);this.el('cadFeatureError').textContent=text;this.el('cadFeatureError').hidden=false;this.callbacks.changed();throw error;}
  }
  private async cancel():Promise<void>{this.draft=undefined;state.cad.editing=false;this.host.classList.remove('cad-feature-editing');this.signature='';await this.latest();this.refresh();this.callbacks.changed();this.callbacks.notice('Edit cancelled. Your original solid is unchanged.');}
  private readPoints():V2[]{const pairs=this.el<HTMLTextAreaElement>('cadFeaturePoints').value.split(';').filter(s=>s.trim()).map(s=>s.split(',').map(v=>v.trim()?Number(v):NaN));if(pairs.length<3||pairs.length>256||pairs.some(p=>p.length!==2||p.some(n=>!Number.isFinite(n)||Math.abs(n)>2000)))throw new Error('Enter 3–256 x,y pairs, separated by semicolons.');return pairs as V2[];}
  private bindSketch():void{
    const item=this.draftItem(),s=item.solid;if(s.kind!=='extrude'&&s.kind!=='revolve')return;
    const svg=this.el('cadFeatureSketch'),select=this.el<HTMLSelectElement>('cadFeaturePoint');select.replaceChildren(...s.points.map((_,i)=>new Option('Point '+(i+1),String(i))));this.point=Math.min(this.point,s.points.length-1);select.value=String(this.point);
    const updateFields=()=>{const p=s.points[this.point];this.el<HTMLInputElement>('cadFeaturePointX').value=String(p[0]);this.el<HTMLInputElement>('cadFeaturePointY').value=String(p[1]);};
    const draw=()=>{const b=sketchBounds(s.points),span=Math.max(10,b.width,b.height),m=span*.1;if(this.drag===null)svg.setAttribute('viewBox',`${b.x-m} ${-b.y-b.height-m} ${Math.max(b.width,1)+2*m} ${Math.max(b.height,1)+2*m}`);svg.innerHTML=`<path d="M0 ${-b.y-b.height-m}V${-b.y+m}" stroke="#b1bcc3" stroke-width="${span/150}"/><polygon points="${s.points.map(p=>p[0]+','+-p[1]).join(' ')}" fill="#efb9cb88" stroke="#a74975" stroke-width="${span/160}"/>${s.points.map((p,i)=>`<circle data-feature-point="${i}" cx="${p[0]}" cy="${-p[1]}" r="${span/65}" fill="${i===this.point?'#f5bd52':'#fff9e8'}" stroke="#874265" stroke-width="${span/200}"/>`).join('')}`;this.el<HTMLTextAreaElement>('cadFeaturePoints').value=s.points.map(p=>p.join(',')).join('; ');};
    draw();updateFields();select.onchange=()=>{this.point=Number(select.value);draw();updateFields();};
    for(const id of ['cadFeaturePointX','cadFeaturePointY'])this.el(id).onchange=()=>{try{s.points[this.point]=[this.number('cadFeaturePointX',s.kind==='revolve'?0:-2000),this.number('cadFeaturePointY')];draw();}catch(error){this.callbacks.notice(String(error));}};
    this.el('cadFeaturePoints').onchange=()=>{try{s.points=this.readPoints();this.bindSketch();}catch(error){this.callbacks.notice(error instanceof Error?error.message:String(error));}};
    this.el<HTMLButtonElement>('cadFeatureRemovePoint').disabled=s.points.length<=3;this.el('cadFeatureRemovePoint').onclick=()=>{if(s.points.length>3){s.points.splice(this.point,1);this.bindSketch();}};
    svg.onpointerdown=event=>{event.preventDefault();const dot=event.target instanceof Element?event.target.closest('[data-feature-point]'):null;if(dot){this.point=this.drag=Number(dot.getAttribute('data-feature-point'));select.value=String(this.point);updateFields();}else{const p=new DOMPoint(event.clientX,event.clientY).matrixTransform((svg as unknown as SVGSVGElement).getScreenCTM()!.inverse());if(s.points.length>=256)return;s.points.push([Math.max(s.kind==='revolve'?0:-2000,Math.min(2000,p.x)),Math.max(-2000,Math.min(2000,-p.y))]);this.point=s.points.length-1;this.bindSketch();}svg.setPointerCapture(event.pointerId);draw();};
    svg.onpointermove=event=>{if(this.drag===null)return;const p=new DOMPoint(event.clientX,event.clientY).matrixTransform((svg as unknown as SVGSVGElement).getScreenCTM()!.inverse());s.points[this.drag]=[Math.round(Math.max(s.kind==='revolve'?0:-2000,Math.min(2000,p.x))*100)/100,Math.round(Math.max(-2000,Math.min(2000,-p.y))*100)/100];draw();updateFields();};
    svg.onpointerup=svg.onpointercancel=()=>{this.drag=null;};
  }
}
