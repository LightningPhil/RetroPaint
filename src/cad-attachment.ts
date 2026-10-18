import { Euler, Matrix3, Matrix4, Quaternion, Vector3 } from 'three';
import type { CadAttachment, CadBody, CadMesh, V3, Workplane } from './cad-model';

const vector = (v: V3) => new Vector3(...v);
const tuple = (v: Vector3): V3 => [v.x,v.y,v.z];
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
