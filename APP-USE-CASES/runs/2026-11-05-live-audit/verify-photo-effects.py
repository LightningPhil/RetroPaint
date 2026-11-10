"""Local natural-photo effects: exact outside/alpha/history and independent appearance metrics."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(name):
    filename='mouse-audit-photo62-'+name+'.retropaint';data=(Path.home()/'Downloads'/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
before=doc('before');a=pixels(before);assert a.shape==(1398,2100,4)
e=json.loads((out/'photo62-evidence.json').read_bytes());r=e['rect'];x0=(850-r['x'])*2100/r['width'];x1=(1050-r['x'])*2100/r['width'];y=(520-r['y'])*1398/r['height'];yy,xx=np.mgrid[:1398,:2100];distance=np.hypot(xx+.5-np.clip(xx+.5,x0,x1),yy+.5-y)
results={}
for name,radius in [('pixelate',33),('pixelate-small',24),('emboss',31)]:
    d=doc(name);b=pixels(d);changed=np.any(a!=b,axis=2);assert changed.any();assert np.array_equal(a[distance>radius],b[distance>radius]);assert np.array_equal(a[:,:,3],b[:,:,3]);assert changed.sum()<a.shape[0]*a.shape[1]*.02
    old=copy.deepcopy(before);new=copy.deepcopy(d);del old['layers'][0]['image'];del new['layers'][0]['image'];assert old==new
    results[name]={'changed_pixels':int(changed.sum()),'outside_radius':radius,'outside_exact':True,'alpha_exact':True}
    if name!='pixelate-small':assert doc(name+'-undone')==before and doc(name+'-redone')==d
    if name=='pixelate':
        counts=[int(np.all(im[1005:1050,800:1200,:3]==im[1005:1050,801:1201,:3],axis=2).sum()) for im in [a,b]]
        assert counts[1]>counts[0]*2;results[name]['adjacent_equal_RGB_before_after']=counts
    if name=='emboss':
        # Relief pulls the photo towards neutral grey; assess only the fully brushed core.
        core=(xx>800)&(xx<1200)&(np.abs(yy-y)<15)
        old_chroma=np.ptp(a[:,:,:3].astype(float),axis=2)[core].mean();new_chroma=np.ptp(b[:,:,:3].astype(float),axis=2)[core].mean()
        assert new_chroma<old_chroma*.5;results[name]['mean_chroma_before_after']=[float(old_chroma),float(new_chroma)]
assert results['pixelate-small']['changed_pixels']<results['pixelate']['changed_pixels']
edge_before=doc('edge-before');edge_after=doc('edge-emboss');ea=pixels(edge_before);eb=pixels(edge_after)
assert np.array_equal(ea[:,:,3],eb[:,:,3]);assert not eb[:,:20,3].any();assert np.any(ea!=eb)
cx=(568-r['x'])*2100/r['width'];y0=(300-r['y'])*1398/r['height'];y1=(400-r['y'])*1398/r['height'];edge_outside=np.hypot(xx+.5-cx,yy+.5-np.clip(yy+.5,y0,y1))>31
assert np.array_equal(ea[edge_outside],eb[edge_outside]);assert doc('edge-undone')==edge_before and doc('edge-redone')==edge_after
results['emboss-transparent-edge']={'all_alpha_exact':True,'clear_border_preserved':True,'outside_exact':True,'whole_history_exact':True}
report={'status':'Pass','scope':'Natural landscape photograph and transparent edge; face-detail Pixelate evidence separate','results':results,'sha256':hashes};(out/'photo62-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(results,indent=2))
