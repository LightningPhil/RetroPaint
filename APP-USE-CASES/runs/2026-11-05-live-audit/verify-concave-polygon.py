"""Native crossing regression and independently sectioned six-corner concave L extrusion."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name,mesh=False):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return read_binary(raw) if mesh else json.loads(raw)
bad_doc=retain('mouse-audit-polygon192 (1).retropaint');bad=retain('mouse-audit-polygon192-3d-mm.stl',True);edges={}
for triangle in bad:
 for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
  edge=tuple(sorted([tuple(a),tuple(b)]));edges[edge]=edges.get(edge,0)+1
nonmanifold=[dict(edge=edge,faces=count) for edge,count in edges.items() if count!=2];assert len(nonmanifold)==1 and nonmanifold[0]['faces']==4
prefix='mouse-audit-polygon192-fixed';base=retain(prefix+'.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
assert canonical(retain(prefix+' (1).retropaint'))==canonical(base);doc=retain(prefix+' (2).retropaint');bodies=doc['layers'][index]['cad']['bodies'];assert len(bodies)==1;body=bodies[0];points=np.array([[0,0],[30,0],[30,10],[10,10],[10,30],[0,30]]);assert np.array_equal(body['solid']['points'],points) and body['solid']['feature']['sketch']=='polygon' and body['solid']['height']==12 and body['solid']['taper']==1 and body['solid']['twist']==0 and body['position']==body['rotation']==[0,0,0] and body['scale']==[1,1,1]
expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies']=bodies;assert canonical(doc)==canonical(expected) and canonical(retain(prefix+' (3).retropaint'))==canonical(doc) and canonical(retain(prefix+' (4).retropaint'))==canonical(base)
tri=retain(prefix+'-3d-mm.stl',True);stats=measure(tri);wanted=np.array([[x,y,z] for z in [0,12] for x,y in points]);actual=np.unique(tri.reshape(-1,3),axis=0);assert len(actual)==12 and np.min(np.linalg.norm(actual[:,None]-wanted[None,:],axis=2),axis=1).max()==0 and stats['triangles']==20 and stats['signed_volume_mm3']==6000 and len(stats['components'])==1 and stats['components'][0]['euler']==2
def ray(x,y):
 hits=[]
 for a,b,c in tri:
  den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-9:continue
  u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den;v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
  if u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7:hits.append(round(u*a[2]+v*b[2]+(1-u-v)*c[2],6))
 return sorted(set(hits))
rays={}
for point,wanted in [((20.31,20.57),[]),((5.31,20.57),[0,12]),((20.31,5.57),[0,12])]:assert ray(*point)==wanted;rays[str(point)]=wanted
ui=json.loads((out/'polygon192-ui.json').read_text(encoding='utf-8'));assert 'crosses or touches' in ui['fixedCrossing']['status'] and ui['fixedCrossing']['pieces']=='0 pieces' and 'crosses or touches' in ui['fixedWithExisting']['status'] and ui['fixedWithExisting']['pieces']=='1 piece';assert all(s['pieces']=='0 pieces' for s in ui['invalid'][:2])
report=dict(status='Pass',confirmed_before_false_closed_edge=nonmanifold,after_crossing_rejection_atomic=True,existing_valid_piece_preserved=True,ordered_six_points_close_once=True,concave_area_mm2=500,material_volume_mm3=6000,closed_outward_euler=2,concavity_and_legs_rays=rays,too_few_and_collinear_native_fail_safely=True,one_undo_removes_only_valid_creation=True,all_original_paint_and_source_exact=True,hashes=hashes)
(out/'polygon192-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
