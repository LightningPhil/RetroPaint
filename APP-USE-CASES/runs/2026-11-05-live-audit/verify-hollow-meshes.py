"""Independent nested-shell repair, reflection and native STL round-trip oracle."""
from pathlib import Path
import hashlib,json
import numpy as np
from stl_oracle import read_binary,measure

root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads'
prefix='mouse-audit-hollow173-canonical'
labels=['canonical','mirrorX','mirrorX-reimport','reversed-all','one-face-reversed','all-components-outward','permuted','canonical-ascii']
hashes={};metrics={};baseline=None
def retain(name):
    raw=(downloads/name).read_bytes();(out/name).write_bytes(raw)
    hashes[name]=hashlib.sha256(raw).hexdigest()
    return raw
for i,label in enumerate(labels):
    suffix=f' ({i})' if i else ''
    project=json.loads(retain(prefix+suffix+'.retropaint'))
    bodies=[b for layer in project['layers'] if 'cad' in layer for b in layer['cad']['bodies']]
    assert len(bodies)==1
    assert bodies[0]['scale']==([-1,1,1] if label=='mirrorX' else [1,1,1])
    tri=read_binary(retain(prefix+'-3d-mm'+suffix+'.stl'))
    stats=measure(tri)
    assert stats['triangles']==48 and stats['signed_volume_mm3']==856
    assert sorted(c['signed_volume_mm3'] for c in stats['components'])==[-216,8,64,1000]
    assert all(c['euler']==2 and c['triangles']==12 for c in stats['components'])
    vertices=np.unique(tri.reshape(-1,3),axis=0)
    if baseline is None:baseline=vertices
    expected=baseline*np.array([-1,1,1] if label in ['mirrorX','mirrorX-reimport'] else [1,1,1])
    assert len(vertices)==len(expected)==32
    assert np.min(np.linalg.norm(vertices[:,None]-expected[None,:],axis=2),axis=1).max()==0
    metrics[label]=stats
report=dict(status='Pass',material_volume_mm3=856,component_volumes_mm3=[1000,-216,8,64],
    all_variants_closed_and_consistently_oriented=True,cavity_and_island_preserved=True,
    mirror_negative_determinant_and_reimport_preserved=True,source_projects_and_meshes=metrics,hashes=hashes)
(out/'hollow173-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['source_projects_and_meshes','hashes']},indent=2))
