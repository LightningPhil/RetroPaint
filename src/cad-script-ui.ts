import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { SCRIPT_EXAMPLES } from './cad-script';
import { numericScriptParameters, openSCADLocation } from './cad-script-editor';
import { renderOpenSCAD } from './openscad-engine';
import { CadWiki } from './cad-wiki';
import { cadCompute } from './cad-engine';
import { activeLayerId } from './layers';
import { currentBodies, selectedBodies } from './cad-document';
import { download } from './export';
import type { CadBody, CadMesh, CadScriptFile } from './cad-model';

interface Callbacks {apply:(body:CadBody,target?:string)=>Promise<void>;notice:(text:string)=>void}
export class CadScriptStudio {
  readonly dialog:HTMLDialogElement;
  private renderer?:THREE.WebGLRenderer;
  private controls?:OrbitControls;
  private camera=new THREE.PerspectiveCamera(38,1,.1,100000);
  private scene=new THREE.Scene();
  private mesh?:THREE.Mesh<THREE.BufferGeometry,THREE.MeshStandardMaterial>;
  private compiled?:CadBody;
  private files:CadScriptFile[]=[];
  private entry='main.scad';
  private editing='main.scad';
  private loading=false;
  private renderAbort?:AbortController;
  private compiledRevision=-1;
  private target?:string;
  private layer=0;
  private revision=0;
  private running=false;
  private autoTimer:ReturnType<typeof setTimeout>|undefined;
  private editor:HTMLTextAreaElement;
  private status:HTMLElement;
  private preview:HTMLElement;
  constructor(root:HTMLElement,private callbacks:Callbacks){
    this.dialog=document.createElement('dialog');this.dialog.id='cadScriptStudio';this.dialog.className='cad-script-studio';this.dialog.setAttribute('aria-labelledby','cadScriptTitle');
    this.dialog.innerHTML=`<header><div><h2 id="cadScriptTitle">Code studio</h2><p>Write a shape. Change a number. Make it real.</p></div><div class="cad-script-actions"><button class="choice" id="cadScriptHelp" type="button">Help wiki</button><button class="choice" id="cadScriptClose" type="button">Close</button></div></header>
      <div class="cad-script-toolbar"><label>Example<select id="cadScriptExample" aria-label="Script example">${Object.keys(SCRIPT_EXAMPLES).map(name=>`<option>${name}</option>`).join('')}</select></label><button class="choice" id="cadScriptLoadExample" type="button">Load example</button><button class="choice" id="cadScriptImport" type="button">Open .scad</button><button class="choice" id="cadScriptSave" type="button">Save .scad</button><input id="cadScriptFile" type="file" accept=".scad,text/plain" hidden><label>Name<input id="cadScriptName" value="Drilled flange" maxlength="60"></label></div>
      <div class="cad-script-workspace"><section class="cad-script-source"><label for="cadScriptSource" id="cadScriptSourceLabel">Model code · millimetres</label><textarea id="cadScriptSource" spellcheck="false" autocomplete="off" autocapitalize="off" aria-describedby="cadScriptStatus"></textarea><details><summary>Parameters</summary><div id="cadScriptParameters" class="cad-script-parameters"></div><p>Unique top-level numeric constants become controls after Preview. Module locals and expressions stay in code.</p></details><details><summary>Project files &amp; libraries</summary><div class="cad-script-actions"><button class="choice" id="cadScriptFolder" type="button">Open folder</button><button class="choice" id="cadScriptFiles" type="button">Add files</button></div><input id="cadScriptFolderInput" type="file" webkitdirectory multiple hidden><input id="cadScriptFilesInput" type="file" multiple hidden><label>Entry script<select id="cadScriptEntry" aria-label="Entry script"></select></label><label>Edit file<select id="cadScriptEditFile" aria-label="Edit file"></select></label><p id="cadScriptFileInfo">Standalone file</p></details></section><section class="cad-script-result"><div id="cadScriptViewport" aria-label="Script preview. Drag to orbit, scroll to zoom."></div><button class="choice" id="cadScriptFit" type="button">Fit preview</button><output id="cadScriptStats">Preview to see your solid.</output><details><summary>Language help &amp; compatibility</summary><p>Powered by the official OpenSCAD 2026.10.27 WebAssembly engine. Uses the real OpenSCAD language: functions, modules, children, comprehensions, include/use, imports, text, surfaces, minkowski and all standard modelling operations.</p><p>Open a .scad file, or Open folder to retain relative paths and libraries. Choose the entry script below. The standard MCAD library is included. Add files supplies extra dependencies or TTF/OTF fonts. Files stay on this device. Missing dependencies stop the render.</p><p>This is a rendered solid view (like desktop F6), not OpenCSG preview. Colours, background modifiers and animation are not retained in the resulting STL solid. Pure 2D designs must be extruded to join the 3D scene. Browser limits: 20 MB dependencies, 2 MB source, five minutes per render, 200,000 triangles and coordinates within ±10,000 mm. Desktop-only paths must be changed to project-relative paths.</p><p>Projects retain code and dependency files. Save .scad exports the current source only. Use Project to keep the complete editable model. Bundled font: Noto Sans; add the fonts your design requests for exact lettering. <a href="openscad/COPYING" target="_blank" rel="noopener">OpenSCAD licence</a></p></details></section></div>
      <footer><output id="cadScriptStatus" role="status" aria-live="polite">Ready. Preview with F5 or Ctrl+Enter.</output><div class="cad-script-actions"><label><input id="cadScriptAuto" type="checkbox"> Auto preview</label><button class="choice" id="cadScriptPreview" type="button">▶ Preview · F5</button><button class="choice" id="cadScriptCancel" type="button" hidden>Cancel render</button><button class="choice" id="cadScriptAdd" type="button" disabled>Add to scene</button><button class="choice" id="cadScriptUpdate" type="button" disabled hidden>Update selected</button></div></footer>`;
    root.append(this.dialog);const wiki=new CadWiki(root);this.field('cadScriptHelp').onclick=()=>wiki.open(this.field('cadScriptHelp'));
this.editor=this.field('cadScriptSource');this.editor.value=SCRIPT_EXAMPLES['Drilled flange'];this.status=this.field('cadScriptStatus');this.preview=this.field('cadScriptViewport');
    this.field('cadScriptCancel').onclick=()=>{this.cancelRender();clearTimeout(this.autoTimer);this.status.textContent='Render cancelled. Your scene is unchanged.';};
    this.field<HTMLInputElement>('cadScriptAuto').onchange=()=>{clearTimeout(this.autoTimer);if(this.field<HTMLInputElement>('cadScriptAuto').checked&&!this.compiled)this.schedule();};
    this.field('cadScriptFolder').onclick=()=>this.field<HTMLInputElement>('cadScriptFolderInput').click();
    this.field('cadScriptFiles').onclick=()=>this.field<HTMLInputElement>('cadScriptFilesInput').click();
    for(const id of ['cadScriptFolderInput','cadScriptFilesInput']){const input=this.field<HTMLInputElement>(id);input.onchange=()=>{const files=Array.from(input.files??[]);input.value='';void this.loadFiles(files,id==='cadScriptFolderInput');};}
    this.field<HTMLSelectElement>('cadScriptEntry').onchange=()=>{this.storeEditor();this.entry=this.field<HTMLSelectElement>('cadScriptEntry').value;this.switchEditor(this.entry);this.changed();};
    this.field<HTMLSelectElement>('cadScriptEditFile').onchange=()=>{if(this.loading)this.changed();this.switchEditor(this.field<HTMLSelectElement>('cadScriptEditFile').value);};
    this.field('cadScriptClose').onclick=()=>this.close();this.dialog.addEventListener('cancel',event=>{event.preventDefault();this.close();});
    this.dialog.addEventListener('keydown',event=>{event.stopPropagation();if(event.key==='F5'||(event.ctrlKey||event.metaKey)&&event.key==='Enter'){event.preventDefault();void this.build();}else if(event.key==='Tab'&&event.target===this.editor&&!event.shiftKey){event.preventDefault();this.editor.setRangeText('  ',this.editor.selectionStart,this.editor.selectionEnd,'end');this.changed();}});
    this.editor.addEventListener('input',()=>this.changed());
    this.field('cadScriptPreview').onclick=()=>void this.build();this.field('cadScriptAdd').onclick=()=>void this.apply(false);this.field('cadScriptUpdate').onclick=()=>void this.apply(true);this.field('cadScriptFit').onclick=()=>this.fit();
    this.field('cadScriptLoadExample').onclick=()=>{this.files=[];this.entry=this.editing='main.scad';this.editor.value=SCRIPT_EXAMPLES[this.field<HTMLSelectElement>('cadScriptExample').value];this.field<HTMLInputElement>('cadScriptName').value=this.field<HTMLSelectElement>('cadScriptExample').value;this.target=undefined;this.field('cadScriptUpdate').hidden=true;this.field('cadScriptAdd').textContent='Add to scene';this.fileOptions();this.changed();this.parameters();};
    this.field('cadScriptSave').onclick=()=>download(new Blob([this.editor.value],{type:'text/plain;charset=utf-8'}),this.editing.split('/').pop()||'retropaint-model.scad');
    const file=this.field<HTMLInputElement>('cadScriptFile');this.field('cadScriptImport').onclick=()=>file.click();file.onchange=()=>{const picked=file.files?.[0];file.value='';if(picked)void this.loadSource(picked);};
    new ResizeObserver(()=>this.render()).observe(this.preview);
  }
  private field<T extends HTMLElement=HTMLButtonElement>(id:string):T{return this.dialog.querySelector('#'+id) as T;}
  private encode(bytes:Uint8Array):string{let result='';for(let i=0;i<bytes.length;i+=8192)result+=String.fromCharCode(...bytes.subarray(i,i+8192));return btoa(result);}
  private decode(data:string):string{return new TextDecoder().decode(Uint8Array.from(atob(data),c=>c.charCodeAt(0)));}
  private storeEditor():void{const data=this.encode(new TextEncoder().encode(this.editor.value));this.files=this.files.filter(file=>file.path!==this.editing);this.files.push({path:this.editing,data});}
  private sourceFor(path:string):string{return path===this.editing?this.editor.value:this.decode(this.files.find(file=>file.path===path)?.data??'');}
  private switchEditor(path:string):void{this.storeEditor();this.editing=path;this.editor.value=this.decode(this.files.find(file=>file.path===path)?.data??'');this.editor.removeAttribute('aria-invalid');this.parameters();this.fileOptions();}
  private fileOptions():void{
    const paths=[...new Set([this.entry,this.editing,...this.files.filter(file=>/\.scad$/i.test(file.path)).map(file=>file.path)])];
    for(const [id,value] of [['cadScriptEntry',this.entry],['cadScriptEditFile',this.editing]]){const select=this.field<HTMLSelectElement>(id);select.replaceChildren();for(const path of paths){const option=document.createElement('option');option.value=path;option.textContent=path;select.append(option);}select.value=value;}
    this.field('cadScriptSourceLabel').textContent=this.editing+' · millimetres';this.field('cadScriptSourceLabel').title=this.editing;
    this.field('cadScriptFileInfo').textContent=new Set([this.entry,...this.files.map(f=>f.path)]).size+' supplied files · rendering '+this.entry+' · saved with Project';
  }
  private beginLoad():number{this.changed();clearTimeout(this.autoTimer);this.loading=true;this.buttons();this.status.textContent='Reading project files…';return this.revision;}
  private finishLoad(revision:number,imported:boolean):void{if(revision===this.revision){this.loading=false;this.buttons();if(imported)this.schedule();}}
  private resetTarget():void{this.target=undefined;this.field('cadScriptUpdate').hidden=true;this.field('cadScriptAdd').textContent='Add to scene';}
  private async loadSource(file:File):Promise<void>{
    const revision=this.beginLoad();let imported=false;
    try{if(file.size>2000000)throw new Error('Keep scripts below 2 MB.');const source=await file.text();if(revision!==this.revision||!this.dialog.open)return;this.files=[];this.entry=this.editing=file.name;this.editor.value=source;this.field<HTMLInputElement>('cadScriptName').value=file.name.replace(/\.scad$/i,'').slice(0,60);this.resetTarget();this.fileOptions();this.parameters();this.status.textContent='File ready. Preview to render '+this.entry+'.';imported=true;}
    catch(error){if(revision===this.revision)this.status.textContent=error instanceof Error?error.message:String(error);}
    finally{this.finishLoad(revision,imported);}
  }
  private async loadFiles(picked:File[],folder:boolean):Promise<void>{
    if(!picked.length)return;const revision=this.beginLoad();let imported=false;
    try{
      if(picked.length>2000||picked.reduce((sum,file)=>sum+file.size,0)>20000000)throw new Error('Choose at most 2,000 files, totalling under 20 MB.');
      const loaded:CadScriptFile[]=[];for(const file of picked){const path=folder?file.webkitRelativePath.split('/').slice(1).join('/'):file.name;loaded.push({path,data:this.encode(new Uint8Array(await file.arrayBuffer()))});}
      if(revision!==this.revision||!this.dialog.open)return;
      this.storeEditor();const merged=folder?loaded:[...this.files.filter(file=>!loaded.some(item=>item.path===file.path)),...loaded];
      if(merged.length>2000||merged.reduce((sum,file)=>sum+file.data.length*3/4-(file.data.endsWith('==')?2:file.data.endsWith('=')?1:0),0)>20000000)throw new Error('The combined project exceeds 2,000 files or 20 MB.');
      if(folder){const entries=loaded.filter(file=>/\.scad$/i.test(file.path));if(!entries.length)throw new Error('This folder contains no .scad files.');this.entry=this.editing=(entries.find(file=>/^(main|index)\.scad$/i.test(file.path))??entries[0]).path;this.resetTarget();this.field<HTMLInputElement>('cadScriptName').value=this.entry.split('/').pop()!.replace(/\.scad$/i,'');}
      this.files=merged;this.editor.value=this.decode(this.files.find(file=>file.path===this.editing)!.data);
      this.fileOptions();this.parameters();this.status.textContent='Files ready. Preview to render '+this.entry+'.';imported=true;
    }catch(error){if(revision===this.revision)this.status.textContent=error instanceof Error?error.message:String(error);}
    finally{this.finishLoad(revision,imported);}
  }
  open(edit=false):void {
    if(edit){const selected=selectedBodies();if(selected.length!==1||!selected[0].script){this.callbacks.notice('Select one script-generated solid to edit its code.');return;}this.files=structuredClone(selected[0].script.files??[]);this.entry=this.editing=selected[0].script.entry??'main.scad';this.editor.value=selected[0].script.source;this.target=selected[0].id;this.field<HTMLInputElement>('cadScriptName').value=selected[0].name;}
    else this.target=undefined;
    this.fileOptions();this.layer=activeLayerId;this.field('cadScriptUpdate').hidden=!this.target;this.field('cadScriptAdd').textContent=this.target?'Add as copy':'Add to scene';this.dialog.showModal();this.initRenderer();this.changed();this.parameters();this.editor.focus();void this.build();
  }
  private cancelRender():void{this.renderAbort?.abort();this.renderAbort=undefined;this.running=false;this.buttons();}
  private close():void{++this.revision;this.cancelRender();this.loading=false;clearTimeout(this.autoTimer);this.dialog.close();this.disposeRenderer();}
  private schedule():void{clearTimeout(this.autoTimer);if(this.dialog.open&&!this.loading&&this.field<HTMLInputElement>('cadScriptAuto').checked)this.autoTimer=setTimeout(()=>void this.build(),600);}
  private changed():void{++this.revision;this.compiled=undefined;this.loading=false;this.cancelRender();this.status.textContent='Code changed. Preview to rebuild; your scene is unchanged.';this.field('cadScriptStats').textContent=this.mesh?'Previous preview · rebuild to see your changes.':'Preview to see your solid.';this.editor.removeAttribute('aria-invalid');this.schedule();}
  private buttons():void{for(const id of ['cadScriptAdd','cadScriptUpdate'])this.field(id).disabled=this.loading||this.running||!this.compiled;this.field('cadScriptPreview').disabled=this.loading||this.running;this.field('cadScriptCancel').hidden=!this.running||!this.renderAbort;}
  private parameters():void {
    const host=this.field('cadScriptParameters');host.replaceChildren();
    for(const parameter of numericScriptParameters(this.editor.value)){const label=document.createElement('label'),input=document.createElement('input');label.textContent=parameter.name;input.type='number';input.step='any';input.value=parameter.value;label.append(input);host.append(label);input.onchange=()=>{if(!input.value||!Number.isFinite(Number(input.value)))return;const current=numericScriptParameters(this.editor.value).find(p=>p.name===parameter.name);if(!current)return;this.editor.value=this.editor.value.slice(0,current.start)+input.value+this.editor.value.slice(current.end);this.changed();};}
  }
  private async build():Promise<void>{
    if(this.running||this.loading||!this.dialog.open)return;clearTimeout(this.autoTimer);this.storeEditor();const revision=++this.revision,source=this.sourceFor(this.entry),controller=new AbortController();this.renderAbort=controller;this.running=true;this.compiled=undefined;this.buttons();this.status.textContent='Rendering '+this.entry+' with OpenSCAD…';
    try{const native=await renderOpenSCAD(source,this.entry,this.files.filter(file=>file.path!==this.entry),controller.signal);if(controller!==this.renderAbort||revision!==this.revision||!this.dialog.open)return;const item=native.body,result=await cadCompute([item]);if(controller!==this.renderAbort||revision!==this.revision||!this.dialog.open)return;if(!result.mesh.triangles||result.mesh.volume<=0)throw new Error('The script produced an empty solid. Check your dimensions and cuts.');this.compiled=item;this.compiledRevision=revision;this.showMesh(result.mesh);this.parameters();const messages=native.logs.filter(line=>/^(WARNING:|ECHO:|Output truncated)/.test(line));this.status.textContent='Preview ready · OpenSCAD 2026.10.27 · '+this.entry+'. Add or Update to change the scene.'+(messages.length?'\n'+messages.join('\n'):'');this.editor.removeAttribute('aria-invalid');}
    catch(error){if(controller!==this.renderAbort||revision!==this.revision)return;const message=error instanceof Error?error.message:String(error);this.status.textContent=message;this.clearMesh();this.field('cadScriptStats').textContent='No valid preview. Your original model is unchanged.';const location=openSCADLocation(message);if(location&&(location.file===this.editing||this.files.some(file=>file.path===location.file))){if(location.file!==this.editing)this.switchEditor(location.file);const lines=this.editor.value.split('\n'),start=lines.slice(0,location.line-1).reduce((sum,line)=>sum+line.length+1,0);this.editor.focus();this.editor.setSelectionRange(start,start+(lines[location.line-1]?.length??0));}this.editor.setAttribute('aria-invalid','true');this.render();}
    finally{if(controller===this.renderAbort){this.renderAbort=undefined;this.running=false;this.buttons();}}
  }
  private async apply(update:boolean):Promise<void>{
    if(!this.compiled||this.running||this.loading||this.compiledRevision!==this.revision)return;
    if(this.layer!==activeLayerId){this.status.textContent='The working layer changed. Close and reopen Code studio.';return;}
    if(update&&!currentBodies().some(item=>item.id===this.target&&!item.locked)){this.status.textContent='The original solid is missing or locked. Add a new copy instead.';return;}
    const item=structuredClone(this.compiled);item.name=this.field<HTMLInputElement>('cadScriptName').value.trim()||'Script model';this.running=true;this.buttons();
    try{await this.callbacks.apply(item,update?this.target:undefined);this.running=false;this.close();}catch(error){this.status.textContent=String(error instanceof Error?error.message:error);}finally{this.running=false;this.buttons();}
  }
  private initRenderer():void {
    if(this.renderer)return;this.scene.background=new THREE.Color('#eef3f0');this.scene.add(new THREE.HemisphereLight(0xffffff,0x536b80,2.5));const key=new THREE.DirectionalLight(0xffffff,3);key.position.set(80,-60,100);this.scene.add(key);
    this.renderer=new THREE.WebGLRenderer({antialias:true});this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));this.preview.append(this.renderer.domElement);this.camera.up.set(0,0,1);this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.addEventListener('change',()=>this.render());this.render();
  }
  private showMesh(mesh:CadMesh):void{this.clearMesh();const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(mesh.positions,3));geometry.setIndex(new THREE.BufferAttribute(mesh.indices,1));geometry.computeVertexNormals();this.mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:'#efbf53',roughness:.55,flatShading:true}));this.scene.add(this.mesh);const size=mesh.bounds.max.map((n,i)=>n-mesh.bounds.min[i]);this.field('cadScriptStats').textContent=`${size.map(n=>n.toFixed(2)).join(' × ')} mm · ${(mesh.volume/1000).toFixed(2)} cm³ · ${mesh.triangles.toLocaleString()} triangles`;this.fit();}
  private fit():void{if(!this.mesh||!this.controls)return;const box=new THREE.Box3().setFromObject(this.mesh),centre=box.getCenter(new THREE.Vector3()),direction=new THREE.Vector3(1,-1,.8).normalize(),right=new THREE.Vector3().crossVectors(direction,this.camera.up).normalize(),up=new THREE.Vector3().crossVectors(right,direction),tan=Math.tan(this.camera.fov*Math.PI/360),aspect=Math.max(.1,this.preview.clientWidth/Math.max(1,this.preview.clientHeight));let distance=5;for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z]){const p=new THREE.Vector3(x,y,z).sub(centre);distance=Math.max(distance,p.dot(direction)+Math.max(Math.abs(p.dot(up))/tan,Math.abs(p.dot(right))/(tan*aspect)));}distance*=1.15;this.camera.position.copy(centre).add(direction.multiplyScalar(distance));this.controls.target.copy(centre);this.camera.near=Math.max(.001,distance/10000);this.camera.far=Math.max(1000,distance*20);this.controls.update();this.render();}
  private render():void{if(!this.renderer||!this.dialog.open)return;const width=Math.max(1,this.preview.clientWidth),height=Math.max(1,this.preview.clientHeight);this.renderer.setSize(width,height,false);this.camera.aspect=width/height;this.camera.updateProjectionMatrix();this.renderer.render(this.scene,this.camera);}
  private clearMesh():void{if(this.mesh){this.scene.remove(this.mesh);this.mesh.geometry.dispose();this.mesh.material.dispose();this.mesh=undefined;}}
  private disposeRenderer():void{this.clearMesh();this.controls?.dispose();this.controls=undefined;this.renderer?.dispose();this.renderer?.domElement.remove();this.renderer=undefined;this.scene.clear();}
}
