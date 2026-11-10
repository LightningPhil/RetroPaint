"""Recheck authentic historical downloads against current native migrations."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];old=root/'APP-USE-CASES/runs/2026-10-19-full-audit'
out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
manifest=json.loads((old/'legacy/producer-manifest.json').read_text())
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def pixels(data):return Image.open(io.BytesIO(data)).convert('RGBA')
def subset(a,b,path=''):
    if isinstance(a,dict):
        for k,v in a.items():
            if not path and k=='version':continue
            assert k in b,path+'/'+k
            subset(v,b[k],path+'/'+k)
    elif isinstance(a,list):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):subset(x,y,path+'/'+str(i))
    elif isinstance(a,str) and a.startswith('data:image/'):
        x=pixels(base64.b64decode(a.split(',')[1]));y=pixels(base64.b64decode(b.split(',')[1]))
        assert x.size==y.size,path
        if version==9 and path=='/layers/1/image':
            assert ImageChops.difference(x,y).getextrema()==((0,1),(0,0),(0,0),(0,0))
            assert sum(p!=q for p,q in zip(x.get_flattened_data(),y.get_flattened_data()))==3
        else:assert x.tobytes()==y.tobytes(),path
    else:assert a==b,path
results=[]
for producer in manifest['producers']:
    version=producer['version'];source=(old/producer['fixture']).read_bytes()
    assert hashlib.sha256(source).hexdigest()==producer['fixture_sha256']
    original=json.loads(source)
    upgraded=json.loads(retain(f'mouse-audit-legacy-v{version}-upgraded.retropaint'))
    reopened=json.loads(retain(f'mouse-audit-legacy-v{version}-reopened.retropaint'))
    assert upgraded==reopened
    subset(original,upgraded)
    actual=pixels(retain(f'mouse-audit-legacy-v{version}-upgraded.png'))
    reference=Image.open(old/f'evidence/LEGACY-v{version}-before.png').convert('RGBA')
    assert actual.size==reference.size
    if version==9:
        assert ImageChops.difference(actual,reference).getextrema()==((0,1),(0,0),(0,0),(0,0))
        assert sum(p!=q for p,q in zip(actual.get_flattened_data(),reference.get_flattened_data()))==3
    else:assert actual.tobytes()==reference.tobytes()
    results.append({'version':version,'producing_revision':producer['producing_revision'],
                    'authentic_fixture_sha256_verified':True,'original_non_raster_fields_retained':True,
                    'current_native_roundtrip_exact':True,'historical_render_dimensions':list(actual.size),
                    'historical_render_pixel_exact':version!=9,
                    'v9_canvas_decode_rounding':{'changed_pixels':3,'max_red_difference':1,'alpha_exact':True} if version==9 else None})
data=retain('mouse-audit-legacy-v9-reopened-3d-mm.stl')
assert data==(old/'evidence/LEGACY-v9-original.stl').read_bytes()
report={'versions':results,'v9_stl_byte_exact_to_historical_cube':True,
        'unavailable_authentic_versions':manifest['unlocated_producing_versions'],'sha256':hashes}
(out/'legacy-import-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
