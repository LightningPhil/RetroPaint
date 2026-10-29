import * as THREE from 'three';
import { cadCompute } from './cad-engine';
import { state } from './state';
import { emit } from './bus';
import type { CadBody, CadEdge, CadEdgeRef } from './cad-model';

/** Pick whole CAD edges, including circular rims, rather than triangle boundaries. */
export class CadEdgePicker {
  readonly group=new THREE.Group();
  choices:CadEdge[]=[];
  private lines:THREE.Line<THREE.BufferGeometry,THREE.LineBasicMaterial>[]=[];
  private hovered=-1;
  private revision=0;
  private changed:(()=>void)|undefined;
  constructor(scene:THREE.Scene,private camera:THREE.PerspectiveCamera,private canvas:HTMLCanvasElement,private render:()=>void,private occlusion:(event:PointerEvent)=>number|undefined){scene.add(this.group);}
  async start(item:CadBody,matrix:THREE.Matrix4,refs:CadEdgeRef[]=[],changed?:()=>void):Promise<void>{
    this.clear();const revision=++this.revision,result=await cadCompute([item],'edges');if(revision!==this.revision)return;
    this.choices=result.edges??[];if(!this.choices.length)throw new Error('This solid has no sharp edges to round or bevel. Try a cube, a cylinder rim, or a hole edge.');
    if(this.choices.length>1024)throw new Error('This solid has too many edges to pick comfortably. Simplify its original sketch first.');
    this.group.matrixAutoUpdate=false;this.group.matrix.copy(matrix);this.group.updateMatrixWorld(true);this.changed=changed;
    for(const[index,edge]of this.choices.entries()){const geometry=new THREE.BufferGeometry().setFromPoints(edge.points.map(p=>new THREE.Vector3(...p))),material=new THREE.LineBasicMaterial({color:0x786b91,transparent:true,opacity:.5,depthTest:false}),line=new THREE.Line(geometry,material);line.renderOrder=8;line.userData.edge=index;this.group.add(line);this.lines.push(line);}
    const key=(ref:CadEdgeRef)=>JSON.stringify([ref.curve,ref.closed,ref.rank??0,ref.groupSize??1,...[...ref.center,...ref.direction,...(ref.closed?[]:[...ref.start,...ref.end])].map(n=>Math.round(n*1e5))]);state.cad.edgeSelection=this.choices.filter(e=>refs.some(ref=>key(ref)===key(e.ref))).map(e=>e.ref);this.update();
  }
  clear():void{++this.revision;for(const line of this.lines){this.group.remove(line);line.geometry.dispose();line.material.dispose();}this.lines=[];this.choices=[];this.hovered=-1;this.changed=undefined;state.cad.edgeSelection=[];this.render();}
  selectAll():void{if(this.choices.length>256)throw new Error('Choose up to 256 edges in a single finish.');state.cad.edgeSelection=this.choices.map(e=>e.ref);this.update();}
  selectNone():void{state.cad.edgeSelection=[];this.update();}
  private update():void{for(const[index,line]of this.lines.entries()){const selected=state.cad.edgeSelection.includes(this.choices[index].ref);line.material.color.setHex(selected?0xe52e83:index===this.hovered?0x008b86:0x786b91);line.material.opacity=selected||index===this.hovered?1:.45;line.material.linewidth=selected?3:2;}this.render();this.changed?.();emit('cad-edges');}
  private hit(event:PointerEvent):number{
    const rect=this.canvas.getBoundingClientRect(),ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2((event.clientX-rect.left)/rect.width*2-1,1-(event.clientY-rect.top)/rect.height*2),this.camera);
    const distance=this.camera.position.distanceTo(this.group.getWorldPosition(new THREE.Vector3())),tolerance=distance*Math.tan(this.camera.fov*Math.PI/360)*18/rect.height;ray.params.Line!.threshold=tolerance;
    const solid=this.occlusion(event);return ray.intersectObjects(this.lines,false).filter(hit=>solid===undefined||hit.distance<=solid+tolerance*.7).sort((a,b)=>(a.distanceToRay??0)-(b.distanceToRay??0))[0]?.object.userData.edge??-1;
  }
  hover(event:PointerEvent):void{const index=this.hit(event);if(index!==this.hovered){this.hovered=index;this.update();}this.canvas.style.cursor=index<0?'grab':'pointer';}
  pick(event:PointerEvent):void{const index=this.hit(event);if(index<0)return;const ref=this.choices[index].ref,selected=state.cad.edgeSelection;if(selected.includes(ref))state.cad.edgeSelection=selected.filter(e=>e!==ref);else{if(selected.length>=256)return;state.cad.edgeSelection=[...selected,ref];}this.update();}
}
