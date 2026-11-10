"""Independent binary STL and saved-recipe checks for exact fixed-plane pulls."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads'
hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(retain('mouse-audit-join-'+stem+'.retropaint'))
reports=[]
for variant,height,z in [('positive30',30,[0,30]),('negative10',-10,[-10,20])]:
    project=doc(variant)
    body=project['layers'][1]['cad']['bodies'][0]
    solid=body['solid'];cube,tool=solid['children']
    assert solid['operation']=='union' and cube['position']==[0,0,10]
    assert cube['solid']['size']==[20,20,20] and cube['scale']==[1,1,1]
    extrude=tool['solid']
    assert extrude['height']==height and extrude['plane']['origin']==[0,0,0]
    assert not extrude.get('feature',{}).get('attachment')
    assert extrude['points']==[[-5,-5],[5,-5],[5,5],[-5,5]]
    data=retain('mouse-audit-join-'+variant+'-3d-mm.stl');count=struct.unpack_from('<I',data,80)[0]
    assert len(data)==84+count*50
    triangles=[];edges=Counter();direction=Counter();volume=0
    for i in range(count):
        values=struct.unpack_from('<12f',data,84+i*50)
        a,b,c=[tuple(values[j:j+3]) for j in [3,6,9]]
        triangles.append((a,b,c))
        for start,end in [(a,b),(b,c),(c,a)]:
            edge=tuple(sorted([start,end]));edges[edge]+=1;direction[edge]+=1 if start<end else -1
        volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
    assert all(n==2 for n in edges.values()) and not any(direction.values())
    bounds=[[min(p[j] for t in triangles for p in t),max(p[j] for t in triangles for p in t)] for j in range(3)]
    assert bounds==[[-10,10],[-10,10],z] and abs(volume-9000)<.02
    reports.append({'variant':variant,'entered_pull_mm':height,'bounds_mm':bounds,'volume_mm3':volume,'closed_outward':True,'triangles':count})
assert doc('negative10')==doc('negative10-reopened')
report={'pulls':reports,'native_negative_project_roundtrip_exact':True,'sha256':hashes}
(out/'fixed-pull-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
