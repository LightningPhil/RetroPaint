"""Verify native selected vector/raster inversion and atomic rejection."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name=f'mouse-audit-vector88-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(o):return np.array(Image.open(io.BytesIO(base64.b64decode(o['image'].split(',')[1]))).convert('RGBA')).astype(int)
before=doc('before');after=doc('inverted');old=before['layers'][0]['objects'];new=after['layers'][0]['objects']
assert old[0]['kind']=='path' and new[0]['kind']=='raster';assert old[0]['id']==new[0]['id'] and old[0]['matrix']==new[0]['matrix']
expected=copy.deepcopy(before);expected['layers'][0]['objects'][0]=new[0];assert expected==after
p=pixels(new[0]);assert tuple(p[60,70])==(0,0,0,255);assert tuple(p[60,11])==(225,119,26,255);assert tuple(p[0,0])==(0,0,0,0)
assert doc('undone')==before and doc('redone')==after
reopened=doc('reopened');expected=copy.deepcopy(after)
# Reader adds its default live coordinate dimensions even to a non-live raster.
assert 'live' not in new[0];expected['layers'][0]['objects'][0]['liveSize']={'width':960,'height':640};assert expected==reopened
raster=doc('raster-onpaper');target=raster['layers'][0]['objects'][2];expected=copy.deepcopy(before);expected['layers'][0]['objects'][2]=target;assert expected==raster
a=pixels(old[2]);b=pixels(target);assert a.shape==b.shape;assert np.array_equal(a[:,:,3],b[:,:,3]);visible=a[:,:,3]>0
assert np.max(abs((255-a[:,:,:3]-b[:,:,:3])[visible]))<=1
assert np.max(abs((255-a[:,:,:3]-b[:,:,:3])[a[:,:,3]==255]))==0
assert doc('rejected')==json.loads((out/'vector-unsupported-effect.retropaint').read_text())
report=dict(status='Pass',unselected_whole_data_exact=True,vector_becomes_honest_raster=True,known_vector_fill_and_border_inverted=True,raster_alpha_exact=True,raster_opaque_inversion_exact=True,translucent_canvas_rounding_max=1,whole_document_history_exact=True,reopen_only_nonlive_default_liveSize_added=True,oversize_rejection_whole_document_exact=True,additional_offpaper_raster_exploration='raster-inverted retained separately; Place explicitly trims raster overhangs',sha256=hashes)
(out/'vector88-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native local vector/raster effects, exact neighbours/history and atomic rejection')
