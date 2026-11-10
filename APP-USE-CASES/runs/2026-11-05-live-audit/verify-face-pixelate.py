"""Independent local-area and blockiness oracle for the required face-detail flow."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(name):
    filename='mouse-audit-face63-'+name+'.retropaint';data=(Path.home()/'Downloads'/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
before=doc('before');after=doc('pixelate');a=pixels(before);b=pixels(after);h,w=a.shape[:2];assert (w,h)==(2615,3269)
e=json.loads((out/'face63-evidence.json').read_bytes());r=e['rect'];x0=(910-r['x'])*w/r['width'];x1=(965-r['x'])*w/r['width'];cy=(240-r['y'])*h/r['height'];yy,xx=np.mgrid[:h,:w];outside=np.hypot(xx+.5-np.clip(xx+.5,x0,x1),yy+.5-cy)>33
assert np.array_equal(a[outside],b[outside]);assert np.array_equal(a[:,:,3],b[:,:,3]);changed=int(np.any(a!=b,axis=2).sum());assert 1000<changed<h*w*.01
left,right,top,bottom=int(x0+20),int(x1-20),int(cy-15),int(cy+15)
flat=[int(np.all(im[top:bottom,left:right,:3]==im[top:bottom,left+1:right+1,:3],axis=2).sum()) for im in [a,b]];assert flat[1]>flat[0]*2
assert doc('undone')==before and doc('redone')==after
old=copy.deepcopy(before);new=copy.deepcopy(after);del old['layers'][0]['image'];del new['layers'][0]['image'];assert old==new
report={'status':'Pass','dimensions':[w,h],'changed_pixels':changed,'outside_radius33_exact':True,'alpha_exact':True,'adjacent_equal_RGB_before_after':flat,'whole_history_exact':True,'sha256':hashes};(out/'face63-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
