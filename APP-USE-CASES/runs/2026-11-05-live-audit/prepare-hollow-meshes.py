"""Independent nested STL shells:1000-216+8+64=856 cubic millimetres."""
from pathlib import Path
import hashlib,json,random,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures/hollow173';out.mkdir(exist_ok=True)
faces=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
def box(edge,centre,inward=False):
    h=edge/2;v=np.array([[-h,-h,-h],[h,-h,-h],[h,h,-h],[-h,h,-h],[-h,-h,h],[h,-h,h],[h,h,h],[-h,h,h]])+centre
    return [v[list(f[::-1] if inward else f)] for f in faces]
components=[dict(name='outer',edge=10,centre=[0,0,5],signed_volume=1000),dict(name='cavity',edge=6,centre=[0,0,5],signed_volume=-216),dict(name='island',edge=2,centre=[0,0,5],signed_volume=8),dict(name='separate',edge=4,centre=[12,3,2],signed_volume=64)];canonical=[t for c in components for t in box(c['edge'],c['centre'],c['signed_volume']<0)];variants={'canonical':canonical,'reversed-all':[t[::-1] for t in canonical],'one-face-reversed':[canonical[0][::-1],*canonical[1:]],'all-components-outward':[t for c in components for t in box(c['edge'],c['centre'])]};permuted=canonical.copy();random.Random(20261107).shuffle(permuted);variants['permuted']=permuted;hashes={}
def normal(t):
    n=np.cross(t[1]-t[0],t[2]-t[0]);return n/np.linalg.norm(n)
for name,triangles in variants.items():
    raw=b'RetroPaint independent HOLLOW173 fixture'.ljust(80,b'\0')+struct.pack('<I',len(triangles))+b''.join(struct.pack('<12fH',*normal(t),*t.ravel(),0) for t in triangles);p=out/(name+'.stl');p.write_bytes(raw);hashes[p.name]=hashlib.sha256(raw).hexdigest()
text='solid hollow173\n'+''.join(' facet normal '+' '.join(map(str,normal(t)))+'\n  outer loop\n'+''.join('   vertex '+' '.join(map(str,v))+'\n' for v in t)+'  endloop\n endfacet\n' for t in canonical)+'endsolid hollow173\n';p=out/'canonical-ascii.stl';p.write_text(text,encoding='ascii');hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest();manifest=dict(description=__doc__,components=components,net_material_volume_mm3=856,triangles=48,independent_encoder='Explicit cube vertices and oriented face table; standard struct binary STL and text ASCII STL. No application importer/exporter used.',hashes=hashes);(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
