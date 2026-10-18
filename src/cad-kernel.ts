import Module, { type Manifold, type ManifoldToplevel, type CrossSection } from 'manifold-3d';
import wasmUrl from 'manifold-3d/manifold.wasm?url';
import { cadInputs, planeMatrix, type CadBody, type CadMesh, type CadSolid, type CadEdge, type CadFace } from './cad-model';
import { attachedPlane } from './cad-attachment';
import { solveSketch } from './cad-sketch-constraints';

let ready: Promise<ManifoldToplevel> | undefined;
export function initKernel(): Promise<ManifoldToplevel> {
  return ready ??= Module({ locateFile: () => wasmUrl }).then(wasm => { wasm.setup(); return wasm; });
}
export async function solidMesh(item: CadBody): Promise<CadMesh> {
  const wasm = await initKernel(), finishes=await prepareFinishes([item],wasm),solid = evaluateBody(wasm, item,undefined,finishes);
  try { return meshData(solid); } finally { solid.delete(); }
}
interface Support { item: CadBody; solid: Manifold; bounds: CadMesh['bounds'] }
async function prepareFinishes(bodies:CadBody[],wasm:ManifoldToplevel):Promise<Map<CadSolid,CadMesh>>{
  const result=new Map<CadSolid,CadMesh>();const visit=async(item:CadBody):Promise<void>=>{const s=item.solid;if(s.kind==='finish'||s.kind==='shell'||s.kind==='loft'||s.kind==='sweep'){const native=await import('./cad-brep');await native.initBrep();result.set(s,native.nativeFinish(s,wasm));}else for(const child of cadInputs(s))await visit(child);};for(const body of bodies)await visit(body);return result;
}
export async function solidEdges(item:CadBody):Promise<CadEdge[]>{const wasm=await initKernel(),native=await import('./cad-brep');await native.initBrep();return native.nativeEdges(item,wasm);}
export async function solidFaces(item:CadBody):Promise<CadFace[]>{const wasm=await initKernel(),native=await import('./cad-brep');await native.initBrep();return native.nativeFaces(item,wasm);}
function evaluateSolid(wasm: ManifoldToplevel, recipe: CadSolid, support?: Support, finishes=new Map<CadSolid,CadMesh>()): Manifold {
  const M = wasm.Manifold, C = wasm.CrossSection;
  const owned: (Manifold | CrossSection)[] = [], own = <T extends Manifold | CrossSection>(o: T): T => { owned.push(o); return o; };
  try {
    if(recipe.kind==='finish'||recipe.kind==='shell'||recipe.kind==='loft'||recipe.kind==='sweep'){const mesh=finishes.get(recipe);if(!mesh)throw new Error('The precision feature is not ready. Try reopening this solid.');return new M(new wasm.Mesh({numProp:3,vertProperties:mesh.positions,triVerts:mesh.indices}));}
    if (recipe.kind === 'boolean') {
      if (!['boolean','finish','shell'].includes(recipe.children[0].solid.kind) && recipe.children[0].solid.feature?.suppressed) throw new Error('The starting solid is suppressed. Enable it before rebuilding.');
      const built = buildBody(wasm, recipe.children[0],undefined,finishes), base = own(built.solid);
      if (recipe.feature?.suppressed) return base.translate([0,0,0]);
      const children = [base];
      for (const child of recipe.children.slice(1)) if (!child.solid.feature?.suppressed||['finish','shell','boolean'].includes(child.solid.kind)) children.push(own(evaluateBody(wasm, child, {item:recipe.children[0],solid:base,bounds:built.bounds},finishes)));
      return recipe.operation === 'union' ? M.union(children) : recipe.operation === 'subtract' ? M.difference(children) : recipe.operation === 'intersect' ? M.intersection(children) : M.hull(children);
    }
    if (recipe.kind === 'extrude') {
      if (Math.abs(recipe.height) < 0.05) throw new Error('Extrude by at least 0.05 mm.');
      let plane = recipe.plane, height = recipe.height;
      const attachment = recipe.feature?.attachment;
      if (attachment) {
        if (!support || support.item.id !== attachment.reference) throw new Error('This sketch has lost its supporting solid. Edit the sketch and choose a fixed workplane.');
        plane = attachedPlane(support.item,support.bounds,attachment);
        const bounds = support.solid.boundingBox(), distance = Math.hypot(...bounds.max.map((v,i)=>v-bounds.min[i]))+1;
        const start = plane.origin.map((v,i)=>v+plane.normal[i]*distance) as [number,number,number], end = plane.origin.map((v,i)=>v-plane.normal[i]*distance) as [number,number,number];
        const hits = support.solid.rayCast(start,end).filter(hit=>hit.normal.reduce((sum,n,i)=>sum+n*plane.normal[i],0)>.999);
        hits.sort((a,b)=>Math.hypot(...a.position.map((v,i)=>v-plane.origin[i]))-Math.hypot(...b.position.map((v,i)=>v-plane.origin[i])));
        if (!hits.length) throw new Error('The sketch’s supporting flat face no longer exists. Restore it, or edit the sketch onto a fixed plane.');
        plane = {...plane,origin:[...hits[0].position]};
        if (recipe.feature?.through) { if(distance>1999)throw new Error('The through cut exceeds the 2000 mm workspace limit.'); height = -distance; }
        const shift = height>0?-.02:.02;
        plane = {...plane,origin:plane.origin.map((v,i)=>v+plane.normal[i]*shift) as [number,number,number]}; height += height>0?.02:-.04;
      }
      const section = own(C.ofPolygons([solveSketch(recipe.points,recipe.feature?.constraints,recipe.feature?.sketch)], 'EvenOdd'));
      const solid = own(section.extrude(Math.abs(height), recipe.twist ? 32 : 0, recipe.twist, [recipe.taper, recipe.taper]));
      const shifted = height < 0 ? own(solid.translate([0, 0, height])) : solid;
      return shifted.transform(planeMatrix(plane));
    }
    if (recipe.kind === 'revolve') {
      const points=solveSketch(recipe.points,recipe.feature?.constraints,recipe.feature?.sketch);
      if (points.some(p => p[0] < -1e-7)) throw new Error('Keep the revolve profile to the right of its axis.');
      const section = own(C.ofPolygons([points.map(p=>[Math.max(0,p[0]),p[1]])], 'EvenOdd'));
      return own(section.revolve(128, recipe.degrees)).transform(planeMatrix(recipe.plane));
    }
    const [x, y, z] = recipe.size;
    if (recipe.shape === 'box') return M.cube([x, y, z], true);
    if (recipe.shape === 'sphere') return own(M.sphere(1, 96)).scale([x / 2, y / 2, z / 2]);
    if (recipe.shape === 'cylinder' || recipe.shape === 'cone' || recipe.shape === 'pyramid') return own(M.cylinder(z, x / 2, recipe.shape === 'cylinder' ? x / 2 : 0, recipe.shape === 'pyramid' ? 4 : 96, true)).scale([1, y / x, 1]);
    if (recipe.shape === 'tube') {
      const thickness = Math.min(recipe.wall, x / 2 - 0.05, y / 2 - 0.05);
      const outer = own(M.cylinder(z, 1, 1, 96, true)), inner = own(M.cylinder(z + 0.2, 1, 1, 96, true));
      return own(outer.scale([x / 2, y / 2, 1])).subtract(own(inner.scale([x / 2 - thickness, y / 2 - thickness, 1])));
    }
    if (recipe.shape === 'wedge') {
      const section = own(C.ofPolygons([[[ -x / 2, -z / 2 ], [x / 2, -z / 2], [-x / 2, z / 2]]]));
      return own(own(section.extrude(y)).translate([0, 0, -y / 2])).rotate([90, 0, 0]);
    }
    const radius = Math.min(x, y) / 2, tube = Math.min(z / 2, radius * 0.45);
    const section = own(own(C.circle(tube, 48)).translate([radius - tube, 0]));
    return own(section.revolve(128)).scale([x / (2 * radius), y / (2 * radius), z / (2 * tube)]);
  } finally { owned.reverse().forEach(o => o.delete()); }
}
function buildBody(wasm: ManifoldToplevel, item: CadBody, support?: Support,finishes?:Map<CadSolid,CadMesh>): { solid: Manifold; bounds: CadMesh['bounds'] } {
  const base = evaluateSolid(wasm, item.solid, support,finishes); let scaled: Manifold | undefined, rotated: Manifold | undefined;
  try { const bounds=base.boundingBox();scaled = base.scale(item.scale); rotated = scaled.rotate(item.rotation); return {solid:rotated.translate(item.position),bounds}; }
  finally { rotated?.delete(); scaled?.delete(); base.delete(); }
}
export function evaluateBody(wasm: ManifoldToplevel, item: CadBody, support?: Support,finishes?:Map<CadSolid,CadMesh>): Manifold { return buildBody(wasm,item,support,finishes).solid; }
export function meshData(solid: Manifold): CadMesh {
  if (solid.status() !== 'NoError') throw new Error(`Could not build this solid (${solid.status()}). Try a smaller cut or a simpler sketch.`);
  if (solid.isEmpty()) throw new Error('That operation leaves no solid. Try overlapping the pieces first.');
  const mesh = solid.getMesh(), positions = new Float32Array(mesh.numVert * 3);
  for (let i = 0; i < mesh.numVert; i++) for (let j = 0; j < 3; j++) positions[i * 3 + j] = mesh.vertProperties[i * mesh.numProp + j];
  return { positions, indices: new Uint32Array(mesh.triVerts), volume: solid.volume(), bounds: solid.boundingBox(), triangles: mesh.numTri };
}
export async function printMesh(bodies: CadBody[], bed = true): Promise<CadMesh> {
  if (!bodies.length) throw new Error('Add a visible solid before exporting.');
  const wasm = await initKernel(),finishes=await prepareFinishes(bodies,wasm), pieces:Manifold[]=[]; let joined: Manifold | undefined, placed: Manifold | undefined;
  try { for(const item of bodies)pieces.push(evaluateBody(wasm,item,undefined,finishes));joined = wasm.Manifold.union(pieces); const low = joined.boundingBox().min[2]; placed = joined.translate([0, 0, bed ? -low : 0]); return meshData(placed); }
  finally { placed?.delete(); joined?.delete(); pieces.forEach(p => p.delete()); }
}
/** Binary STL coordinates are millimetres; every facet gets its outward geometric normal. */
export function binaryStl(mesh: CadMesh): ArrayBuffer {
  const buffer = new ArrayBuffer(84 + mesh.triangles * 50), view = new DataView(buffer);
  new Uint8Array(buffer, 0, 80).set(new TextEncoder().encode('RetroPaint 3D | millimetres | solid geometry'));
  view.setUint32(80, mesh.triangles, true);
  for (let i = 0; i < mesh.triangles; i++) {
    const p = [0, 1, 2].map(c => Array.from(mesh.positions.subarray(mesh.indices[i*3+c]*3, mesh.indices[i*3+c]*3+3)));
    const a = p[1].map((n,j) => n-p[0][j]), b = p[2].map((n,j) => n-p[0][j]);
    const normal = [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]], length = Math.hypot(...normal) || 1;
    const values = [...normal.map(n => n/length), ...p.flat()]; values.forEach((n,j) => view.setFloat32(84+i*50+j*4, n, true));
  }
  return buffer;
}
