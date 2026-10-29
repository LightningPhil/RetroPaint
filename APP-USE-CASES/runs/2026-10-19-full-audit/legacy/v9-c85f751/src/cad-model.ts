/** Serializable, millimetre-based solid recipes. No renderer or WASM objects enter projects. */
export type V2 = [number, number];
export type V3 = [number, number, number];
export type M4 = [number, number, number, number, number, number, number, number, number, number, number, number, number, number, number, number];
export type Primitive = 'box' | 'sphere' | 'cylinder' | 'cone' | 'torus' | 'tube' | 'pyramid' | 'wedge';
export interface Workplane { origin: V3; u: V3; v: V3; normal: V3 }
export interface CadAttachment { reference: string; anchor: V3; u: V3; normal: V3 }
export type CadSketchConstraint = { id: string } & (
  | { kind: 'length' | 'angle'; edge: number; value: number }
  | { kind: 'angle-between'; edge: number; other: number; value: number }
  | { kind: 'diameter'; value: number }
  | { kind: 'horizontal' | 'vertical'; edge: number }
  | { kind: 'parallel' | 'perpendicular'; edge: number; other: number });
export interface CadFeature { label?: string; sketchName?: string; suppressed?: boolean; sketch?: 'rectangle' | 'circle' | 'polygon'; attachment?: CadAttachment; through?: boolean; constraints?: CadSketchConstraint[] }
/** Geometric references survive rebuilds without relying on transient kernel edge numbers. */
export interface CadEdgeRef { curve: string; center: V3; start: V3; end: V3; direction: V3; closed: boolean; rank: number; groupSize: number }
export interface CadEdge { ref: CadEdgeRef; points: V3[]; length: number }
/** Normalized geometry identifies a whole surface after upstream dimensions change. */
export interface CadFaceRef { surface: string; center: V3; min: V3; max: V3; normal: V3 }
export interface CadFace { ref: CadFaceRef; positions: number[]; indices: number[] }
export interface CadProfile { name: string; shape: 'rectangle' | 'circle' | 'polygon'; points: V2[]; plane: Workplane; rotation: number; constraints?: CadSketchConstraint[] }
export interface CadPath { name: string; points: V3[]; smooth: boolean }
export type CadForm =
  | { kind: 'loft'; profiles: CadProfile[]; ruled: boolean }
  | { kind: 'sweep'; profile: CadProfile; path: CadPath; transition: 'right' | 'round'; roll: number };
export type CadSolid = (
  | { kind: 'primitive'; shape: Primitive; size: V3; wall: number }
  | { kind: 'extrude'; points: V2[]; plane: Workplane; height: number; taper: number; twist: number }
  | { kind: 'revolve'; points: V2[]; degrees: number; plane: Workplane }
  | CadForm
  | { kind: 'boolean'; operation: 'union' | 'subtract' | 'intersect' | 'hull'; children: CadBody[] }
  | { kind: 'finish'; mode: 'fillet' | 'chamfer'; size: number; edges: CadEdgeRef[]; source: CadBody }
  | { kind: 'shell'; thickness: number; faces: CadFaceRef[]; source: CadBody }) & { feature?: CadFeature };
