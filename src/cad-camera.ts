import * as THREE from 'three';
import type { CadView } from './cad-model';
export type CadCamera=THREE.PerspectiveCamera|THREE.OrthographicCamera;
export function sameCadView(a:CadView|undefined,b:CadView):boolean{return !!a&&a.projection===b.projection&&Math.abs(a.span-b.span)<1e-6&&['position','target','up'].every(key=>(a[key as 'position']).every((v,i)=>Math.abs(v-b[key as 'position'][i])<1e-6));}
export function cameraSpan(camera:CadCamera,target:THREE.Vector3):number{return camera instanceof THREE.PerspectiveCamera?2*camera.position.distanceTo(target)*Math.tan(camera.fov*Math.PI/360)/camera.zoom:(camera.top-camera.bottom)/camera.zoom;}
export function cameraAspect(camera:CadCamera,aspect:number):void{if(camera instanceof THREE.PerspectiveCamera)camera.aspect=aspect;else{const half=(camera.top-camera.bottom)/2;camera.left=-half*aspect;camera.right=half*aspect;}camera.updateProjectionMatrix();}
export function captureCadView(camera:CadCamera,target:THREE.Vector3):CadView{return{position:camera.position.toArray(),target:target.toArray(),up:camera.up.toArray(),projection:camera instanceof THREE.OrthographicCamera?'orthographic':'perspective',span:cameraSpan(camera,target)};}
export function cameraForView(view:CadView,aspect:number):CadCamera{const c=view.projection==='orthographic'?new THREE.OrthographicCamera(-view.span*aspect/2,view.span*aspect/2,view.span/2,-view.span/2,.1,30000):new THREE.PerspectiveCamera(38,aspect,.1,30000);c.position.set(...view.position);c.up.set(...view.up);c.lookAt(new THREE.Vector3(...view.target));c.updateMatrixWorld(true);return c;}
