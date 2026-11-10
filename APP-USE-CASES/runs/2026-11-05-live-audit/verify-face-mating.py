"""Native face-pair rejections, independent opposing normals/contact and actual STL."""
from pathlib import Path
import copy,hashlib,itertools,json
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name,mesh=False):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return read_binary(raw) if mesh else json.loads(raw)
base=retain('mouse-audit-mate179.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
assert canonical(retain('mouse-audit-mate179 (1).retropaint'))==canonical(base)
mated=retain('mouse-audit-mate179 (2).retropaint');b=mated['layers'][index]['cad']['bodies'][0];assert np.allclose(b['position'],[-30,0,30])
x,y,z=np.deg2rad(b['rotation']);rx=np.array([[1,0,0],[0,np.cos(x),-np.sin(x)],[0,np.sin(x),np.cos(x)]]);ry=np.array([[np.cos(y),0,np.sin(y)],[0,1,0],[-np.sin(y),0,np.cos(y)]]);rz=np.array([[np.cos(z),-np.sin(z),0],[np.sin(z),np.cos(z),0],[0,0,1]]);rotation=rz@ry@rx
assert np.allclose(rotation@[0,0,1],[0,0,-1]);assert np.allclose(rotation@[0,0,10]+b['position'],[-30,0,20])
expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies'][0].update(position=b['position'],rotation=b['rotation']);assert canonical(expected)==canonical(mated)
tri=retain('mouse-audit-mate179-3d-mm.stl',True);stats=measure(tri);vertices=np.array(list(itertools.product([-10,10],repeat=3)))@rotation.T+b['position'];actual=np.unique(tri.reshape(-1,3),axis=0);assert len(actual)==8 and np.min(np.linalg.norm(actual[:,None]-vertices[None,:],axis=2),axis=1).max()<.000001;assert stats['signed_volume_mm3']==8000 and stats['bounds_mm']==[[-40,-10,20],[-20,10,40]]
assert canonical(retain('mouse-audit-mate179 (3).retropaint'))==canonical(base)
ui=json.loads((out/'mate179-ui.json').read_text(encoding='utf-8'));assert all(word in probe['status'] for word,probe in zip(['selected moving piece first','flat face','unlocked','target piece','different piece'],ui['probes']))
report=dict(status='Pass',moving_top_normal_after=[0,0,-1],target_top_normal=[0,0,1],shared_face_centre_mm=[-30,0,20],moving_bounds_mm=stats['bounds_mm'],signed_volume_mm3=8000,wrong_first_curved_locked_identical_rejections_source_exact=True,target_and_other_source_exact=True,one_undo_exact=True,hashes=hashes)
(out/'mate179-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
