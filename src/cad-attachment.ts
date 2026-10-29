import { Euler, Matrix3, Matrix4, Quaternion, Vector3 } from 'three';
import type { CadAttachment, CadBody, CadMesh, V2, V3, Workplane } from './cad-model';

const vector = (v: V3) => new Vector3(...v);
const tuple = (v: Vector3): V3 => [v.x,v.y,v.z];
/** Probe the profile footprint: a face's bounding-box centre may lie in an earlier hole. */
export function resolveSupportPlane(plane:Workplane,points:V2[],distance:number,rayCast:(start:V3,end:V3)=>{normal:readonly number[];position:readonly number[]}[]):Workplane{
  const centre=points.reduce((sum,p)=>[sum[0]+p[0]/points.length,sum[1]+p[1]/points.length] as V2,[0,0] as V2);
  const probes=[centre,...points.map((p,i)=>[(p[0]+points[(i+1)%points.length][0])/2,(p[1]+points[(i+1)%points.length][1])/2] as V2),...points];
  let nearest:number|undefined;
  for(const p of probes){
    const origin=plane.origin.map((v,i)=>v+p[0]*plane.u[i]+p[1]*plane.v[i]) as V3;
    for(const hit of rayCast(origin.map((v,i)=>v+plane.normal[i]*distance) as V3,origin.map((v,i)=>v-plane.normal[i]*distance) as V3)){
      if(hit.normal.reduce((sum,n,i)=>sum+n*plane.normal[i],0)<=.999)continue;
      const offset=hit.position.reduce((sum,v,i)=>sum+(v-origin[i])*plane.normal[i],0);
      if(nearest===undefined||Math.abs(offset)<Math.abs(nearest))nearest=offset;
    }
    if(nearest!==undefined&&Math.abs(nearest)<1e-6)break;
  }
  if(nearest===undefined)throw new Error('The sketch’s supporting flat face no longer exists. Restore it, or edit the sketch onto a fixed plane.');
  // Move only along the normal; probing away from the origin must not move the sketch sideways.
  return {...plane,origin:plane.origin.map((v,i)=>v+plane.normal[i]*nearest!) as V3};
}
function matrix(item: CadBody): Matrix4 {
  return new Matrix4().compose(vector(item.position), new Quaternion().setFromEuler(new Euler(...item.rotation.map(n=>n*Math.PI/180) as V3,'ZYX')), vector(item.scale));
}
/** Store the face in the support's coordinates, independent of its later placement. */
export function captureAttachment(item: CadBody, bounds: CadMesh['bounds'], plane: Workplane): CadAttachment {
  const transform = matrix(item), inverse = transform.clone().invert(), local = vector(plane.origin).applyMatrix4(inverse);
  const normal = vector(plane.normal).applyMatrix3(new Matrix3().setFromMatrix4(transform).transpose()).normalize();
  const u = vector(plane.u).transformDirection(inverse); u.addScaledVector(normal,-u.dot(normal)).normalize();
  return { reference:item.id, anchor:tuple(local).map((v,i)=>(v-bounds.min[i])/(bounds.max[i]-bounds.min[i]||1)) as V3, normal:tuple(normal), u:tuple(u) };
}
/** Dimensions follow the support; sketch axes retain millimetres, including on scaled solids. */
export function attachedPlane(item: CadBody, bounds: CadMesh['bounds'], attachment: CadAttachment): Workplane {
  const transform = matrix(item), origin = vector(attachment.anchor.map((v,i)=>bounds.min[i]+v*(bounds.max[i]-bounds.min[i])) as V3).applyMatrix4(transform);
  const normal = vector(attachment.normal).applyMatrix3(new Matrix3().getNormalMatrix(transform)).normalize();
  const u = vector(attachment.u).transformDirection(transform); u.addScaledVector(normal,-u.dot(normal)).normalize();
  return { origin:tuple(origin), normal:tuple(normal), u:tuple(u), v:tuple(new Vector3().crossVectors(normal,u).normalize()) };
}
