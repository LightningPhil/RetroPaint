"""Unique copy identity, scoped nested-history edit, transform, mesh and Undo."""
from pathlib import Path
import copy,hashlib,json,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(stage):
    name=f'mouse-audit-solid162-{stage}.retropaint';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
docs={n:load(n) for n in ['nested-baseline','copy-transformed','copy-child-edited','child-undone','all-undone','copy-resized-confirmed','resize-undone']};base=docs['nested-baseline'];index=next(i for i,l in enumerate(base['layers']) if 'cad' in l);original=base['layers'][index]['cad']['bodies'][0]
for d in docs.values():assert d['layers'][index]['cad']['bodies'][0]==original
moved=docs['copy-transformed']['layers'][index]['cad']['bodies'][1];assert moved['id']!=original['id'] and moved['position']==[80,-20,5] and moved['scale']==[1,1,1];expected=copy.deepcopy(original);expected.update(id=moved['id'],name=original['name']+' copy',position=[80,-20,5]);assert moved==expected
expected=copy.deepcopy(moved);child=expected['solid']['source']['solid']['children'][0]['solid'];child['size'][0]=22;child['feature']={'label':'Shell cube'};assert docs['copy-child-edited']['layers'][index]['cad']['bodies'][1]==expected
expected=copy.deepcopy(moved);expected['scale']=[2,1,1];assert docs['copy-resized-confirmed']['layers'][index]['cad']['bodies'][1]==expected
def without_preview(d):
    d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
for a,b in [('copy-transformed','child-undone'),('nested-baseline','all-undone'),('copy-transformed','resize-undone')]:assert without_preview(docs[a])==without_preview(docs[b])
for d in docs.values():
    assert all(l==base['layers'][i] for i,l in enumerate(d['layers']) if i!=index)
name='mouse-audit-solid162-mesh-confirmed-3d-mm.stl';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();count=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*count;tri=np.array([struct.unpack_from('<12fH',raw,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3);lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert np.allclose(lo,[60,-30,5],atol=.001) and np.allclose(hi,[130,-10,25],atol=.001) and abs(volume-2*6688.252)<3
report=dict(status='Pass',copy_root_identity_unique=True,original_body_and_other_paint_layers_exact=True,nested_child_history_edit_scoped_to_copy=True,undo_restores_source_fields=True,mesh_bounds_mm=[lo.tolist(),hi.tolist()],mesh_volume_mm3=volume,hashes=hashes,notes='Internal retained-source IDs are scoped within each copied body; native child Preview/Apply succeeds and leaves the original tree exact. CAD cached render PNGs regenerate across edits/Undo and are excluded from source-field identity. Initial resize attempt did not commit; confirmed replay70mm and independent mesh retained.');(out/'solid162-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
