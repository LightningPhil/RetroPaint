import { CadPullPreview } from './cad-pull-preview';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { TransformControls } from 'three/addons/controls/TransformControls.js';
import { toCreasedNormals } from 'three/addons/utils/BufferGeometryUtils.js';
import { cadCompute } from './cad-engine';
import { cadLayers, currentBodies, replaceBodies, selectBodies, selectedBodies } from './cad-document';
import { activeLayer, layers, renderLayers, layerChanged } from './layers';
import { W, H } from './canvas';
import { pushHistory } from './history';
import { state } from './state';
import { emit } from './bus';
import { basePlane, cadInputs, planeMatrix, readCadLayer, sketchPoints, snap, type CadBody, type CadMesh, type CadEdgeRef, type CadFaceRef, type V2, type V3, type Workplane } from './cad-model';
import { invalidatePicture } from './render-state';
import { CadEdgePicker } from './cad-edge-picker';
import { CadFacePicker } from './cad-face-picker';
import { pathBeziers, profileWorld, sweepPlane } from './cad-profiles';
import type { CadForm, CadView } from './cad-model';
import { cameraAspect, cameraForView, cameraSpan, captureCadView, sameCadView, type CadCamera } from './cad-camera';

interface DisplayBody { key: string; mesh: THREE.Mesh<THREE.BufferGeometry, THREE.MeshStandardMaterial>; data: CadMesh }
interface Callbacks { notice: (text: string) => void; sketch: (points: V2[], plane: Workplane, target?: string) => void; face: (plane: Workplane, target: string) => void; changed: () => void }
const vec = (p: V3) => new THREE.Vector3(...p), tuple = (p: THREE.Vector3): V3 => [p.x, p.y, p.z];
const rad = Math.PI / 180;
const hasFinish=(solid:CadBody['solid']):boolean=>['finish','shell','loft','sweep'].includes(solid.kind)||cadInputs(solid).some(body=>hasFinish(body.solid));
export class CadViewport {
  readonly renderer: THREE.WebGLRenderer;
  camera:CadCamera = new THREE.PerspectiveCamera(38, 1, 0.1, 30000);
  readonly scene = new THREE.Scene();
  readonly controls: OrbitControls;
  readonly transform: TransformControls;
  readonly nodes = new Map<string, DisplayBody>();
  readonly decoration = new THREE.Group();
  readonly sketchGroup = new THREE.Group();
  readonly pivot = new THREE.Object3D();
  readonly pullPreview:CadPullPreview;
  readonly edges:CadEdgePicker;
  readonly faces:CadFacePicker;
  private boxes: THREE.BoxHelper[] = [];
  private raycaster = new THREE.Raycaster();
  private plane: Workplane = basePlane('xy');
  private faceTarget: string | undefined;
  private polygon: V2[] = [];
  private sketchAnchor:V2|undefined;
  private down: { x: number; y: number; point?: V2; points?: V2[] } | null = null;
  private drag: { items: CadBody[]; matrix: THREE.Matrix4; starts: Map<string, THREE.Matrix4> } | null = null;
  private revision = 0;
  private disposed = false;
  private scheduled = false;
  private previewTimer = 0;
  private pending = new Map<string, Promise<CadMesh>>();
  private resizeObserver: ResizeObserver;
  pictureMode=false;
  private background=document.createElement('canvas');
  private foreground=document.createElement('canvas');
  private measureGroup=new THREE.Group();
  private measureLabel=document.createElement('output');
  private measurements:Array<{point:THREE.Vector3;normal:THREE.Vector3}>=[];
  private section:THREE.Plane|undefined;
  private appearance:'solid'|'xray'|'wireframe'='solid';
  private savedViewSignature='null';
  private previewSignature='';
  private previewCanvases=new Map<number,HTMLCanvasElement>();
  constructor(readonly host: HTMLElement, private callbacks: Callbacks) {
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); this.renderer.setClearColor(0, 0);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace; this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.shadowMap.enabled=true;this.renderer.shadowMap.type=THREE.PCFShadowMap;
    const canvas = this.renderer.domElement; canvas.id = 'cadCanvas'; canvas.tabIndex = 0;
    canvas.setAttribute('aria-label', '3D workbench. Drag to orbit, right-drag to pan, scroll to zoom. Select a piece to move it.');
    this.edges=new CadEdgePicker(this.scene,this.camera,canvas,()=>this.render(),event=>this.hit(event)?.distance);
    this.faces=new CadFacePicker(this.scene,this.camera,canvas,()=>this.render(),event=>this.hit(event)?.distance);
    this.pullPreview=new CadPullPreview(host,()=>this.camera);this.scene.add(this.pullPreview.group);
    host.prepend(canvas); this.camera.up.set(0, 0, 1); this.camera.position.set(130, -170, 130);
    this.background.className='cad-picture-back';this.foreground.className='cad-picture-front';this.background.setAttribute('aria-hidden','true');this.foreground.setAttribute('aria-hidden','true');host.prepend(this.background);host.append(this.foreground);this.measureLabel.className='cad-measure-label';this.measureLabel.hidden=true;host.append(this.measureLabel);this.scene.add(this.measureGroup);this.renderer.localClippingEnabled=true;
    this.controls = new OrbitControls(this.camera, canvas); this.controls.target.set(0,0,10); this.controls.enableDamping = false; this.controls.minDistance = 3; this.controls.maxDistance = 6000; this.controls.update();
    this.controls.addEventListener('change', () => this.render());
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x7d8795, 2.8));
    const key = new THREE.DirectionalLight(0xfff5e5, 3.5); key.position.set(-100, -120, 200);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-220;key.shadow.camera.right=220;key.shadow.camera.top=220;key.shadow.camera.bottom=-220;key.shadow.camera.far=700;key.shadow.normalBias=.05; this.scene.add(key);
    const fill = new THREE.DirectionalLight(0xc6e6ff, 1.5); fill.position.set(100,100,70); this.scene.add(fill);
    const grid = new THREE.GridHelper(200, 20, 0x839b9f, 0xb4c7c5); grid.rotation.x = Math.PI / 2; grid.position.z = -0.03; this.decoration.add(grid);
    const outline = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-100,-100,0),new THREE.Vector3(100,-100,0),new THREE.Vector3(100,100,0),new THREE.Vector3(-100,100,0)]),new THREE.LineBasicMaterial({ color: 0x7c9199 })); this.decoration.add(outline);
    const axis = new THREE.AxesHelper(30); axis.position.set(-100,-100,0.05); this.decoration.add(axis);
    const ground=new THREE.Mesh(new THREE.PlaneGeometry(1000,1000),new THREE.ShadowMaterial({opacity:.13}));ground.position.z=-.06;ground.receiveShadow=true;this.decoration.add(ground);
    this.scene.add(this.decoration, this.pivot, this.sketchGroup);
    this.transform = new TransformControls(this.camera, canvas); this.transform.setSize(0.85); this.scene.add(this.transform.getHelper());
    this.transform.addEventListener('change', () => this.render());
    this.transform.addEventListener('dragging-changed', event => { this.controls.enabled = !event.value && !this.isSketchTool(); });
    this.transform.addEventListener('mouseDown', () => this.startDrag());
    this.transform.addEventListener('objectChange', () => this.updateDrag());
    this.transform.addEventListener('mouseUp', () => this.finishDrag());
    canvas.addEventListener('pointerdown', this.pointerDown);
    canvas.addEventListener('pointermove', this.pointerMove);
    canvas.addEventListener('pointerup', this.pointerUp);
    canvas.addEventListener('pointercancel', this.pointerCancel);
    canvas.addEventListener('dblclick', event => { if (state.cad.tool === 'polygon') { event.preventDefault(); this.finishPolygon(); } });
    canvas.addEventListener('contextmenu', event => event.preventDefault());
    canvas.addEventListener('webglcontextlost', event => { event.preventDefault(); callbacks.notice('The 3D view paused. Your solids are safe. Return to Paint and reopen the workshop.'); });
    this.resizeObserver = new ResizeObserver(() => this.resize()); this.resizeObserver.observe(host); this.resizeObserver.observe(canvas);
    const saved=activeLayer().cad?.view;this.savedViewSignature=JSON.stringify(saved??null);if(saved){this.replaceCamera(cameraForView(saved,W/H));this.controls.target.set(...saved.target);this.controls.update();this.pictureMode=true;}this.resize();this.refreshPicture();
  }
  private isSketchTool(): boolean { return ['rectangle','circle','polygon'].includes(state.cad.tool); }
  private resize(): void {
    const canvas=this.renderer.domElement;this.host.classList.toggle('cad-picture-mode',this.pictureMode);
    if(this.pictureMode){const availableW=this.host.clientWidth,availableH=this.host.clientHeight-(this.host.closest('.cad-has-timeline')?120:0),scale=Math.min(availableW/W,availableH/H),width=Math.max(1,W*scale),height=Math.max(1,H*scale);for(const element of [canvas,this.background,this.foreground])Object.assign(element.style,{width:width+'px',height:height+'px',left:(availableW-width)/2+'px',top:(availableH-height)/2+'px'});}else canvas.removeAttribute('style');
    const w=canvas.clientWidth,h=canvas.clientHeight;if(!w||!h)return;this.renderer.setSize(w,h,false);cameraAspect(this.camera,w/h);this.render();
  }
  private replaceCamera(next:CadCamera):void{this.camera=next;this.controls.object=next;this.transform.camera=next;this.edges.setCamera(next);this.faces.setCamera(next);}
  setProjection(projection:CadView['projection']):void{const view=captureCadView(this.camera,this.controls.target);if(view.projection===projection)return;view.projection=projection;this.replaceCamera(cameraForView(view,this.renderer.domElement.clientWidth/this.renderer.domElement.clientHeight));this.controls.update();this.render();}
  setPictureMode(value:boolean):void{this.pictureMode=value;this.decoration.visible=!value;this.resize();this.refreshPicture();void this.sync();}
  refreshPicture():void{this.background.hidden=this.foreground.hidden=!this.pictureMode;if(!this.pictureMode)return;const index=layers.indexOf(activeLayer()),now=performance.now();for(const [canvas,sheets]of [[this.background,layers.slice(0,index)],[this.foreground,layers.slice(index+1)]] as const){canvas.width=W;canvas.height=H;renderLayers(canvas.getContext('2d')!,now,undefined,sheets);}this.decoration.visible=false;}
  pinPictureView(history=true,notify=true):void{const view=captureCadView(this.camera,this.controls.target);readCadLayer({units:'mm',bodies:[],view});if(cadLayers().every(l=>sameCadView(l.cad!.view,view)))return;if(history)pushHistory();for(const layer of cadLayers())layer.cad={...layer.cad!,view:structuredClone(view)};this.savedViewSignature=JSON.stringify(view);this.updatePreviews();if(notify)layerChanged();}
  resetInspection():void{this.section=undefined;this.appearance='solid';this.clearMeasure();this.applyAppearance();}
  setInspection(appearance:'solid'|'xray'|'wireframe',axis:number|null=null,offset=0,flip=false):void{this.appearance=appearance;this.section=axis===null?undefined:new THREE.Plane(new THREE.Vector3().setComponent(axis,flip?1:-1),flip?-offset:offset);this.applyAppearance();}
  private applyAppearance():void{for(const layer of cadLayers())for(const item of layer.cad!.bodies){const material=this.nodes.get(item.id)?.mesh.material;if(!material)continue;material.clippingPlanes=this.section?[this.section]:[];material.side=this.section?THREE.DoubleSide:THREE.FrontSide;material.wireframe=this.appearance==='wireframe';material.opacity=layer.opacity*(this.appearance==='xray'?.25:1);material.transparent=material.opacity<1;material.depthWrite=this.appearance!=='xray';material.needsUpdate=true;}this.render();}
  render(): void {
    if (this.scheduled || this.disposed) return; this.scheduled = true;
    requestAnimationFrame(() => { this.scheduled = false; if (!this.disposed && state.cad.open) { this.boxes.forEach(box => box.update());this.positionMeasureLabel();this.pullPreview.layout(); this.renderer.render(this.scene,this.camera); } });
  }
  async sync(): Promise<void> {
    if(this.drag)return;
    const saved=activeLayer().cad?.view,signature=JSON.stringify(saved??null),viewChanged=signature!==this.savedViewSignature;this.savedViewSignature=signature;if(viewChanged){if(saved){this.replaceCamera(cameraForView(saved,W/H));this.controls.target.set(...saved.target);this.controls.update();}this.pictureMode=!!saved;this.decoration.visible=!this.pictureMode;this.resize();}
    const revision = ++this.revision, ids = new Set<string>();
    for (const layer of cadLayers()) for (const saved of layer.cad!.bodies) {
      const item = state.cad.preview?.id === saved.id ? state.cad.preview : saved;
      ids.add(item.id); const key = JSON.stringify(item.solid), existing = this.nodes.get(item.id);
      if (!existing || existing.key !== key) {
        try {
          let job = this.pending.get(key);
          if (!job) { job = cadCompute([{ ...item, position:[0,0,0], rotation:[0,0,0], scale:[1,1,1] }]).then(result => result.mesh); this.pending.set(key,job); }
          const data = await job;
          if (this.disposed || revision !== this.revision) return;
          if (existing) this.removeNode(item.id);
          let geometry = new THREE.BufferGeometry(); geometry.setAttribute('position',new THREE.BufferAttribute(data.positions,3)); geometry.setIndex(new THREE.BufferAttribute(data.indices,1)); geometry.computeVertexNormals();const rounded=hasFinish(item.solid);if(rounded){const smooth=toCreasedNormals(geometry,Math.PI/12);geometry.dispose();geometry=smooth;}
          // Split normals at CAD creases; round solids keep their smooth shading.
          const flat = !rounded&&(item.solid.kind !== 'primitive' || ['box','wedge','pyramid'].includes(item.solid.shape));
          const mesh = new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({ color:item.color, roughness:0.56, metalness:0.04, flatShading:flat }));
          mesh.userData.id = item.id; this.scene.add(mesh); this.nodes.set(item.id,{key,mesh,data});
          mesh.castShadow=true;mesh.receiveShadow=true;
        } catch (error) { if (revision === this.revision) this.callbacks.notice(error instanceof Error ? error.message : String(error)); }
      }
      const node = this.nodes.get(item.id); if (!node) continue;
      node.mesh.position.set(...item.position); node.mesh.rotation.set(item.rotation[0]*rad,item.rotation[1]*rad,item.rotation[2]*rad,'ZYX'); node.mesh.scale.set(...item.scale);
      node.mesh.visible = item.visible && layer.visible && (!this.pictureMode||layer===activeLayer()); node.mesh.material.color.set(item.color); node.mesh.material.opacity = layer.opacity; node.mesh.material.transparent = layer.opacity < 1;
      node.mesh.updateMatrixWorld(true);
    }
    if (revision !== this.revision) return;
    for (const id of this.nodes.keys()) if (!ids.has(id)) this.removeNode(id);
    // Cache only the current scene's recipes; geometry buffers are also shared by duplicates.
    const keys = new Set([...this.nodes.values()].map(n => n.key)); for (const key of this.pending.keys()) if (!keys.has(key)) this.pending.delete(key);
    if(viewChanged&&!saved)this.fit();this.selection();this.applyAppearance();this.refreshPicture(); this.callbacks.changed();this.resize(); this.render(); clearTimeout(this.previewTimer); this.previewTimer = window.setTimeout(() => this.updatePreviews(), 350);
  }
  private removeNode(id: string): void { const node = this.nodes.get(id); if (!node) return; this.scene.remove(node.mesh); node.mesh.geometry.dispose(); node.mesh.material.dispose(); this.nodes.delete(id); }
  selection(): void {
    this.boxes.forEach(box => { this.scene.remove(box); box.geometry.dispose(); (box.material as THREE.Material).dispose(); }); this.boxes = [];
    const items = selectedBodies().filter(b => b.visible), bounds = new THREE.Box3();
    for (const item of items) {
      const node = this.nodes.get(item.id); if (!node || !node.mesh.visible) continue;
      const box = new THREE.BoxHelper(node.mesh,item.locked ? 0x8a8b9a : 0xd44979); this.scene.add(box); this.boxes.push(box); bounds.expandByObject(node.mesh);
    }
    this.transform.detach();
    if (!state.cad.preview && !state.cad.editing && items.length && items.every(b => !b.locked) && !bounds.isEmpty() && ['translate','rotate','scale'].includes(state.cad.tool)) {
      this.pivot.position.copy(items.length === 1 ? vec(items[0].position) : bounds.getCenter(new THREE.Vector3())); this.pivot.rotation.set(0,0,0); this.pivot.scale.set(1,1,1);
      if (state.cad.tool === 'scale' && items.length === 1) this.pivot.rotation.copy(this.nodes.get(items[0].id)!.mesh.rotation);
      this.transform.setMode(state.cad.tool as 'translate'|'rotate'|'scale'); this.transform.setSpace(state.cad.tool === 'scale' ? 'local' : 'world'); this.transform.attach(this.pivot);
    }
    this.transform.setTranslationSnap(state.cad.snap ? state.cad.grid : null); this.transform.setRotationSnap(state.cad.snap ? state.cad.angle*rad : null); this.transform.setScaleSnap(state.cad.snap ? 0.1 : null);
    this.controls.enabled = !this.isSketchTool(); this.render();
  }
  bounds(id: string): THREE.Box3 | null { const node = this.nodes.get(id); return node ? new THREE.Box3().setFromObject(node.mesh) : null; }
  private startDrag(): void {
    const items = selectedBodies(); if (!items.length || items.some(b => b.locked)) return;
    this.pivot.updateMatrixWorld(true); this.drag = { items: structuredClone(items), matrix:this.pivot.matrixWorld.clone(), starts:new Map(items.map(item => [item.id,this.nodes.get(item.id)!.mesh.matrix.clone()])) };state.cad.gesture=true; pushHistory(); emit('cad-gesture',true);
  }
  private updateDrag(): void {
    if (!this.drag) return;
    this.pivot.updateMatrixWorld(true); const delta = this.pivot.matrixWorld.clone().multiply(this.drag.matrix.clone().invert());
    for (const item of this.drag.items) { const mesh = this.nodes.get(item.id)?.mesh; if (!mesh) continue; const matrix = delta.clone().multiply(this.drag.starts.get(item.id)!); matrix.decompose(mesh.position,mesh.quaternion,mesh.scale); mesh.updateMatrixWorld(true); }
    this.render();
  }
  private finishDrag(): void {
    if (!this.drag) return; const ids = new Set(this.drag.items.map(b => b.id));
    const next = currentBodies().map(item => { if (!ids.has(item.id)) return item; const mesh = this.nodes.get(item.id)!.mesh, e = new THREE.Euler().setFromQuaternion(mesh.quaternion,'ZYX'); return {...item,position:tuple(mesh.position),rotation:[e.x/rad,e.y/rad,e.z/rad] as V3,scale:tuple(mesh.scale)}; });
    this.drag = null;state.cad.gesture=false;
    try{replaceBodies(next,false);}catch(error){this.callbacks.notice(error instanceof Error?error.message:String(error));void this.sync();}
    finally{emit('cad-gesture',false);this.callbacks.changed();}
  }
  private ray(event: PointerEvent): void { const r = this.renderer.domElement.getBoundingClientRect(); this.camera.updateMatrixWorld();this.raycaster.setFromCamera(new THREE.Vector2((event.clientX-r.left)/r.width*2-1,-(event.clientY-r.top)/r.height*2+1),this.camera); }
  private hit(event: PointerEvent): THREE.Intersection | undefined { this.ray(event); return this.raycaster.intersectObjects([...this.nodes.values()].filter(n => n.mesh.visible).map(n => n.mesh),false).find(hit=>!this.section||this.section.distanceToPoint(hit.point)>=-.00001); }
  private sketchPoint(event: PointerEvent): V2 | undefined {
    this.ray(event); const hit = this.raycaster.ray.intersectPlane(new THREE.Plane().setFromNormalAndCoplanarPoint(vec(this.plane.normal),vec(this.plane.origin)),new THREE.Vector3());
    if (!hit) return; const relative = hit.sub(vec(this.plane.origin)), step = state.cad.snap ? state.cad.grid : 0;
    return [snap(relative.dot(vec(this.plane.u)),step),snap(relative.dot(vec(this.plane.v)),step)];
  }
  private pointerDown = (event: PointerEvent): void => {
    if(this.pullPreview.group.children.length)return;
    if (event.button !== 0 || this.transform.dragging || ((state.cad.editing || state.cad.preview)&&!['edge','shellFace'].includes(state.cad.tool))) return;
    this.down = {x:event.clientX,y:event.clientY,point:this.isSketchTool()?(this.sketchAnchor??this.sketchPoint(event)):undefined};
    if (this.isSketchTool()) { event.preventDefault(); this.renderer.domElement.setPointerCapture(event.pointerId); }
  };
  private pointerMove = (event: PointerEvent): void => {
    if(state.cad.tool==='edge'){this.edges.hover(event);return;}
    if(state.cad.tool==='shellFace'){this.faces.hover(event);return;}
    if(state.cad.tool==='polygon'&&this.polygon.length){const end=this.sketchPoint(event);if(end)this.showSketch([...this.polygon,end],false);return;}
    if ((!this.down?.point&&!this.sketchAnchor) || !this.isSketchTool()) return;
    const end = this.sketchPoint(event); if (!end) return;
    const [x,y] = this.down?.point??this.sketchAnchor!;
    if (state.cad.tool === 'polygon') { this.showSketch([...this.polygon,end],false); return; }
    const width=end[0]-x,height=event.shiftKey?Math.sign(end[1]-y||1)*Math.abs(width):end[1]-y;
    const points = state.cad.tool === 'circle' ? sketchPoints('circle',x,y,Math.hypot(width,height)*2,Math.hypot(width,height)*2) : sketchPoints('rectangle',x,y,width,height);
    if(this.down)this.down.points = points; this.showSketch(points,true);
  };
  private pointerUp = (event: PointerEvent): void => {
    if(this.down?.point&&this.isSketchTool()&&state.cad.tool!=='polygon')this.pointerMove(event);
    const start = this.down; this.down = null; if (!start || this.transform.dragging || this.drag) return;
    if(state.cad.tool==='edge'){if(Math.hypot(event.clientX-start.x,event.clientY-start.y)<5)this.edges.pick(event);return;}
    if(state.cad.tool==='shellFace'){if(Math.hypot(event.clientX-start.x,event.clientY-start.y)<5)this.faces.pick(event);return;}
    if (this.isSketchTool()) {
      if (state.cad.tool === 'polygon') {
        const point=this.sketchPoint(event);
        if(this.polygon.length>=3){
          const first=vec(this.plane.origin).addScaledVector(vec(this.plane.u),this.polygon[0][0]).addScaledVector(vec(this.plane.v),this.polygon[0][1]).project(this.camera),r=this.renderer.domElement.getBoundingClientRect();
          if((point&&Math.hypot(point[0]-this.polygon[0][0],point[1]-this.polygon[0][1])<.01)||Math.hypot(event.clientX-(r.left+(first.x+1)*r.width/2),event.clientY-(r.top+(1-first.y)*r.height/2))<=12){this.finishPolygon();return;}
        }
        if (point && (!this.polygon.length || Math.hypot(point[0]-this.polygon.at(-1)![0],point[1]-this.polygon.at(-1)![1])>0.01)) this.polygon.push(point); this.showSketch(this.polygon,false); return;
      }
      if (start.points && (this.sketchAnchor||Math.hypot(event.clientX-start.x,event.clientY-start.y)>4)) {this.sketchAnchor=undefined;this.callbacks.sketch(start.points,structuredClone(this.plane),this.faceTarget);}
      else{this.sketchAnchor=start.point;if(start.point)this.showSketch([start.point],false);this.callbacks.notice(state.cad.tool==='circle'?'Centre set. Move the pointer, then click the circle edge.':'First corner set. Move the pointer, then click the opposite corner.');}
      return;
    }
    if (Math.hypot(event.clientX-start.x,event.clientY-start.y)>5 || (this.transform.object && this.transform.axis)) return;
    if(state.cad.tool==='measure'){this.measure(event);return;}
    const hit=this.hit(event), id=hit?.object.userData.id as string | undefined;
    if (state.cad.tool === 'face' && hit && id) { this.pickFace(hit,id); return; }
    if (!id || !currentBodies().some(b => b.id === id)) { if (id) this.callbacks.notice('Choose that piece’s 3D layer to edit it.'); else selectBodies([]); return; }
    selectBodies(event.shiftKey ? state.cad.selected.includes(id) ? state.cad.selected.filter(s => s!==id) : [...state.cad.selected,id] : [id]);
  };
  private pointerCancel = (): void => { this.down = null;this.sketchAnchor=undefined; if (this.drag) this.finishDrag(); };
  private pickFace(hit: THREE.Intersection, id: string): void {
    if (!hit.face || !currentBodies().some(b => b.id === id && !b.locked)) { this.callbacks.notice('Choose an unlocked piece on this 3D layer.'); return; }
    const mesh = hit.object as THREE.Mesh<THREE.BufferGeometry>, normal=hit.face.normal.clone().applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld)).normalize();
    // A smooth curved surface has no connected coplanar patch large enough to sketch on.
    const geometry=mesh.geometry, indices=geometry.index, positions=geometry.getAttribute('position'), localNormal=hit.face.normal, origin=new THREE.Vector3().fromBufferAttribute(positions,hit.face.a),indexAt=(i:number)=>indices?indices.getX(i):i; let area=0;
    for(let i=0;i<(indices?.count??positions.count);i+=3){const a=new THREE.Vector3().fromBufferAttribute(positions,indexAt(i)),b=new THREE.Vector3().fromBufferAttribute(positions,indexAt(i+1)),c=new THREE.Vector3().fromBufferAttribute(positions,indexAt(i+2)),cross=b.sub(a).cross(c.sub(a));if(cross.clone().normalize().dot(localNormal)>0.99999&&Math.abs(a.sub(origin).dot(localNormal))<0.0001)area+=cross.length()/2;}
    if(area < 0.5 || (area < (geometry.boundingBox?.getSize(new THREE.Vector3()).lengthSq()??100)*0.01 && this.nodes.get(id)?.data.triangles!>100)){this.callbacks.notice('Pick a flat face, such as a cube side or cylinder end.');return;}
    const reference=Math.abs(normal.z)>0.9?new THREE.Vector3(1,0,0):new THREE.Vector3(0,0,1);
    const u=reference.addScaledVector(normal,-reference.dot(normal)).normalize(),v=normal.clone().cross(u).normalize();
    // Anchor to the face centre rather than the exact tap, making dimensions repeatable.
    const bounds=this.bounds(id)!,centre=bounds.getCenter(new THREE.Vector3()),point=centre.addScaledVector(normal,hit.point.clone().sub(centre).dot(normal));
    this.plane={origin:tuple(point),u:tuple(u),v:tuple(v),normal:tuple(normal)}; this.faceTarget=id; this.polygon=[];
    selectBodies([id]); this.showPlane(); this.callbacks.face(structuredClone(this.plane),id);
  }
  setPlane(plane: Workplane, target?: string): void { this.plane=structuredClone(plane);this.faceTarget=target;this.polygon=[];this.clearSketch();this.showPlane(); }
  getPlane(): Workplane { return structuredClone(this.plane); }
  getTarget(): string | undefined { return this.faceTarget; }
  setTool(): void { this.sketchAnchor=undefined;this.down=null;this.polygon=[];if(!this.isSketchTool()){this.camera.up.set(0,0,1);this.controls.update();}if(state.cad.tool!=='measure')this.clearMeasure();if(state.cad.tool!=='edge'){this.edges.clear();this.renderer.domElement.style.cursor='';}if(state.cad.tool!=='shellFace')this.faces.clear();this.selection();if(this.isSketchTool()||state.cad.tool==='face')this.showPlane();else this.clearSketch(); }
  clearMeasure():void{for(const child of [...this.measureGroup.children]){this.measureGroup.remove(child);const item=child as THREE.Mesh;item.geometry?.dispose();(item.material as THREE.Material)?.dispose();}this.measurements=[];this.measureLabel.hidden=true;emit('cad-measure',null);this.render();}
  private measure(event:PointerEvent):void{
    const hit=this.hit(event);if(!hit?.face)return;let point=hit.point.clone(),snapped=false;const mesh=hit.object as THREE.Mesh<THREE.BufferGeometry>,positions=mesh.geometry.getAttribute('position'),rect=this.renderer.domElement.getBoundingClientRect();let closest=11;
    for(let i=0;i<positions.count;i++){const vertex=new THREE.Vector3().fromBufferAttribute(positions,i).applyMatrix4(mesh.matrixWorld);if(this.section&&this.section.distanceToPoint(vertex)<0)continue;const screen=vertex.clone().project(this.camera),distance=Math.hypot((screen.x+1)*rect.width/2+rect.left-event.clientX,(1-screen.y)*rect.height/2+rect.top-event.clientY);if(distance<closest&&vertex.clone().sub(this.raycaster.ray.origin).dot(this.raycaster.ray.direction)<=hit.distance+cameraSpan(this.camera,this.controls.target)*.03){closest=distance;point=vertex;snapped=true;}}
    if(this.measurements.length===2)this.clearMeasure();this.measurements.push({point,normal:hit.face.normal.clone().applyNormalMatrix(new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld)).normalize()});
    const material=new THREE.MeshBasicMaterial({color:0xbc3e80,depthTest:false}),sphere=new THREE.Mesh(new THREE.SphereGeometry(cameraSpan(this.camera,this.controls.target)*.006,12,8),material);sphere.position.copy(point);sphere.renderOrder=15;this.measureGroup.add(sphere);
    if(this.measurements.length===2){const [a,b]=this.measurements,delta=b.point.clone().sub(a.point),distance=delta.length(),angle=Math.acos(THREE.MathUtils.clamp(a.normal.dot(b.normal),-1,1))*180/Math.PI,line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([a.point,b.point]),new THREE.LineBasicMaterial({color:0xbc3e80,depthTest:false}));line.renderOrder=15;this.measureGroup.add(line);this.measureLabel.value=distance.toFixed(3)+' mm';this.measureLabel.hidden=false;emit('cad-measure',{distance,delta:tuple(delta),angle,point:tuple(point),snapped});this.callbacks.notice(`Distance ${distance.toFixed(3)} mm · face-normal angle ${angle.toFixed(2)}°`);}else{emit('cad-measure',{point:tuple(point),snapped});this.callbacks.notice((snapped?'Vertex snapped. ':'Point set. ')+'Pick the second point; drag to orbit.');}this.render();
  }
  private positionMeasureLabel():void{if(this.measurements.length!==2||this.measureLabel.hidden)return;const midpoint=this.measurements[0].point.clone().add(this.measurements[1].point).multiplyScalar(.5).project(this.camera),r=this.renderer.domElement.getBoundingClientRect(),host=this.host.getBoundingClientRect();this.measureLabel.style.left=(r.left-host.left+(midpoint.x+1)*r.width/2)+'px';this.measureLabel.style.top=(r.top-host.top+(1-midpoint.y)*r.height/2-15)+'px';}
  async pickBodyEdges(item:CadBody):Promise<void>{const pose=new THREE.Object3D();pose.position.set(...item.position);pose.rotation.set(...item.rotation.map(n=>n*rad) as V3,'ZYX');pose.updateMatrix();state.cad.tool='edge';this.setTool();await this.edges.start({...structuredClone(item),position:[0,0,0],rotation:[0,0,0]},pose.matrix);}
  async pickFeatureEdges(root:CadBody,path:number[],source:CadBody,refs:CadEdgeRef[],changed:()=>void):Promise<void>{const matrix=new THREE.Matrix4();let item=root;const append=(item:CadBody)=>{const pose=new THREE.Object3D();pose.position.set(...item.position);pose.rotation.set(...item.rotation.map(n=>n*rad) as V3,'ZYX');pose.scale.set(...item.scale);pose.updateMatrix();matrix.multiply(pose.matrix);};append(item);for(const index of path){item=cadInputs(item.solid)[index];append(item);}state.cad.tool='edge';this.setTool();await this.edges.start(source,matrix,refs,changed);}
  async pickBodyFaces(item:CadBody):Promise<void>{const pose=new THREE.Object3D();pose.position.set(...item.position);pose.rotation.set(...item.rotation.map(n=>n*rad) as V3,'ZYX');pose.updateMatrix();state.cad.tool='shellFace';this.setTool();await this.faces.start({...structuredClone(item),position:[0,0,0],rotation:[0,0,0]},pose.matrix);}
  async pickFeatureFaces(root:CadBody,path:number[],source:CadBody,refs:CadFaceRef[],changed:()=>void):Promise<void>{const matrix=new THREE.Matrix4();let item=root;const append=(item:CadBody)=>{const pose=new THREE.Object3D();pose.position.set(...item.position);pose.rotation.set(...item.rotation.map(n=>n*rad) as V3,'ZYX');pose.scale.set(...item.scale);pose.updateMatrix();matrix.multiply(pose.matrix);};append(item);for(const index of path){item=cadInputs(item.solid)[index];append(item);}state.cad.tool='shellFace';this.setTool();await this.faces.start(source,matrix,refs,changed);}
  finishPolygon(): void { if(this.polygon.length<3){this.callbacks.notice('Tap at least three points, then Finish sketch.');return;}const points=this.polygon;this.polygon=[];this.showSketch(points,true);this.callbacks.sketch(points,structuredClone(this.plane),this.faceTarget); }
  cancelSketch():void{this.sketchAnchor=undefined;this.down=null;this.polygon=[];this.clearSketch();}
  clearSketch(): void { this.pullPreview.clear();this.sketchGroup.userData.form=false;for(const child of [...this.sketchGroup.children]){this.sketchGroup.remove(child);const object=child as THREE.Line;object.geometry?.dispose();if(object.material)for(const material of Array.isArray(object.material)?object.material:[object.material])material.dispose();}this.render(); }
  showPlane(): void {
    this.clearSketch();const geometry=new THREE.PlaneGeometry(100,100),material=new THREE.MeshBasicMaterial({color:0x77c9d2,transparent:true,opacity:0.1,side:THREE.DoubleSide,depthWrite:false});
    const plane=new THREE.Mesh(geometry,material);plane.applyMatrix4(new THREE.Matrix4().fromArray(planeMatrix(this.plane)));plane.position.addScaledVector(vec(this.plane.normal),0.025);this.sketchGroup.add(plane);this.render();
  }
  showSketch(points: V2[], closed=true): void {
    this.showPlane();if(!points.length)return;
    const world=points.map(p=>vec(this.plane.origin).addScaledVector(vec(this.plane.u),p[0]).addScaledVector(vec(this.plane.v),p[1]).addScaledVector(vec(this.plane.normal),0.05));
    const geometry=new THREE.BufferGeometry().setFromPoints(world),material=new THREE.LineBasicMaterial({color:0xb42b64,depthTest:false});
    this.sketchGroup.add(closed?new THREE.LineLoop(geometry,material):new THREE.Line(geometry,material));
    if(!closed){for(const p of world){const dot=new THREE.Mesh(new THREE.SphereGeometry(cameraSpan(this.camera,vec(this.plane.origin))/Math.max(1,this.host.clientHeight)*4,8,6),new THREE.MeshBasicMaterial({color:0xb42b64,depthTest:false}));dot.position.copy(p);dot.renderOrder=7;this.sketchGroup.add(dot);}}
    if(closed&&points.length>=3){const shape=new THREE.Shape(points.map(p=>new THREE.Vector2(...p))),fill=new THREE.Mesh(new THREE.ShapeGeometry(shape),new THREE.MeshBasicMaterial({color:0xe44591,transparent:true,opacity:.3,side:THREE.DoubleSide,depthTest:false,depthWrite:false}));fill.applyMatrix4(new THREE.Matrix4().fromArray(planeMatrix(this.plane)));fill.renderOrder=5;this.sketchGroup.add(fill);}
    this.render();
  }
  showFormInputs(form:CadForm,matrix=new THREE.Matrix4()):void {
    this.clearSketch();this.sketchGroup.userData.form=true;
    const line=(points:V3[],closed:boolean,color:number)=>{if(points.some(p=>p.some(n=>!Number.isFinite(n))))return;const geometry=new THREE.BufferGeometry().setFromPoints(points.map(p=>vec(p).applyMatrix4(matrix))),material=new THREE.LineBasicMaterial({color,depthTest:false,transparent:true,opacity:.8});this.sketchGroup.add(closed?new THREE.LineLoop(geometry,material):new THREE.Line(geometry,material));};
    if(form.kind==='loft')form.profiles.forEach((p,i)=>line(profileWorld(p),true,i%2?0xb34b87:0x008b86));
    else{const points=form.path.points;if(points.length<2)return;const path=points.length>2&&form.path.smooth?pathBeziers(points).flatMap(c=>new THREE.CubicBezierCurve3(...c.map(vec) as [THREE.Vector3,THREE.Vector3,THREE.Vector3,THREE.Vector3]).getPoints(32).map(tuple)):points;line(path,false,0x9256a7);line(profileWorld({...form.profile,plane:sweepPlane(points,form.roll),rotation:0}),true,0x008b86);}
    this.render();
  }
  showFeatureForm(root:CadBody,path:number[],form:CadForm):void {
    const matrix=new THREE.Matrix4();let item=root;const append=(body:CadBody)=>{const pose=new THREE.Object3D();pose.position.set(...body.position);pose.rotation.set(...body.rotation.map(n=>n*rad) as V3,'ZYX');pose.scale.set(...body.scale);pose.updateMatrix();matrix.multiply(pose.matrix);};append(item);for(const index of path){item=cadInputs(item.solid)[index];append(item);}this.showFormInputs(form,matrix);
  }
  view(name: string): void {
    const target=this.controls.target.clone(),distance=this.camera.position.distanceTo(target);
    this.camera.up.copy(name==='sketch'?vec(this.plane.v):new THREE.Vector3(0,0,1));
    const direction=name==='top'?new THREE.Vector3(0,0,1):name==='bottom'?new THREE.Vector3(0,0,-1):name==='front'?new THREE.Vector3(0,-1,0):name==='back'?new THREE.Vector3(0,1,0):name==='right'?new THREE.Vector3(1,0,0):name==='left'?new THREE.Vector3(-1,0,0):name==='sketch'?vec(this.plane.normal):new THREE.Vector3(1,-1.3,1);
    if(name==='sketch')target.copy(vec(this.plane.origin));this.controls.target.copy(target);this.camera.position.copy(target).add(direction.normalize().multiplyScalar(distance));this.controls.update();this.render();
  }
  fit(selectionOnly=false): void {
    const box=new THREE.Box3();for(const[id,node]of this.nodes)if(node.mesh.visible&&(!selectionOnly||state.cad.selected.includes(id)))box.expandByObject(node.mesh);
    if(this.sketchGroup.userData.form)box.expandByObject(this.sketchGroup);
    if(box.isEmpty()){this.camera.position.set(130,-170,130);this.controls.target.set(0,0,10);}else{const centre=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()),aspect=this.renderer.domElement.clientWidth/this.renderer.domElement.clientHeight,distance=Math.max(35,size.length()*1.6,Math.max(size.x,size.y)/aspect*1.7);this.controls.target.copy(centre);this.camera.position.copy(centre).add(new THREE.Vector3(1,-1.3,1).normalize().multiplyScalar(distance));if(this.camera instanceof THREE.OrthographicCamera){const span=Math.max(25,size.length()*1.25,size.length()/aspect*1.25);this.camera.top=span/2;this.camera.bottom=-span/2;this.camera.zoom=1;cameraAspect(this.camera,aspect);}}this.controls.update();this.render();
  }
  updatePreviews(): void {
    if(this.disposed||state.cad.preview||state.cad.editing)return;
    const sheets=cadLayers(),view=this.pictureMode?captureCadView(this.camera,this.controls.target):sheets.find(l=>l.cad?.view)?.cad?.view,signature=JSON.stringify([W,H,view,sheets.map(l=>[l.id,l.cad!.bodies.map(b=>[b.id,this.nodes.get(b.id)?.key,b.visible,b.color,b.position,b.rotation,b.scale])])]);
    // Returning from a timeline/inspection preview must preserve the unchanged picture bytes.
    if(signature===this.previewSignature&&sheets.every(l=>this.previewCanvases.get(l.id)===l.canvas)){this.refreshPicture();return;}
    const edgeVisible=this.edges.group.visible,faceVisible=this.faces.group.visible;this.edges.group.visible=false;this.faces.group.visible=false;this.measureGroup.visible=false;const visibility=new Map([...this.nodes].map(([id,n])=>[id,n.mesh.visible])),materials=new Map([...this.nodes].map(([id,n])=>{const m=n.mesh.material;return[id,{opacity:m.opacity,transparent:m.transparent,side:m.side,wireframe:m.wireframe,clippingPlanes:m.clippingPlanes,depthWrite:m.depthWrite}] as const;})),helper=this.transform.getHelper(),wasHelper=helper.visible;helper.visible=false;this.decoration.visible=false;this.sketchGroup.visible=false;this.pullPreview.group.visible=false;this.boxes.forEach(b=>b.visible=false);for(const node of this.nodes.values()){Object.assign(node.mesh.material,{opacity:1,transparent:false,side:THREE.FrontSide,wireframe:false,clippingPlanes:[],depthWrite:true,needsUpdate:true});}
    const camera=view?cameraForView(view,W/H):new THREE.PerspectiveCamera(38,W/H,.1,30000);if(!view)camera.up.set(0,0,1);cameraAspect(camera,W/H);
    const allIds=new Set(cadLayers().flatMap(l=>l.cad!.bodies.filter(b=>b.visible).map(b=>b.id))),box=new THREE.Box3();for(const[id,node]of this.nodes)if(allIds.has(id))box.expandByObject(node.mesh);
    if(!view&&!box.isEmpty()){const centre=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()),distance=Math.max(40,size.length()*1.7,Math.max(size.x,size.y)/(W/H)*1.9);camera.position.copy(centre).add(new THREE.Vector3(1,-1.3,1).normalize().multiplyScalar(distance));camera.lookAt(centre);}
    const originalSize=this.renderer.getSize(new THREE.Vector2()),ratio=Math.min(1,1200/Math.max(W,H));this.renderer.setSize(Math.max(1,Math.round(W*ratio)),Math.max(1,Math.round(H*ratio)),false);
    for(const layer of cadLayers()){
      const ids=new Set(layer.cad!.bodies.filter(b=>b.visible).map(b=>b.id));for(const[id,node]of this.nodes)node.mesh.visible=ids.has(id);
      this.renderer.render(this.scene,camera);const ctx=layer.canvas.getContext('2d')!;ctx.clearRect(0,0,layer.canvas.width,layer.canvas.height);ctx.drawImage(this.renderer.domElement,0,0,layer.canvas.width,layer.canvas.height);
    }
    for(const[id,node]of this.nodes){node.mesh.visible=visibility.get(id)??false;Object.assign(node.mesh.material,materials.get(id),{needsUpdate:true});}
    this.renderer.setSize(originalSize.x,originalSize.y,false);this.edges.group.visible=edgeVisible;this.faces.group.visible=faceVisible;this.measureGroup.visible=true;helper.visible=wasHelper;this.decoration.visible=!this.pictureMode;this.sketchGroup.visible=true;this.pullPreview.group.visible=true;this.boxes.forEach(b=>b.visible=true);this.previewSignature=signature;this.previewCanvases=new Map(sheets.map(l=>[l.id,l.canvas]));this.refreshPicture();invalidatePicture();emit('cad-preview');this.render();
  }
  dispose(update=true): void {
    if(this.drag)this.finishDrag();if(update)this.updatePreviews();this.edges.clear();this.faces.clear();this.disposed=true;++this.revision;clearTimeout(this.previewTimer);this.resizeObserver.disconnect();this.controls.dispose();this.transform.dispose();
    for(const id of [...this.nodes.keys()])this.removeNode(id);this.clearSketch();this.clearMeasure();this.scene.traverse(object=>{if(object instanceof THREE.Line||object instanceof THREE.Mesh){object.geometry.dispose();for(const material of Array.isArray(object.material)?object.material:[object.material])material.dispose();}if(object instanceof THREE.DirectionalLight)object.shadow.dispose();});this.pending.clear();this.pullPreview.dispose();this.renderer.dispose();this.renderer.domElement.remove();this.background.remove();this.foreground.remove();this.measureLabel.remove();
  }
}
