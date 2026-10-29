import { body, type CadBody, type V3 } from './cad-model';

interface Bounds { min:V3;max:V3 }
interface BoundsTree extends Bounds { items?:number[];left?:BoundsTree;right?:BoundsTree }
interface StlShell extends Bounds { faces:number[];volume:number;depth:number;tree?:BoundsTree }
function boundsTree(items:number[],bounds:(i:number)=>Bounds):BoundsTree{
  const min:V3=[Infinity,Infinity,Infinity],max:V3=[-Infinity,-Infinity,-Infinity];
  for(const i of items){const b=bounds(i);for(let k=0;k<3;k++){min[k]=Math.min(min[k],b.min[k]);max[k]=Math.max(max[k],b.max[k]);}}
  if(items.length<=12)return{min,max,items};
  const axis=[0,1,2].sort((a,b)=>(max[b]-min[b])-(max[a]-min[a]))[0];
  items.sort((a,b)=>{const x=bounds(a),y=bounds(b);return x.min[axis]+x.max[axis]-y.min[axis]-y.max[axis];});
  const middle=Math.floor(items.length/2);return{min,max,left:boundsTree(items.slice(0,middle),bounds),right:boundsTree(items.slice(middle),bounds)};
}
const encloses=(outer:Bounds,inner:Bounds)=>outer.min.every((n,i)=>n<=inner.min[i]+1e-7&&outer.max[i]>=inner.max[i]-1e-7);
function enclosingItems(tree:BoundsTree,box:Bounds,out:number[]):void{
  if(!encloses(tree,box))return;if(tree.items)out.push(...tree.items);else{enclosingItems(tree.left!,box,out);enclosingItems(tree.right!,box,out);}
}
/** Shell signs come from geometric nesting, independent of any facet's input winding. */
function orientShells(shells:StlShell[],positions:number[],indices:number[]):void{
  const point=(index:number):V3=>positions.slice(index*3,index*3+3) as V3;
  const triangle=(face:number)=>indices.slice(face*3,face*3+3).map(point);
  const triangleBounds=new Map<number,Bounds>();
  const faceBounds=(face:number):Bounds=>{let b=triangleBounds.get(face);if(!b){const p=triangle(face);b={min:[0,1,2].map(i=>Math.min(...p.map(v=>v[i]))) as V3,max:[0,1,2].map(i=>Math.max(...p.map(v=>v[i]))) as V3};triangleBounds.set(face,b);}return b;};
  const direction:V3=[1,.3713906763541037,.5291058848352268];
  const contains=(shell:StlShell,p:V3):boolean=>{
    shell.tree??=boundsTree([...shell.faces],faceBounds);const hits:number[]=[];
    const visit=(node:BoundsTree):void=>{
      let low=0,high=Infinity;for(let i=0;i<3;i++){low=Math.max(low,(node.min[i]-p[i])/direction[i]);high=Math.min(high,(node.max[i]-p[i])/direction[i]);}if(high<low)return;
      if(!node.items){visit(node.left!);visit(node.right!);return;}
      for(const face of node.items){
        const [a,b,c]=triangle(face),e=b.map((v,i)=>v-a[i]),f=c.map((v,i)=>v-a[i]),h=[direction[1]*f[2]-direction[2]*f[1],direction[2]*f[0]-direction[0]*f[2],direction[0]*f[1]-direction[1]*f[0]],det=e.reduce((sum,v,i)=>sum+v*h[i],0);
        if(Math.abs(det)<1e-14)continue;const s=p.map((v,i)=>v-a[i]),u=s.reduce((sum,v,i)=>sum+v*h[i],0)/det;if(u< -1e-9||u>1+1e-9)continue;
        const q=[s[1]*e[2]-s[2]*e[1],s[2]*e[0]-s[0]*e[2],s[0]*e[1]-s[1]*e[0]],v=direction.reduce((sum,n,i)=>sum+n*q[i],0)/det;if(v< -1e-9||u+v>1+1e-9)continue;
        const t=f.reduce((sum,n,i)=>sum+n*q[i],0)/det;if(t>1e-8)hits.push(t);
      }
    };
    visit(shell.tree);hits.sort((a,b)=>a-b);return hits.filter((t,i)=>i===0||t-hits[i-1]>1e-7).length%2===1;
  };
  const tree=boundsTree(shells.map((_,i)=>i),i=>shells[i]);
  for(const shell of [...shells].sort((a,b)=>Math.abs(b.volume)-Math.abs(a.volume))){
    const candidates:number[]=[];enclosingItems(tree,shell,candidates);
    const p=triangle(shell.faces[0]).reduce((sum,v)=>sum.map((n,i)=>n+v[i]/3) as V3,[0,0,0] as V3);
    const parent=candidates.map(i=>shells[i]).filter(other=>Math.abs(other.volume)>Math.abs(shell.volume)+1e-6&&encloses(other,shell)).sort((a,b)=>Math.abs(a.volume)-Math.abs(b.volume)).find(other=>contains(other,p));
    shell.depth=parent?parent.depth+1:0;
    if((shell.volume>0)!==(shell.depth%2===0))for(const face of shell.faces)[indices[face*3+1],indices[face*3+2]]=[indices[face*3+2],indices[face*3+1]];
  }
}

