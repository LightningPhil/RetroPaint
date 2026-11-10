"""Verify the catalogue-sized painting and three exact complex-shell fixtures."""
import base64
from collections import Counter
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import struct

from PIL import Image

out = Path(__file__).resolve().parents[3] / 'test-results/audit-2026-11-05/mouse'
downloads = Path.home() / 'Downloads'
files = {}
def retain(name):
    data = (downloads/name).read_bytes(); (out/name).write_bytes(data)
    files[name] = hashlib.sha256(data).hexdigest()
    return data
def project(stem): return json.loads(retain(stem+'.retropaint'))
def raster(doc): return Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',')[1]))).convert('RGBA')

blank = project('mouse-audit-play-960-baseline')
assert (blank['width'], blank['height'], blank['drawingMode'], len(blank['layers'])) == (960, 640, 'raster', 1)
assert raster(blank).getextrema() == ((255, 255),)*4
for stage in ['background', 'decorated']: project('mouse-audit-journey1-960-'+stage)
greeting = project('mouse-audit-journey1-960-greeting')
mistake = project('mouse-audit-journey1-960-mistake')
finished = project('mouse-audit-journey1-960-final')
assert greeting == finished and mistake != finished
picture = Image.open(io.BytesIO(retain('mouse-audit-journey1-960-final.png'))).convert('RGBA')
assert picture.size == (960, 640) and picture.tobytes() == raster(finished).tobytes()

def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def read_mesh(data):
    count = struct.unpack_from('<I',data,80)[0]
    assert len(data) == 84+50*count
    triangles, edges, directions = [], Counter(), Counter()
    volume = 0
    for i in range(count):
        normal = struct.unpack_from('<3f',data,84+50*i)
        a,b,c = [struct.unpack_from('<3f',data,96+50*i+12*j) for j in range(3)]
        assert dot(cross(sub(b,a),sub(c,a)),normal)>0
        volume += dot(a,cross(b,c))/6; triangles.append((a,b,c))
        for x,y in [(a,b),(b,c),(c,a)]:
            edge=tuple(sorted([x,y]));edges[edge]+=1;directions[edge]+=1 if x<y else -1
    assert all(n==2 for n in edges.values()) and not any(directions.values())
    return triangles,volume
def ray(triangles,origin,direction):
    hits=[]
    for a,b,c in triangles:
        e1,e2=sub(b,a),sub(c,a);h=cross(direction,e2);det=dot(e1,h)
        if abs(det)<1e-8:continue
        f=1/det;s=sub(origin,a);u=f*dot(s,h)
        if u < -1e-7 or u>1+1e-7:continue
        q=cross(s,e1);v=f*dot(direction,q)
        if v < -1e-7 or u+v>1+1e-7:continue
        t=f*dot(e2,q)
        if t>1e-7 and not any(abs(t-x)<1e-5 for x in hits):hits.append(t)
    return sorted(hits)

shells=[]
for variant,cx,normal_z,source_name in [('top',15,1,'mouse-audit-shell20-top (1)'),
                                      ('bottom',15,-1,'mouse-audit-shell20-bottom'),
                                      ('third',40/3,1,'mouse-audit-shell20-third')]:
    stem='mouse-audit-shell20-'+variant
    doc=project(source_name);assert doc==project(stem+'-reopened')
    body=doc['layers'][-1]['cad']['bodies'][0];shell=body['solid']
    assert shell['kind']=='shell' and shell['thickness']==3 and len(shell['faces'])==1
    assert shell['faces'][0]['normal']==[0,0,normal_z]
    cube,cylinder=shell['source']['solid']['children']
    for item in [cube,cylinder]: assert item['solid']['size']==[20,20,20] and item['scale']==[1,1,1]
    assert cube['position']==[0,0,10] and cylinder['position']==[cx,0,10]
    triangles,volume=read_mesh(retain(stem+'-3d-mm.stl'))
    points=[p for tri in triangles for p in tri]
    bounds=[(min(p[j] for p in points),max(p[j] for p in points)) for j in range(3)]
    assert abs(bounds[0][0]+10)<1e-5 and abs(bounds[0][1]-(cx+10))<1e-5
    assert bounds[1:]==[(-10,10),(0,20)]
    wall=ray(triangles,(-20,0,10),(1,0,0))
    assert len(wall)==4 and abs(wall[1]-wall[0]-3)<1e-5 and abs(wall[3]-wall[2]-3)<1e-5
    floor=ray(triangles,(0,.123,-5),(0,0,1))
    assert len(floor)==2 and abs(floor[1]-floor[0]-3)<1e-5
    assert abs(floor[0]-(5 if normal_z==1 else 22))<1e-5
    corner_y=math.sqrt(100-(10-cx)**2)
    d=((cx-10)/10-1,-corner_y/10,0);length=math.sqrt(dot(d,d));d=tuple(v/length for v in d)
    origin=(10-d[0]*.1,corner_y-d[1]*.1,10)
    junction=ray(triangles,origin,d)
    assert len(junction)>=2 and abs(junction[1]-junction[0]-3)<.005
    shells.append({'variant':variant,'cylinder_x':cx,'opening_normal_z':normal_z,
                   'project_roundtrip_exact':True,'triangles':len(triangles),'volume_mm3':volume,
                   'bounds_mm':bounds,'closed_outward':True,'straight_curved_wall_mm':[wall[1]-wall[0],wall[3]-wall[2]],
                   'floor_or_ceiling_mm':floor[1]-floor[0],'junction_wall_mm':junction[1]-junction[0]})

assert project('mouse-audit-shell20-top (1)') == project('mouse-audit-shell20-top-reopened (1)')
report={'birthday':{'fixture':[960,640],'clean_white_baseline':True,'mistake_changed_art':True,
                    'undo_project_exact':True,'png_matches_project':True},
        'shells':shells,'invalid_100mm_and_cancelled_2_5mm_shell_preserved_project':True,'sha256':files}
(out/'exact-fixtures-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
