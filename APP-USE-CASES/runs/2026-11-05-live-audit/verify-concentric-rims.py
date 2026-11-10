"""Independent similar-radius rim identity, dimensions and topology oracle."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-rims209';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(6)]
def body(d):return next(l['cad']['bodies'][0] for l in d['layers'] if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
assert canonical(docs[1])==canonical(docs[3]) and canonical(docs[2])==canonical(docs[4])==canonical(docs[5])
for d in docs:
 expected=copy.deepcopy(docs[0]);next(l for l in expected['layers'] if 'cad'in l)['cad']['bodies']=[body(d)];assert canonical(expected)==canonical(d)
for i,wall in [(1,.1),(2,.12)]:
 s=body(docs[i])['solid'];assert s['kind']=='finish' and s['mode']=='chamfer' and s['size']==.05 and len(s['edges'])==1
 e=s['edges'][0];assert e['curve']=='CIRCLE' and e['closed'] and e['center']==[.5,.5,1] and e['direction']==[0,0,1] and e['rank']==0 and e['groupSize']==2
 assert s['source']['solid']['shape']=='tube' and s['source']['solid']['size']==[20,20,10] and s['source']['solid']['wall']==wall and body(docs[i])['position']==[0,0,5]
assert body(docs[1])['solid']['edges']==body(docs[2])['solid']['edges']
results=[];raws=[]
for n,r in [(0,9.9),(1,9.88),(2,9.88)]:
 raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws.append(raw);tri=read_binary(raw);stats=measure(tri);volume=math.pi*(100-r*r)*10-math.pi*(r*.05**2+.05**3/3)
 assert abs(stats['signed_volume_mm3']-volume)<.1 and len(stats['components'])==1 and stats['components'][0]['euler']==0
 assert np.max(abs(np.array(stats['bounds_mm'])-[[-10,-10,0],[10,10,10]]))<.003
 rays=[]
 for z in [.025,9,9.975]:
  inner=r+max(0,z-9.95);a,b=math.sqrt(100-.123**2),math.sqrt(inner*inner-.123**2);expected=[-a,-b,b,a];actual=ray_y(tri,.123,z)
  assert len(actual)==4 and np.max(abs(np.array(actual)-expected))<.003;rays.append(dict(z=z,actual_y=actual,expected_y=expected))
 results.append(dict(index=n,mesh=stats,analytic_volume_mm3=volume,rays=rays))
assert raws[1]==raws[2]
ui=json.loads((out/'rims209-ui.json').read_text(encoding='utf-8'));assert ui['states'][0]['count'].startswith('4 edges') and ui['states'][1]['count'].startswith('1 edges')
report=dict(status='Pass',case='FEATURE-013',similar_top_radii9_9_and10_distinguished_by_rank0_group2=True,same_whole_circle_reference_survives_wall01_to012=True,outer_radius10_and_bottom_bore_unchanged=True,only_inner_top_bevel005_verified_by_independent_rays=True,closed_oriented_genus1=True,volume_within_predeclared01mm3_and_rays003mm=True,undo_redo_actual_reopen_cancel_source_exact=True,reopened_final_stl_byte_exact=True,meshes=results,hashes=hashes)
(out/'rims209-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