export interface CadBody {
  id: string; name: string; color: string; visible: boolean; locked: boolean;
  position: V3; rotation: V3; scale: V3; solid: CadSolid;
}
export interface CadLayer { units: 'mm'; bodies: CadBody[] }
export interface CadMesh { positions: Float32Array; indices: Uint32Array; volume: number; bounds: { min: V3; max: V3 }; triangles: number }
export const PALETTE = ['#f8bf45', '#57bfca', '#ee839b', '#9f89dc', '#7cbf8a', '#ee9464'];
export const XY: Workplane = { origin: [0, 0, 0], u: [1, 0, 0], v: [0, 1, 0], normal: [0, 0, 1] };
export function basePlane(name: string): Workplane {
  if (name === 'xz') return { origin: [0, 0, 0], u: [1, 0, 0], v: [0, 0, 1], normal: [0, -1, 0] };
  if (name === 'yz') return { origin: [0, 0, 0], u: [0, 1, 0], v: [0, 0, 1], normal: [1, 0, 0] };
  return structuredClone(XY);
}
export function cadId(): string { return crypto.randomUUID(); }
export function body(solid: CadSolid, name: string, index = 0): CadBody {
  return { id: cadId(), name, color: PALETTE[index % PALETTE.length], visible: true, locked: false, position: [0, 0, 0], rotation: [0, 0, 0], scale: [1, 1, 1], solid:structuredClone(solid) };
}
export function primitive(shape: Primitive, size: V3 = [20, 20, 20], index = 0): CadBody {
  const result = body({ kind: 'primitive', shape, size, wall: 2 }, shape === 'box' ? 'Cube' : shape[0].toUpperCase() + shape.slice(1), index);
  result.position[2] = size[2] / 2; return result;
}
export function snap(value: number, step: number): number { return step > 0 ? Math.round(value / step) * step : value; }
export function planeMatrix(p: Workplane): M4 { return [...p.u, 0, ...p.v, 0, ...p.normal, 0, ...p.origin, 1]; }
export function sketchPoints(shape: string, x: number, y: number, width: number, height: number): V2[] {
  if (shape === 'circle') return Array.from({ length: 96 }, (_, i) => { const a = i * Math.PI / 48; return [x + Math.cos(a) * width / 2, y + Math.sin(a) * height / 2]; });
  return [[x, y], [x + width, y], [x + width, y + height], [x, y + height]];
}
function rec(value: unknown): Record<string, unknown> { if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid CAD data.'); return value as Record<string, unknown>; }
function n(value: unknown, min = -10000, max = 10000): number { if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max) throw new Error('CAD dimensions must be finite millimetres within the workspace limits.'); return value; }
function vec(value: unknown, min?: number, max?: number): V3 { if (!Array.isArray(value) || value.length !== 3) throw new Error('Invalid CAD vector.'); return value.map(v => n(v, min, max)) as V3; }
export function readSketchConstraints(value: unknown, count: number, shape: string): CadSketchConstraint[] | undefined {
  if(value===undefined)return undefined;
  if(!Array.isArray(value)||value.length>64)throw new Error('A sketch supports up to 64 dimensions and constraints.');
  const ids=new Set<string>();
  return value.map(value=>{const c=rec(value);if(typeof c.id!=='string'||!c.id.length||c.id.length>80||ids.has(c.id))throw new Error('Sketch constraint IDs must be unique.');ids.add(c.id);
    const id=c.id,kind=c.kind;
    if(kind==='diameter'){if(shape!=='circle')throw new Error('Diameter dimensions need a circle sketch.');return{id,kind,value:n(c.value,.01,2000)};}
    if(shape==='circle')throw new Error('Choose a diameter dimension for a circle sketch.');
    const edge=n(c.edge,0,count-1);if(!Number.isInteger(edge))throw new Error('A constraint needs a valid sketch line.');
    if(kind==='length'||kind==='angle')return{id,kind,edge,value:kind==='length'?n(c.value,.01,20000):n(c.value,-360,360)};
    if(kind==='horizontal'||kind==='vertical')return{id,kind,edge};
    if(kind==='parallel'||kind==='perpendicular'||kind==='angle-between'){const other=n(c.other,0,count-1);if(!Number.isInteger(other)||other===edge)throw new Error('Choose two different sketch lines.');return kind==='angle-between'?{id,kind,edge,other,value:n(c.value,0,180)}:{id,kind,edge,other};}
    throw new Error('Unknown sketch constraint.');
  });
}
export function readCadLayer(value: unknown): CadLayer | undefined {
  if (value === undefined) return undefined;
  const data = rec(value); let count = 0;
  const plane = (value: unknown): Workplane => {
    const p = rec(value), result = { origin: vec(p.origin), u: vec(p.u, -1, 1), v: vec(p.v, -1, 1), normal: vec(p.normal, -1, 1) };
    const dot = (a: V3, b: V3) => a.reduce((s, x, i) => s + x * b[i], 0);
    if ([result.u, result.v, result.normal].some(a => Math.abs(dot(a, a) - 1) > 0.001) || Math.abs(dot(result.u, result.v)) > 0.001 || Math.abs(dot(result.u, result.normal)) > 0.001 || Math.abs(dot(result.v, result.normal)) > 0.001 || dot([result.u[1]*result.v[2]-result.u[2]*result.v[1],result.u[2]*result.v[0]-result.u[0]*result.v[2],result.u[0]*result.v[1]-result.u[1]*result.v[0]],result.normal)<0.999) throw new Error('Invalid CAD workplane.');
    return result;
  };
  const points = (value: unknown): V2[] => { if (!Array.isArray(value) || value.length < 3 || value.length > 256) throw new Error('A CAD sketch needs 3–256 points.'); return value.map(p => { if (!Array.isArray(p) || p.length !== 2) throw new Error('Invalid CAD sketch point.'); return [n(p[0]), n(p[1])]; }); };
  const readBody = (value: unknown, depth: number): CadBody => {
    if (++count > 2048 || depth > 64) throw new Error('This CAD scene is too complex to open.');
    const b = rec(value), s = rec(b.solid); let solid: CadSolid;
    if (s.kind === 'primitive') {
      if (!['box','sphere','cylinder','cone','torus','tube','pyramid','wedge'].includes(String(s.shape))) throw new Error('Unknown CAD primitive.');
      solid = { kind: 'primitive', shape: s.shape as Primitive, size: vec(s.size, 0.1, 2000), wall: n(s.wall, 0.1, 1000) };
    } else if (s.kind === 'extrude') {const height=n(s.height,-2000,2000);if(Math.abs(height)<.05)throw new Error('CAD extrusions need at least 0.05 mm of depth.');solid = { kind: 'extrude', points: points(s.points), plane: plane(s.plane), height, taper: n(s.taper, 0.01, 5), twist: n(s.twist, -720, 720) };}
    else if (s.kind === 'revolve') {const profile=points(s.points);if(profile.some(p=>p[0]<0))throw new Error('A revolve profile must stay to the right of its axis.');solid = { kind: 'revolve', points: profile, plane: plane(s.plane), degrees: n(s.degrees, 1, 360) };}
    else if(s.kind==='loft'||s.kind==='sweep'){
      const profile=(value:unknown):CadProfile=>{const p=rec(value);if(!['rectangle','circle','polygon'].includes(String(p.shape))||typeof p.name!=='string')throw new Error('Invalid loft or sweep profile.');const vertices=points(p.points);return{name:p.name.slice(0,60),shape:p.shape as 'polygon',points:vertices,plane:plane(p.plane),rotation:n(p.rotation??0,-36000,36000),constraints:readSketchConstraints(p.constraints,vertices.length,String(p.shape))};};
      if(s.kind==='loft'){
        if(!Array.isArray(s.profiles)||s.profiles.length<2||s.profiles.length>16||typeof s.ruled!=='boolean')throw new Error('A loft needs 2–16 profiles.');
        solid={kind:'loft',profiles:s.profiles.map(profile),ruled:s.ruled};
      }else{
        const path=rec(s.path);if(!Array.isArray(path.points)||path.points.length<2||path.points.length>64||typeof path.smooth!=='boolean'||typeof path.name!=='string'||!['right','round'].includes(String(s.transition)))throw new Error('A sweep needs a path with 2–64 points and valid sweep settings.');
        const vertices=path.points.map(p=>vec(p));if(vertices.some((p,i)=>i>0&&Math.hypot(...p.map((v,k)=>v-vertices[i-1][k]))<.01))throw new Error('Keep sweep path points at least 0.01 mm apart.');
        solid={kind:'sweep',profile:profile(s.profile),path:{name:path.name.slice(0,60),points:vertices,smooth:path.smooth},transition:s.transition as 'right',roll:n(s.roll,-36000,36000)};
      }
    }
    else if (s.kind === 'boolean') {
      if (!['union','subtract','intersect','hull'].includes(String(s.operation)) || !Array.isArray(s.children) || s.children.length < 1 || s.children.length > 128) throw new Error('Invalid CAD build operation.');
      solid = { kind: 'boolean', operation: s.operation as 'union', children: s.children.map(c => readBody(c, depth + 1)) };
    } else if (s.kind === 'finish') {
      if(!['fillet','chamfer'].includes(String(s.mode))||!Array.isArray(s.edges)||!s.edges.length||s.edges.length>256)throw new Error('Choose 1–256 edges for a fillet or chamfer.');
      const edges=s.edges.map(value=>{const e=rec(value);if(typeof e.curve!=='string'||e.curve.length>40||typeof e.closed!=='boolean')throw new Error('Invalid CAD edge reference.');const rank=n(e.rank??0,0,1023),groupSize=n(e.groupSize??1,1,1024);if(!Number.isInteger(rank)||!Number.isInteger(groupSize)||rank>=groupSize)throw new Error('Invalid CAD edge group.');return {curve:e.curve,closed:e.closed,center:vec(e.center),start:vec(e.start),end:vec(e.end),direction:vec(e.direction,-1,1),rank,groupSize};});
      solid={kind:'finish',mode:s.mode as 'fillet',size:n(s.size,.01,1000),edges,source:readBody(s.source,depth+1)};
    } else if(s.kind==='shell'){
      if(!Array.isArray(s.faces)||s.faces.length>128)throw new Error('Choose up to 128 open faces for a shell.');
      const faces=s.faces.map(value=>{const f=rec(value);if(typeof f.surface!=='string'||f.surface.length>40)throw new Error('Invalid CAD face reference.');const min=vec(f.min),max=vec(f.max),normal=vec(f.normal,-1,1);if(min.some((v,i)=>v>max[i])||(f.surface==='PLANE'&&Math.abs(Math.hypot(...normal)-1)>.001))throw new Error('Invalid CAD face bounds or normal.');return{surface:f.surface,center:vec(f.center),min,max,normal};});
      solid={kind:'shell',thickness:n(s.thickness,.01,1000),faces,source:readBody(s.source,depth+1)};
    } else throw new Error('Unknown CAD solid.');
    if (s.feature !== undefined) {
      const f = rec(s.feature), feature: CadFeature = {};
      for (const key of ['label','sketchName'] as const) if (f[key] !== undefined) { if (typeof f[key] !== 'string') throw new Error('Invalid feature name.'); feature[key] = f[key].slice(0, 60); }
      for (const key of ['suppressed', 'through'] as const) if (f[key] !== undefined) { if (typeof f[key] !== 'boolean') throw new Error('Invalid CAD feature flag.'); feature[key] = f[key]; }
      if (f.sketch !== undefined) { if (!['rectangle','circle','polygon'].includes(String(f.sketch))) throw new Error('Invalid sketch type.'); feature.sketch = f.sketch as 'polygon'; }
      if(f.constraints!==undefined){if(solid.kind!=='extrude'&&solid.kind!=='revolve')throw new Error('Sketch constraints belong to a sketch feature.');feature.sketch??=solid.points.length===96?'circle':solid.points.length===4&&solid.points.every((p,i)=>p[0]===solid.points[(i+1)%4][0]||p[1]===solid.points[(i+1)%4][1])?'rectangle':'polygon';feature.constraints=readSketchConstraints(f.constraints,solid.points.length,feature.sketch);}
      if (f.attachment !== undefined) { const a = rec(f.attachment); if (typeof a.reference !== 'string' || !a.reference.length || a.reference.length > 80) throw new Error('Invalid face reference.'); const u = vec(a.u, -1, 1), normal = vec(a.normal, -1, 1); if (Math.abs(Math.hypot(...u)-1)>.001 || Math.abs(Math.hypot(...normal)-1)>.001 || Math.abs(u.reduce((v,n,i)=>v+n*normal[i],0))>.001) throw new Error('Invalid attached sketch axes.'); feature.attachment = { reference:a.reference, anchor:vec(a.anchor), u, normal }; }
      solid.feature = feature;
    }
    const scale = vec(b.scale, -100, 100); if (scale.some(v => Math.abs(v) < 0.001)) throw new Error('CAD solids cannot have zero size.');
    if(typeof b.id!=='string'||!b.id.length||b.id.length>80)throw new Error('Invalid CAD piece ID.');
    return { id: b.id, name: String(b.name??'Piece').slice(0, 60), color: /^#[\da-f]{6}$/i.test(String(b.color)) ? String(b.color) : PALETTE[0], visible: Boolean(b.visible), locked: Boolean(b.locked), position: vec(b.position), rotation: vec(b.rotation, -36000, 36000), scale, solid };
  };
  if (data.units !== 'mm' || !Array.isArray(data.bodies) || data.bodies.length > 128) throw new Error('Invalid CAD layer.');
  const bodies = data.bodies.map(b => readBody(b, 0));
  if (new Set(bodies.map(b => b.id)).size !== bodies.length) throw new Error('CAD body IDs must be unique.');
  return { units: 'mm', bodies };
}
export function cadInputs(s:CadSolid):CadBody[]{return s.kind==='boolean'?s.children:s.kind==='finish'||s.kind==='shell'?[s.source]:[];}
