import * as THREE from 'three';
import { cadCompute } from './cad-engine';
import { state } from './state';
import { emit } from './bus';
import type { CadBody, CadFace, CadFaceRef } from './cad-model';

/** Whole B-rep faces, including curved surfaces, independent of display triangles. */
export class CadFacePicker {
  readonly group=new THREE.Group();
  choices:CadFace[]=[];
  private meshes:THREE.Mesh<THREE.BufferGeometry,THREE.MeshBasicMaterial>[]=[];
  private hovered=-1;
  private revision=0;
  private changed:(()=>void)|undefined;
  constructor(scene:THREE.Scene,private camera:THREE.PerspectiveCamera|THREE.OrthographicCamera,private canvas:HTMLCanvasElement,private render:()=>void,private occlusion:(event:PointerEvent)=>number|undefined){scene.add(this.group);}
  setCamera(camera:THREE.PerspectiveCamera|THREE.OrthographicCamera):void{this.camera=camera;}
  async start(item:CadBody,matrix:THREE.Matrix4,refs:CadFaceRef[]=[],changed?:()=>void):Promise<void>{
    this.clear();const revision=++this.revision,result=await cadCompute([item],'faces');if(revision!==this.revision)return;
    if(!result.faces.length||result.faces.length>1024)throw new Error('This solid has too many faces to pick comfortably. Simplify its original sketch first.');
    this.choices=result.faces;this.group.matrixAutoUpdate=false;this.group.matrix.copy(matrix);this.group.updateMatrixWorld(true);this.changed=changed;
    for(const[index,face]of this.choices.entries()){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(face.positions,3));geometry.setIndex(face.indices);const material=new THREE.MeshBasicMaterial({color:0xe52e83,transparent:true,opacity:.025,side:THREE.DoubleSide,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2}),mesh=new THREE.Mesh(geometry,material);mesh.renderOrder=8;mesh.userData.face=index;this.group.add(mesh);this.meshes.push(mesh);}
    const key=(ref:CadFaceRef)=>JSON.stringify([ref.surface,...[...ref.center,...ref.min,...ref.max,...ref.normal].map(n=>Math.round(n*1e5))]);state.cad.faceSelection=this.choices.filter(f=>refs.some(ref=>key(ref)===key(f.ref))).map(f=>f.ref);this.update();
  }
  clear():void{++this.revision;for(const mesh of this.meshes){this.group.remove(mesh);mesh.geometry.dispose();mesh.material.dispose();}this.meshes=[];this.choices=[];this.hovered=-1;this.changed=undefined;state.cad.faceSelection=[];this.render();}
  selectNone():void{state.cad.faceSelection=[];this.update();}
  private update():void{for(const[index,mesh]of this.meshes.entries()){const selected=state.cad.faceSelection.includes(this.choices[index].ref);mesh.material.color.setHex(selected?0xe52e83:0x008b86);mesh.material.opacity=selected?.55:index===this.hovered?.35:.025;}this.render();this.changed?.();emit('cad-faces');}
  private hit(event:PointerEvent):number{const rect=this.canvas.getBoundingClientRect(),ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((event.clientX-rect.left)/rect.width*2-1,1-(event.clientY-rect.top)/rect.height*2),this.camera);const solid=this.occlusion(event);return ray.intersectObjects(this.meshes,false).find(hit=>solid===undefined||hit.distance<=solid+.03)?.object.userData.face??-1;}
  hover(event:PointerEvent):void{const index=this.hit(event);if(index!==this.hovered){this.hovered=index;this.update();}this.canvas.style.cursor=index<0?'grab':'pointer';}
  pick(event:PointerEvent):void{const index=this.hit(event);if(index<0)return;const ref=this.choices[index].ref,selected=state.cad.faceSelection;if(selected.includes(ref))state.cad.faceSelection=selected.filter(f=>f!==ref);else{if(selected.length>=128)return;state.cad.faceSelection=[...selected,ref];}this.update();}
}
