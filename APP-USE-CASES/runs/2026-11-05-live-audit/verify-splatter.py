"""Bound random native splatter without requiring a repeat of its RNG."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-spray66-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def px(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
before=doc('before');middle=doc('middle');edge=doc('edge');a=px(before);b=px(middle);c=px(edge)
e=json.loads((out/'spray66-evidence.json').read_bytes());r=e['rect'];yy,xx=np.mgrid[:640,:960];results=[]
for name,old,new in [('middle',a,b),('edge',b,c)]:
    x,y=e[name];cx=(x-r['x'])*960/r['width'];cy=(y-r['y'])*640/r['height'];changed=np.any(old!=new,axis=2);assert changed.any()
    assert np.array_equal(old[np.hypot(xx+.5-cx,yy+.5-cy)>240],new[np.hypot(xx+.5-cx,yy+.5-cy)>240])
    assert np.all(new[:,:,3]==255)
    rgb=new[:,:,:3][changed].astype(float)
    # Derive opacity from the high-contrast green channel. Repeated translucent
    # drops accumulate integer canvas rounding; allow3 channel levels, rather
    # than amplifying red-channel rounding by its tiny16-level contrast.
    weight=(255-rgb[:,1])/184
    assert np.max(np.abs(rgb-(255-weight[:,None]*np.array([16,184,144]))))<=3
    assert np.any(np.all(new[:,:,:3]==[239,71,111],axis=2))
    mask=changed.copy();components=[]
    for py,pxx in zip(*np.where(mask)):
        if not mask[py,pxx]:continue
        pending=[(py,pxx)];mask[py,pxx]=False;size=0
        while pending:
            sy,sx=pending.pop();size+=1
            for ny,nx in [(sy-1,sx),(sy+1,sx),(sy,sx-1),(sy,sx+1)]:
                if 0<=ny<640 and 0<=nx<960 and mask[ny,nx]:mask[ny,nx]=False;pending.append((ny,nx))
        components.append(size)
    assert len(components)>5 and max(components)>min(components)*3
    results.append({'sample':name,'changed_pixels':int(changed.sum()),'separate_drop_components':len(components),'outside_radius240_exact':True,'chosen_Pink_with_antialiasing':True})
assert np.any(np.any(b!=c,axis=2)[:,-1]);assert np.array_equal(b[:,:300],c[:,:300])
assert doc('undone')==middle and doc('redone')==edge
report={'status':'Pass','results':results,'opposite_edge_exact':True,'whole_Undo_Redo_exact':True,'sha256':hashes};(out/'spray66-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(results,indent=2))
