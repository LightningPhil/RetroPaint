import * as THREE from 'three';
import { planeMatrix, type V2, type Workplane } from './cad-model';
import { cameraSpan, type CadCamera } from './cad-camera';

/** A disposable construction preview. Only Apply changes the document. */
export class CadPullPreview {
  readonly group=new THREE.Group();
  readonly handle=document.createElement('button');
  private tip=new THREE.Vector3();
  private depth=0;
  private change:((depth:number)=>void)|undefined;
  private drag:{y:number;depth:number;scale:number}|undefined;
  constructor(private host:HTMLElement,private camera:()=>CadCamera){
    this.handle.id='cadPullHandle';this.handle.type='button';this.handle.hidden=true;
    this.handle.title='Drag up to pull out, down to push in. Arrow keys adjust by 1 mm.';
    this.host.append(this.handle);
    this.handle.addEventListener('pointerdown',e=>{if(e.button!==0)return;e.preventDefault();e.stopPropagation();this.drag={y:e.clientY,depth:this.depth,scale:cameraSpan(this.camera(),this.tip)/Math.max(1,host.clientHeight)};this.handle.setPointerCapture(e.pointerId);});
    this.handle.addEventListener('pointermove',e=>{if(!this.drag)return;const d=this.drag;this.change?.(Math.max(-2000,Math.min(2000,Math.round((d.depth+(d.y-e.clientY)*d.scale)*10)/10)));});
    this.handle.addEventListener('pointerup',()=>{this.drag=undefined;});
    this.handle.addEventListener('pointercancel',()=>{const d=this.drag;this.drag=undefined;if(d)this.change?.(d.depth);});
    this.handle.addEventListener('keydown',e=>{if(!['ArrowUp','ArrowDown'].includes(e.key))return;e.preventDefault();e.stopPropagation();this.change?.(this.depth+(e.key==='ArrowUp'?1:-1)*(e.shiftKey?10:1));});
  }
  show(points:V2[],plane:Workplane,depth:number,taper:number,twist:number,change:(depth:number)=>void):void{
    this.disposeGeometry();this.depth=depth;this.change=change;
    const shape=new THREE.Shape(points.map(p=>new THREE.Vector2(...p)));
    const geometry=new THREE.ExtrudeGeometry(shape,{depth:1,steps:Math.max(1,Math.ceil(Math.abs(twist)/10)),bevelEnabled:false});
    const pos=geometry.getAttribute('position');
    for(let i=0;i<pos.count;i++){const z=pos.getZ(i),angle=twist*Math.PI/180*z,scale=1+(taper-1)*z,x=pos.getX(i)*scale,y=pos.getY(i)*scale;pos.setXYZ(i,x*Math.cos(angle)-y*Math.sin(angle),x*Math.sin(angle)+y*Math.cos(angle),z*depth);}
    geometry.applyMatrix4(new THREE.Matrix4().fromArray(planeMatrix(plane)));
    const color=depth<0?0xe25263:0x249d93;
    const mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({color,transparent:true,opacity:.35,side:THREE.DoubleSide,depthTest:false,depthWrite:false}));mesh.renderOrder=8;this.group.add(mesh);
    const edges=new THREE.LineSegments(new THREE.EdgesGeometry(geometry),new THREE.LineBasicMaterial({color,depthTest:false}));edges.renderOrder=9;this.group.add(edges);
    const centre=points.reduce((a,p)=>[a[0]+p[0]/points.length,a[1]+p[1]/points.length] as V2,[0,0] as V2);
    this.tip.set(...plane.origin).addScaledVector(new THREE.Vector3(...plane.u),centre[0]).addScaledVector(new THREE.Vector3(...plane.v),centre[1]).addScaledVector(new THREE.Vector3(...plane.normal),depth);
    this.handle.hidden=false;this.handle.textContent=`↕ ${depth<0?'Push':'Pull'} ${Math.abs(depth).toFixed(1)} mm`;
    this.handle.setAttribute('aria-label',`Push or pull sketch, depth ${depth.toFixed(1)} millimetres`);this.layout();
  }
  layout():void{
    if(this.handle.hidden||this.drag)return;
    this.camera().updateMatrixWorld();const p=this.tip.clone().project(this.camera()),host=this.host.getBoundingClientRect(),canvas=this.host.querySelector('canvas')!.getBoundingClientRect(),actions=this.host.querySelector<HTMLElement>('#cadSketchActions');
    const bottom=actions&&!actions.hidden?actions.offsetTop-36:canvas.bottom-host.top-36;
    this.handle.style.left=`${Math.max(75,Math.min(this.host.clientWidth-75,canvas.left-host.left+(p.x+1)*canvas.width/2))}px`;
    this.handle.style.top=`${Math.max(80,Math.min(bottom,canvas.top-host.top+(1-p.y)*canvas.height/2))}px`;
  }
  private disposeGeometry():void{for(const child of [...this.group.children]){const mesh=child as THREE.Mesh;mesh.geometry.dispose();for(const m of Array.isArray(mesh.material)?mesh.material:[mesh.material])m.dispose();this.group.remove(child);}}
  clear():void{this.drag=undefined;this.change=undefined;this.handle.hidden=true;this.disposeGeometry();}
  dispose():void{this.clear();this.handle.remove();}
}
