import { Euler, Quaternion, Vector3 } from 'three';
import type { CadBody, V3, Workplane } from './cad-model';

export function mateBody(body: CadBody, moving: Workplane, target: Workplane): CadBody {
  const rotation=new Quaternion().setFromUnitVectors(new Vector3(...moving.normal),new Vector3(...target.normal).negate());
  const orientation=new Quaternion().setFromEuler(new Euler(...body.rotation.map(v=>v*Math.PI/180) as V3,'ZYX')).premultiply(rotation);
  const position=new Vector3(...body.position).sub(new Vector3(...moving.origin)).applyQuaternion(rotation).add(new Vector3(...target.origin));
  const euler=new Euler().setFromQuaternion(orientation,'ZYX');
  return {...body,position:[position.x,position.y,position.z],rotation:[euler.x*180/Math.PI,euler.y*180/Math.PI,euler.z*180/Math.PI]};
}
