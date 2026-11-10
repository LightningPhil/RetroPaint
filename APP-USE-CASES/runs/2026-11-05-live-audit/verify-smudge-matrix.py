"""Measure native Smudge displacement without reproducing its algorithm."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(name,prefix='smudge60'):
    filename='mouse-audit-'+prefix+'-'+name+'.retropaint';data=(Path.home()/'Downloads'/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][1]['image'].split(',',1)[1]))).convert('RGBA'))
before=doc('before');a=pixels(before);assert np.array_equal(a,np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/smudge60/settled.png')))
yy,xx=np.mgrid[:240,:320];evidence=json.loads((out/'smudge60-evidence.json').read_bytes());r=evidence['rect'];x0=(877-r['x'])*320/r['width'];x1=(1057-r['x'])*320/r['width'];y=(393-r['y'])*240/r['height'];outside=np.hypot(xx+.5-np.clip(xx+.5,x0,x1),yy+.5-y)>24
results={}
for strength in ['strong','weak']:
    d=doc(strength);b=pixels(d);assert np.array_equal(a[outside],b[outside]);assert d['layers'][0]==before['layers'][0]
    assert not np.any(b[:,:,1]),'Smudge sampled the green neighbour'
    visible=b[:,:,3]>0;assert np.all(b[:,:,:3].max(axis=2)[visible]>0),'Opaque black injected'
    assert np.any((b[:,:,3]>0)&(b[:,:,3]<255)),'No feathered alpha edge'
    red=b[:,:,0].astype(float)*b[:,:,3]/65025;displaced=float(red[:,140:].sum());assert displaced>0
    # A rightward drag must not move the original red left boundary.
    assert np.array_equal(a[:,:40],b[:,:40])
    assert doc(strength+'-undone')==before and doc(strength+'-redone')==d
    old=copy.deepcopy(before);new=copy.deepcopy(d);del old['layers'][1]['image'];del new['layers'][1]['image'];assert old==new
    results[strength]={'red_pixel_equivalents_right_of_original_edge':displaced,'changed_pixels':int(np.any(a!=b,axis=2).sum()),'feathered_pixels':int(((b[:,:,3]>0)&(b[:,:,3]<255)).sum()),'outside_radius24_exact':True,'neighbour_exact':True,'history_exact':True}
assert results['strong']['red_pixel_equivalents_right_of_original_edge']>results['weak']['red_pixel_equivalents_right_of_original_edge']
wet_before=doc('before','smudge61');assert len(wet_before['layers'][1]['live']['fills'])==2
wet_results={}
for strength in ['strong','weak']:
    d=doc(strength,'smudge61');b=pixels(d)
    assert np.array_equal(a[outside],b[outside]);assert d['layers'][0]==wet_before['layers'][0]
    assert not np.any(b[:,:,1]);visible=b[:,:,3]>0;assert np.all(b[:,:,:3].max(axis=2)[visible]>0)
    assert np.any((b[:,:,3]>0)&(b[:,:,3]<255))
    displaced=float((b[:,:,0].astype(float)*b[:,:,3]/65025)[:,140:].sum());assert displaced>0
    assert doc(strength+'-undone','smudge61')==wet_before and doc(strength+'-redone','smudge61')==d
    assert not d['layers'][1]['live']['fills']
    wet_results[strength]={'displaced_red_pixel_equivalents':displaced,'outside_exact':True,'neighbour_exact':True,'whole_history_exact':True}
assert wet_results['strong']['displaced_red_pixel_equivalents']>wet_results['weak']['displaced_red_pixel_equivalents']
def png(name):
    filename='mouse-audit-smudge61-'+name+'.png';data=(Path.home()/'Downloads'/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return np.array(Image.open(io.BytesIO(data)).convert('RGBA'))
frame1=png('before-12345');frame2=png('before-23456');assert np.array_equal(png('undone-23456'),frame2)
for frame,level in [(frame1,255),(frame2,136)]:
    expected=np.empty_like(a);expected[:]=[0,255,0,255];expected[60:180,40:140]=[level,0,0,255];expected[60:180,160:260]=[0,0,level,255];assert np.array_equal(frame,expected)
report={'status':'Pass','scope':'Settled raster and animated live-ink variants; exact native history and restored animation frame','results':results,'wet_results':wet_results,'sha256':hashes};(out/'smudge60-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
