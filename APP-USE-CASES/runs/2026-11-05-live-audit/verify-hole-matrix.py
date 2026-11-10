"""Verify local native Black Hole hold/movement and stability after release."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(name):
    filename='mouse-audit-hole64-'+name+'.retropaint';data=(Path.home()/'Downloads'/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
before=doc('before');a=pixels(before);e=json.loads((out/'hole64-evidence.json').read_bytes());r=e['rect'];yy,xx=np.mgrid[:640,:960]
def point(p):return ((p[0]-r['x'])*960/r['width'],(p[1]-r['y'])*640/r['height'])
cx,cy=point(e['hold']);x0,y=point(e['from']);x1,_=point(e['to']);results={}
for name,later,undone in [('held','held-later','held-undone'),('held-six-seconds','six-seconds-later','six-seconds-undone'),('moved','moved-later','moved-undone')]:
    d=doc(name);b=pixels(d);changed=np.any(a!=b,axis=2);assert changed.any();assert np.all(b[:,:,3]==255)
    outside=(np.hypot(xx+.5-cx,yy+.5-cy) if name!='moved' else np.hypot(xx+.5-np.clip(xx+.5,x0,x1),yy+.5-y))>60
    assert np.array_equal(a[outside],b[outside]);assert doc(later)==d;assert doc(undone)==before
    results[name]={'changed_pixels':int(changed.sum()),'outside_radius60_exact':True,'after_release_whole_project_stable':True,'Undo_exact':True}
assert results['held-six-seconds']['changed_pixels']>results['held']['changed_pixels']*10
assert doc('moved-redone')==doc('moved')
report={'status':'Pass','scope':'Native timed holds, movement, release and history; physical cancellation/blur while held remains unexecuted (automated regression passes).','results':results,'sha256':hashes};(out/'hole64-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(results,indent=2))
