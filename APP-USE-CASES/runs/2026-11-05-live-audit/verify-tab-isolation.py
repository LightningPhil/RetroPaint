"""Check actual Chrome Duplicate, independent edits and per-tab resumed files."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def doc(name):
    name='mouse-audit-tab-'+name+'.retropaint';data=(downloads/name).read_bytes()
    (out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
original=doc('original-before-refresh');duplicate=doc('duplicate-before-refresh')
assert original!=duplicate
assert original==doc('original-after-refresh') and duplicate==doc('duplicate-after-refresh')
for i in [0,1,3]:assert original['layers'][i]==duplicate['layers'][i]
def raster(d):
    layer=next(x for x in d['layers'] if x['name']=='Character')
    assert layer['opacity']==.5
    return Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))).convert('RGBA')
a,b=raster(original),raster(duplicate)
assert a.getpixel((320,450))==(30,136,229,255) and a.getpixel((720,450))==(0,0,0,0)
assert b.getpixel((320,450))==(0,0,0,0) and b.getpixel((720,450))==(67,160,71,255)
report={'actual_chrome_duplicate_command':True,'different_settled_edits':True,
        'both_native_refresh_resume_files_whole_project_exact':True,
        'neighbouring_layers_and_half_opacity_preserved':True,
        'recovered_pictures_remain_distinct':True,'sha256':hashes}
(out/'tab-isolation-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
