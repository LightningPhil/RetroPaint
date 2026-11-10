"""Independent whole-circle references and original-source reselection oracle."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3]; out=root/'test-results/audit-2026-11-05/mouse'; downloads=Path.home()/'Downloads'; hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def load(prefix,n):return json.loads(retain(prefix+(f' ({n})' if n else '')+'.retropaint'))
def body(d):return next(l['cad']['bodies'][0] for l in d['layers'] if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
circles=[]
for key in ['cylinder','drilled']:
 p='mouse-audit-edge207-'+key;base,d=load(p,0),load(p,1);s=body(d)['solid'];e=s['edges'][0]
 assert s['kind']=='finish' and len(s['edges'])==1 and e['curve']=='CIRCLE' and e['closed'] and np.max(abs(np.array(e['center'])-[.5,.5,1]))<1e-10 and e['direction']==[0,0,1]
 expected_source=copy.deepcopy(body(base));expected_source['position']=[0,0,0];assert s['source']==expected_source
 expected=copy.deepcopy(base);next(l for l in expected['layers'] if 'cad'in l)['cad']['bodies']=[body(d)];assert canonical(expected)==canonical(d)
 tri=read_binary(retain(p+'-3d-mm.stl'));stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==(2 if key=='cylinder' else 0)
 if key=='cylinder':
  r,c=10,1;removed=math.pi*((2*r*c-c*c)*c-2/3*c**3-(r-c)*math.pi*c*c/2);volume=2000*math.pi-removed;budget=volume*.0002;assert s['mode']=='fillet' and s['size']==1
 else:
  r,c=2,.5;volume=8000-80*math.pi-math.pi*(r*c*c+c**3/3);budget=.03;assert s['mode']=='chamfer' and s['size']==.5
 within_budget=abs(stats['signed_volume_mm3']-volume)<budget
 if key=='cylinder':assert within_budget
 else:assert not within_budget  # Retain the failed predeclared .03mm3 criterion, do not widen it.
 circles.append(dict(specimen=key,reference=e,mesh=stats,analytic_volume_mm3=volume,volume_tolerance_mm3=budget,volume_within_original_tolerance=within_budget))
cui=json.loads((out/'edge207-ui.json').read_text(encoding='utf-8'));dui=json.loads((out/'edge207-drilled-ui.json').read_text(encoding='utf-8'))
assert cui['states'][0]['count'].startswith('2 edges') and cui['states'][1]['count'].startswith('0 edges') and next(s for s in cui['states'] if s['stage']=='cylinder-upper-rim-tap')['count'].startswith('1 edges')
assert dui['states'][0]['count'].startswith('14 edges') and dui['states'][1]['count'].startswith('1 edges')
p='mouse-audit-reselect208';docs=[load(p,n) for n in range(7)];assert canonical(docs[1])==canonical(docs[2])==canonical(docs[4]) and canonical(docs[3])==canonical(docs[5])==canonical(docs[6])
for i,z in [(1,1),(3,0)]:
 s=body(docs[i])['solid'];assert s['kind']=='finish' and s['mode']=='chamfer' and s['size']==2 and np.max(abs(np.array(s['edges'][0]['center'])-[.5,1,1]))<1e-10
 inner=s['source']['solid'];assert inner['kind']=='finish' and inner['mode']=='fillet' and inner['size']==2 and inner['edges'][0]['center']==[.5,0,z]
 before=copy.deepcopy(body(docs[1]));before['solid']['source']['solid']['edges']=inner['edges'];assert body(docs[i])==before
for d in docs:
 expected=copy.deepcopy(docs[0]);next(l for l in expected['layers'] if 'cad'in l)['cad']['bodies']=[body(d)];assert canonical(expected)==canonical(d)
results=[];raws=[]
for n in range(4):
 raw=retain(p+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws.append(raw);tri=read_binary(raw);stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==2
 volume=8000-20*(4-math.pi)-40;assert abs(stats['signed_volume_mm3']-volume)<.03
 rays=[]
 for z in [.1,1,19,19.9]:
  if n<2:front=-10 if z<18 else -8-math.sqrt(4-(z-18)**2)
  else:front=-10 if z>2 else -8-math.sqrt(4-(z-2)**2)
  back=10 if z<18 else 28-z;actual=ray_y(tri,.123,z);assert len(actual)==2 and np.max(abs(np.array(actual)-[front,back]))<.01;rays.append(dict(z=z,actual_y=actual,expected_y=[front,back]))
 results.append(dict(index=n,mesh=stats,analytic_volume_mm3=volume,rays=rays))
assert raws[0]==raws[1] and raws[2]==raws[3]
ui=json.loads((out/'reselect208-ui.json').read_text(encoding='utf-8'));assert '12 selected edges' in next(s for s in ui['states'] if s['stage']=='earlier-finish-original-cube-all12')['text'] and '1 selected edges' in next(s for s in ui['states'] if s['stage']=='replacement-bottom-front-edge')['text']
report=dict(status='Partial',cases={'FEATURE-009':'Partial','FEATURE-014':'Pass'},deferred_precision_note='EDGE207 drilled entrance: volume error0.040126mm3 exceeds original0.030mm3 criterion; source whole-circle selection verified, accuracy follow-up retained',whole_circles_and_real_edge_inventory=True,smooth_cylinder_side_not_selected=True,earlier_reselection_uses_intact12_edge_cube=True,different_original_bottom_front_reference_verified=True,later_top_back_chamfer_recipe_and_real_geometry_preserved=True,cancel_source_and_stl_byte_exact=True,apply_undo_redo_actual_reopen_source_exact=True,reopened_final_stl_byte_exact=True,paint_and_unrelated_source_exact=True,circles=circles,nested_meshes=results,hashes=hashes)
(out/'edge207-reselect208-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['circles','nested_meshes','hashes']},indent=2))
