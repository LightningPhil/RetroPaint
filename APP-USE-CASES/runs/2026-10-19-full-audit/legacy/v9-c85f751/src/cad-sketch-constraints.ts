import { readSketchConstraints, sketchPoints, type CadSketchConstraint, type V2 } from './cad-model';

const wrap=(a:number)=>Math.atan2(Math.sin(a),Math.cos(a));
const moduloPi=(a:number)=>Math.atan2(Math.sin(2*a),Math.cos(2*a))/2;
interface Row { error:number; gradient:Float64Array }
/** A small, workplane-local least-displacement solver. No saved recipe is mutated. */
export function solveSketch(seed:V2[],constraints:CadSketchConstraint[]|undefined,shape='polygon'):V2[]{
  if(!constraints?.length)return structuredClone(seed);
  readSketchConstraints(constraints,seed.length,shape);
  if(shape==='circle'){
    const diameter=constraints[0];if(diameter.kind!=='diameter')throw new Error('Use a diameter for a circle.');
    if(constraints.some(c=>c.kind!=='diameter'||Math.abs(c.value-diameter.value)>1e-7))throw new Error('These diameter dimensions conflict. Remove or edit one of them.');
    const xs=seed.map(p=>p[0]),ys=seed.map(p=>p[1]);return sketchPoints('circle',(Math.min(...xs)+Math.max(...xs))/2,(Math.min(...ys)+Math.max(...ys))/2,diameter.value,diameter.value);
  }
  const rules=[...constraints];
  // Rectangle outlines retain their square corners even when a dimension rotates them.
  if(shape==='rectangle'&&seed.length===4)rules.push({id:'rect-a',kind:'parallel',edge:0,other:2},{id:'rect-b',kind:'parallel',edge:1,other:3},{id:'rect-c',kind:'perpendicular',edge:0,other:1});
  const size=seed.length*2,start=seed.flat(),scale=Math.max(1,Math.min(100,Math.max(...seed.map(p=>p[0]))-Math.min(...seed.map(p=>p[0])),Math.max(...seed.map(p=>p[1]))-Math.min(...seed.map(p=>p[1]))));
  const direction=(x:number[],e:number)=>{const a=e*2,b=((e+1)%seed.length)*2,dx=x[b]-x[a],dy=x[b+1]-x[a+1];return{a,b,dx,dy,length:Math.hypot(dx,dy),angle:Math.atan2(dy,dx)};};
  const branches=rules.map(c=>{if(c.kind!=='angle-between')return 1;const angle=wrap(direction(start,c.edge).angle-direction(start,c.other).angle),target=c.value*Math.PI/180;return Math.abs(wrap(angle-target))<=Math.abs(wrap(angle+target))?1:-1;});
  const rows=(x:number[]):Row[]=>rules.map((c,i)=>{
    if(c.kind==='diameter')throw new Error('A diameter needs a circle.');
    const a=direction(x,c.edge),gradient=new Float64Array(size);let error=0;
    const linear=(edge:typeof a,gx:number,gy:number)=>{gradient[edge.a]-=gx;gradient[edge.a+1]-=gy;gradient[edge.b]+=gx;gradient[edge.b+1]+=gy;};
    const angular=(edge:typeof a,factor:number)=>{const squared=Math.max(edge.length**2,1e-16);linear(edge,-edge.dy/squared*factor,edge.dx/squared*factor);};
    if(c.kind==='horizontal'){error=a.dy;linear(a,0,1);}else if(c.kind==='vertical'){error=a.dx;linear(a,1,0);}
    else if(c.kind==='length'){error=a.length-c.value;linear(a,a.dx/Math.max(a.length,1e-8),a.dy/Math.max(a.length,1e-8));}
    else if(c.kind==='angle'){error=wrap(a.angle-c.value*Math.PI/180)*scale;angular(a,scale);}
    else if('other' in c){const b=direction(x,c.other);error=(c.kind==='angle-between'?wrap(a.angle-b.angle-branches[i]*c.value*Math.PI/180):moduloPi(a.angle-b.angle-(c.kind==='perpendicular'?Math.PI/2:0)))*scale;angular(a,scale);angular(b,-scale);}
    return{error,gradient};
  });
  let x=[...start],damping=1e-7;
  for(let iteration=0;iteration<100;iteration++){
    const r=rows(x),cost=r.reduce((v,a)=>v+a.error*a.error,0);if(r.every(a=>Math.abs(a.error)<1e-7))break;
    const matrix=r.map((a,i)=>Float64Array.from([...r.map((b,j)=>a.gradient.reduce((v,g,k)=>v+g*b.gradient[k],0)+(i===j?damping:0)),a.error]));
    // Pivoted elimination solves (J Jᵀ + λ I) y = residual, including redundant relations.
    for(let k=0;k<r.length;k++){let pivot=k;for(let i=k+1;i<r.length;i++)if(Math.abs(matrix[i][k])>Math.abs(matrix[pivot][k]))pivot=i;[matrix[k],matrix[pivot]]=[matrix[pivot],matrix[k]];const divisor=matrix[k][k];if(Math.abs(divisor)<1e-20)continue;for(let j=k;j<=r.length;j++)matrix[k][j]/=divisor;for(let i=0;i<r.length;i++)if(i!==k){const f=matrix[i][k];for(let j=k;j<=r.length;j++)matrix[i][j]-=f*matrix[k][j];}}
    const delta=Array.from({length:size},(_,k)=>r.reduce((v,a,i)=>v-a.gradient[k]*matrix[i][r.length],0));let accepted=false;
    for(let step=1;step>=1/128;step/=2){const next=x.map((v,k)=>v+delta[k]*step),nextCost=rows(next).reduce((v,a)=>v+a.error*a.error,0);if(Number.isFinite(nextCost)&&nextCost<cost){x=next;damping=Math.max(1e-10,damping*.3);accepted=true;break;}}
    if(!accepted){damping*=10;if(damping>1e6)break;}
  }
  if(rows(x).some(r=>!Number.isFinite(r.error)||Math.abs(r.error)>1e-5))throw new Error('These dimensions or constraints conflict. Edit or remove a conflicting constraint; your last valid sketch is kept.');
  const result=seed.map((_,i)=>[x[i*2],x[i*2+1]] as V2);
  if(result.some((p,i)=>p.some(v=>!Number.isFinite(v)||Math.abs(v)>10000)||Math.hypot(p[0]-result[(i+1)%result.length][0],p[1]-result[(i+1)%result.length][1])<.0001))throw new Error('These constraints collapse a line or move it beyond the workspace. Try different dimensions.');
  let area=0;const cross=(a:V2,b:V2,c:V2)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  for(let i=0;i<result.length;i++){const a=result[i],b=result[(i+1)%result.length];area+=a[0]*b[1]-b[0]*a[1];for(let j=i+2;j<result.length;j++){if(i===0&&j===result.length-1)continue;const c=result[j],d=result[(j+1)%result.length];if(cross(a,b,c)*cross(a,b,d)<-1e-10&&cross(c,d,a)*cross(c,d,b)<-1e-10)throw new Error('Those dimensions make the outline cross itself. Try a smaller change.');}}
  if(Math.abs(area)<.0001)throw new Error('Those constraints flatten the sketch. Keep a closed outline with some area.');
  return result;
}
export function constraintLabel(c:CadSketchConstraint):string{
  const line='edge' in c?'Line '+(c.edge+1):'',pair='other' in c?line+' & '+(c.other+1):line;
  return c.kind==='diameter'?`Ø ${c.value} mm`:c.kind==='length'?`${line} · ${c.value} mm`:c.kind==='angle'?`${line} · ${c.value}° to X`:c.kind==='angle-between'?`${pair} · ${c.value}°`:`${pair} · ${c.kind}`;
}
