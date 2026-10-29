import './cad.css';
import './cad-script.css';
import { CadScriptStudio } from './cad-script-ui';
import { bus, emit } from './bus';
import { state } from './state';
import { activeLayer, addLayer, canAddLayer, deleteLayer, layerChanged, layers, moveLayer, switchLayer } from './layers';
import { pushHistory, redo, undo, canUndo, canRedo } from './history';
import { play } from './audio';
import { download } from './export';
import { saveProjectFile } from './project';
import { cadCompute } from './cad-engine';
import { addBody, cadLayers, combinedBody, currentBodies, duplicateSelected, ensureCadLayer, featureBody, finishedBody, shelledBody, removeSelected, replaceBodies, selectBodies, selectedBodies, updateSelected } from './cad-document';
import { basePlane, body, PALETTE, primitive, readCadLayer, sketchPoints, type CadBody, type CadProfile, type Primitive, type V2, type V3, type Workplane } from './cad-model';
import { CadViewport } from './cad-viewport';
import { captureAttachment } from './cad-attachment';
import { featureTree, sketchType } from './cad-features';
import { CadFeaturePanel } from './cad-feature-ui';
import { CadFormEditor, type ProfileSource } from './cad-form-ui';
import { defaultForm } from './cad-profiles';
import { CadSketchEditor } from './cad-sketch-ui';
import { solveSketch } from './cad-sketch-constraints';
import type { CadSketchConstraint } from './cad-model';
import { CadInspectPanel } from './cad-inspect-ui';
import { advancedEnabled, setAdvancedMode } from './advanced-mode';
import { message } from './editor';
import { dockWorkshopLayers } from './layer-ui';

