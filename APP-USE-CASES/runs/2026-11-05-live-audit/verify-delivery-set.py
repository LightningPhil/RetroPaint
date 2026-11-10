"""Independently decode the files delivered and reopened through native dialogs."""
import base64, copy, hashlib, io, json, struct
from collections import Counter
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads'; hashes={}
def retain(name):
    data=(downloads/name).read_bytes(); (out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest(); return data
def doc(s):return json.loads(retain('mouse-audit-'+s+'.retropaint'))
baseline=doc('cadmix-photo-reopened-undo'); delivery=doc('delivery-cadmix')
reopened=doc('delivery-project-reopened'); flat=doc('delivery-png-opened')
imported=doc('delivery-stl-opened')
assert delivery==reopened
expected=copy.deepcopy(baseline)
expected['active']=delivery['active']
expected['layers'][1]['opacity']=.5
for k in ['image','cad']:expected['layers'][2][k]=delivery['layers'][2][k]
assert expected==delivery
assert baseline['layers'][2]['cad']['bodies']==delivery['layers'][2]['cad']['bodies']
assert baseline['layers'][2]['cad']['view']!=delivery['layers'][2]['cad']['view']
def png(name):return Image.open(io.BytesIO(retain('mouse-audit-'+name+'.png'))).convert('RGBA')
a=png('delivery-cadmix');b=png('delivery-project-reopened')
assert a.size==(768,512) and a.tobytes()==b.tobytes()
assert len(flat['layers'])==1 and (flat['width'],flat['height'])==a.size
decoded=Image.open(io.BytesIO(base64.b64decode(flat['layers'][0]['image'].split(',')[1]))).convert('RGBA')
assert decoded.tobytes()==a.tobytes()
data=retain('mouse-audit-delivery-cadmix-3d-mm.stl')
count=struct.unpack_from('<I',data,80)[0]; assert len(data)==84+50*count
triangles=[];edges=Counter();directions=Counter();volume=0
for i in range(count):
    t=[struct.unpack_from('<3f',data,96+50*i+12*j) for j in range(3)]
    triangles.append(t);a,b,c=t
    volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
    for start,end in [(a,b),(b,c),(c,a)]:
        edge=tuple(sorted([start,end]));edges[edge]+=1;directions[edge]+=1 if start<end else -1
assert count==1556 and all(n==2 for n in edges.values()) and not any(directions.values())
points=[p for t in triangles for p in t]
bounds=[[min(p[j] for p in points),max(p[j] for p in points)] for j in range(3)]
assert bounds==[[-10,25],[-10,10],[0,20]] and 6680<volume<6700
# Vertical rays at non-boundary coordinates prove the floor and open cavity.
def z_hits(x,y):
    hits=[]
    for a,b,c in triangles:
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-9:continue
        u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
        if u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7:hits.append(round(u*a[2]+v*b[2]+(1-u-v)*c[2],5))
    return sorted(set(hits))
assert z_hits(.31,.57)==[0,3] and z_hits(-8.31,.57)==[0,20]
mesh=next(l for l in imported['layers'] if l['name']=='3D 2')['cad']['bodies'][0]
assert mesh['solid']['kind']=='mesh' and mesh['position']==[0,0,0] and mesh['scale']==[1,1,1]
p=mesh['solid']['positions'];indices=mesh['solid']['indices']
loaded=[[tuple(p[k*3:k*3+3]) for k in indices[i:i+3]] for i in range(0,len(indices),3)]
def canonical(ts):return Counter(tuple(sorted(t)) for t in ts)
assert canonical(loaded)==canonical(triangles)
report={'native_project_reopened_whole_document_exact':True,
        'photo_recipe_source_crop_text_and_solid_preserved':True,
        'guide_opacity':.5,'native_orbit_zoom_fit_pin_changed_only_camera':True,
        'native_png_reexport_and_single_image_reopen_pixel_exact':[768,512],
        'scoped_stl':{'triangles':count,'closed_outward':True,'bounds_mm':bounds,'volume_mm3':volume,
                      'cavity_floor_mm':3,'wall_ray_full_height_mm':20},
        'native_stl_import_triangles_exact':True,'sha256':hashes}
(out/'delivery-set-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
