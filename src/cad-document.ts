import { activeLayer, addLayer, canAddLayer, layerChanged, layers, switchLayer, type Layer } from './layers';
import { pushHistory } from './history';
import { body, cadId, readCadLayer, type CadBody, type CadSolid, type CadEdgeRef, type CadFaceRef } from './cad-model';
import { state } from './state';
import { artwork } from './artwork';
import { emit } from './bus';

export function cadLayers(): Layer[] { return layers.filter(layer => layer.cad); }
export function ensureCadLayer(create = false): Layer {
  if (!create && activeLayer().cad) return activeLayer();
  const existing = !create && cadLayers().at(-1);
  if (existing) { switchLayer(existing.id); return existing; }
  if (!canAddLayer()) throw new Error('The layer stack is full. Remove a sheet before adding a 3D layer.');
  const name=`3D ${cadLayers().length + 1}`;
  pushHistory(); addLayer({ units:'mm',bodies:[] }); const layer = activeLayer();
  layer.name = name; layerChanged(); return layer;
}
export function currentBodies(): CadBody[] { return activeLayer().cad?.bodies ?? []; }
export function selectedBodies(): CadBody[] { return currentBodies().filter(b => state.cad.selected.includes(b.id)); }
export function replaceBodies(next: CadBody[], history = true): void {
  const layer = activeLayer(); if (!layer.cad) throw new Error('Choose a 3D layer first.');
  if (next.length > 128) throw new Error('A 3D layer can hold up to 128 pieces. Add another 3D layer for more.');
  readCadLayer({units:'mm',bodies:next});
  if (history) pushHistory(); layer.cad = { units: 'mm', bodies: next }; artwork.markWork(); layerChanged();
}
export function addBody(item: CadBody): void { replaceBodies([...currentBodies(), item]); selectBodies([item.id]); }
export function selectBodies(ids: string[]): void { state.cad.selected = ids; emit('cad-selection'); }
export function updateSelected(change: (item: CadBody) => CadBody): void {
  const ids = new Set(selectedBodies().filter(b => !b.locked).map(b => b.id));
  if (!ids.size) throw new Error('Select an unlocked piece first.');
  replaceBodies(currentBodies().map(item => ids.has(item.id) ? change(structuredClone(item)) : item));
}
export function duplicateSelected(count = 1, offset: [number, number, number] = [25, 0, 0], degrees = 0): void {
  const source = selectedBodies(); if (!source.length) throw new Error('Select a piece to copy.');
  const copies: CadBody[] = [];
  for (let i = 1; i <= count; i++) for (const item of source) {
    const copy = structuredClone(item), angle = degrees * i * Math.PI / 180, [x,y,z] = item.position;
    copy.id = cadId(); copy.name += ' copy'; copy.locked = false;
    copy.position = degrees ? [x*Math.cos(angle)-y*Math.sin(angle),x*Math.sin(angle)+y*Math.cos(angle),z] : [x+offset[0]*i,y+offset[1]*i,z+offset[2]*i];
    copy.rotation[2] += degrees * i; copies.push(copy);
  }
  replaceBodies([...currentBodies(), ...copies]); selectBodies(copies.map(c => c.id));
}
export function removeSelected(): void {
  const remove = new Set(selectedBodies().filter(b => !b.locked).map(b => b.id));
  if (!remove.size) return; replaceBodies(currentBodies().filter(b => !remove.has(b.id))); selectBodies([]);
}
export function combinedBody(operation: 'union' | 'subtract' | 'intersect' | 'hull', items: CadBody[]): CadBody {
  const result = body({ kind: 'boolean', operation, children: structuredClone(items) }, { union: 'Joined solid', subtract: 'Cut solid', intersect: 'Intersection', hull: 'Convex hull' }[operation]);
  result.color = items[0].color; return result;
}
export function featureBody(solid: CadSolid): CadBody { return body(solid, solid.kind === 'revolve' ? 'Revolved sketch' : 'Extruded sketch', currentBodies().length); }
export function finishedBody(item:CadBody,mode:'fillet'|'chamfer',size:number,edges:CadEdgeRef[]):CadBody{
  const source={...structuredClone(item),position:[0,0,0] as [number,number,number],rotation:[0,0,0] as [number,number,number]};
  return {...structuredClone(item),scale:[1,1,1],solid:{kind:'finish',mode,size,edges:structuredClone(edges),source}};
}
export function shelledBody(item:CadBody,thickness:number,faces:CadFaceRef[]):CadBody{
  const source={...structuredClone(item),position:[0,0,0] as [number,number,number],rotation:[0,0,0] as [number,number,number]};
  return{...structuredClone(item),scale:[1,1,1],solid:{kind:'shell',thickness,faces:structuredClone(faces),source}};
}
