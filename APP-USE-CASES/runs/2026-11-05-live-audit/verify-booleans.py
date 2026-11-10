"""Independent box CSG bounds/volumes, gap topology, cylindrical cavity and atomic source edits."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';fixtures=root/'test-results/audit-2026-11-05/fixtures/boolean195';downloads=Path.home()/'Downloads';prefix='mouse-audit-boolean195';hashes={}
def retain(name,mesh=False):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return read_binary(raw) if mesh else json.loads(raw)
ui=json.loads((out/'boolean195-ui.json').read_text(encoding='utf-8'));docs={i:retain(prefix+(f' ({i})' if i else '')+'.retropaint') for i in range(16)}
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
def ray(tri,x,y):
 a,b,c=tri[:,0],tri[:,1],tri[:,2];den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]);v=abs(den)>1e-9;a,b,c,den=a[v],b[v],c[v],den[v]
 u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/den;v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/den;hit=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)
 return sorted(set(np.round((u*a[:,2]+v*b[:,2]+(1-u-v)*c[:,2])[hit],6).tolist()))
expected={
 'overlap-union':('union',12000,[[0,0,0],[30,20,20]],1),
 'overlap-subtract-A':('subtract',4000,[[0,0,0],[10,20,20]],1),
 'overlap-subtract-B':('subtract',4000,[[20,0,0],[30,20,20]],1),
 'overlap-intersect':('intersect',4000,[[10,0,0],[20,20,20]],1),
 'overlap-hull':('hull',12000,[[0,0,0],[30,20,20]],1),
 'gapped-union':('union',2000,[[0,0,0],[30,10,10]],2),
 'gapped-hull':('hull',3000,[[0,0,0],[30,10,10]],1),
 'inside-cylinder-subtract':('subtract',8000-80*math.pi,[[0,0,0],[20,20,20]],1),
 'inside-cylinder-target-width30':('subtract',12000-80*math.pi,[[-5,0,0],[25,20,20]],1)}
results={}
for s in ui['samples']:
 stage=s['stage'];fixture='overlap' if stage.startswith('overlap') else 'gapped' if stage.startswith('gapped') else 'cylinder';base=json.loads((fixtures/(fixture+'.retropaint')).read_text());doc=docs[s['docIndex']];bodies=doc['layers'][1]['cad']['bodies'];assert len(bodies)==1;r=bodies[0]['solid'];op,volume,bounds,components=expected[stage];assert r['kind']=='boolean' and r['operation']==op
 children=copy.deepcopy(base['layers'][1]['cad']['bodies'])
 if stage=='overlap-subtract-B':children.reverse()
 if stage=='inside-cylinder-target-width30':children[0]['solid']['size'][0]=30;children[0]['solid']['feature']={'label':'Keep A'}
 assert r['children']==children
 base['layers'][1]['cad']['bodies']=bodies;assert canonical(base)==canonical(doc)
 suffix=f" ({s['stlIndex']})" if s['stlIndex'] else '';tri=retain(prefix+'-3d-mm'+suffix+'.stl',True);stats=measure(tri)
 assert np.max(abs(np.array(stats['bounds_mm'])-bounds))<.001 and len(stats['components'])==components
 # A96-sided radius2 cylinder20 high has <0.18mm3 discretization error; budget0.20mm3 before mesh decoding.
 tolerance=.20 if fixture=='cylinder' else .02
 assert abs(stats['signed_volume_mm3']-volume)<tolerance and all(c['signed_volume_mm3']>0 for c in stats['components'])
 rays={}
 if fixture=='gapped':
  hits=ray(tri,15.31,5.57);assert hits==([] if op=='union' else [0,10]);rays['gap']=hits
 if fixture=='cylinder':
  assert ray(tri,10.31,10.57)==[];assert ray(tri,5.31,5.57)==[0,20];rays={'hole':[],'wall':[0,20]};assert stats['components'][0]['euler']==0
 results[stage]=dict(mesh=stats,analytic_volume_mm3=volume,absolute_volume_tolerance_mm3=tolerance,rays=rays)
assert canonical(docs[6])==canonical(docs[0])
assert canonical(docs[9])==canonical(docs[10])==canonical(json.loads((fixtures/'gapped.retropaint').read_text()))
assert canonical(docs[11])==canonical(docs[12])==canonical(docs[14]) and canonical(docs[13])==canonical(docs[15])
assert 'no solid'in ui['emptyIntersection']['status'] and ui['emptyIntersection']['pieces']=='2 pieces'
f=ui['failedRebuild'];assert 'no solid'in f['status'] and f['pieces']=='1 piece' and f['editorOpen'] and [x['value'] for x in f['fields'] if 'Size'in x['id']]==['1']*3
assert len(ui['reopened'])==9 and all('Keep A'in s['tree'] and s['pieces']=='1 piece' for s in ui['reopened'])
report=dict(status='Pass',all_four_operations_analytic_bounds_volume=True,reversed_subtraction_target_preserved=True,gapped_union_two_components_2000_vs_hull_one_component_3000=True,real_cylinder_through_hole_rays=True,source_children_exact_in_every_result=True,unrelated_far_layer_and_original_paint_exact=True,empty_intersection_atomic=True,failed_nested_rebuild_keeps_final_and_draft=True,corrected_nested_edit_single_undo_redo_exact=True,all_nine_actual_projects_reopened_with_source_tree=True,meshes=results,hashes=hashes)
(out/'boolean195-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
