"""Independent rotated vertex set, world bounds, volume, Undo and invalid inputs."""
from pathlib import Path
import copy,hashlib,itertools,json,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(stage):
    name=f'mouse-audit-solid163-transform168-{stage}.retropaint';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
docs={stage:load(stage) for stage in ['applied','undone','redone','after-invalid']};base=json.loads((downloads/'mouse-audit-solid157-cube-baseline.retropaint').read_text());index=next(i for i,l in enumerate(base['layers']) if 'cad' in l)
def canonical(d):
    d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
assert canonical(docs['undone'])==canonical(base);expected=copy.deepcopy(base);body=expected['layers'][index]['cad']['bodies'][0];body['position']=[-12.5,4,10];body['rotation']=[0,0,30];assert all(canonical(docs[n])==canonical(expected) for n in ['applied','redone','after-invalid'])
name='mouse-audit-solid163-transform168-redone-3d-mm.stl';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();count=struct.unpack_from('<I',raw,80)[0];assert count==12 and len(raw)==684;tri=np.array([struct.unpack_from('<12fH',raw,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3);theta=np.pi/6;rotation=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]]);vertices=np.array(list(itertools.product([-10,10],repeat=3)))@rotation.T+[-12.5,4,10];actual_vertices=np.unique(tri.reshape(-1,3),axis=0);assert len(actual_vertices)==8 and np.all(np.min(np.linalg.norm(actual_vertices[:,None,:]-vertices[None,:,:],axis=2),axis=1)<.000002);volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert abs(volume-8000)<.002
ui=json.loads((out/'solid168-ui.json').read_text());assert all('must be between' in r['status'] for r in ui['invalid']);report=dict(status='Pass',position_mm=[-12.5,4,10],rotation_degrees=[0,0,30],local_dimensions_mm=[20,20,20],world_bounds_mm=[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()],signed_volume_mm3=volume,rotated_vertex_set_matches_independent_matrix=True,undo_redo_and_invalid_source_exact=True,hashes=hashes);(out/'solid168-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