const el = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
let root: HTMLElement | undefined, viewport: CadViewport | undefined, tab = 'add', busy = false, objectPage = 0, returningLayer = 0;
let sketch: { points: V2[]; plane: Workplane; target?: string; shape?:CadProfile['shape']; constraints?:CadSketchConstraint[] } | undefined;
let profileConstraints:CadSketchConstraint[]=[];
let profilePlane:Workplane=basePlane('xy');
let profile: V2[] = [[0,0],[15,0],[18,5],[13,15],[10,30],[14,40],[12,40],[8,30],[11,15],[16,5],[13,2],[0,2]];
let sketchKind = 'extrude', alignReference: string | undefined, profileDrag: number | null = null;
let fitScheduled=false;
let featurePanel:CadFeaturePanel|undefined;
let inspectPanel:CadInspectPanel|undefined;
let edgeTarget:CadBody|undefined,shellTarget:CadBody|undefined;
const forms=new Map<string,CadFormEditor>();
function drawingProfile():CadProfile|undefined{return sketch?{name:'Drawn sketch',shape:sketch.shape??sketchType({kind:'extrude',points:sketch.points,plane:sketch.plane,height:1,taper:1,twist:0}),points:structuredClone(sketch.points),constraints:structuredClone(sketch.constraints),plane:structuredClone(sketch.plane),rotation:0}:undefined;}
function profileSources():ProfileSource[]{return currentBodies().flatMap(root=>featureTree(root).flatMap(entry=>{if(!entry.sketch||entry.sweepPath)return[];const s=entry.item.solid,p=s.kind==='loft'?s.profiles[entry.profile??0]:s.kind==='sweep'?s.profile:s.kind==='extrude'||s.kind==='revolve'?{name:entry.label,shape:sketchType(s),points:s.points,constraints:s.feature?.constraints,plane:s.plane,rotation:0}:undefined;return p?[{name:root.name+' · '+entry.label,profile:p}]:[];}));}
const backgroundState=new Map<HTMLElement,boolean>();
export function cadWorkbench(): CadViewport | undefined { return viewport; }
function isolateWorkshop(open:boolean):void{if(open){for(const child of document.body.children)if(child instanceof HTMLElement&&child!==root){backgroundState.set(child,child.inert);child.inert=true;}}else{for(const[element,inert]of backgroundState)element.inert=inert;backgroundState.clear();}}
const icons: Record<Primitive, string> = {
  box:'<path fill="#f8cf68" d="m9 15 15-8 15 8-15 8z"/><path fill="#eaa245" d="m9 15 15 8v19L9 34z"/><path fill="#ffe8a4" d="m24 23 15-8v19l-15 8z"/>',
  sphere:'<circle cx="24" cy="25" r="17" fill="#79cad2"/><ellipse cx="19" cy="19" rx="6" ry="4" fill="#daf8ef" stroke="none"/>',
  cylinder:'<path fill="#ed9eb7" d="M8 14v22c0 10 32 10 32 0V14"/><ellipse cx="24" cy="14" rx="16" ry="7" fill="#ffd1df"/>',
  cone:'<path fill="#b4a1df" d="M7 37 24 7l17 30c-6 9-28 9-34 0Z"/><path fill="none" d="M7 37c7-7 27-7 34 0"/>',
  torus:'<ellipse cx="24" cy="26" rx="20" ry="13" fill="#f0ad6a"/><ellipse cx="24" cy="24" rx="9" ry="5" fill="#fff9ef"/>',
  tube:'<path fill="#91c6a1" d="M7 15v23c1 10 34 10 34 0V15"/><ellipse cx="24" cy="15" rx="17" ry="8" fill="#bce5b8"/><ellipse cx="24" cy="15" rx="11" ry="4" fill="#618e87"/>',
  pyramid:'<path fill="#f4ca65" d="M5 35 25 6l18 28-21 10z"/><path fill="#ffe4a4" d="m25 6-3 38 21-10z"/>',
  wedge:'<path fill="#9db8df" d="m6 35 16-24 19 24-17 9z"/><path fill="#d3e6f8" d="m22 11 2 33 17-9z"/>'
};
const art = (shape: Primitive) => `<svg viewBox="0 0 48 48" aria-hidden="true" fill="none" stroke="#334153" stroke-width="1.7" stroke-linejoin="round">${icons[shape]}</svg>`;
function button(id: string, label: string, extra = ''): string { return `<button type="button" class="choice" id="${id}" ${extra}>${label}</button>`; }
function numberField(id: string, label: string, value: number, min = -2000, max = 2000, step = 0.1): string { return `<label>${label}<input id="${id}" type="number" value="${value}" min="${min}" max="${max}" step="${step}"></label>`; }
function fields3(prefix: string, labels: string[], values: V3, min?: number, max?: number): string { return `<div class="cad-fields three">${labels.map((label,i)=>numberField(prefix+i,label,values[i],min,max)).join('')}</div>`; }
function notice(text: string): void { if(root)el('cadStatus').textContent=text; }
function attempt(action: () => void): void { if(busy||state.cad.gesture)return;if(state.cad.editing||state.cad.preview){notice(state.cad.editing?'Apply or cancel your feature edit first.':'Return to Latest in the timeline before changing the solid.');return;}try{action();play('clunk');refresh();}catch(error){notice(error instanceof Error?error.message:String(error));} }
function num(id: string, min = -2000, max = 2000): number {
  const input=el<HTMLInputElement>(id), value=Number(input.value);if(!input.value.trim()||!Number.isFinite(value)||value<min||value>max)throw new Error(`${input.closest('label')?.textContent?.trim()||'Value'} must be between ${min} and ${max}.`);return value;
}
function vector(prefix: string, min?: number, max?: number): V3 { return [num(prefix+'0',min,max),num(prefix+'1',min,max),num(prefix+'2',min,max)]; }
function setValue(id: string, value: string|number): void { const input=el<HTMLInputElement>(id);if(!busy&&document.activeElement!==input)input.value=typeof value==='number'?String(Math.round(value*1000)/1000):value; }
function setTab(next: string): void {
  if(state.cad.editing&&next!=='history'){notice('Apply or cancel your feature edit first.');return;}
  if(next!=='build'&&['edge','shellFace'].includes(state.cad.tool)&&!state.cad.editing){state.cad.tool='translate';viewport?.setTool();}
  if(tab==='build'&&next!=='build')viewport?.clearSketch();
  if(tab==='inspect'&&next!=='inspect')inspectPanel?.leave();
  if(tab==='sketch'&&next!=='sketch')viewport?.clearSketch();
  if(next==='sketch'&&tab!=='sketch'){
    if(viewport?.getTarget()&&!currentBodies().some(b=>b.id===viewport!.getTarget())){viewport.setPlane(basePlane('xy'));el<HTMLSelectElement>('cadPlane').value='xy';sketch=undefined;}
    setSketchKind('extrude');
  }
  tab=next;for(const panel of root!.querySelectorAll<HTMLElement>('[data-cad-panel]'))panel.hidden=panel.dataset.cadPanel!==tab;
  for(const button of root!.querySelectorAll<HTMLElement>('[data-cad-tab]')){const active=button.dataset.cadTab===tab;button.setAttribute('aria-selected',String(active));button.classList.toggle('active',active);button.tabIndex=active?0:-1;}
  if(next!=='sketch'&&['face','rectangle','circle','polygon'].includes(state.cad.tool)){state.cad.tool='translate';viewport?.setTool();}
  if(next==='sketch'&&sketchKind==='extrude'&&!['face','rectangle','circle','polygon'].includes(state.cad.tool)){state.cad.tool='rectangle';viewport?.setTool();viewport?.view('sketch');}
  if(next==='build')forms.get(el<HTMLSelectElement>('cadBuildPage').value)?.showGuide();
  refresh();
}
function mount(): void {
  root=document.createElement('section');root.id='cadWorkshop';root.hidden=true;root.setAttribute('aria-label','3D workshop');
  root.innerHTML=`
    <header class="cad-header"><div class="cad-brand"><span class="cad-brand-cube">${art('box')}</span><div><strong>3D workshop</strong><small>Little ideas. Real things.</small></div></div><span class="cad-mm">Everything in mm</span><div class="cad-header-actions">${button('cadUndo','↶ Undo')}${button('cadRedo','↷ Redo')}${button('cadSaveProject','💾 Project')}${button('cadClose','🎨 Paint')}</div></header>
    <div id="cadView" class="cad-view"><div class="cad-view-buttons" aria-label="Camera views">${['iso','top','front','right'].map(v=>`<button type="button" class="choice" data-cad-view="${v}">${v==='iso'?'◈ 3D':v[0].toUpperCase()+v.slice(1)}</button>`).join('')}${button('cadFit','⊡ Fit')}</div>
      <div class="cad-empty" id="cadEmpty"><span>Make something<br><b>you can hold.</b></span><small>Start with a shape →</small></div>
      <div class="cad-tools" aria-label="3D manipulation"><button class="choice" data-cad-tool="translate" title="Move · W">↔ <span>Move</span></button><button class="choice" data-cad-tool="rotate" title="Rotate · E">⟳ <span>Rotate</span></button><button class="choice" data-cad-tool="scale" title="Size · R">⤢ <span>Size</span></button><button class="choice" id="cadDrop" title="Place selection on the print bed">⇣ <span>To bed</span></button></div>
      <div class="cad-view-tip" id="cadViewTip">Drag to orbit · Right-drag to pan · Scroll to zoom · Shift-click selects more</div>
      <div class="cad-axis-key"><b>X</b><b>Y</b><b>Z</b><span>200 × 200 mm bed</span></div>
    </div>
    <aside class="cad-panel"><div class="cad-layer-heading"><span id="cadActiveLayer">3D 1</span><span id="cadPieceCount">0 pieces</span></div>
      <nav class="cad-tabs" role="tablist" aria-label="3D workshop tools">${[['add','🧊','Shapes'],['move','↔','Edit'],['sketch','✎','Sketch'],['build','⚒','Build'],['layers','▱','Layers'],['print','↥','Print']].map(([id,icon,label])=>`<button type="button" role="tab" class="choice" data-cad-tab="${id}" aria-controls="cadPage${id}" aria-selected="${id==='add'}">${icon} ${label}</button>`).join('')}</nav>
      <div class="cad-panel-page" id="cadPageadd" data-cad-panel="add"><h2>Start with a shape</h2><div class="cad-primitives">${(Object.keys(icons) as Primitive[]).map(shape=>`<button type="button" class="choice cad-primitive" data-cad-primitive="${shape}">${art(shape)}<span>${shape==='box'?'Cube':shape[0].toUpperCase()+shape.slice(1)}</span></button>`).join('')}</div><p class="cad-hint">New pieces share this 3D layer. Tap a piece, then grab its coloured handles.</p><div class="cad-mini-card"><strong>From flat to fantastic</strong><p>Draw on a face and pull it into 3D, or spin a profile into a vase.</p>${button('cadStartSketch','✎ Draw a sketch')}</div></div>
      <div class="cad-panel-page" id="cadPagemove" data-cad-panel="move" hidden><h2 id="cadEditTitle">Select a piece</h2><label class="cad-full-field">Name<input id="cadBodyName" maxlength="60"></label><div class="cad-subtabs"><button type="button" class="choice active" data-cad-edit="transform">Position & turn</button><button type="button" class="choice" data-cad-edit="size">Size & colour</button></div>
        <div data-cad-edit-page="transform"><h3>Position · mm</h3>${fields3('cadPos',['X','Y','Z'],[0,0,0],-10000,10000)}<h3>Rotation · degrees</h3>${fields3('cadRot',['X°','Y°','Z°'],[0,0,0],-36000,36000)}${button('cadApplyTransform','Apply position & turn')}</div>
        <div data-cad-edit-page="size" hidden><h3>Dimensions · mm <small>(local axes)</small></h3>${fields3('cadSize',['Width X','Depth Y','Height Z'],[20,20,20],0.1,2000)}<label class="cad-check"><input id="cadKeepRatio" type="checkbox"> Keep proportions</label>${numberField('cadWall','Tube wall · mm',2,0.1,1000)}<div class="cad-colours">${PALETTE.map(color=>`<button type="button" data-cad-color="${color}" style="--cad-color:${color}" aria-label="Piece colour ${color}"></button>`).join('')}<input id="cadColour" type="color" aria-label="Custom piece colour" value="${PALETTE[0]}"></div>${button('cadApplySize','Apply size')}</div>
        <div class="cad-actions">${button('cadDuplicate','⧉ Copy')}${button('cadDelete','⌫ Delete')}</div><p class="cad-hint" id="cadSelectedInfo">Select a piece in the workbench or Layers.</p></div>
      <div class="cad-panel-page" id="cadPagesketch" data-cad-panel="sketch" hidden><div class="cad-subtabs"><button type="button" class="choice active" data-cad-sketch-kind="extrude">Pull a sketch</button><button type="button" class="choice" data-cad-sketch-kind="revolve">Revolve</button></div>
        <div id="cadExtrudePage"><div class="cad-fields"><label>Workplane<select id="cadPlane"><option value="xy">Floor · XY</option><option value="xz">Front · XZ</option><option value="yz">Side · YZ</option><option value="face" disabled>Picked face</option></select></label>${button('cadPickFace','▧ Pick flat face')}</div><div class="cad-actions">${button('cadRectSketch','▭ Rectangle')}${button('cadCircleSketch','○ Circle')}${button('cadPolygonSketch','⬠ Polygon')}</div><div class="cad-fields">${numberField('cadSketchX','Start X / centre X',-10)}${numberField('cadSketchY','Start Y / centre Y',-10)}${numberField('cadSketchW','Width / diameter',20,0.1,2000)}${numberField('cadSketchH','Height',20,0.1,2000)}</div><div class="cad-actions">${button('cadUseDimensions','Use these dimensions')}${button('cadFinishPolygon','Finish polygon')}${button('cadRevolveSketch','Revolve this sketch')}</div><p class="cad-hint" id="cadSketchHint">Click two opposite corners for a rectangle; click centre then edge for a circle. Dragging also works. Polygon: tap corners, then tap the first corner or Finish. Use dimensions for exact sizes.</p></div>
        <div id="cadRevolvePage" hidden><label class="cad-full-field">Profile<select id="cadProfilePreset"><option value="vase">Hollow vase</option><option value="goblet">Goblet</option><option value="knob">Knob</option><option value="custom">Draw my own</option></select></label><svg id="cadProfile" viewBox="-4 -64 60 70" aria-label="Revolve profile: radius horizontally, height vertically" role="img"></svg><div class="cad-actions">${button('cadProfileUndo','Undo point')}${button('cadProfileClear','Clear profile')}</div><p class="cad-hint">Tap to add profile points. Drag dots to edit. Radius stays to the right of the axis. The shape closes automatically.</p><label class="cad-full-field">Radius,height pairs · mm<textarea id="cadProfilePoints" rows="2" aria-label="Revolve profile coordinates" spellcheck="false"></textarea></label></div>
        ${button('cadNextFeature','Next → Make it 3D')}<div id="cadSketchFinish" hidden>${button('cadBackSketch','← Back to sketch')}<div class="cad-fields"><label id="cadFeatureAmountLabel">Pull · mm<input id="cadFeatureAmount" type="number" value="10" min="-2000" max="2000" step="0.1"></label><label>Result<select id="cadFeatureOperation"><option value="auto">Auto · pull adds, push cuts</option><option value="new" selected>New piece</option><option value="join">Join to face piece</option><option value="cut">Cut into face piece</option></select></label></div><label class="cad-check" id="cadThroughRow" hidden><input type="checkbox" id="cadThrough"> Cut all the way through</label><div class="cad-fields" id="cadExtrudeExtras">${numberField('cadTaper','Top size ×',1,0.01,5,0.05)}${numberField('cadTwist','Twist °',0,-720,720,1)}</div>${button('cadCreateFeature','↑ Make solid')}</div><small class="cad-hint" id="cadFeatureSummary">No sketch yet</small></div>
      <div class="cad-panel-page" id="cadPagebuild" data-cad-panel="build" hidden><label class="cad-full-field">Build tools<select id="cadBuildPage"><option value="combine">Join & cut</option><option value="align">Align & snap together</option><option value="repeat">Repeat & mirror</option></select></label>
        <div data-cad-build-page="combine"><h2>Make a new solid</h2><div class="cad-build-buttons">${[['union','⊕','Join pieces'],['subtract','⊖','Subtract cutters'],['intersect','◉','Keep overlap'],['hull','⬡','Wrap with hull']].map(([op,symbol,label])=>`<button class="choice" type="button" data-cad-boolean="${op}"><b>${symbol}</b>${label}</button>`).join('')}</div><label class="cad-full-field">Keep / target piece<select id="cadBooleanTarget" aria-label="Boolean target piece"></select></label><p class="cad-hint">Select at least two pieces. Subtract keeps the target and removes the others. The originals stay editable inside the result. Open History to change a sketch, cutter or build step.</p></div>
        <div data-cad-build-page="align" hidden><h2>Line things up</h2><label class="cad-full-field">Reference piece<select id="cadAlignTarget"></select></label><div class="cad-fields"><label>Axis<select id="cadAlignAxis"><option value="0">X</option><option value="1">Y</option><option value="2">Z</option></select></label><label>Match<select id="cadAlignMode"><option value="center">Centres</option><option value="min">Minimum edges</option><option value="max">Maximum edges</option><option value="after">Touch after reference</option><option value="before">Touch before reference</option></select></label></div>${numberField('cadAlignGap','Gap · mm',0,-1000,1000)}${button('cadAlign','Align selected pieces')}<div class="cad-actions">${button('cadCentre','Centre on bed')}${button('cadGround','Drop to bed')}</div>${button('cadSnapFaces','Snap face to face')}<p class="cad-hint" id="cadMateHint">Face snapping: select one moving piece, then tap its flat face and a target flat face. The faces meet with opposing normals.</p></div>
        <div data-cad-build-page="repeat" hidden><h2>Make a pattern</h2>${numberField('cadArrayCount','Extra copies',3,1,30,1)}${fields3('cadArrayStep',['Step X','Step Y','Step Z'],[25,0,0],-2000,2000)}${button('cadLinearArray','Make a line of copies')}${numberField('cadArrayAngle','Angle per copy · °',30,-360,360,1)}${button('cadCircularArray','Copies around Z axis')}<div class="cad-actions">${[0,1,2].map((axis)=>button('cadMirror'+axis,'Mirror '+['X','Y','Z'][axis])).join('')}</div><p class="cad-hint">Circular patterns turn around the origin. Move the original away from the centre first.</p></div></div>
      <div class="cad-panel-page" id="cadPagelayers" data-cad-panel="layers" hidden><h2>3D layers & pieces</h2><div class="cad-fields"><label>Working layer<select id="cadLayerSelect"></select></label>${button('cadNewLayer','＋ 3D layer')}</div><div class="cad-fields"><label>Layer name<input id="cadLayerName" maxlength="60"></label><label class="cad-check"><input type="checkbox" id="cadLayerVisible" checked> Visible</label></div><div class="cad-body-list" id="cadBodyList"></div><div class="cad-pagination">${button('cadObjectsPrev','←')}<span id="cadObjectPage">1 / 1</span>${button('cadObjectsNext','→')}</div><div class="cad-actions">${button('cadSelectAll','Select all')}${button('cadMoveLayer','Move selection to…')}${button('cadRemoveLayer','Delete layer')}</div><select id="cadDestinationLayer" aria-label="Destination 3D layer"></select><p class="cad-hint">Pieces have their own show / hide and lock buttons. Shift-click to select several. All 3D layers also appear in Paint’s layer stack.</p></div>
      <div class="cad-panel-page" id="cadPageprint" data-cad-panel="print" hidden><h2>Make it real</h2><div class="cad-print-art">${art('box')}<span>3D → STL</span></div><label class="cad-full-field">Export<select id="cadPrintScope"><option value="visible">All visible 3D layers</option><option value="layer">Visible pieces on this layer</option><option value="selection">Selected visible pieces</option></select></label><label class="cad-check"><input id="cadPrintBed" type="checkbox" checked> Place bottom at Z = 0</label>${fields3('cadBed',['Bed X · mm','Bed Y · mm','Height · mm'],[200,200,200],10,2000)}${button('cadCheckPrint','Check solid & size')}<div id="cadPrintReport" class="cad-print-report">Solids are joined for export. Hidden pieces stay out. STL dimensions use millimetres.</div>${button('cadExportStl','↥ Export STL')}<p class="cad-hint">STL is the printable shape. Save Project keeps editable solids, sketches, 3D layers and your painting.</p></div>
      <div class="cad-snap-bar"><label class="cad-check"><input type="checkbox" id="cadSnap" checked> Snap</label><label>Grid <select id="cadGrid"><option value="0.1">0.1 mm</option><option value="0.5">0.5 mm</option><option value="1" selected>1 mm</option><option value="5">5 mm</option><option value="10">10 mm</option></select></label><label>Turn <select id="cadAngle"><option value="1">1°</option><option value="5">5°</option><option value="15" selected>15°</option><option value="45">45°</option><option value="90">90°</option></select></label></div>
    </aside><footer id="cadStatus" class="cad-status" role="status" aria-live="polite">Welcome to your little workshop. Pick a shape to begin.</footer>`;
  const codeTab=document.createElement('button');codeTab.type='button';codeTab.className='choice';codeTab.dataset.cadTab='code';codeTab.setAttribute('role','tab');codeTab.setAttribute('aria-controls','cadPagecode');codeTab.setAttribute('aria-selected','false');codeTab.textContent='⌨ Code';root.querySelector('.cad-tabs')!.append(codeTab);
  const codePage=document.createElement('div');codePage.id='cadPagecode';codePage.className='cad-panel-page';codePage.dataset.cadPanel='code';codePage.hidden=true;codePage.innerHTML=`<h2>Build with code</h2><p class="cad-hint">Powered by the real OpenSCAD engine. Change dimensions, repeat shapes, cut holes and build reusable modules.</p>${button('cadOpenScript','⌨ Open Code studio')}${button('cadEditScript','Edit selected solid’s code')}<p class="cad-hint">Preview safely, then Add to scene. Select a script model to edit and update it later. Projects keep its source; STL exports the finished solid.</p><div class="cad-mini-card"><strong>Try a drilled flange</strong><p>Six bolt holes, a central bore, and editable dimensions — all from a short script.</p></div>`;root.querySelector('.cad-snap-bar')!.before(codePage);
  const scriptStudio=new CadScriptStudio(root,{notice,apply:async(item,target)=>{if(busy||state.cad.editing||state.cad.preview)throw new Error('Finish the current edit before applying code.');if(target){const original=currentBodies().find(b=>b.id===target);if(!original||original.locked)throw new Error('The original solid is missing or locked.');replaceBodies(currentBodies().map(b=>b.id===target?{...original,solid:item.solid,script:item.script,name:item.name}:b));selectBodies([target]);}else addBody(item);await viewport?.sync();viewport?.fit();notice(target?'Script model updated. Undo restores its previous code and shape.':'Script model added. Select it and choose Code to edit its source.');refresh();}});
  elIn(root,'cadOpenScript').onclick=()=>attempt(()=>scriptStudio.open());elIn(root,'cadEditScript').onclick=()=>attempt(()=>scriptStudio.open(true));
  for(const page of root.querySelectorAll<HTMLElement>('[data-cad-panel]')){const inner=document.createElement('div');inner.className='cad-page-content';inner.append(...page.childNodes);page.append(inner);}
  const actions=document.createElement('div');actions.id='cadSketchActions';actions.hidden=true;actions.innerHTML=button('cadQuickPull','↑ Pull')+button('cadQuickCut','↓ Cut')+button('cadQuickHole','Through hole')+button('cadQuickApply','✓ Apply')+button('cadQuickCancel','Cancel');elIn(root,'cadView').append(actions);
  const toggle=document.createElement('button');toggle.id='cadToolsToggle';toggle.type='button';toggle.className='choice';toggle.textContent='⚒ Tools';toggle.setAttribute('aria-expanded','true');elIn(root,'cadView').append(toggle);
  const hide=document.createElement('button');hide.id='cadHideTools';hide.type='button';hide.className='choice';hide.textContent='✕';hide.setAttribute('aria-label','Hide CAD tools');root.querySelector('.cad-layer-heading')!.append(hide);
  const help=document.createElement('dialog');help.id='cadHelpDialog';help.setAttribute('aria-labelledby','cadHelpTitle');help.innerHTML=`<h2 id="cadHelpTitle">Build, play, make.</h2><div id="cadHelpContent"><p><b>Shapes</b> adds a solid. Tap a piece and drag its coloured handles to move, turn or resize it.</p><p><b>Sketch</b> draws on the floor or a picked flat face. Choose Next to pull, join or cut it. Revolve spins a profile around the vertical axis.</p><p><b>Build</b> joins solids, cuts holes, aligns faces and repeats pieces. Loft blends sketches; Sweep carries a sketch along a path. Shell hollows a solid: pick openings and a wall thickness. <b>Print</b> checks dimensions and exports STL in mm.</p><p><b>History</b> edits original sketches, hole sizes, pull depths and revolve settings. Preview, Apply or Cancel. The timeline shows earlier stages; Latest returns to your finished solid.</p><div class="cad-help-keys"><span>W / E / R</span><span>Move / Rotate / Size</span><span>F · Shift-click</span><span>Fit · Select more</span><span>Ctrl/Cmd Z · D</span><span>Undo · Duplicate</span><span>Ctrl/Cmd S</span><span>Save editable project</span></div></div>${button('cadHelpDone','Let’s build')}`;root.append(help);
  const helpButton=document.createElement('button');helpButton.id='cadHelp';helpButton.type='button';helpButton.className='choice';helpButton.textContent='?';helpButton.setAttribute('aria-label','3D workshop help');root.querySelector('.cad-header-actions')!.prepend(helpButton);
  const historyTab=document.createElement('button');historyTab.type='button';historyTab.className='choice';historyTab.dataset.cadTab='history';historyTab.setAttribute('role','tab');historyTab.setAttribute('aria-controls','cadPagehistory');historyTab.setAttribute('aria-selected','false');historyTab.textContent='▱ History';root.querySelector('.cad-tabs')!.append(historyTab);
  const editHistory=document.createElement('button');editHistory.type='button';editHistory.id='cadEditHistory';editHistory.className='choice';editHistory.textContent='▱ Edit original features & sketches';elIn(root,'cadSelectedInfo').before(editHistory);editHistory.onclick=()=>setTab('history');
  elIn(root,'cadBuildPage').append(new Option('Fillet & chamfer edges','edges'));const finishes=document.createElement('div');finishes.dataset.cadBuildPage='edges';finishes.hidden=true;finishes.innerHTML=`<h2>Soften the edges</h2><div class="cad-finish-art" aria-hidden="true"><span>┏</span><b>→</b><span>╭</span><b>or</b><span>◩</span></div><div class="cad-fields"><label>Finish<select id="cadFinishMode"><option value="fillet">Fillet · round</option><option value="chamfer">Chamfer · bevel</option></select></label>${numberField('cadFinishSize','Radius · mm',2,.01,1000,.1)}</div><div class="cad-actions">${button('cadPickEdges','⌁ Pick edges')}${button('cadAllEdges','Select all')}${button('cadNoEdges','Clear')}</div><p class="cad-edge-count" id="cadEdgeCount">Select one solid, then pick its edges.</p>${button('cadPreviewFinish','◈ Preview finish →')}<p class="cad-hint">Tap edges to toggle them. Drag to orbit. Preview opens an editable feature; Apply keeps it and Cancel keeps your original.</p>`;elIn(root,'cadPagebuild').querySelector('.cad-page-content')!.append(finishes);
  elIn(root,'cadBuildPage').append(new Option('Shell · hollow a solid','shell'));const shell=document.createElement('div');shell.dataset.cadBuildPage='shell';shell.hidden=true;shell.innerHTML=`<h2>Make room inside</h2><div class="cad-finish-art cad-shell-art" aria-hidden="true"><span>■</span><b>→</b><span>▣</span></div>${numberField('cadShellThickness','Wall thickness · mm',2,.01,1000,.1)}<div class="cad-actions">${button('cadPickShellFaces','▧ Pick open faces')}${button('cadClearShellFaces','Clear')}</div><p class="cad-edge-count" id="cadShellFaceCount">Select one solid, then pick faces to leave open.</p>${button('cadPreviewShell','▣ Preview shell →')}<p class="cad-hint">Pink faces become openings. Tap to toggle; drag to orbit. Walls grow inward, keeping the outside size. Clear all openings for an enclosed cavity.</p>`;elIn(root,'cadPagebuild').querySelector('.cad-page-content')!.append(shell);
  for(const kind of ['loft','sweep'] as const){const title=kind==='loft'?'Loft between sketches':'Sweep a sketch along a path',page=document.createElement('div'),id=kind==='loft'?'cadLoft':'cadSweep';page.dataset.cadBuildPage=kind;page.hidden=true;page.innerHTML=`<h2>${title}</h2><div id="${id}Editor" class="cad-form-editor"></div>${button(id+'Make',kind==='loft'?'⋈ Make loft':'∿ Make sweep')}<p class="cad-hint">A new editable solid. History keeps every sketch${kind==='sweep'?', the path':''} and setting. Undo removes it in one step.</p>`;elIn(root,'cadBuildPage').append(new Option(title,kind));elIn(root,'cadPagebuild').querySelector('.cad-page-content')!.append(page);forms.set(kind,new CadFormEditor(elIn(root,id+'Editor'),defaultForm(kind),id,{changed:fitPage,notice,sources:profileSources,drawing:drawingProfile,guide:form=>{if(state.cad.open&&tab==='build'&&el<HTMLSelectElement>('cadBuildPage').value===kind&&!state.cad.editing&&!state.cad.preview)viewport?.showFormInputs(form);}}));}
  elIn(root,'cadRevolvePage').insertAdjacentHTML('afterend',`${button('cadSketchConstraints','↔ Dimensions & constraints')}<div id="cadSketchConstraintPage" hidden>${button('cadBackConstraints','← Outline & workplane')}<div id="cadSketchConstraintEditor" class="cad-constraint-editor"></div></div>`);
  document.body.append(root);featurePanel=new CadFeaturePanel(root,{viewport:()=>viewport,notice,run:action=>solidAction(action,true),changed:fitPage,open:()=>{setTab('history');showTools(true);},pick:()=>{if(mobileTools())showTools(false);},sources:profileSources,drawing:drawingProfile});inspectPanel=new CadInspectPanel(root,{viewport:()=>viewport,changed:fitPage,notice,run:solidAction,attempt,paint:paintBesideCad,pick:()=>{if(mobileTools())showTools(false);}});el('cadPageadd').querySelector('.cad-page-content')!.insertAdjacentHTML('beforeend',button('cadImportShortcut','＋ Import STL'));el('cadPagelayers').querySelector('.cad-page-content')!.insertAdjacentHTML('beforeend',button('cadPictureShortcut','▣ Picture layers & placement'));bind();new ResizeObserver(fitPage).observe(root.querySelector('.cad-panel')!);
}
function elIn(parent:HTMLElement,id:string):HTMLElement{return parent.querySelector<HTMLElement>('#'+id)!;}
function mobileTools():boolean{return matchMedia('(max-width:800px) and (min-height:501px)').matches;}
function showTools(show:boolean):void{root!.querySelector('.cad-panel')!.classList.toggle('cad-tools-hidden',!show);el('cadToolsToggle').setAttribute('aria-expanded',String(show));if(show)fitPage();else el('cadCanvas')?.focus({preventScroll:true});}
function fitPage():void{
  if(fitScheduled||!state.cad.open)return;fitScheduled=true;
  requestAnimationFrame(()=>{
    fitScheduled=false;
    const page=root!.querySelector<HTMLElement>('[data-cad-panel]:not([hidden])'),inner=page?.querySelector<HTMLElement>('.cad-page-content');
    if(!page||!inner||!page.clientHeight)return;
    inner.style.zoom='1';
    if(matchMedia('(max-width:800px), (max-height:500px) and (max-width:1000px)').matches)return;
    const available=page.clientHeight-2;
    let zoom=1;
    // Fractional zoom can reflow and round form controls differently from the
    // unscaled measurement. Check the resulting layout before accepting it.
    for(let attempt=0;attempt<4;attempt++){
      const height=inner.getBoundingClientRect().height;
      if(height<=available)break;
      zoom*=available/Math.max(1,height);inner.style.zoom=String(zoom);
    }
  });
}
export async function openCad(): Promise<void> {
  if(!advancedEnabled()){message('Switch to Advanced mode in More to edit 3D. Your model stays intact.');return;}
  if(state.cad.open)return;if(!root)mount();returningLayer=activeLayer().cad?(layers.find(l=>!l.cad)?.id??0):activeLayer().id;
  ensureCadLayer();featurePanel?.reset();state.cad.open=true;state.cad.gesture=false;state.cad.selected=[];state.cad.tool='translate';sketch=undefined;mateFirst=undefined;root!.hidden=false;document.body.classList.add('cad-open');
  setAdvancedMode(true);dockWorkshopLayers(root);isolateWorkshop(true);
  el<HTMLSelectElement>('cadPlane').value='xy';el('cadPlane').querySelector<HTMLOptionElement>('[value="face"]')!.disabled=true;setSketchKind(sketchKind);showTools(true);
  try {
    viewport=new CadViewport(el('cadView'),{notice,sketch:(points,plane,target)=>{sketch={points,plane,target,shape:state.cad.tool==='circle'?'circle':state.cad.tool==='polygon'?'polygon':'rectangle'};el<HTMLSelectElement>('cadFeatureOperation').value=target?'auto':'new';lockSketchOutline();el('cadFeatureSummary').textContent=`${points.length===96?'Circle':points.length===4?'Rectangle':points.length+' point sketch'} · ${target?'on face':'on workplane'}`;notice('Sketch ready. Choose Pull, Cut or Through hole beside the drawing.');sketchActions();showTools(!mobileTools());},face:(plane,target)=>{if(mateFirst){finishMate(plane,target);return;}sketch=undefined;el<HTMLSelectElement>('cadFeatureOperation').value='auto';el<HTMLSelectElement>('cadPlane').value='face';el('cadPlane').querySelector<HTMLOptionElement>('[value="face"]')!.disabled=false;setTab('sketch');setSketchKind('extrude');state.cad.tool='rectangle';viewport!.setTool();viewport!.view('sketch');notice('Face ready. Click two corners to draw a rectangle, or choose Circle / Polygon. Then Pull or Cut.');refresh();},changed:refresh});
    await viewport.sync();if(!activeLayer().cad?.view)viewport.fit();setTab(tab);refresh();el('cadCanvas').focus({preventScroll:true});emit('cad-open',true);
  }catch(error){state.cad.open=false;root!.hidden=true;document.body.classList.remove('cad-open');isolateWorkshop(false);dockWorkshopLayers();viewport?.dispose();viewport=undefined;throw error;}
}
function closeCad(persistPicture=true,update=true): void {
  if(busy)return;if(layers.every(l=>l.cad)&&!canAddLayer()){notice('The layer stack is full. Remove a 3D layer to make room for a paint sheet.');return;}if(persistPicture&&viewport?.pictureMode)viewport.pinPictureView(true,false);viewport?.dispose(update);viewport=undefined;featurePanel?.reset();state.cad.open=false;state.cad.selected=[];mateFirst=undefined;root!.hidden=true;document.body.classList.remove('cad-open');isolateWorkshop(false);
  const paint=!activeLayer().cad?activeLayer():layers.find(l=>l.id===returningLayer&&!l.cad)??layers.find(l=>!l.cad);if(paint)switchLayer(paint.id);else if(canAddLayer())addLayer();
  dockWorkshopLayers();emit('cad-open',false);el('studioBtn').focus({preventScroll:true});
}
function paintBesideCad(above:boolean):void{if(!canAddLayer())throw new Error('The layer stack is full. Remove a sheet before adding a picture layer.');const source=activeLayer();pushHistory();viewport?.setPictureMode(true);viewport?.pinPictureView(false,false);closeCad(false);switchLayer(source.id);addLayer();activeLayer().name=above?'Paint above 3D':'Backdrop';if(!above)moveLayer(activeLayer().id,source.id,false);layerChanged();setAdvancedMode(true);emit('restore-layers',true);message(above?'Painting on a new picture layer above the editable 3D layer.':'Painting on a new picture layer below the editable 3D layer.');}
async function solidAction(action: () => Promise<void>,featureEdit=false): Promise<void> {
  if(busy)return;if(!featureEdit&&(state.cad.editing||state.cad.preview)){notice(state.cad.editing?'Apply or cancel your feature edit first.':'Return to Latest in the timeline before changing or exporting the solid.');return;}busy=true;root!.setAttribute('aria-busy','true');root!.classList.add('cad-working');notice('Building your solid…');
  refresh();
  try{await action();play('clunk');}catch(error){notice(error instanceof Error?error.message:String(error));}
  finally{busy=false;root!.removeAttribute('aria-busy');root!.classList.remove('cad-working');refresh();}
}
async function saveCadProject():Promise<void>{viewport?.updatePreviews();await saveProjectFile(el<HTMLInputElement>('fileName').value);notice('Project ready, including editable solids, 3D layers and your painting.');}
async function validateAndAdd(item: CadBody): Promise<void> { await cadCompute([item]);addBody(item);await viewport?.sync();viewport?.fit();notice(`${item.name} ready. Grab a handle to move, turn or resize it.`); }
function targetOptions(select: HTMLSelectElement, candidates: CadBody[], previous?: string): void {
  const signature=candidates.map(b=>b.id+b.name).join('|');if(select.dataset.signature!==signature){select.replaceChildren(...candidates.map(b=>new Option(b.name,b.id)));select.dataset.signature=signature;}if(previous&&candidates.some(b=>b.id===previous))select.value=previous;
}
function refresh(): void {
  if(root)el<HTMLButtonElement>('cadEditScript').disabled=busy||selectedBodies().length!==1||!selectedBodies()[0]?.script||!!selectedBodies()[0]?.locked;
  if(root){sketchActions();if(tab==='sketch'&&sketchKind==='extrude'&&!sketch)el('cadFeatureSummary').textContent='No closed sketch yet';}
  if(root){
    const drawing=['rectangle','circle','polygon'].includes(state.cad.tool);
    el<HTMLButtonElement>('cadUseDimensions').disabled=state.cad.tool==='polygon'||!!sketch?.constraints?.length;
    el('cadViewTip').textContent=drawing?(state.cad.tool==='polygon'?'Tap corners · Tap first corner or press Enter to finish':'Click two corners / centre then edge · Or drag to draw'):'Drag to orbit · Right-drag to pan · Scroll to zoom · Shift-click selects more';
    for(const [id,tool]of [['cadRectSketch','rectangle'],['cadCircleSketch','circle'],['cadPolygonSketch','polygon'],['cadPickFace','face']]){el(id).classList.toggle('active',state.cad.tool===tool);el(id).setAttribute('aria-pressed',String(state.cad.tool===tool));}
  }
  if(!state.cad.open||!root)return;
  el('layersPanel').inert=busy||state.cad.gesture||!!state.cad.editing||!!state.cad.preview;
  const selected=selectedBodies(),first=selected[0],working=activeLayer();el('cadActiveLayer').textContent=working.name;el('cadPieceCount').textContent=`${currentBodies().length} ${currentBodies().length===1?'piece':'pieces'}`;
  el('cadEmpty').hidden=tab==='sketch'||cadLayers().some(l=>l.cad!.bodies.length>0)||(tab==='build'&&forms.has(el<HTMLSelectElement>('cadBuildPage').value));el<HTMLButtonElement>('cadUndo').disabled=!canUndo()||busy||state.cad.gesture;el<HTMLButtonElement>('cadRedo').disabled=!canRedo()||busy||state.cad.gesture;
  for(const button of root.querySelectorAll<HTMLElement>('[data-cad-tool]')){const active=button.dataset.cadTool===state.cad.tool;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}
  el('cadEditTitle').textContent=selected.length>1?`${selected.length} pieces selected`:first?.name??'Select a piece';
  for(const id of ['cadBodyName','cadApplyTransform','cadApplySize','cadDelete','cadDuplicate','cadColour'])el<HTMLInputElement>(id).disabled=!first||busy||(id!=='cadDuplicate'&&selected.some(b=>b.locked));
  if(first){setValue('cadBodyName',first.name);first.position.forEach((v,i)=>setValue('cadPos'+i,v));first.rotation.forEach((v,i)=>setValue('cadRot'+i,v));const data=viewport?.nodes.get(first.id)?.data;const size=data?data.bounds.max.map((v,i)=>(v-data.bounds.min[i])*Math.abs(first.scale[i])):first.solid.kind==='primitive'?first.solid.size:[20,20,20];size.forEach((v,i)=>setValue('cadSize'+i,v));setValue('cadColour',first.color);el<HTMLInputElement>('cadWall').disabled=first.solid.kind!=='primitive'||first.solid.shape!=='tube';if(first.solid.kind==='primitive')setValue('cadWall',first.solid.wall*Math.min(Math.abs(first.scale[0]),Math.abs(first.scale[1])));el('cadSelectedInfo').textContent=first.locked?'Locked piece. Unlock it in Layers to edit.':`${selected.length>1?'Fields use the first piece; changes apply to the selection. ':''}${data?(data.volume*Math.abs(first.scale[0]*first.scale[1]*first.scale[2])/1000).toFixed(2)+' cm³ · '+data.triangles.toLocaleString()+' triangles':''}`;}
  const choices=selected.length>0?selected:currentBodies();targetOptions(el('cadBooleanTarget'),choices,el<HTMLSelectElement>('cadBooleanTarget').value);targetOptions(el('cadAlignTarget'),selected.length?selected:currentBodies(),alignReference??el<HTMLSelectElement>('cadAlignTarget').value);
  if(tab==='layers')refreshLayerList();
  featurePanel?.refresh();
  inspectPanel?.refresh();
  const edgeCount=edgeTarget&&currentBodies().includes(edgeTarget)?state.cad.edgeSelection.length:0;el('cadEdgeCount').textContent=state.cad.tool==='edge'?`${edgeCount} edges selected · tap to toggle, drag to orbit`:'Select one solid, then pick its edges.';el<HTMLButtonElement>('cadPickEdges').disabled=selected.length!==1||!!first?.locked;el<HTMLButtonElement>('cadPreviewFinish').disabled=!edgeCount||state.cad.tool!=='edge';for(const id of ['cadAllEdges','cadNoEdges'])el<HTMLButtonElement>(id).disabled=!viewport?.edges.choices.length;
  const shellReady=state.cad.tool==='shellFace'&&shellTarget&&currentBodies().includes(shellTarget)&&!!viewport?.faces.choices.length;el('cadShellFaceCount').textContent=shellReady?`${state.cad.faceSelection.length} ${state.cad.faceSelection.length===1?'face':'faces'} left open · ${state.cad.faceSelection.length?'pink faces will be removed':'enclosed cavity'}`:'Select one solid, then pick faces to leave open.';el<HTMLButtonElement>('cadPickShellFaces').disabled=selected.length!==1||!!first?.locked;el<HTMLButtonElement>('cadPreviewShell').disabled=!shellReady;el<HTMLButtonElement>('cadClearShellFaces').disabled=!shellReady;
  fitPage();
}
function refreshLayerList(): void {
  const choices=cadLayers();for(const id of ['cadLayerSelect','cadDestinationLayer']){const select=el<HTMLSelectElement>(id),value=id==='cadLayerSelect'?String(activeLayer().id):select.value;select.replaceChildren(...choices.map(l=>new Option(l.name,String(l.id))));if(choices.some(l=>String(l.id)===value))select.value=value;}
  setValue('cadLayerName',activeLayer().name);el<HTMLInputElement>('cadLayerVisible').checked=activeLayer().visible;el<HTMLButtonElement>('cadNewLayer').disabled=!canAddLayer();
  const bodies=currentBodies(),pageSize=3;objectPage=Math.min(objectPage,Math.max(0,Math.ceil(bodies.length/pageSize)-1));const list=el('cadBodyList');
  const signature=JSON.stringify([objectPage,bodies.map(b=>[b.id,b.name,b.color,b.visible,b.locked]),state.cad.selected]);if(list.dataset.signature===signature)return;list.dataset.signature=signature;list.replaceChildren();
  for(const item of bodies.slice(objectPage*pageSize,(objectPage+1)*pageSize)){
    const row=document.createElement('div');row.className='cad-body-row';const pick=document.createElement('button');pick.type='button';pick.className='choice';pick.textContent=item.name;pick.style.setProperty('--piece-color',item.color);pick.setAttribute('aria-pressed',String(state.cad.selected.includes(item.id)));pick.addEventListener('click',event=>selectBodies(event.shiftKey?[...new Set([...state.cad.selected,item.id])]:[item.id]));
    const eye=document.createElement('button');eye.type='button';eye.className='choice';eye.textContent=item.visible?'◉':'◌';eye.setAttribute('aria-label',`${item.visible?'Hide':'Show'} ${item.name}`);eye.onclick=()=>attempt(()=>replaceBodies(bodies.map(b=>b.id===item.id?{...b,visible:!b.visible}:b)));
    const lock=document.createElement('button');lock.type='button';lock.className='choice';lock.textContent=item.locked?'🔒':'◇';lock.setAttribute('aria-label',`${item.locked?'Unlock':'Lock'} ${item.name}`);lock.onclick=()=>attempt(()=>replaceBodies(bodies.map(b=>b.id===item.id?{...b,locked:!b.locked}:b)));row.append(pick,eye,lock);list.append(row);
  }
  if(!bodies.length){const hint=document.createElement('p');hint.className='cad-hint';hint.textContent='An empty 3D layer, ready for your next idea.';list.append(hint);}
  el('cadObjectPage').textContent=`${objectPage+1} / ${Math.max(1,Math.ceil(bodies.length/pageSize))}`;el<HTMLButtonElement>('cadObjectsPrev').disabled=objectPage===0;el<HTMLButtonElement>('cadObjectsNext').disabled=(objectPage+1)*pageSize>=bodies.length;
}
function setSketchKind(kind: string): void {
  if(kind!==sketchKind){el<HTMLSelectElement>('cadFeatureOperation').value='new';el<HTMLInputElement>('cadThrough').checked=false;}
  sketchKind=kind;el('cadExtrudePage').hidden=kind!=='extrude';el('cadRevolvePage').hidden=kind!=='revolve';el('cadExtrudeExtras').hidden=kind!=='extrude';
  el('cadFeatureAmountLabel').firstChild!.textContent=kind==='extrude'?'Depth · + pull / − push · mm':'Revolve · degrees';el<HTMLInputElement>('cadFeatureAmount').value=kind==='extrude'?'10':'360';el('cadCreateFeature').textContent=kind==='extrude'?'↑ Make solid':'⟳ Revolve profile';
  for(const b of root!.querySelectorAll<HTMLElement>('[data-cad-sketch-kind]'))b.classList.toggle('active',b.dataset.cadSketchKind===kind);
  if(kind==='revolve'){state.cad.tool='translate';viewport?.setTool();renderProfile();el('cadFeatureSummary').textContent='Revolve a profile around its vertical axis. Use “Revolve this sketch” to spin your drawn shape.';}
  else{state.cad.tool='rectangle';viewport?.setTool();viewport?.view('sketch');if(sketch)viewport?.showSketch(sketch.points);}
  el('cadSketchFinish').hidden=true;el('cadNextFeature').hidden=false;
  el('cadSketchConstraintPage').hidden=true;el('cadSketchConstraints').hidden=false;lockSketchOutline();
  el('cadThroughRow').hidden=kind!=='extrude'||el<HTMLSelectElement>('cadFeatureOperation').value!=='cut';
  if(state.cad.open)refresh();fitPage();
}
function revolveDrawnSketch():void{
  if(state.cad.tool==='polygon')viewport?.finishPolygon();
  if(!sketch)throw new Error('Draw a rectangle, circle or polygon first.');
  // The left edge is a predictable axis that never crosses the profile.
  // Keep that axis in the original workplane, including picked and rotated faces.
  const left=Math.min(...sketch.points.map(p=>p[0])),plane=sketch.plane;
  profile=sketch.points.map(([x,y])=>[x-left,y]);profileConstraints=[];
  profilePlane={origin:plane.origin.map((n,i)=>n+left*plane.u[i]) as V3,u:[...plane.u],v:plane.normal.map(n=>-n) as V3,normal:[...plane.v]};
  el<HTMLSelectElement>('cadProfilePreset').value='custom';
  el<HTMLSelectElement>('cadFeatureOperation').value='new';
  setSketchKind('revolve');
  el('cadFeatureSummary').textContent='Your sketch · spins around its left edge, in its original workplane.';
}
function sketchActions():void{
  const ready=!!sketch&&tab==='sketch'&&sketchKind==='extrude';
  el('cadSketchActions').hidden=!ready;
  el('cadQuickApply').hidden=el('cadSketchFinish').hidden;
  el<HTMLButtonElement>('cadQuickHole').disabled=!sketch?.target;
  el<HTMLButtonElement>('cadQuickCut').disabled=!sketch?.target;
}
function pullPreview():void{
  if(!sketch||sketchKind!=='extrude'||el('cadSketchFinish').hidden)return;
  const amount=Number(el<HTMLInputElement>('cadFeatureAmount').value),taper=Number(el<HTMLInputElement>('cadTaper').value),twist=Number(el<HTMLInputElement>('cadTwist').value);
  if(!Number.isFinite(amount)||Math.abs(amount)>2000||!Number.isFinite(taper)||!Number.isFinite(twist)||Math.abs(twist)>720||taper<=0||taper>5)return;
  const operation=el<HTMLSelectElement>('cadFeatureOperation').value;
  let depth=operation==='cut'?-Math.abs(amount):amount;
  const through=operation==='cut'&&el<HTMLInputElement>('cadThrough').checked;
  if(through&&sketch.target){const bounds=viewport?.bounds(sketch.target);if(bounds)depth=-Math.max(.1,bounds.max.distanceTo(bounds.min));}
  viewport?.pullPreview.show(sketch.points,sketch.plane,depth,taper,twist,value=>{
    if(busy)return;el<HTMLInputElement>('cadThrough').checked=false;
    el<HTMLSelectElement>('cadFeatureOperation').value=sketch?.target?'auto':'new';
    el<HTMLInputElement>('cadFeatureAmount').value=String(value);pullPreview();
  });
  if(through)viewport!.pullPreview.handle.hidden=true;
  viewport?.render();
}
function beginPull(kind?:'pull'|'cut'|'hole'):void{
  if(state.cad.tool==='polygon'&&!sketch)viewport?.finishPolygon();
  if(sketchKind==='extrude'&&!sketch)throw new Error('Draw a sketch first: click two corners, or drag.');
  el('cadExtrudePage').hidden=true;el('cadRevolvePage').hidden=true;el('cadSketchConstraintPage').hidden=true;el('cadSketchConstraints').hidden=true;el('cadSketchFinish').hidden=false;el('cadNextFeature').hidden=true;
  if(sketchKind!=='extrude')return;
  if(kind){el<HTMLSelectElement>('cadFeatureOperation').value=kind==='pull'?(sketch?.target?'auto':'new'):'cut';el<HTMLInputElement>('cadFeatureAmount').value=kind==='pull'?'10':'-10';el<HTMLInputElement>('cadThrough').checked=kind==='hole';}
  el('cadThroughRow').hidden=el<HTMLSelectElement>('cadFeatureOperation').value!=='cut';
  state.cad.tool='translate';viewport?.setTool();viewport?.transform.detach();viewport?.view('iso');pullPreview();sketchActions();
  notice(kind==='hole'?'Through hole preview. The red volume will be removed all the way through. Choose Apply to cut it.':'Drag the depth handle up to pull or down to push. Green adds material; red removes it. Apply to keep the result.');
  if(mobileTools()&&kind)showTools(false);
}
function lockSketchOutline():void{
  for(const page of ['cadExtrudePage','cadRevolvePage']){const driven=page==='cadExtrudePage'?!!sketch?.constraints?.length:!!profileConstraints.length;for(const control of el(page).querySelectorAll<HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement|HTMLButtonElement>('input,select,textarea,button'))control.disabled=driven;el(page).querySelector('svg')?.setAttribute('aria-disabled',String(driven));}
}
function editSketchConstraints():void{
  if(sketchKind==='extrude'&&!sketch)throw new Error('Draw a sketch or use the dimension fields first.');
  if(sketchKind==='revolve'&&profile.length<3)throw new Error('Draw at least three profile points first.');
  el('cadExtrudePage').hidden=true;el('cadRevolvePage').hidden=true;el('cadSketchConstraints').hidden=true;el('cadSketchConstraintPage').hidden=false;
  const draft=sketch,shape=sketchKind==='revolve'?'polygon':draft?.shape??sketchType({kind:'extrude',points:draft!.points,plane:draft!.plane,height:1,taper:1,twist:0});
  if(draft&&sketchKind==='extrude')draft.shape=shape;
  const revolve=sketchKind==='revolve';new CadSketchEditor(el('cadSketchConstraintEditor'),'cadSketchConstraint',{points:()=>revolve?profile:draft!.points,shape:()=>shape,constraints:()=>revolve?profileConstraints:draft!.constraints,update:(points,constraints)=>{if(revolve){if(points.some(p=>p[0]<-1e-7))throw new Error('Keep the revolve profile to the right of its axis.');profile=points;profileConstraints=constraints;}else{draft!.points=points;draft!.constraints=constraints;}lockSketchOutline();}},{changed:fitPage,notice,guide:()=>{if(!revolve)viewport?.showSketch(draft!.points);}});fitPage();
}
function renderProfile(): void {
  const svg=el<SVGSVGElement & HTMLElement>('cadProfile');svg.replaceChildren();
  const radius=Math.max(50,...profile.map(p=>p[0])),top=Math.max(60,...profile.map(p=>p[1])),bottom=Math.min(0,...profile.map(p=>p[1])),margin=Math.max(radius,top-bottom)*.07;
  svg.setAttribute('viewBox',`${-margin} ${-top-margin} ${radius+2*margin} ${top-bottom+2*margin}`);svg.setAttribute('tabindex','0');
  const make=(name:string,attrs:Record<string,string>)=>{const node=document.createElementNS('http://www.w3.org/2000/svg',name);if(name==='path')node.setAttribute('fill','none');for(const[k,v]of Object.entries(attrs))node.setAttribute(k,v);return node;};
  const step=Math.max(10,10**Math.floor(Math.log10(Math.max(radius,top-bottom)/5))),weight=Math.max(radius,top-bottom)/60;
  for(let i=0;i<=radius;i+=step)svg.append(make('path',{d:`M${i} ${-top}V${-bottom}`,stroke:'#d5ded8','stroke-width':String(weight*.2)}));
  for(let i=Math.floor(bottom/step)*step;i<=top;i+=step)svg.append(make('path',{d:`M0 ${-i}H${radius}`,stroke:'#d5ded8','stroke-width':String(weight*.2)}));
  svg.append(make('path',{d:`M0 ${-top-margin/2}V${-bottom+margin/2}H${radius+margin/2}`,stroke:'#87929f','stroke-width':String(weight*.5)}));
  svg.append(make('polygon',{points:profile.map(p=>`${p[0]},${-p[1]}`).join(' '),fill:'#efb9cb88',stroke:'#b74775','stroke-width':String(weight*.6)}));
  profile.forEach((p,i)=>svg.append(make('circle',{cx:String(p[0]),cy:String(-p[1]),r:String(weight*1.1),fill:'#fff9e8',stroke:'#8e4068','stroke-width':String(weight*.5),'data-point':String(i)})));
  setValue('cadProfilePoints',profile.map(p=>p.map(n=>Math.round(n*10)/10).join(',')).join('; '));
}
async function createFeature(): Promise<void> {
  const amount=num('cadFeatureAmount',sketchKind==='revolve'?1:-2000,sketchKind==='revolve'?360:2000),requested=el<HTMLSelectElement>('cadFeatureOperation').value;
  const operation=requested==='auto'?(sketchKind==='extrude'&&sketch?.target?(amount<0?'cut':'join'):'new'):requested;
  let item:CadBody,target:CadBody|undefined;
  if(sketchKind==='revolve')item=featureBody({kind:'revolve',points:solveSketch(profile,profileConstraints),degrees:amount,plane:profilePlane,feature:{sketch:'polygon',constraints:structuredClone(profileConstraints)}});
  else{
    if(!sketch)throw new Error('Draw a sketch or use the dimension fields first.');
    const plane=structuredClone(sketch.plane);target=currentBodies().find(b=>b.id===(sketch?.target??state.cad.selected[0]));
    const height=operation==='cut'?-Math.abs(amount):amount;
    item=featureBody({kind:'extrude',points:sketch.points,plane,height,taper:num('cadTaper',0.01,5),twist:num('cadTwist',-720,720)});
    item.solid.feature={sketch:sketch.shape??sketchType(item.solid),constraints:structuredClone(sketch.constraints)};
    if(operation!=='new'&&target&&sketch.target===target.id){const data=viewport!.nodes.get(target.id)?.data;if(!data)throw new Error('Wait for the target solid to finish building.');item.solid.feature.attachment=captureAttachment(target,data.bounds,plane);item.solid.feature.through=operation==='cut'&&el<HTMLInputElement>('cadThrough').checked;}
    else if(operation==='cut'&&el<HTMLInputElement>('cadThrough').checked)throw new Error('Pick a supporting face to make a through cut.');
    // Fixed workplanes keep the entered depth and origin exactly. Face-attached
    // features add their contact overlap only during evaluation in each kernel.
  }
  if(operation!=='new'){
    target??=selectedBodies()[0];if(!target||target.locked)throw new Error('Pick an unlocked target piece before joining or cutting.');
    const result=combinedBody(operation==='join'?'union':'subtract',[target,item]);await cadCompute([result]);replaceBodies(currentBodies().map(b=>b.id===target!.id?result:b));selectBodies([result.id]);await viewport?.sync();
  }else await validateAndAdd(item);
  viewport?.clearSketch();state.cad.tool='translate';viewport?.setTool();sketch=undefined;notice('Solid ready. History keeps its original sketch and dimensions editable.');setTab('move');
}
async function booleanOperation(operation:'union'|'subtract'|'intersect'|'hull'):Promise<void>{
  let items=selectedBodies();if(items.length<2)throw new Error('Shift-click at least two pieces, or select them in Layers.');if(items.some(b=>b.locked))throw new Error('Unlock selected pieces before combining.');
  const target=el<HTMLSelectElement>('cadBooleanTarget').value;items=[...items].sort((a,b)=>Number(b.id===target)-Number(a.id===target));const result=combinedBody(operation,items);await cadCompute([result]);const ids=new Set(items.map(b=>b.id));replaceBodies([...currentBodies().filter(b=>!ids.has(b.id)),result]);selectBodies([result.id]);await viewport?.sync();notice('Solid built. Open History to edit the original pieces, sketches and build settings.');
}
function dropSelection(centre=false):void{
  const items=selectedBodies().filter(b=>!b.locked);if(!items.length)throw new Error('Select an unlocked piece first.');
  const bounds=items.map(b=>viewport!.bounds(b.id)).filter(b=>b!==null);if(!bounds.length)return;
  const low=Math.min(...bounds.map(b=>b!.min.z)),minX=Math.min(...bounds.map(b=>b!.min.x)),maxX=Math.max(...bounds.map(b=>b!.max.x)),minY=Math.min(...bounds.map(b=>b!.min.y)),maxY=Math.max(...bounds.map(b=>b!.max.y));
  updateSelected(b=>({...b,position:[b.position[0]-(centre?(minX+maxX)/2:0),b.position[1]-(centre?(minY+maxY)/2:0),b.position[2]-low]}));
}
function align():void{
  const target=el<HTMLSelectElement>('cadAlignTarget').value,reference=viewport!.bounds(target);if(!reference)throw new Error('Select a reference piece.');const items=selectedBodies().filter(b=>b.id!==target&&!b.locked);if(!items.length)throw new Error('Select two or more unlocked pieces to align.');
  const axis=num('cadAlignAxis',0,2),mode=el<HTMLSelectElement>('cadAlignMode').value,gap=num('cadAlignGap',-1000,1000),key=(['x','y','z'] as const)[axis];
  const ids=new Set(items.map(b=>b.id));replaceBodies(currentBodies().map(b=>{if(!ids.has(b.id))return b;const bounds=viewport!.bounds(b.id)!;const delta=mode==='min'?reference.min[key]-bounds.min[key]:mode==='max'?reference.max[key]-bounds.max[key]:mode==='after'?reference.max[key]+gap-bounds.min[key]:mode==='before'?reference.min[key]-gap-bounds.max[key]:(reference.min[key]+reference.max[key]-bounds.min[key]-bounds.max[key])/2;const position=[...b.position] as V3;position[axis]+=delta;return{...b,position};}));notice('Pieces aligned in millimetres.');
}
let mateFirst:{plane:Workplane;id:string;picked:boolean}|undefined;
function finishMate(plane:Workplane,target:string):void{
  if(!mateFirst)return;
  if(!mateFirst.picked){if(mateFirst.id!==target){selectBodies([mateFirst.id]);notice('Tap a flat face on your selected moving piece first.');return;}mateFirst={plane,id:target,picked:true};notice('Now tap a flat face on the target piece.');state.cad.tool='face';return;}
  if(target===mateFirst.id){notice('Choose a face on a different piece.');return;}
  // Quaternion rotation and pivot translation are performed by a small viewport-independent helper.
  const first=mateFirst;mateFirst=undefined;void import('./cad-mate').then(({mateBody})=>attempt(()=>{const moving=currentBodies().find(b=>b.id===first.id);if(!moving)throw new Error('The moving piece is no longer on this layer.');const result=mateBody(moving,first.plane,plane);replaceBodies(currentBodies().map(b=>b.id===result.id?result:b));selectBodies([result.id]);state.cad.tool='translate';viewport?.setTool();notice('Faces snapped together. Join them in Build to make one printable solid.');}));
}
function printBodies():CadBody[]{const scope=el<HTMLSelectElement>('cadPrintScope').value;return scope==='selection'?selectedBodies().filter(b=>b.visible):scope==='layer'?(activeLayer().visible?currentBodies().filter(b=>b.visible):[]):cadLayers().filter(l=>l.visible).flatMap(l=>l.cad!.bodies.filter(b=>b.visible));}
async function checkPrint(save=false):Promise<void>{
  const items=printBodies(),result=await cadCompute(items,'print',el<HTMLInputElement>('cadPrintBed').checked),mesh=result.mesh,size=mesh.bounds.max.map((v,i)=>v-mesh.bounds.min[i]);
  const bed=vector('cadBed',10,2000),fits=size.every((v,i)=>v<=bed[i]+0.001),below=mesh.bounds.min[2]<-0.01;
  el('cadPrintReport').textContent=`${size.map(v=>v.toFixed(2)).join(' × ')} mm\n${(mesh.volume/1000).toFixed(2)} cm³ · ${mesh.triangles.toLocaleString()} triangles\nClosed solid geometry · ${fits?'Fits the entered build volume':'Larger than the entered build volume'}${below?' · Below Z = 0':''}`;
  if(save){download(new Blob([result.stl!],{type:'model/stl'}),`${(el<HTMLInputElement>('fileName').value||'retropaint').replace(/[<>:"/\\|?*]/g,'-')}-3d-mm.stl`);play('save');notice('STL ready in millimetres. Open it in your slicer to choose orientation, supports and print settings.');}else notice('Solid checked. See the size and volume in the Print panel.');
}
function bind():void{
  const on=(id:string,action:()=>void)=>el(id).addEventListener('click',()=>attempt(action));
  const run=(id:string,action:()=>Promise<void>)=>el(id).addEventListener('click',()=>void solidAction(action));
  on('cadClose',closeCad);on('cadUndo',undo);on('cadRedo',redo);run('cadSaveProject',saveCadProject);
  on('cadImportShortcut',()=>{setTab('inspect');inspectPanel?.open('import');});on('cadPictureShortcut',()=>{setTab('inspect');inspectPanel?.open('picture');});
  on('cadHelp',()=>el<HTMLDialogElement>('cadHelpDialog').showModal());on('cadHelpDone',()=>el<HTMLDialogElement>('cadHelpDialog').close());
  el('cadToolsToggle').onclick=()=>showTools(root!.querySelector('.cad-panel')!.classList.contains('cad-tools-hidden'));el('cadHideTools').onclick=()=>showTools(false);
  root!.querySelectorAll<HTMLElement>('[data-cad-tab]').forEach(b=>{b.addEventListener('click',()=>setTab(b.dataset.cadTab!));b.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;event.preventDefault();const tabs=[...root!.querySelectorAll<HTMLElement>('[data-cad-tab]')],index=tabs.indexOf(b),next=event.key==='Home'?tabs[0]:event.key==='End'?tabs.at(-1)!:tabs[(index+(event.key==='ArrowRight'?1:tabs.length-1))%tabs.length];setTab(next.dataset.cadTab!);next.focus();});});
  root!.querySelectorAll<HTMLElement>('[data-cad-view]').forEach(b=>b.onclick=()=>viewport?.view(b.dataset.cadView!));on('cadFit',()=>viewport?.fit());
  root!.querySelectorAll<HTMLElement>('[data-cad-tool]').forEach(b=>b.onclick=()=>{state.cad.tool=b.dataset.cadTool as typeof state.cad.tool;viewport?.setTool();refresh();});
  root!.querySelectorAll<HTMLElement>('[data-cad-primitive]').forEach(b=>b.onclick=()=>void solidAction(async()=>{const item=primitive(b.dataset.cadPrimitive as Primitive,[20,20,20],currentBodies().length);if(currentBodies().length){item.position[0]=(currentBodies().length%5)*25;item.position[1]=Math.floor(currentBodies().length/5)*25;}await validateAndAdd(item);setTab('move');if(mobileTools())showTools(false);}));
  on('cadDrop',()=>dropSelection());on('cadGround',()=>dropSelection());on('cadCentre',()=>dropSelection(true));on('cadStartSketch',()=>{setTab('sketch');state.cad.tool='rectangle';viewport?.setTool();viewport?.view('sketch');});
  root!.querySelectorAll<HTMLElement>('[data-cad-edit]').forEach(b=>b.onclick=()=>{for(const p of root!.querySelectorAll<HTMLElement>('[data-cad-edit-page]'))p.hidden=p.dataset.cadEditPage!==b.dataset.cadEdit;for(const t of root!.querySelectorAll<HTMLElement>('[data-cad-edit]'))t.classList.toggle('active',t===b);fitPage();});
  on('cadApplyTransform',()=>{const position=vector('cadPos',-10000,10000),rotation=vector('cadRot',-36000,36000),first=selectedBodies()[0];if(!first)throw new Error('Select a piece first.');const delta=position.map((v,i)=>v-first.position[i]);updateSelected(b=>({...b,position:b.position.map((v,i)=>v+delta[i]) as V3,rotation}));});
  run('cadApplySize',async()=>{
    const sizes=vector('cadSize',0.1,2000),selected=selectedBodies(),first=selected[0];
    if(!first||selected.some(b=>b.locked))throw new Error('Select unlocked pieces first.');
    const data=viewport?.nodes.get(first.id)?.data;if(!data)throw new Error('Wait for the solid to finish loading.');
    const old=data.bounds.max.map((v,i)=>(v-data.bounds.min[i])*Math.abs(first.scale[i])),ratios=sizes.map((v,i)=>v/old[i]);
    if(el<HTMLInputElement>('cadKeepRatio').checked){const changed=ratios.find(v=>Math.abs(v-1)>0.001)??1;ratios.fill(changed);}
    const wall=first.solid.kind==='primitive'&&first.solid.shape==='tube'?num('cadWall',0.1,1000):undefined;
    const ids=new Set(selected.map(b=>b.id)),next=currentBodies().map(b=>{
      if(!ids.has(b.id))return b;
      // A wall entered in mm is a physical dimension, not a pre-scale value.
      // Keep the tube parametric while absorbing its size into the primitive.
      if(wall!==undefined&&b.solid.kind==='primitive'&&b.solid.shape==='tube')return {...b,scale:b.scale.map(Math.sign) as V3,solid:{...b.solid,size:b.solid.size.map((v,i)=>v*Math.abs(b.scale[i])*ratios[i]) as V3,wall}};
      return {...b,scale:b.scale.map((v,i)=>v*ratios[i]) as V3};
    });
    readCadLayer({units:'mm',bodies:next});
    for(const item of next)if(ids.has(item.id))await cadCompute([item]);
    replaceBodies(next);await viewport?.sync();notice('Size applied in millimetres. Undo restores the previous solid.');
  });
  el('cadBodyName').addEventListener('change',()=>attempt(()=>{const name=el<HTMLInputElement>('cadBodyName').value.trim()||'Piece';updateSelected(b=>({...b,name}));}));
  root!.querySelectorAll<HTMLElement>('[data-cad-color]').forEach(b=>b.onclick=()=>attempt(()=>updateSelected(item=>({...item,color:b.dataset.cadColor!}))));el('cadColour').addEventListener('change',()=>attempt(()=>updateSelected(b=>({...b,color:el<HTMLInputElement>('cadColour').value}))));
  on('cadDuplicate',()=>duplicateSelected());on('cadDelete',removeSelected);
  for(const [id,tool]of [['cadRectSketch','rectangle'],['cadCircleSketch','circle'],['cadPolygonSketch','polygon'],['cadPickFace','face']] as const)on(id,()=>{state.cad.tool=tool;sketch=undefined;el('cadFeatureSummary').textContent='Draw a new sketch';mateFirst=undefined;viewport?.setTool();if(tool!=='face')viewport?.view('sketch');notice(tool==='face'?'Tap a flat face on a piece.':tool==='circle'?'Click the centre, then the edge. Dragging also works.':tool==='polygon'?'Click each corner, then click the first corner to close the profile.':'Click two opposite corners. Dragging also works.');if(mobileTools())showTools(false);});
  el('cadPlane').addEventListener('change',()=>{if(el<HTMLSelectElement>('cadPlane').value==='face')return;viewport?.setPlane(basePlane(el<HTMLSelectElement>('cadPlane').value));sketch=undefined;state.cad.tool='rectangle';viewport?.setTool();viewport?.view('sketch');});
  on('cadUseDimensions',()=>{const shape=state.cad.tool==='circle'?'circle':'rectangle',points=sketchPoints(shape,num('cadSketchX'),num('cadSketchY'),num('cadSketchW',0.1,2000),num('cadSketchH',0.1,2000));sketch={points,plane:viewport!.getPlane(),target:viewport!.getTarget(),shape};el<HTMLSelectElement>('cadFeatureOperation').value=sketch.target?'auto':'new';viewport?.showSketch(points);el('cadFeatureSummary').textContent=`${shape==='circle'?'Ellipse / circle':'Rectangle'} ready · exact dimensions`;});on('cadFinishPolygon',()=>viewport?.finishPolygon());on('cadRevolveSketch',revolveDrawnSketch);run('cadCreateFeature',createFeature);
  on('cadSketchConstraints',editSketchConstraints);
  on('cadBackConstraints',()=>{el('cadSketchConstraintPage').hidden=true;el('cadSketchConstraints').hidden=false;el('cadExtrudePage').hidden=sketchKind!=='extrude';el('cadRevolvePage').hidden=sketchKind!=='revolve';if(sketchKind==='revolve')renderProfile();lockSketchOutline();});
  on('cadNextFeature',()=>beginPull());
  on('cadQuickPull',()=>beginPull('pull'));on('cadQuickCut',()=>beginPull('cut'));on('cadQuickHole',()=>beginPull('hole'));run('cadQuickApply',createFeature);
  on('cadQuickCancel',()=>{sketch=undefined;viewport?.cancelSketch();setSketchKind('extrude');notice('Sketch cancelled. The solid is unchanged.');});
  on('cadBackSketch',()=>{viewport?.pullPreview.clear();state.cad.tool='rectangle';viewport?.setTool();viewport?.view('sketch');if(sketch)viewport?.showSketch(sketch.points);el('cadSketchFinish').hidden=true;el('cadNextFeature').hidden=false;el('cadSketchConstraints').hidden=false;el('cadExtrudePage').hidden=sketchKind!=='extrude';el('cadRevolvePage').hidden=sketchKind!=='revolve';lockSketchOutline();});
  root!.querySelectorAll<HTMLElement>('[data-cad-sketch-kind]').forEach(b=>b.onclick=()=>setSketchKind(b.dataset.cadSketchKind!));
  for(const id of ['cadFeatureAmount','cadTaper','cadTwist','cadThrough'])el(id).addEventListener('input',pullPreview);
  el('cadFeatureOperation').addEventListener('change',()=>{pullPreview();el('cadThroughRow').hidden=sketchKind!=='extrude'||el<HTMLSelectElement>('cadFeatureOperation').value!=='cut';fitPage();});
  el('cadProfilePreset').addEventListener('change',()=>{const preset=el<HTMLSelectElement>('cadProfilePreset').value;profilePlane=basePlane('xy');profileConstraints=[];profile=preset==='vase'?[[0,0],[15,0],[18,5],[13,15],[10,30],[14,40],[12,40],[8,30],[11,15],[16,5],[13,2],[0,2]]:preset==='goblet'?[[0,0],[15,0],[15,2],[4,4],[3,24],[14,27],[19,40],[17,42],[15,30],[2,27],[0,27]]:preset==='knob'?[[0,0],[8,0],[8,6],[15,8],[18,12],[15,18],[0,18]]:[];renderProfile();});
  const svg=el('cadProfile'),profilePoint=(event:PointerEvent):V2=>{const point=new DOMPoint(event.clientX,event.clientY).matrixTransform((svg as unknown as SVGSVGElement).getScreenCTM()!.inverse()),step=state.cad.snap?state.cad.grid:0.1;return [Math.max(0,Math.min(2000,Math.round(point.x/step)*step)),Math.max(0,Math.min(2000,Math.round(-point.y/step)*step))];};
  svg.addEventListener('pointerdown',event=>{if(profileConstraints.length)return;event.preventDefault();svg.focus();const dot=event.target instanceof Element?event.target.closest('[data-point]'):null;profileDrag=dot?Number(dot.getAttribute('data-point')):profile.push(profilePoint(event))-1;svg.setPointerCapture(event.pointerId);renderProfile();});svg.addEventListener('pointermove',event=>{if(profileDrag===null)return;profile[profileDrag]=profilePoint(event);renderProfile();});for(const event of ['pointerup','pointercancel'])svg.addEventListener(event,()=>{profileDrag=null;});
  on('cadProfileUndo',()=>{profile.pop();renderProfile();});on('cadProfileClear',()=>{profile=[];renderProfile();});el('cadProfilePoints').addEventListener('change',()=>attempt(()=>{const pairs=el<HTMLTextAreaElement>('cadProfilePoints').value.split(';').filter(s=>s.trim()).map(s=>s.split(',').map(Number));if(pairs.length<3||pairs.length>256||pairs.some(p=>p.length!==2||!p.every(Number.isFinite)||p[0]<0||p[0]>2000||Math.abs(p[1])>2000))throw new Error('Enter 3–256 radius,height pairs, separated by semicolons.');profile=pairs as V2[];renderProfile();}));
  el('cadBuildPage').addEventListener('change',()=>{const page=el<HTMLSelectElement>('cadBuildPage').value;if((state.cad.tool==='edge'&&page!=='edges')||(state.cad.tool==='shellFace'&&page!=='shell')){state.cad.tool='translate';viewport?.setTool();}for(const p of root!.querySelectorAll<HTMLElement>('[data-cad-build-page]'))p.hidden=p.dataset.cadBuildPage!==page;if(forms.has(page)){forms.get(page)!.showGuide();viewport?.fit();notice(page==='loft'?'Edit the profiles in order, then Make loft. History keeps every sketch.':'Edit the profile and path, then Make sweep. Drag the path points or enter exact coordinates.');}else viewport?.clearSketch();refresh();});
  root!.querySelectorAll<HTMLElement>('[data-cad-boolean]').forEach(b=>b.onclick=()=>void solidAction(()=>booleanOperation(b.dataset.cadBoolean as 'union')));on('cadAlign',align);el('cadAlignTarget').addEventListener('change',()=>{alignReference=el<HTMLSelectElement>('cadAlignTarget').value;});
  on('cadLinearArray',()=>duplicateSelected(Math.round(num('cadArrayCount',1,30)),vector('cadArrayStep')));on('cadCircularArray',()=>duplicateSelected(Math.round(num('cadArrayCount',1,30)),[0,0,0],num('cadArrayAngle',-360,360)));for(let i=0;i<3;i++)on('cadMirror'+i,()=>updateSelected(b=>{const scale=[...b.scale] as V3;scale[i]*=-1;return{...b,scale};}));
  on('cadSnapFaces',()=>{if(selectedBodies().length!==1||selectedBodies()[0].locked)throw new Error('Select one unlocked moving piece first.');mateFirst={plane:basePlane('xy'),id:selectedBodies()[0].id,picked:false};state.cad.tool='face';viewport?.setTool();notice('Tap the flat face on your selected moving piece.');if(mobileTools())showTools(false);});
  for(const kind of ['loft','sweep'] as const)run(kind==='loft'?'cadLoftMake':'cadSweepMake',async()=>{const recipe=forms.get(kind)!.read(),item=body(recipe,kind==='loft'?'Loft':'Sweep',currentBodies().length);readCadLayer({units:'mm',bodies:[item]});await validateAndAdd(item);state.cad.tool='translate';viewport?.setTool();setTab('history');notice(`${item.name} ready. Its profiles${kind==='sweep'?', path':''} and settings stay editable in History.`);});
  run('cadPickEdges',async()=>{const items=selectedBodies();if(items.length!==1||items[0].locked)throw new Error('Select one unlocked solid first.');edgeTarget=items[0];notice('Loading the precision edge tools…');await viewport!.pickBodyEdges(edgeTarget);notice('Tap edges to select them. Drag to orbit. Open Tools to choose a radius or bevel size.');if(mobileTools())showTools(false);});
  on('cadAllEdges',()=>viewport?.edges.selectAll());on('cadNoEdges',()=>viewport?.edges.selectNone());
  el('cadFinishMode').onchange=()=>{el('cadFinishSize').closest('label')!.firstChild!.textContent=el<HTMLSelectElement>('cadFinishMode').value==='fillet'?'Radius · mm':'Equal setback · mm';};
  run('cadPreviewFinish',async()=>{if(!edgeTarget||!currentBodies().includes(edgeTarget)||!state.cad.edgeSelection.length)throw new Error('Pick edges on this solid again before finishing.');await featurePanel!.newFeature(finishedBody(edgeTarget,el<HTMLSelectElement>('cadFinishMode').value as 'fillet',num('cadFinishSize',.01,1000),state.cad.edgeSelection));});
  run('cadPickShellFaces',async()=>{const items=selectedBodies();if(items.length!==1||items[0].locked)throw new Error('Select one unlocked solid first.');shellTarget=items[0];notice('Loading the precision face tools…');await viewport!.pickBodyFaces(shellTarget);notice('Tap faces to leave them open. Pink faces will be removed. Drag to orbit; open Tools to set wall thickness.');if(mobileTools())showTools(false);});
  on('cadClearShellFaces',()=>viewport?.faces.selectNone());
  run('cadPreviewShell',async()=>{if(!shellTarget||!currentBodies().includes(shellTarget)||state.cad.tool!=='shellFace'||!viewport?.faces.choices.length)throw new Error('Pick faces on this solid again before shelling.');await featurePanel!.newFeature(shelledBody(shellTarget,num('cadShellThickness',.01,1000),state.cad.faceSelection));});
  bus.addEventListener('cad-faces',()=>{if(state.cad.open)refresh();});
  bus.addEventListener('cad-edges',()=>{if(state.cad.open)refresh();});
  el('cadLayerSelect').addEventListener('change',()=>{switchLayer(Number(el<HTMLSelectElement>('cadLayerSelect').value));selectBodies([]);objectPage=0;refresh();});on('cadNewLayer',()=>{ensureCadLayer(true);selectBodies([]);objectPage=0;refresh();});
  el('cadLayerName').addEventListener('change',()=>attempt(()=>{pushHistory();activeLayer().name=el<HTMLInputElement>('cadLayerName').value.trim()||'3D layer';layerChanged();}));el('cadLayerVisible').addEventListener('change',()=>attempt(()=>{pushHistory();activeLayer().visible=el<HTMLInputElement>('cadLayerVisible').checked;layerChanged();}));
  on('cadObjectsPrev',()=>{objectPage--;refreshLayerList();});on('cadObjectsNext',()=>{objectPage++;refreshLayerList();});on('cadSelectAll',()=>selectBodies(currentBodies().map(b=>b.id)));
  on('cadMoveLayer',()=>{const target=layers.find(l=>l.id===Number(el<HTMLSelectElement>('cadDestinationLayer').value)),source=activeLayer(),items=selectedBodies().filter(b=>!b.locked);if(!target?.cad||target===source||!items.length)throw new Error('Select pieces and choose a different destination 3D layer.');if(target.cad.bodies.length+items.length>128)throw new Error('The destination layer is full.');pushHistory();const ids=new Set(items.map(b=>b.id));source.cad={...source.cad,units:'mm',bodies:currentBodies().filter(b=>!ids.has(b.id))};target.cad={...target.cad,units:'mm',bodies:[...target.cad.bodies,...items]};switchLayer(target.id);selectBodies(items.map(b=>b.id));layerChanged();});
  on('cadRemoveLayer',()=>{if(cadLayers().length<2)throw new Error('Keep one 3D layer. You can delete individual pieces.');const id=activeLayer().id,next=cadLayers().find(l=>l.id!==id)!;pushHistory();switchLayer(next.id);deleteLayer(id);selectBodies([]);layerChanged();});
  run('cadCheckPrint',()=>checkPrint());run('cadExportStl',()=>checkPrint(true));
  for(const id of ['cadSnap','cadGrid','cadAngle'])el(id).addEventListener('change',()=>{state.cad.snap=el<HTMLInputElement>('cadSnap').checked;state.cad.grid=Number(el<HTMLSelectElement>('cadGrid').value);state.cad.angle=Number(el<HTMLSelectElement>('cadAngle').value);viewport?.selection();});
  bus.addEventListener('layers',()=>{if(state.cad.open){if(!activeLayer().cad){closeCad();return;}void viewport?.sync();refresh();}});
  bus.addEventListener('cad-selection',()=>{viewport?.selection();refresh();});bus.addEventListener('history',()=>{if(state.cad.open){refresh();queueMicrotask(()=>{if(state.cad.open)void viewport?.sync();});}});
  for(const event of ['document-created','document-opened'])bus.addEventListener(event,()=>{if(state.cad.open)closeCad(false,false);});
  document.addEventListener('keydown',event=>{if(!state.cad.open||busy||state.cad.gesture||state.cad.editing||state.cad.preview||document.querySelector('dialog[open]')||event.defaultPrevented||event.target instanceof HTMLInputElement||event.target instanceof HTMLTextAreaElement||event.target instanceof HTMLSelectElement)return;const key=event.key.toLowerCase();if(key==='?'){event.preventDefault();el<HTMLDialogElement>('cadHelpDialog').showModal();return;}if(event.ctrlKey||event.metaKey){if(key==='z'){event.preventDefault();attempt(event.shiftKey?redo:undo);}if(key==='y'){event.preventDefault();attempt(redo);}if(key==='d'){event.preventDefault();attempt(()=>duplicateSelected());}if(key==='s'){event.preventDefault();void solidAction(saveCadProject);}if(key==='a'){event.preventDefault();selectBodies(currentBodies().map(b=>b.id));}return;}if(key==='delete'||key==='backspace'){event.preventDefault();attempt(removeSelected);}if(key==='escape'){mateFirst=undefined;sketch=undefined;el('cadFeatureSummary').textContent='Sketch cancelled';state.cad.tool='translate';viewport?.cancelSketch();viewport?.setTool();selectBodies([]);}if(key==='enter'&&state.cad.tool==='polygon'){event.preventDefault();viewport?.finishPolygon();}const tools:Record<string,typeof state.cad.tool>={w:'translate',e:'rotate',r:'scale'};if(tools[key]){event.preventDefault();state.cad.tool=tools[key];viewport?.setTool();refresh();}if(key==='f'){event.preventDefault();viewport?.fit();}});
}
