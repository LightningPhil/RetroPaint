import { basePlane, sketchPoints, type CadForm, type CadProfile, type V2, type V3, type Workplane } from './cad-model';
import { solveSketch } from './cad-sketch-constraints';

export function newProfile(name='Profile',z=0,size=20):CadProfile {
  const plane=basePlane('xy');plane.origin[2]=z;
  return{name,shape:'circle',points:sketchPoints('circle',0,0,size,size),plane,rotation:0};
}
export function defaultForm(kind:'loft'|'sweep'):CadForm {
  return kind==='loft'?{kind,profiles:[newProfile('Base sketch'),newProfile('Top sketch',30,12)],ruled:false}:{kind,profile:newProfile('Sweep profile',0,6),path:{name:'Sweep path',points:[[0,0,0],[0,0,15],[15,0,25],[30,0,25]],smooth:true},transition:'right',roll:0};
}
export const subtract3=(a:V3,b:V3)=>a.map((v,i)=>v-b[i]) as V3;
const unit=(a:V3):V3=>{const length=Math.hypot(...a);return a.map(v=>v/length) as V3;};
/** The sweep section starts perpendicular to the first path tangent. Roll is in degrees. */
export function sweepPlane(points:V3[],roll:number):Workplane {
  const normal=unit(subtract3(points[1],points[0])),reference:V3=Math.abs(normal[0])>.95?[0,1,0]:[1,0,0],dot=reference.reduce((v,n,i)=>v+n*normal[i],0),u=unit(reference.map((v,i)=>v-dot*normal[i]) as V3),v:V3=[normal[1]*u[2]-normal[2]*u[1],normal[2]*u[0]-normal[0]*u[2],normal[0]*u[1]-normal[1]*u[0]],angle=roll*Math.PI/180;
  return{origin:[...points[0]],normal,u:u.map((n,i)=>n*Math.cos(angle)+v[i]*Math.sin(angle)) as V3,v:v.map((n,i)=>n*Math.cos(angle)-u[i]*Math.sin(angle)) as V3};
}
/** Interpolating Catmull–Rom segments: all path points lie on the actual sweep spine. */
export function pathBeziers(points:V3[]):V3[][] {
  return points.slice(0,-1).map((a,i)=>{const before=points[Math.max(0,i-1)],b=points[i+1],after=points[Math.min(points.length-1,i+2)];return[a,a.map((v,k)=>v+(b[k]-before[k])/6) as V3,b.map((v,k)=>v-(after[k]-a[k])/6) as V3,b];});
}
export function profilePlane(profile:CadProfile):Workplane {const p=profile.plane,a=profile.rotation*Math.PI/180;return{...p,u:p.u.map((v,i)=>v*Math.cos(a)+p.v[i]*Math.sin(a)) as V3,v:p.v.map((v,i)=>v*Math.cos(a)-p.u[i]*Math.sin(a)) as V3};}
export function profileWorld(profile:CadProfile):V3[] {const plane=profilePlane(profile);return solveSketch(profile.points,profile.constraints,profile.shape).map(([x,y])=>plane.origin.map((v,i)=>v+plane.u[i]*x+plane.v[i]*y) as V3);}
export function checkProfile(points:V2[]):void {
  if(points.length<3||points.length>256||points.some(p=>p.length!==2||p.some(n=>!Number.isFinite(n)||Math.abs(n)>10000)))throw new Error('A profile needs 3–256 finite x,y points in mm.');
  const cross=(a:V2,b:V2,c:V2)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  let area=0;
  for(let i=0;i<points.length;i++){const a=points[i],b=points[(i+1)%points.length];if(Math.hypot(a[0]-b[0],a[1]-b[1])<.0001)throw new Error('A profile contains repeated adjacent points.');area+=a[0]*b[1]-b[0]*a[1];
    for(let j=i+2;j<points.length;j++){if(i===0&&j===points.length-1)continue;const c=points[j],d=points[(j+1)%points.length];if(cross(a,b,c)*cross(a,b,d)<-1e-10&&cross(c,d,a)*cross(c,d,b)<-1e-10)throw new Error('A profile crosses itself. Move its points to make one simple closed outline.');}
  }
  if(Math.abs(area)<.0001)throw new Error('A profile needs a closed outline with some area.');
}
