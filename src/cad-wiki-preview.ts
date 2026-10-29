import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { renderOpenSCAD } from './openscad-engine';
import { cadCompute } from './cad-engine';
import type { WikiExample } from './cad-wiki-content';

/** Disposable preview: deliberately has no document editing or apply callback. */
export class WikiPreview {
  readonly dialog=document.createElement('dialog');
  private abort?:AbortController;
  private renderer?:THREE.WebGLRenderer;
  private controls?:OrbitControls;
  private mesh?:THREE.Mesh<THREE.BufferGeometry,THREE.MeshStandardMaterial>;
  private scene=new THREE.Scene();
  private camera=new THREE.PerspectiveCamera(38,1,.01,100000);
  private viewport:HTMLDivElement;
  private status:HTMLOutputElement;
  private resize:ResizeObserver;
  constructor(root:HTMLElement){
    this.dialog.id='cadWikiPreview';this.dialog.setAttribute('aria-labelledby','cadWikiPreviewTitle');
    this.dialog.innerHTML='<header><div><h2 id="cadWikiPreviewTitle">Example preview</h2><p>Your code and scene stay unchanged.</p></div><button type="button" class="choice">Close preview</button></header><div id="cadWikiPreviewCanvas" aria-label="Example model. Drag to orbit, scroll to zoom."></div><output id="cadWikiPreviewStatus" role="status" aria-live="polite"></output>';
    root.append(this.dialog);this.viewport=this.dialog.querySelector('div#cadWikiPreviewCanvas')!;this.status=this.dialog.querySelector('output')!;
    this.dialog.querySelector('button')!.onclick=()=>this.close();this.dialog.addEventListener('cancel',event=>{event.preventDefault();event.stopPropagation();this.close();});this.dialog.addEventListener('keydown',event=>event.stopPropagation());
    this.resize=new ResizeObserver(()=>this.render());this.resize.observe(this.viewport);
  }
  async show(example:WikiExample):Promise<void>{
    this.close();const controller=new AbortController();this.abort=controller;this.dialog.querySelector('h2')!.textContent=example.title;this.dialog.showModal();this.status.textContent='Rendering example with OpenSCAD…';
    try{
      const files=Object.entries(example.files??{}).map(([path,source])=>{let binary='';for(const byte of new TextEncoder().encode(source))binary+=String.fromCharCode(byte);return{path,data:btoa(binary)};});
      const native=await renderOpenSCAD(example.code,'main.scad',files,controller.signal);if(this.abort!==controller)return;
      const result=await cadCompute([native.body]);if(this.abort!==controller)return;
      this.renderer=new THREE.WebGLRenderer({antialias:true});this.renderer.setPixelRatio(Math.min(devicePixelRatio,2));this.viewport.append(this.renderer.domElement);this.scene.background=new THREE.Color('#eef3f0');this.scene.add(new THREE.HemisphereLight(0xffffff,0x536b80,2.5));const light=new THREE.DirectionalLight(0xffffff,3);light.position.set(80,-60,100);this.scene.add(light);
      const mesh=result.mesh,geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(mesh.positions,3));geometry.setIndex(new THREE.BufferAttribute(mesh.indices,1));geometry.computeVertexNormals();this.mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:'#efbf53',roughness:.55,flatShading:true}));this.scene.add(this.mesh);
      const box=new THREE.Box3().setFromObject(this.mesh),center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()),radius=Math.max(.01,size.length()/2),aspect=Math.max(.1,this.viewport.clientWidth/Math.max(1,this.viewport.clientHeight)),angle=Math.atan(Math.tan(this.camera.fov*Math.PI/360)*Math.min(1,aspect)),distance=radius/Math.sin(angle)*1.1;
      this.camera.up.set(0,0,1);this.camera.position.copy(center).add(new THREE.Vector3(1,-1,.8).normalize().multiplyScalar(distance));this.camera.near=Math.max(.001,distance/10000);this.camera.far=Math.max(1000,distance*20);this.controls=new OrbitControls(this.camera,this.renderer.domElement);this.controls.target.copy(center);this.controls.addEventListener('change',()=>this.render());this.controls.update();
      const warnings=native.logs.filter(line=>/^(ECHO:|WARNING:)/.test(line));this.status.textContent=`Ready · ${size.toArray().map(n=>n.toFixed(2)).join(' × ')} mm · ${(mesh.volume/1000).toFixed(2)} cm³ · ${mesh.triangles.toLocaleString()} triangles${warnings.length?'\n'+warnings.join('\n'):''}`;this.render();
    }catch(error){if(this.abort===controller)this.status.textContent=error instanceof Error?error.message:String(error);}
  }
  close():void{this.abort?.abort();this.abort=undefined;if(this.dialog.open)this.dialog.close();this.controls?.dispose();this.controls=undefined;this.mesh?.geometry.dispose();this.mesh?.material.dispose();this.mesh=undefined;this.renderer?.dispose();this.renderer?.domElement.remove();this.renderer=undefined;this.scene.clear();}
  private render():void{if(!this.renderer||!this.dialog.open)return;const w=Math.max(1,this.viewport.clientWidth),h=Math.max(1,this.viewport.clientHeight);this.renderer.setSize(w,h,false);this.camera.aspect=w/h;this.camera.updateProjectionMatrix();this.renderer.render(this.scene,this.camera);}
}
