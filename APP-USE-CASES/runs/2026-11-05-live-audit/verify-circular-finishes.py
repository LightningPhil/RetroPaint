"""Independent analytic volumes and topology for native circular finishes."""
from collections import Counter
import copy,hashlib,json,math,struct
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(retain('mouse-audit-hole-'+name+'.retropaint'))
def body(p):return next(x for x in p['layers'] if x['name']=='Trace plate')['cad']['bodies'][0]
fillet=doc('fillet05');cancelled=doc('fillet05-reselect-cancel')
assert body(fillet)==body(cancelled)
renamed=doc('fillet05-renamed');chamfer=doc('chamfer05')
assert chamfer==doc('chamfer05-reopened')
assert body(renamed)['solid']['feature']['label']==body(chamfer)['solid']['feature']['label']
assert len(body(renamed)['solid']['feature']['label'])==60
results=[]
outer=json.loads(retain('mouse-audit-cylinder-rim-fillet1.retropaint'))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def ray(triangles,z):
    origin=(-20,.123,z);direction=(1,0,0);hits=[]
    for a,b,c in triangles:
        e1,e2=sub(b,a),sub(c,a);h=cross(direction,e2);det=dot(e1,h)
        if abs(det)<1e-8:continue
        f=1/det;s=sub(origin,a);u=f*dot(s,h)
        if u< -1e-7 or u>1+1e-7:continue
        q=cross(s,e1);v=f*dot(direction,q)
        if v< -1e-7 or u+v>1+1e-7:continue
        t=f*dot(e2,q)
        if t>1e-7 and not any(abs(t-x)<1e-5 for x in hits):hits.append(t)
    return sorted(hits)
for label,mode in [('fillet05','fillet'),('chamfer05','chamfer'),('outer','fillet')]:
    is_outer=label=='outer'
    p=outer if is_outer else fillet if mode=='fillet' else chamfer
    s=(next(x for x in p['layers'] if x['name']=='Cylinder rim')['cad']['bodies'][0] if is_outer else body(p))['solid']
    assert s['kind']=='finish' and s['mode']==mode and s['size']==(1 if is_outer else .5)
    assert len(s['edges'])==1
    edge=s['edges'][0]
    assert edge['curve']=='CIRCLE' and edge['closed'] and edge['center']==[.5,.5,1]
    assert edge['direction']==[0,0,1]
    data=retain('mouse-audit-cylinder-rim-fillet1-3d-mm.stl' if is_outer else 'mouse-audit-hole-'+label+'-3d-mm.stl')
    count=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*count
    edges=Counter();directions=Counter();volume=0;points=[];triangles=[]
    for i in range(count):
        values=struct.unpack_from('<12f',data,84+i*50)
        a,b,c=[tuple(values[j:j+3]) for j in [3,6,9]];points.extend([a,b,c]);triangles.append((a,b,c))
        volume+=sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
        for start,end in [(a,b),(b,c),(c,a)]:
            edge=tuple(sorted([start,end]));edges[edge]+=1;directions[edge]+=1 if start<end else -1
    assert all(n==2 for n in edges.values()) and not any(directions.values())
    bounds=[[min(p[j] for p in points),max(p[j] for p in points)] for j in range(3)]
    expected_bounds=[[-10,10],[-10,10],[0,20]] if is_outer else [[-10,10],[-5,5],[0,5]]
    assert all(abs(x-y)<.002 for a,b in zip(bounds,expected_bounds) for x,y in zip(a,b))
    radius,size=(10,1) if is_outer else (2,.5)
    removed=math.pi*(2*radius*size**2+5/3*size**3-math.pi/2*(radius+size)*size**2) if mode=='fillet' else math.pi*(radius*size**2+size**3/3)
    if is_outer:
        removed=math.pi*((2*radius*size-size**2)*size-2/3*size**3-(radius-size)*math.pi*size**2/2)
        analytic=2000*math.pi-removed
        top,bottom=ray(triangles,19.9),ray(triangles,.1)
        assert len(top)==len(bottom)==2
        assert abs(20-top[0]-math.sqrt((9+math.sqrt(.19))**2-.123**2))<.01
        assert abs(20-bottom[0]-math.sqrt(100-.123**2))<.01
    else:
        analytic=1000-20*math.pi-removed
        top,bottom=ray(triangles,4.9),ray(triangles,.1)
        assert len(top)==len(bottom)==4
        top_radius=2.2 if mode=='fillet' else 2.4
        assert abs(20-top[1]-math.sqrt(top_radius**2-.123**2))<.01
        assert abs(20-bottom[1]-math.sqrt(4-.123**2))<.01
    # The outer-cylinder BREP is tessellated around its full 20 mm circumference.
    # Its polygonal approximation must stay within 0.02%; smaller hole finishes
    # use the tighter absolute oracle established above.
    assert abs(volume-analytic)<(analytic*.0002 if is_outer else .03)
    results.append({'specimen':'outer cylinder rim' if is_outer else 'hole entrance','mode':mode,'radius_or_setback_mm':size,'triangles':count,
                    'closed_outward':True,'volume_mm3':volume,'analytic_volume_mm3':analytic,
                    'bounds_mm':bounds,'top_finish_and_unchanged_bottom_cross_sections_verified':True})
report={'original_edge_reselection_cancel_body_exact':True,
        'named_feature_native_reopen_whole_project_exact':True,
        'long_name_stored_length':60,'hole_entrance_finishes':results,'sha256':hashes}
(out/'circular-finish-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
