"""Check one targeted native edit per reopened scene kind and atomic rejection."""
import copy,hashlib,io,json,math
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def doc(name):
    name='mouse-audit-vector-'+name+'.retropaint';data=(downloads/name).read_bytes()
    (out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('detail-transformed');reopened=doc('mixed-reopened')
# Import supplies a default liveSize even for a static PNG, where it has no
# rendering role. The source bitmap, dimensions, identity and matrix stay exact.
canonical=copy.deepcopy(before)
canonical['layers'][0]['objects'][9]['liveSize']=reopened['layers'][0]['objects'][9]['liveSize']
assert canonical==reopened
before=reopened
stages=[('path',0),('stamp',2),('spiro',3),('text',6),('raster',9)];results=[]
for name,index in stages:
    after=doc('roundtrip-'+name);a,b=copy.deepcopy(before),copy.deepcopy(after)
    old=a['layers'][0]['objects'][index];new=b['layers'][0]['objects'][index]
    assert old['id']==new['id'] and old['kind']==new['kind'] and old['matrix']!=new['matrix']
    assert [o['id'] for o in a['layers'][0]['objects']]==[o['id'] for o in b['layers'][0]['objects']]
    matrix=new['matrix'];old['matrix']=matrix
    assert a==b,(name,'neighbour/source change')
    if name=='path':assert matrix==[1,0,0,1,100,100]
    if name=='stamp':assert abs(matrix[0]-100/82)<1e-10 and abs(matrix[3]-100/82)<1e-10
    if name=='spiro':assert abs(matrix[0]-.35*math.cos(math.pi/6))<1e-10 and abs(matrix[1]-.175)<1e-10
    if name=='text':assert all(abs(x-y)<1e-8 for x,y in zip(matrix,[1.5,0,0,1.5,120,400]))
    if name=='raster':assert all(abs(x-y)<1e-8 for x,y in zip(matrix,[0,1,-1,0,764,400]))
    results.append({'stage':name,'object_id':new['id'],'neighbours_and_original_definitions_exact':True})
    before=after
assert doc('malformed-preserved')==before
renders=[]
for name in ['detail-transformed','mixed-reopened']:
    name='mouse-audit-vector-'+name+'.png';data=(downloads/name).read_bytes()
    (out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
    renders.append(Image.open(io.BytesIO(data)).convert('RGBA'))
assert renders[0].size==renders[1].size==(960,640) and renders[0].tobytes()==renders[1].tobytes()
report={'fresh_page_native_mixed_reopen_exact_except_unused_static_liveSize_default':True,'objects':10,
        'fresh_page_composition_pixel_exact':True,'targeted_edits':results,
        'singular_external_object_rejected_whole_project_exact':True,'sha256':hashes}
(out/'vector-roundtrip-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
