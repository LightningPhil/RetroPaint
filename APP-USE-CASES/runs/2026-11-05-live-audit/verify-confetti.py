"""Independent native burst colour/area checks and exact random-history oracle."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-confetti67-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def px(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
before=doc('before');rainbow=doc('rainbow');solid=doc('solid');a=px(before);b=px(rainbow);c=px(solid)
e=json.loads((out/'confetti67-evidence.json').read_bytes());r=e['rect'];yy,xx=np.mgrid[:640,:960]
def distance(p):return np.hypot(xx+.5-(p[0]-r['x'])*960/r['width'],yy+.5-(p[1]-r['y'])*640/r['height'])
outside=np.minimum.reduce([distance(p) for p in e['rainbow']])>275;assert np.array_equal(a[outside],b[outside])
rgb=b[:,:,:3][np.any(a!=b,axis=2)].astype(float);chroma=np.ptp(rgb,axis=1);colourful=rgb[chroma>100];assert len(colourful)>100
dominant=np.argmax(colourful,axis=1);assert len(np.unique(dominant))==3
assert np.array_equal(b[distance(e['solid'])>275],c[distance(e['solid'])>275])
changed=np.any(b!=c,axis=2);assert changed.any();assert np.any(np.all(c[:,:,:3]==[67,160,71],axis=2))
# Infer coverage using the high-contrast red channel and compare green/blue.
source=b[:,:,:3][changed].astype(float);target=c[:,:,:3][changed].astype(float);ink=np.array([67,160,71]);channel=np.argmax(np.abs(ink-source),axis=1);rows=np.arange(len(source));weight=(target[rows,channel]-source[rows,channel])/(ink[channel]-source[rows,channel])
assert np.max(np.abs(target-(source+(ink-source)*weight[:,None])))<=3
assert np.all(c[:,:,3]==255);assert doc('undone')==rainbow and doc('redone')==solid
report={'status':'Pass','rainbow_has_all_three_dominant_channels':True,'solid_green_RGB':[67,160,71],'outside_radius275_exact':True,'whole_random_arrangement_Undo_Redo_exact':True,'sha256':hashes};(out/'confetti67-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS Rainbow colours, solid Green, bounded footprints and exact random history')