/** Read STL locally; repair connected face winding while preserving enclosed cavities. */
export function importStl(buffer:ArrayBuffer,name:string,unit:'mm'|'cm'|'in'='mm',discardCollapsed=false):CadBody{
  if(buffer.byteLength>20_000_000)throw new Error('Choose an STL smaller than 20 MB.');
  const view=new DataView(buffer),count=buffer.byteLength>=84?view.getUint32(80,true):0,vertices:number[]=[];
  if(count>0&&84+count*50===buffer.byteLength){if(count>200000)throw new Error('Use an STL with at most 200,000 triangles.');for(let i=0;i<count;i++)for(let k=0;k<9;k++)vertices.push(view.getFloat32(84+i*50+12+k*4,true));}
  else{const text=new TextDecoder().decode(buffer);if(!/^\s*solid\b/i.test(text))throw new Error('This is not a binary or ASCII STL file.');const number='([+-]?(?:\\d+\\.?\\d*|\\.\\d+)(?:e[+-]?\\d+)?)',pattern=new RegExp('\\bvertex\\s+'+number+'\\s+'+number+'\\s+'+number+'(?=\\s|$)','gi');for(const match of text.matchAll(pattern)){vertices.push(Number(match[1]),Number(match[2]),Number(match[3]));if(vertices.length>1_800_000)throw new Error('Use an STL with at most 200,000 triangles.');}if(vertices.length%9||vertices.length/9!==[...text.matchAll(/\bendfacet\b/gi)].length)throw new Error('This ASCII STL contains incomplete triangles.');}
  if(vertices.length<36)throw new Error('The STL needs a closed solid with at least four triangles.');
  const factor=unit==='in'?25.4:unit==='cm'?10:1,positions:number[]=[],indices:number[]=[],unique=new Map<string,number>();
  for(let i=0;i<vertices.length;i+=3){const point=vertices.slice(i,i+3).map(v=>v*factor);if(point.some(v=>!Number.isFinite(v)||Math.abs(v)>10000))throw new Error('STL coordinates must fit within ±10,000 mm. Check the import units.');const key=point.map(v=>Math.round(v*1e6)).join(',');let index=unique.get(key);if(index===undefined){index=positions.length/3;unique.set(key,index);positions.push(...point);}indices.push(index);}
  // OpenSCAD may emit zero-width triangles on a revolution axis. Removing these
  // changes no surface; the ordinary closed-edge checks below still apply.
  if(discardCollapsed){let write=0;for(let i=0;i<indices.length;i+=3){const a=indices[i],b=indices[i+1],c=indices[i+2];if(a!==b&&b!==c&&a!==c){indices[write++]=a;indices[write++]=b;indices[write++]=c;}}indices.length=write;if(write<12)throw new Error('OpenSCAD produced no closed solid.');}
  const edges=new Map<string,{face:number;direction:number;paired:boolean}>(),adjacency:Array<Array<[number,number]>>=Array.from({length:indices.length/3},()=>[]);
  for(let face=0;face<adjacency.length;face++){
    const t=indices.slice(face*3,face*3+3);if(new Set(t).size<3)throw new Error('The STL contains collapsed triangles. Repair it before importing.');
    for(let i=0;i<3;i++){const a=t[i],b=t[(i+1)%3],direction=a<b?1:-1,key=Math.min(a,b)+','+Math.max(a,b),other=edges.get(key);if(other){if(other.paired)throw new Error('This STL has non-manifold edges. Repair it to a closed solid first.');const relation=-direction*other.direction;adjacency[face].push([other.face,relation]);adjacency[other.face].push([face,relation]);other.paired=true;}else edges.set(key,{face,direction,paired:false});}
  }
  if([...edges.values()].some(e=>!e.paired))throw new Error('This STL has open edges. Repair the holes before importing it as a solid.');
  const orientation=new Int8Array(adjacency.length),shells:StlShell[]=[];
  for(let first=0;first<adjacency.length;first++)if(!orientation[first]){const queue=[first];orientation[first]=1;for(let head=0;head<queue.length;head++)for(const [neighbor,relation]of adjacency[queue[head]]){const expected=orientation[queue[head]]*relation;if(orientation[neighbor]&&orientation[neighbor]!==expected)throw new Error('The STL surface cannot be oriented as a solid.');if(!orientation[neighbor]){orientation[neighbor]=expected;queue.push(neighbor);}}
    let volume=0;const min:V3=[Infinity,Infinity,Infinity],max:V3=[-Infinity,-Infinity,-Infinity];for(const face of queue){const [ia,ib,ic]=indices.slice(face*3,face*3+3),a=positions.slice(ia*3,ia*3+3),b=positions.slice(ib*3,ib*3+3),c=positions.slice(ic*3,ic*3+3);volume+=orientation[face]*(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;for(const p of [a,b,c])for(let i=0;i<3;i++){min[i]=Math.min(min[i],p[i]);max[i]=Math.max(max[i],p[i]);}}if(Math.abs(volume)<1e-6)throw new Error('The STL contains a component with no solid volume.');for(const face of queue)if(orientation[face]<0)[indices[face*3+1],indices[face*3+2]]=[indices[face*3+2],indices[face*3+1]];shells.push({faces:queue,volume,min,max,depth:0});
  }
  orientShells(shells,positions,indices);
  return body({kind:'mesh',positions,indices,sourceName:name},name.replace(/\.stl$/i,'')||'Imported STL');
}
