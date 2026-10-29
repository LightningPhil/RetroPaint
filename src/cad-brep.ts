/** Native CAD finishing and inward-offset shells, loaded on demand. */
import init, { type OpenCascadeInstance } from 'replicad-opencascadejs';
import wasmUrl from 'replicad-opencascadejs/wasm?url';
import * as r from 'replicad';
import type { Manifold, ManifoldToplevel } from 'manifold-3d';
import { attachedPlane, resolveSupportPlane } from './cad-attachment';
import { checkProfile, pathBeziers, profilePlane, sweepPlane } from './cad-profiles';
import { solveSketch } from './cad-sketch-constraints';
import { type CadBody, type CadEdge, type CadFace, type CadMesh, type CadSolid, type V2, type V3, type Workplane } from './cad-model';

let ready:Promise<OpenCascadeInstance>|undefined;
let oc:OpenCascadeInstance;
export async function initBrep():Promise<void>{oc=await(ready??=init({locateFile:()=>wasmUrl,print:()=>{},printErr:()=>{}}).catch(()=>{ready=undefined;throw new Error('The precision CAD engine could not load. Try opening the precision tools again.');}));r.setOC(oc);}
const dot=(a:V3,b:V3)=>a.reduce((v,n,i)=>v+n*b[i],0);
const sub=(a:V3,b:V3)=>a.map((v,i)=>v-b[i]) as V3;
const length=(a:V3)=>Math.hypot(...a);
const unit=(a:V3):V3=>a.map(v=>v/(length(a)||1)) as V3;
const cross=(a:V3,b:V3):V3=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const positive=(a:V3):V3=>{const sign=a.find(n=>Math.abs(n)>.00001)??1;return sign<0?a.map(n=>-n) as V3:a;};
type Finish=Extract<CadSolid,{kind:'finish'}>;
type Shell=Extract<CadSolid,{kind:'shell'}>;
interface Support {item:CadBody;shape:r.Shape3D;bounds:CadMesh['bounds']}
class Build {
  private owned=new Set<{delete:()=>void}>();
  constructor(readonly wasm:ManifoldToplevel){}
  own<T extends {delete:()=>void}>(value:T):T{this.owned.add(value);return value;}
  dispose():void{for(const value of [...this.owned].reverse())try{value.delete();}catch{/* Consuming sketch operations release their own inputs. */}this.owned.clear();}
  bounds(shape:r.AnyShape):CadMesh['bounds']{const box=this.own(shape.boundingBox),[min,max]=box.bounds;return{min,max};}
  manifold(shape:r.Shape3D):Manifold{
    const data=shape.mesh({tolerance:.005,angularTolerance:.06}),seen=new Map<string,number>(),from:number[]=[],to:number[]=[];
    for(let i=0;i<data.vertices.length;i+=3){const key=data.vertices.slice(i,i+3).map(n=>Math.round(n*1e6)).join(','),previous=seen.get(key);if(previous!==undefined){from.push(i/3);to.push(previous);}else seen.set(key,i/3);}
    const mesh=new this.wasm.Mesh({numProp:3,vertProperties:new Float32Array(data.vertices),triVerts:new Uint32Array(data.triangles),mergeFromVert:new Uint32Array(from),mergeToVert:new Uint32Array(to)});
    return new this.wasm.Manifold(mesh);
  }
  body(item:CadBody,support?:Support):Support{
    // Absorb primitive sizing before building; this keeps cylinders analytic after resizing.
    const s=item.solid,abs=item.scale.map(Math.abs) as V3,absorb=s.kind==='primitive'&&['box','sphere','cylinder','tube','pyramid','wedge'].includes(s.shape);
    // Stretch both inner ellipse axes along with the outside. A scalar wall
    // multiplied by the smaller scale silently widens the hole on the other
    // axis, changing material volume when a precision feature is introduced.
    let shape:r.Shape3D;
    if(s.kind==='primitive'&&s.shape==='tube'){
      if(s.wall>=Math.min(s.size[0],s.size[1])/2)throw new Error('Tube wall must be less than half its width and depth. Choose a thinner wall or a larger tube.');
      const [x,y,z]=s.size.map((v,i)=>v*abs[i]);
      shape=this.tube(x,y,z,(s.size[0]/2-s.wall)*abs[0],(s.size[1]/2-s.wall)*abs[1]);
    }else shape=this.solid(absorb?{...s,size:s.size.map((v,i)=>v*abs[i]) as V3,wall:s.wall*Math.min(abs[0],abs[1])}:s,support);
    const bounds=this.bounds(shape),scale=absorb?item.scale.map(v=>Math.sign(v)) as V3:item.scale;
    if(scale.some(v=>Math.abs(v-1)>.0000001))shape=this.scale(shape,scale);
    for(let i=0;i<3;i++)if(item.rotation[i])shape=this.own(shape.rotate(item.rotation[i],[0,0,0],(['X','Y','Z'] as const)[i]));
    shape=this.own(shape.translate(item.position));
    // Attachment coordinates refer to the source recipe before its body transform.
    const rawBounds=absorb?{min:bounds.min.map((v,i)=>v/abs[i]) as V3,max:bounds.max.map((v,i)=>v/abs[i]) as V3}:bounds;
    return{item,shape,bounds:rawBounds};
  }
  private scale(shape:r.Shape3D,scale:V3):r.Shape3D{
    const absolute=scale.map(Math.abs);
    if(Math.max(...absolute)-Math.min(...absolute)<1e-8){shape=this.own(shape.scale(absolute[0]));for(let i=0;i<3;i++)if(scale[i]<0)shape=this.own(shape.mirror((['YZ','XZ','XY'] as const)[i]));return shape;}
    // General affine scaling of an existing complex B-rep uses sewn planar patches.
    // Preserve closed topology, and merge coplanar patches before exposing edges.
    const mesh=shape.mesh({tolerance:.005,angularTolerance:.08});
    if(mesh.triangles.length>60000)throw new Error('This scaled solid is too detailed to finish. Resize its original sketch or primitive in History instead.');
    const points=Array.from({length:mesh.vertices.length/3},(_,i)=>mesh.vertices.slice(i*3,i*3+3).map((v,k)=>v*scale[k]) as V3),faces:r.Face[]=[];
    for(let i=0;i<mesh.triangles.length;i+=3){const triangle=mesh.triangles.slice(i,i+3).map(index=>points[index]);if(scale[0]*scale[1]*scale[2]<0)triangle.reverse();faces.push(this.own(r.makePolygon(triangle)));}
    const sewn=this.own(r.makeSolid(faces)),unify=this.own(new oc.ShapeUpgrade_UnifySameDomain(sewn.wrapped,true,true,false));unify.Build();const result=this.own(r.cast(unify.Shape()));if(!r.isShape3D(result))throw new Error('Could not preserve this scaled solid. Edit its original dimensions in History.');return result;
  }
  private tube(x:number,y:number,z:number,innerX:number,innerY:number):r.Shape3D{
    const outer=this.own(this.ellipse(x/2,y/2).extrude(z).translateZ(-z/2));
    const inner=this.own(this.ellipse(innerX,innerY).extrude(z+.2).translateZ(-z/2-.1));
    return this.own(outer.cut(inner));
  }
  private polygon(points:V2[],plane:Workplane):r.Sketch{
    const vertices=points.map(([x,y])=>plane.origin.map((v,i)=>v+plane.u[i]*x+plane.v[i]*y) as V3);
    const edges=vertices.map((p,i)=>this.own(r.makeLine(p,vertices[(i+1)%vertices.length]))),wire=this.own(r.assembleWire(edges));
    return this.own(new r.Sketch(wire,{defaultOrigin:plane.origin,defaultDirection:plane.normal}));
  }
  private ellipse(rx:number,ry:number,plane?:r.Plane):r.Sketch{return this.own(Math.abs(rx-ry)<1e-8?r.sketchCircle(rx,plane?{plane}:{}):r.sketchEllipse(rx,ry,plane?{plane}:{}));}
  private sketch(points:V2[],plane:Workplane):r.Sketch{
    if(points.length===96){const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),x=(Math.max(...xs)+Math.min(...xs))/2,y=(Math.max(...ys)+Math.min(...ys))/2,rx=(Math.max(...xs)-Math.min(...xs))/2,ry=(Math.max(...ys)-Math.min(...ys))/2;
      if(rx>0&&ry>0&&points.every(p=>Math.abs(((p[0]-x)/rx)**2+((p[1]-y)/ry)**2-1)<.0001)){
        const origin=plane.origin.map((v,i)=>v+plane.u[i]*x+plane.v[i]*y) as V3,p=this.own(new r.Plane(origin,plane.u,plane.normal));return this.ellipse(rx,ry,p);
      }
    }
    return this.polygon(points,plane);
  }
  private polyhedron(points:V3[],faces:number[][]):r.Shape3D{return this.own(r.makeSolid(faces.map(indices=>this.own(r.makePolygon(indices.map(i=>points[i]))))));}
  private extrude(s:Extract<CadSolid,{kind:'extrude'}>,support?:Support):r.Shape3D{
    let plane=s.plane,height=s.height;
    if(s.feature?.attachment){const a=s.feature.attachment;if(!support||a.reference!==support.item.id)throw new Error('This sketch has lost its supporting solid. Restore it or choose a fixed workplane.');plane=attachedPlane(support.item,support.bounds,a);
      const base=this.manifold(support.shape);try{const b=base.boundingBox(),distance=Math.hypot(...sub(b.max,b.min))+1;plane=resolveSupportPlane(plane,solveSketch(s.points,s.feature?.constraints,s.feature?.sketch),distance,(start,end)=>base.rayCast(start,end));if(s.feature.through){if(distance>1999)throw new Error('The through cut exceeds the workspace limit.');height=-distance;}const shift=height>0?-.02:.02;plane={...plane,origin:plane.origin.map((v,i)=>v+plane.normal[i]*shift) as V3};height-=shift;}finally{base.delete();}}
    // Existing negative pulls extrude the profile from the lower plane.
    if(height<0)plane={...plane,origin:plane.origin.map((v,i)=>v+plane.normal[i]*height) as V3};
    return this.own(this.sketch(solveSketch(s.points,s.feature?.constraints,s.feature?.sketch),plane).extrude(Math.abs(height),{extrusionProfile:s.taper!==1?{endFactor:s.taper,profile:'linear'}:undefined,twistAngle:s.twist||undefined}));
  }
  solid(s:CadSolid,support?:Support):r.Shape3D{
    if(s.kind==='mesh'){if(s.indices.length/3>3000)throw new Error('This imported mesh is too detailed for precision edge or shell tools. Use Join, Subtract or sketch cuts, or import a simpler STL.');const points=Array.from({length:s.positions.length/3},(_,i)=>s.positions.slice(i*3,i*3+3) as V3);return this.polyhedron(points,Array.from({length:s.indices.length/3},(_,i)=>s.indices.slice(i*3,i*3+3)));}
    if(s.kind==='loft'||s.kind==='sweep'){
      try{
        let result:r.Shape3D;
        if(s.kind==='loft'){
          s.profiles.forEach(p=>checkProfile(solveSketch(p.points,p.constraints,p.shape)));
          if(s.profiles.length<2||s.profiles.length>16)throw new Error('A loft needs 2–16 profiles.');
          const profiles=s.profiles.map(p=>this.sketch(solveSketch(p.points,p.constraints,p.shape),profilePlane(p)));result=this.own(profiles[0].loftWith(profiles.slice(1),{ruled:s.ruled}));
        }else{
          const section=solveSketch(s.profile.points,s.profile.constraints,s.profile.shape);checkProfile(section);const points=s.path.points;
          if(points.length<2||points.length>64||points.some((p,i)=>p.some(n=>!Number.isFinite(n)||Math.abs(n)>10000)||(i>0&&length(sub(p,points[i-1]))<.01))||length(sub(points[0],points.at(-1)!))<.01)throw new Error('Use an open path with 2–64 distinct points.');
          const edges=s.path.smooth&&points.length>2?pathBeziers(points).map(p=>this.own(r.makeBezierCurve(p))):points.slice(1).map((p,i)=>this.own(r.makeLine(points[i],p))),wire=this.own(r.assembleWire(edges)),profile=this.sketch(section,sweepPlane(points,s.roll));
          result=this.own(r.genericSweep(profile.wire,wire,{transitionMode:s.transition,forceProfileSpineOthogonality:true}));
        }
        const checker=this.own(new oc.BRepCheck_Analyzer(result.wrapped));if(!checker.IsValid()||r.measureVolume(result)<=.000001)throw new Error('The result is not a valid solid.');return result;
      }catch(error){if(error instanceof Error&&/profile|path|loft needs/.test(error.message))throw error;throw new Error(s.kind==='loft'?'Cannot loft these profiles. Separate their planes, simplify crossing outlines, or try ruled sides. Your sketches are preserved.':'Cannot sweep this profile along the path. Try a smaller profile, gentler bends or a different corner setting. Your sketch and path are preserved.');}
    }
    if(s.kind==='shell'){const input=this.body(s.source);if(s.feature?.suppressed)return input.shape;return this.shell(input.shape,s);}
    if(s.kind==='finish'){const input=this.body(s.source);if(s.feature?.suppressed)return input.shape;return this.finish(input.shape,s);}
    if(s.kind==='boolean'){
      if(s.children[0].solid.feature?.suppressed&&!['boolean','finish','shell'].includes(s.children[0].solid.kind))throw new Error('The starting solid is suppressed. Enable it before rebuilding.');
      const base=this.body(s.children[0]);if(s.feature?.suppressed)return base.shape;
      if(s.operation==='hull'){
        const solids=s.children.map(item=>this.body(item).shape),meshes=solids.map(shape=>this.manifold(shape));let hull:Manifold|undefined;try{hull=this.wasm.Manifold.hull(meshes);const m=hull.getMesh(),points=Array.from({length:m.numVert},(_,i)=>Array.from(m.vertProperties.slice(i*m.numProp,i*m.numProp+3)) as V3);return this.polyhedron(points,Array.from({length:m.numTri},(_,i)=>Array.from(m.triVerts.slice(i*3,i*3+3))));}finally{hull?.delete();meshes.forEach(m=>m.delete());}
      }
      let shape=base.shape;for(const child of s.children.slice(1))if(!child.solid.feature?.suppressed||['finish','shell','boolean'].includes(child.solid.kind)){const tool=this.body(child,base).shape;shape=this.own(s.operation==='union'?shape.fuse(tool):s.operation==='subtract'?shape.cut(tool):shape.intersect(tool));}return shape;
    }
    if(s.kind==='extrude')return this.extrude(s,support);
    if(s.kind==='revolve'){
      const plane={origin:s.plane.origin,u:s.plane.u,v:s.plane.normal,normal:s.plane.v.map(v=>-v) as V3};
      const points=solveSketch(s.points,s.feature?.constraints,s.feature?.sketch);if(points.some(p=>p[0]<-1e-7))throw new Error('Keep the revolve profile to the right of its axis.');
      return this.own(this.polygon(points.map(p=>[Math.max(0,p[0]),p[1]]),plane).revolve(s.plane.normal,{origin:s.plane.origin,angle:s.degrees}));
    }
    const[x,y,z]=s.size;
    if(s.shape==='box')return this.own(r.makeBox([-x/2,-y/2,-z/2],[x/2,y/2,z/2]));
    if(s.shape==='sphere')return this.own(Math.abs(x-y)<1e-8&&Math.abs(x-z)<1e-8?r.makeSphere(x/2):r.makeEllipsoid(x/2,y/2,z/2));
    if(s.shape==='cylinder'||s.shape==='tube'){
      const outer=this.own(this.ellipse(x/2,y/2).extrude(z).translateZ(-z/2));
      if(s.shape==='cylinder')return outer;
      if(s.wall>=Math.min(x,y)/2)throw new Error('Tube wall must be less than half its width and depth. Choose a thinner wall or a larger tube.');
      const wall=s.wall,inner=this.own(this.ellipse(x/2-wall,y/2-wall).extrude(z+.2).translateZ(-z/2-.1));return this.own(outer.cut(inner));
    }
    if(s.shape==='cone'){const plane={origin:[0,0,0] as V3,u:[1,0,0] as V3,v:[0,0,1] as V3,normal:[0,-1,0] as V3};let shape=this.own(this.polygon([[0,-z/2],[x/2,-z/2],[0,z/2]],plane).revolve([0,0,1],{origin:[0,0,0],angle:360}));if(x!==y)shape=this.scale(shape,[1,y/x,1]);return shape;}
    if(s.shape==='pyramid')return this.polyhedron([[x/2,0,-z/2],[0,y/2,-z/2],[-x/2,0,-z/2],[0,-y/2,-z/2],[0,0,z/2]],[[3,2,1,0],[0,1,4],[1,2,4],[2,3,4],[3,0,4]]);
    if(s.shape==='wedge')return this.polyhedron([[-x/2,-y/2,-z/2],[x/2,-y/2,-z/2],[-x/2,-y/2,z/2],[-x/2,y/2,-z/2],[x/2,y/2,-z/2],[-x/2,y/2,z/2]],[[0,2,1],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]]);
    const radius=Math.min(x,y)/2,tube=Math.min(z/2,radius*.45),plane=this.own(new r.Plane([radius-tube,0,0],[1,0,0],[0,-1,0]));let shape=this.own(this.ellipse(tube,z/2,plane).revolve([0,0,1],{origin:[0,0,0],angle:360}));if(x!==y)shape=this.scale(shape,[x/(2*radius),y/(2*radius),1]);return shape;
  }
  edges(shape:r.Shape3D):{edge:r.Edge;data:CadEdge}[]{
    const bounds=this.bounds(shape),normalize=(p:V3)=>p.map((v,i)=>(v-bounds.min[i])/(bounds.max[i]-bounds.min[i]||1)) as V3,faces=shape.faces.map(f=>this.own(f)),adjacent=new Map<number,r.Face[]>();
    for(const face of faces){const seen=new Set<number>();for(const edge of face.edges){this.own(edge);if(seen.has(edge.hashCode))continue;seen.add(edge.hashCode);const list=adjacent.get(edge.hashCode)??[];list.push(face);adjacent.set(edge.hashCode,list);}}
    const result:{edge:r.Edge;data:CadEdge}[]=[];
    for(const edge of shape.edges){this.own(edge);const neighbours=adjacent.get(edge.hashCode);if(neighbours?.length!==2||edge.length<.0001)continue;
      const continuity=oc.BRep_Tool.Continuity(edge.wrapped,neighbours[0].wrapped,neighbours[1].wrapped);if(continuity!==oc.GeomAbs_Shape.GeomAbs_C0)continue;
      const midpoint=this.own(edge.pointAt(.5)),firstNormal=this.own(neighbours[0].normalAt(midpoint)),secondNormal=this.own(neighbours[1].normalAt(midpoint));if(firstNormal.dot(secondNormal)>.9999)continue;
      const at=(t:number)=>{const p=this.own(edge.pointAt(t));return p.toTuple();},closed=edge.isClosed||length(sub(at(0),at(1)))<.00001,count=closed?64:edge.geomType==='LINE'?1:32,points=Array.from({length:count+1},(_,i)=>at(i/count));
      const samples=closed?points.slice(0,-1):points,edgeBounds=closed?this.bounds(edge):undefined,center=[0,1,2].map(i=>edgeBounds?(edgeBounds.min[i]+edgeBounds.max[i])/2:samples.reduce((sum,p)=>sum+p[i],0)/samples.length) as V3,direction=positive(unit(closed?cross(sub(points[Math.floor(count/4)],center),sub(points[Math.floor(count/2)],center)):sub(points.at(-1)!,points[0])));
      result.push({edge,data:{ref:{curve:edge.geomType,closed,center:normalize(center),start:normalize(points[0]),end:normalize(points.at(-1)!),direction,rank:0,groupSize:1},points,length:edge.length}});
    }
    const groups=new Map<string,typeof result>();for(const candidate of result)if(candidate.data.ref.closed){const ref=candidate.data.ref,key=[...ref.center,...ref.direction].map(n=>Math.round(n*1e5)).join(','),group=groups.get(key)??[];group.push(candidate);groups.set(key,group);}for(const group of groups.values()){group.sort((a,b)=>a.data.length-b.data.length);group.forEach((e,i)=>{e.data.ref.rank=i;e.data.ref.groupSize=group.length;});}
    return result;
  }
  faces(shape:r.Shape3D,mesh=false):{face:r.Face;data:CadFace}[]{
    const bounds=this.bounds(shape),normalize=(p:V3)=>p.map((v,i)=>(v-bounds.min[i])/(bounds.max[i]-bounds.min[i]||1)) as V3;
    if(mesh)shape.mesh({tolerance:.005,angularTolerance:.06});
    return shape.faces.map(face=>{this.own(face);const box=this.bounds(face),properties=this.own(r.measureShapeSurfaceProperties(face)),center=properties.centerOfMass,normal=face.geomType==='PLANE'?this.own(face.normalAt(center)).toTuple():[0,0,0] as V3,triangles=mesh?face.triangulation():null;
      return{face,data:{ref:{surface:face.geomType,center:normalize(center),min:normalize(box.min),max:normalize(box.max),normal},positions:triangles?.vertices??[],indices:triangles?.trianglesIndexes??[]}};
    });
  }
  private shell(shape:r.Shape3D,recipe:Shell):r.Shape3D{
    const candidates=this.faces(shape),selected:r.Face[]=[],used=new Set<r.Face>();
    for(const ref of recipe.faces){const scored=candidates.filter(c=>!used.has(c.face)&&c.data.ref.surface===ref.surface).map(c=>{const f=c.data.ref;return{...c,score:length(sub(f.center,ref.center))+length(sub(f.min,ref.min))+length(sub(f.max,ref.max))+.1*length(sub(f.normal,ref.normal))};}).sort((a,b)=>a.score-b.score);
      if(!scored[0]||scored[0].score>.01||(scored[1]&&Math.abs(scored[1].score-scored[0].score)<.00001))throw new Error('An open face changed or disappeared. Edit Shell and reselect its faces; your original solid is safe.');selected.push(scored[0].face);used.add(scored[0].face);
    }
    try{
      const solids=shape.solids.map(s=>this.own(s));if(solids.length!==1)throw new Error('Select one connected solid.');
      const before=r.measureVolume(shape);
      const checked=(offset:r.Shape3D):r.Shape3D=>{
        // With no removed faces OCC returns the inward offset; subtract it for a sealed cavity.
        const result=recipe.faces.length?offset:this.own(shape.cut(offset)),checker=this.own(new oc.BRepCheck_Analyzer(result.wrapped)),after=r.measureVolume(result);
        if(!checker.IsValid()||after<=.000001||after>=before-.000001)throw new Error('Invalid wall thickness');return result;
      };
      try{
        const filter=this.own(new r.FaceFinder()).inList(selected.map(f=>this.own(f.clone())));
        return checked(this.own(shape.shell({filter,thickness:recipe.thickness})));
      }catch{
        // Boolean outlines can lose small shoulder faces during an inward
        // offset. Intersect all offset surfaces so OCC trims those crossings
        // instead of silently returning the unchanged input solid.
        const removed=this.own(new oc.NCollection_List_TopoDS_Shape());for(const face of selected)removed.Append(face.wrapped);
        const builder=this.own(new oc.BRepOffsetAPI_MakeThickSolid());
        builder.MakeThickSolidByJoin(shape.wrapped,removed,-recipe.thickness,.001,oc.BRepOffset_Mode.BRepOffset_Skin,true,false,oc.GeomAbs_JoinType.GeomAbs_Arc,true);
        if(!builder.IsDone())throw new Error('Offset intersections could not be resolved');
        const offset=this.own(r.cast(builder.Shape()));if(!r.isShape3D(offset))throw new Error('Offset is not a solid');return checked(offset);
      }
    }catch{throw new Error(`Cannot shell this solid at ${recipe.thickness} mm. Try a thinner wall or different open faces. Your original solid is unchanged.`);}
  }
  private finish(shape:r.Shape3D,recipe:Finish):r.Shape3D{
    const candidates=this.edges(shape),selected:r.Edge[]=[],used=new Set<r.Edge>();
    for(const ref of recipe.edges){const scored=candidates.filter(c=>c.data.ref.closed===ref.closed&&!used.has(c.edge)&&(!ref.closed||(c.data.ref.rank===(ref.rank??0)&&c.data.ref.groupSize===(ref.groupSize??1)))).map(c=>{const e=c.data.ref,type=e.curve===ref.curve?0:(e.curve==='CIRCLE'||e.curve==='ELLIPSE')&&(ref.curve==='CIRCLE'||ref.curve==='ELLIPSE')?0:1;const ends=ref.closed?0:Math.min(length(sub(e.start,ref.start))+length(sub(e.end,ref.end)),length(sub(e.end,ref.start))+length(sub(e.start,ref.end)))/2;return{...c,score:type+length(sub(e.center,ref.center))+ends+.1*(1-Math.abs(dot(e.direction,ref.direction)))};}).sort((a,b)=>a.score-b.score);
      if(!scored[0]||scored[0].score>.005||(scored[1]&&Math.abs(scored[1].score-scored[0].score)<.00001))throw new Error('A selected edge changed or disappeared. Edit this feature and reselect its edges; your original solid is safe.');selected.push(scored[0].edge);used.add(scored[0].edge);
    }
    try{const result=this.own(recipe.mode==='fillet'?shape.fillet(recipe.size,f=>f.inList(selected.map(e=>this.own(e.clone())))):shape.chamfer(recipe.size,f=>f.inList(selected.map(e=>this.own(e.clone())))));
      const checker=this.own(new oc.BRepCheck_Analyzer(result.wrapped));if(!checker.IsValid())throw new Error('Invalid result');return result;
    }catch{throw new Error(`Cannot ${recipe.mode} these edges at ${recipe.size} mm. Try a smaller size or fewer edges. Your original solid is unchanged.`);}
  }
}
export function nativeEdges(item:CadBody,wasm:ManifoldToplevel):CadEdge[]{const build=new Build(wasm);try{return build.edges(build.body(item).shape).map(e=>e.data);}catch(error){throw error instanceof Error?error:new Error('Could not rebuild this solid for edge selection. Try editing its original sketch or dimensions.');}finally{build.dispose();}}
export function nativeFaces(item:CadBody,wasm:ManifoldToplevel):CadFace[]{const build=new Build(wasm);try{return build.faces(build.body(item).shape,true).map(f=>f.data);}catch(error){throw error instanceof Error?error:new Error('Could not rebuild this solid for face selection. Try editing its original sketch or dimensions.');}finally{build.dispose();}}
export function nativeFinish(recipe:Extract<CadSolid,{kind:'finish'|'shell'|'loft'|'sweep'}>,wasm:ManifoldToplevel):CadMesh{
  const build=new Build(wasm);let solid:Manifold|undefined;try{const shape=build.solid(recipe);solid=build.manifold(shape);if(solid.status()!=='NoError'||solid.isEmpty())throw new Error('This feature could not make closed solid geometry. Try a smaller size.');const m=solid.getMesh();return{positions:new Float32Array(m.vertProperties),indices:new Uint32Array(m.triVerts),bounds:solid.boundingBox(),volume:solid.volume(),triangles:m.numTri};}catch(error){throw error instanceof Error?error:new Error('Could not rebuild this precision feature. Try a smaller size or a simpler source sketch.');}finally{solid?.delete();build.dispose();}
}
