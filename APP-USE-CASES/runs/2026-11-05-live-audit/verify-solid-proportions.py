"""Nonuniform initial scale, proportional/free resize, preserved anchor and Undo."""
from pathlib import Path
import copy,hashlib,json,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(stage):
    name=f'mouse-audit-solid159-{stage}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
baseline=load('nonuniform-baseline');prop=load('proportional');free=load('free');restored=load('restored-after-invalid');assert baseline==restored;index=next(i for i,l in enumerate(baseline['layers']) if 'cad' in l);body=baseline['layers'][index]['cad']['bodies'][0];assert body['solid']['size']==[20,20,20] and body['scale']==[1,.5,1.5]
metrics={}
for stage,document,scale,dimensions,volume in [('proportional',prop,[2,1,3],[40,20,60],48000),('free',free,[2,.5,1.5],[40,10,30],12000)]:
    expected=copy.deepcopy(baseline);expected['layers'][index]['cad']['bodies'][0]['scale']=scale;expected['layers'][index]['image']=document['layers'][index]['image'];assert document==expected
    name=f'mouse-audit-solid159-{stage}-3d-mm.stl';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();count=struct.unpack_from('<I',data,80)[0];assert count==12 and len(data)==684;tri=np.array([struct.unpack_from('<12fH',data,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3);bounds=tri.max(axis=(0,1))-tri.min(axis=(0,1));actual=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert np.array_equal(bounds,dimensions) and actual==volume
    metrics[stage]=dict(dimensions_mm=bounds.tolist(),signed_volume_mm3=actual)
ui=json.loads((out/'solid159-ui.json').read_text());valid=[r for r in ui['invalid'] if r['input']!=''];assert all('must be between' in r['status'] for r in valid);assert all(ui['stages'][name]['dimensions']==dims for name,dims in [('proportional',[40,20,60]),('free',[40,10,30])]);report=dict(status='Pass',nonuniform_preexisting_scale_not_compounded=True,anchor_and_other_project_fields_exact=True,undo_and_invalid_source_exact=True,invalid_inputs=[r['input'] for r in valid],metrics=metrics,hashes=hashes);(out/'solid159-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
