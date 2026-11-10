"""Exact transformed asymmetric vertices and independently decoded placement outputs."""
from pathlib import Path
import copy,hashlib,itertools,json
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};metrics={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def document(name):return json.loads(retain(name))
base=document('mouse-audit-placement175-fixed.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l);body=base['layers'][index]['cad']['bodies'][0]
assert body['position']==[-13,8,-7] and body['rotation']==[20,30,40] and body['scale']==[1.5,.75,2]
local=np.vstack([np.array([[-10,-5,-5],[10,-5,-5],[-10,-5,25],[-10,5,-5],[10,5,-5],[-10,5,25]]),np.array(list(itertools.product([-2,2],repeat=3)))+[15,8,22]])
x,y,z=np.deg2rad([20,30,40]);cx,sx,cy,sy,cz,sz=np.cos(x),np.sin(x),np.cos(y),np.sin(y),np.cos(z),np.sin(z)
rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]);rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
vertices=(local*[1.5,.75,2])@(rz@ry@rx).T+[-13,8,-7];low,high=vertices.min(axis=0),vertices.max(axis=0)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
for i,(stage,delta) in enumerate([('drop',np.array([0,0,-low[2]])),('centre',np.array([-(low[0]+high[0])/2,-(low[1]+high[1])/2,-low[2]]))]):
 project=document(f'mouse-audit-placement175-fixed ({i+1}).retropaint');expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies'][0]['position']=(np.array([-13,8,-7])+delta).tolist()
 actualbody=project['layers'][index]['cad']['bodies'][0];assert np.allclose(actualbody['position'],expected['layers'][index]['cad']['bodies'][0]['position'],atol=.000002)
 expected['layers'][index]['cad']['bodies'][0]['position']=actualbody['position'];assert canonical(project)==canonical(expected)
 suffix=f' ({i})' if i else '';tri=read_binary(retain('mouse-audit-placement175-fixed-3d-mm'+suffix+'.stl'));stats=measure(tri);actual=np.unique(tri.reshape(-1,3),axis=0)
 assert len(actual)==14 and np.min(np.linalg.norm(actual[:,None]-(vertices+delta)[None,:],axis=2),axis=1).max()<.000005
 assert abs(stats['bounds_mm'][0][2])<.000005 and abs(stats['signed_volume_mm3']-6894)<.003
 if stage=='centre':assert np.max(np.abs(np.array(stats['bounds_mm']).sum(axis=0)[:2]))<.000005
 metrics[stage]=stats
restored=document('mouse-audit-placement175-fixed (3).retropaint');assert canonical(restored)==canonical(base)
old=read_binary(retain('mouse-audit-placement175-3d-mm (1).stl'));assert measure(old)['bounds_mm'][0][2]==5.25
report=dict(status='Pass',bug_before_minimum_z_mm=5.25,after_minimum_z_mm=0,centres_true_world_bounds=True,unchanged_rotation_scale_and_dimensions=True,other_source_and_paint_exact=True,two_undos_restore_exact_source=True,meshes=metrics,hashes=hashes)
(out/'placement175-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
