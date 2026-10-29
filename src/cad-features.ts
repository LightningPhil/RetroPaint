import { captureAttachment } from './cad-attachment';
import { cadCompute } from './cad-engine';
import { cadInputs, sketchPoints, type CadBody, type CadSolid, type V2, type V3 } from './cad-model';

export interface FeatureEntry { key: string; path: number[]; sketch: boolean; label: string; depth: number; item: CadBody; profile?: number; sweepPath?: boolean }
export function featureKey(path: number[], sketch = false): string { return (path.join('.') || 'root')+(sketch?':sketch':''); }
export function featureName(item: CadBody): string {
  const s=item.solid;
  return s.feature?.label || (s.kind==='mesh'?'Imported STL':s.kind==='loft'?'Loft':s.kind==='sweep'?'Sweep':s.kind==='shell'?'Shell':s.kind==='finish'?(s.mode==='fillet'?'Fillet':'Chamfer'):s.kind==='boolean'?{union:'Join',subtract:'Cut / hole',intersect:'Intersection',hull:'Hull'}[s.operation]:s.kind==='extrude'?'Extrusion':s.kind==='revolve'?'Revolve':item.name);
}
/** Paths are scoped to the solid: copies may share original construction IDs safely. */
export function featureTree(root: CadBody): FeatureEntry[] {
  const entries:FeatureEntry[]=[];
  const visit=(item:CadBody,path:number[],depth:number)=>{
    entries.push({key:featureKey(path),path,sketch:false,label:featureName(item),depth,item});
    if(item.solid.kind==='loft'||item.solid.kind==='sweep'){
      const profiles=item.solid.kind==='loft'?item.solid.profiles:[item.solid.profile];
      profiles.forEach((p,i)=>entries.push({key:featureKey(path)+':profile:'+i,path,sketch:true,label:p.name||'Profile '+(i+1),depth:depth+1,item,profile:i}));
      if(item.solid.kind==='sweep')entries.push({key:featureKey(path)+':path',path,sketch:true,label:item.solid.path.name||'Sweep path',depth:depth+1,item,sweepPath:true});
    }
    if(cadInputs(item.solid).length)cadInputs(item.solid).forEach((child,i)=>visit(child,[...path,i],depth+1));
    else if(item.solid.kind==='extrude'||item.solid.kind==='revolve')entries.push({key:featureKey(path,true),path,sketch:true,label:item.solid.feature?.sketchName||(item.solid.kind==='revolve'?'Profile sketch':`${sketchType(item.solid)} sketch`),depth:depth+1,item});
  };
  visit(root,[],0);return entries;
}
export function featureTimeline(root: CadBody): FeatureEntry[] {
  const entries:FeatureEntry[]=[];
  const visit=(item:CadBody,path:number[])=>{cadInputs(item.solid).forEach((child,i)=>visit(child,[...path,i]));entries.push({key:featureKey(path),path,sketch:false,label:featureName(item),depth:path.length,item});};
  visit(root,[]);return entries;
}
export function featureAt(root:CadBody,path:number[]):CadBody {
  let item=root;for(const index of path){const child=cadInputs(item.solid)[index];if(!child)throw new Error('This feature changed. Select it again in History.');item=child;}return item;
}
export function editFeature(root:CadBody,path:number[],change:(item:CadBody)=>void):CadBody {
  const next=structuredClone(root);change(featureAt(next,path));return next;
}
/** Show just the input of an earlier finish, retaining all ancestor placements. */
export function featureInputView(root:CadBody,path:number[]):CadBody{
  const visit=(item:CadBody,depth:number):CadBody=>{
    const children=cadInputs(item.solid),input=depth===path.length?(item.solid.kind==='finish'||item.solid.kind==='shell'?structuredClone(item.solid.source):undefined):visit(children[path[depth]],depth+1);
    if(!input)throw new Error('Select a fillet, chamfer or shell first.');return{...structuredClone(item),solid:{kind:'boolean',operation:'union',children:[input]}};
  };return visit(root,0);
}
/** Rollback is a view of completed construction, never a replacement of the document. */
export function historyStage(root:CadBody,step:number):CadBody {
  const order=featureTimeline(root),allowed=new Set(order.slice(0,step+1).map(e=>e.key));
  const visit=(item:CadBody,path:number[]):CadBody|undefined=>{
    if(allowed.has(featureKey(path)))return structuredClone(item);
    if(!cadInputs(item.solid).length)return undefined;
    const children=cadInputs(item.solid).flatMap((child,i)=>{const part=visit(child,[...path,i]);return part?[part]:[];});
    return children.length?{...structuredClone(item),solid:{kind:'boolean',operation:'union',children}}:undefined;
  };
  const result=visit(root,[]);if(!result)throw new Error('Choose a completed feature.');return result;
}
export function sketchType(s:CadSolid):'rectangle'|'circle'|'polygon' {
  if(s.feature?.sketch)return s.feature.sketch;
  if(s.kind!=='extrude')return 'polygon';
  const p=s.points;
  if(p.length===4&&p.every((v,i)=>v[0]===p[(i+1)%4][0]||v[1]===p[(i+1)%4][1]))return 'rectangle';
  if(p.length===96){const b=sketchBounds(p),rx=b.width/2,ry=b.height/2,cx=b.x+rx,cy=b.y+ry;if(rx>0&&ry>0&&p.every(v=>Math.abs(((v[0]-cx)/rx)**2+((v[1]-cy)/ry)**2-1)<.0001))return 'circle';}return 'polygon';
}
export function sketchBounds(points:V2[]):{x:number;y:number;width:number;height:number}{const x=Math.min(...points.map(p=>p[0])),y=Math.min(...points.map(p=>p[1]));return{x,y,width:Math.max(...points.map(p=>p[0]))-x,height:Math.max(...points.map(p=>p[1]))-y};}
export function resizeSketch(s:CadSolid,x:number,y:number,width:number,height:number):void {
  if(s.kind!=='extrude'&&s.kind!=='revolve')throw new Error('This feature has no sketch outline.');
  const shape=sketchType(s);if(shape==='polygon')throw new Error('Edit the polygon’s points.');
  s.points=sketchPoints(shape,x,y,width,height);s.feature={...s.feature,sketch:shape};
}
/** Upgrade earlier face sketches once, before edits, so existing projects gain dependencies too. */
export async function prepareFeatureHistory(root:CadBody):Promise<CadBody> {
  const next=structuredClone(root);
  const visit=async(item:CadBody):Promise<void>=>{
    if(item.solid.kind==='finish'||item.solid.kind==='shell'){await visit(item.solid.source);return;}
    if(item.solid.kind!=='boolean')return;
    for(const child of item.solid.children)await visit(child);
    const [support,...tools]=item.solid.children;
    for(const tool of tools){const s=tool.solid;if(s.kind!=='extrude'||s.feature?.attachment)continue;
      const {mesh}=await cadCompute([{...support,position:[0,0,0],rotation:[0,0,0],scale:[1,1,1]}]);
      const attachment=captureAttachment(support,mesh.bounds,s.plane);
      const axis=attachment.normal.findIndex(n=>Math.abs(n)>.999);
      // Older workplane cuts remain fixed; only recognizable face sketches become attached.
      if(axis<0||Math.min(Math.abs(attachment.anchor[axis]),Math.abs(attachment.anchor[axis]-1))>.006)continue;
      s.feature={...s.feature,sketch:sketchType(s),attachment};
      // Earlier face tools included a small kernel overlap in their saved height.
      s.height=s.height>0?Math.max(.05,s.height-.02):Math.min(-.05,s.height+.04);
    }
  };
  await visit(next);return next;
}
export function setFeaturePlane(s:CadSolid,axis:'xy'|'xz'|'yz',origin:V3):void {
  if(s.kind!=='extrude'&&s.kind!=='revolve')throw new Error('This feature has no sketch plane.');
  const u:V3=axis==='yz'?[0,1,0]:[1,0,0],v:V3=axis==='xy'?[0,1,0]:[0,0,1],normal:V3=axis==='xy'?[0,0,1]:axis==='xz'?[0,-1,0]:[1,0,0];
  s.plane={u,v,normal,origin};s.feature={...s.feature,attachment:undefined,through:false};
}
