"""Three negative-determinant reflections of a genuinely asymmetric two-part model."""
from pathlib import Path
import copy,hashlib,itertools,json
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-solid172-mirror-v2-baseline';hashes={};metrics={}
def retain(name):
    raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
base=json.loads(retain(prefix+'.retropaint'));index=next(i for i,l in enumerate(base['layers']) if 'cad' in l);body=base['layers'][index]['cad']['bodies'][0];assert body['solid']['kind']=='boolean' and body['solid']['operation']=='union' and body['position']==[0,0,0] and body['scale']==[1,1,1];children=body['solid']['children'];cube=next(c for c in children if c['solid']['shape']=='box');wedge=next(c for c in children if c['solid']['shape']=='wedge');assert cube['position']==[15,8,22] and cube['scale']==[.2,.2,.2] and wedge['position']==[0,0,10] and wedge['scale']==[1,.5,1.5]
vertices=np.vstack([np.array([[-10,-5,-5],[10,-5,-5],[-10,-5,25],[-10,5,-5],[10,5,-5],[-10,5,25]]),np.array(list(itertools.product([-2,2],repeat=3)))+[15,8,22]])
def canonical(d):
    d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
for n,axis in [(0,None),(1,0),(2,1),(3,2)]:
    sign=np.ones(3);suffix=f' ({n})' if n else '';name=prefix+'-3d-mm'+suffix+'.stl'
    if axis is not None:
        sign[axis]=-1;d=json.loads(retain(prefix+suffix+'.retropaint'));expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies'][0]['scale']=sign.tolist();assert canonical(d)==canonical(expected)
    tri=read_binary(retain(name));wanted=vertices*sign;actual=np.unique(tri.reshape(-1,3),axis=0);assert len(actual)==14;assert np.min(np.linalg.norm(actual[:,None]-wanted[None,:],axis=2),axis=1).max()<.00001;stats=measure(tri);assert stats['triangles']==20 and stats['signed_volume_mm3']==3064 and sorted(c['signed_volume_mm3'] for c in stats['components'])==[64,3000] and all(c['euler']==2 for c in stats['components']);metrics['XYZ'[axis] if axis is not None else 'baseline']=stats
restored=json.loads(retain(prefix+' (4).retropaint'));assert canonical(restored)==canonical(base);report=dict(status='Pass',reflection_about_model_origin=True,all_axes_independently_distinguishable=True,negative_determinant_each_axis=True,all_components_outward_and_closed=True,unchanged_volume_mm3=3064,other_source_and_paint_fields_exact=True,undo_source_exact=True,meshes=metrics,hashes=hashes,remaining='Nested cavity mirror/reimport repair branch uses independently encoded HOLLOW173 fixture.');(out/'solid172-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['hashes','meshes']},indent=2))
