"""Independent saved-file oracle for LIVE-051, including weighted edges."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(prefix,name):
    filename=f'mouse-audit-{prefix}-{name}.retropaint';data=(Path.home()/'Downloads'/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
bad_before=pixels(doc('invert58','symmetry-before'));bad=pixels(doc('invert58','symmetry-effect'))
bad_count=int(np.sum(bad_before[:,:,3]!=bad[:,:,3]));assert bad_count>0
before=doc('invert59','before');once=doc('invert59','once');twice=doc('invert59','twice')
a=pixels(before);b=pixels(once);c=pixels(twice)
assert np.array_equal(a[:,:,3],b[:,:,3]) and np.array_equal(a[:,:,3],c[:,:,3])
assert np.array_equal(a[a[:,:,3]==0],b[a[:,:,3]==0]) and np.array_equal(a[a[:,:,3]==0],c[a[:,:,3]==0])
yy,xx=np.mgrid[:640,:960];cx=(942-561.000244140625)*960/811.9994506835938;cy=(410-122)*640/541.3333740234375
outside=(np.hypot(xx+.5-cx,yy+.5-cy)>31)&(np.hypot(xx+.5-(960-cx),yy+.5-cy)>31)
assert np.array_equal(a[outside],b[outside]) and np.array_equal(a[outside],c[outside])
changed=np.any(a!=b,axis=2)&(a[:,:,3]>0)
source=a[:,:,:3][changed].astype(float);first=b[:,:,:3][changed].astype(float);second=c[:,:,:3][changed].astype(float)
assert np.all((source==0)|(source==255))
weights=np.abs(first-source)/255;weight=weights.mean(axis=1)
assert np.max(np.ptp(weights,axis=1))<=2/255
expected=first+(255-2*first)*weight[:,None]
error=float(np.abs(second-expected).max());assert error<=3,error
edge=(weight>0)&(weight<1);assert edge.any()
for x in [450,475,490]:
    assert b[340,x].tolist()==[0,255,255,128]
    assert np.array_equal(a[340,x],c[340,x])
assert doc('invert59','undone')==once and doc('invert59','redone')==twice
for current in [once,twice]:
    old=copy.deepcopy(before);new=copy.deepcopy(current);del old['layers'][0]['image'];del new['layers'][0]['image'];assert old==new
report={'status':'Pass','regression':'LIVE-051','pre_fix_alpha_changes':bad_count,'post_fix_alpha_changes':0,'weighted_edge_pixels':int(edge.sum()),'double_pass_weighted_error_max':error,'outside_mirrored_radius31_exact':True,'transparent_pixels_exact':True,'history_whole_project_exact':True,'native_tap':[942,410],'source_centre':[cx,cy],'sha256':hashes}
(out/'invert59-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
