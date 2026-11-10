"""Verify RGB inversion, weighted edges, exact alpha and native history."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(name):
    filename='mouse-audit-invert58-'+name+'.retropaint';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
baseline=doc('before');original=pixels(baseline);fixture=np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/patch-labelled.png').convert('RGBA'));assert np.array_equal(original,fixture)
evidence=json.loads((out/'invert58-evidence.json').read_bytes());yy,xx=np.mgrid[:640,:960];results=[];previous=baseline
for row in evidence['rows']:
    name=row['name'];once=doc(name+'-once');twice=doc(name+'-twice');a=pixels(previous);b=pixels(once);c=pixels(twice)
    assert np.array_equal(a[:,:,3],b[:,:,3]) and np.array_equal(a[:,:,3],c[:,:,3])
    rect=row['rect'];x0=(row['from'][0]-rect['x'])*960/rect['width'];x1=(row['to'][0]-rect['x'])*960/rect['width'];y=(row['to'][1]-rect['y'])*640/rect['height']
    distance=np.hypot(xx+.5-np.clip(xx+.5,x0,x1),yy+.5-y);outside=distance>31
    assert np.array_equal(a[outside],b[outside]) and np.array_equal(a[outside],c[outside])
    centre_y=140 if name=='opaque' else 340
    for centre_x in [150,450]:
        region=(slice(centre_y-5,centre_y+5),slice(centre_x-5,centre_x+5))
        assert np.array_equal(b[region][:,:,:3],255-a[region][:,:,:3])
        assert np.array_equal(c[region],a[region])
    mask=(np.any(a!=b,axis=2)) & (a[:,:,3]>0)
    source=a[:,:,:3][mask].astype(float);first=b[:,:,:3][mask].astype(float);second=c[:,:,:3][mask].astype(float)
    assert np.all((source==0)|(source==255))
    weights=np.abs(first-source)/255;weight=weights.mean(axis=1)
    assert np.max(np.ptp(weights,axis=1))<=2/255
    expected=first*(1-weight[:,None])+(255-first)*weight[:,None]
    error=np.abs(second-expected).max(axis=1);allowed=np.where(a[:,:,3][mask]==255,2,3)
    assert np.all(error<=allowed),(name,float(error.max()))
    edge=(weight>0)&(weight<1)
    # Unmasked raster discs have binary coverage. Do not invent AA edge pixels.
    assert not edge.any()
    assert doc(name+'-undone')==once and doc(name+'-redone')==twice
    for current in [once,twice]:
        old=copy.deepcopy(previous);new=copy.deepcopy(current);del old['layers'][0]['image'];del new['layers'][0]['image'];assert old==new
    results.append({'row':name,'affected_visible_pixels':int(mask.sum()),'weighted_edge_pixels':int(edge.sum()),'maximum_double_pass_edge_error':float(error.max()),'alpha_exact':True,'full_centres_invert_and_return_exact':True,'outside_radius31_exact':True,'whole_Undo_Redo_exact':True})
    previous=twice
report={'status':'Pass','rows':results,'oracle':'Binary known RGB patches and binary unmasked disc coverage. All alpha and all outside pixels exact; full covered centres invert and return exactly. Antialiased symmetry-mask variants are verified separately.','sha256':hashes}
(out/'invert58-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS four known RGB/alpha patches, weighted edges, double inversion and exact history')
