"""Independent check of the native measured tracing journey."""
from collections import Counter
import hashlib,json,math,struct
from pathlib import Path
root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'; downloads=Path.home()/'Downloads'; hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(suffix=''):return json.loads(retain('mouse-audit-trace-plate'+suffix+'.retropaint'))
source=doc(); assert source==doc('-reopened')
layers=source['layers']; guide=next(x for x in layers if x['name']=='Backdrop')
assert not guide['visible']
cad=next(x['cad'] for x in layers if x['name']=='Trace plate')
assert len(cad['bodies'])==1 and cad['view']['projection']=='orthographic'
data=retain('mouse-audit-trace-plate-3d-mm.stl');count=struct.unpack_from('<I',data,80)[0]
assert len(data)==84+50*count
edges=Counter();direction=Counter();points=[];volume=0
for i in range(count):
    v=struct.unpack_from('<12f',data,84+i*50);a,b,c=[tuple(v[j:j+3]) for j in [3,6,9]]
    points.extend([a,b,c])
    volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
    for start,end in [(a,b),(b,c),(c,a)]:
        edge=tuple(sorted([start,end]));edges[edge]+=1;direction[edge]+=1 if start<end else -1
assert all(n==2 for n in edges.values()) and not any(direction.values())
bounds=[[min(p[j] for p in points),max(p[j] for p in points)] for j in range(3)]
assert bounds==[[-10,10],[-5,5],[0,5]]
expected=1000-20*math.pi
# The round hole is polygonal in STL; the discrepancy must be under 0.1 mm³.
assert abs(volume-expected)<.1
report={'native_project_roundtrip_exact':True,'guide_hidden':True,
        'explicit_guide_reference_mm':20,'bounds_mm':bounds,'hole_diameter_mm':4,
        'triangles':count,'closed_outward':True,'volume_mm3':volume,
        'analytic_volume_mm3':expected,'sha256':hashes}
(out/'trace-plate-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
