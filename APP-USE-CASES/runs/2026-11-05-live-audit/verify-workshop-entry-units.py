"""Preserved paint and independently measured cube after workshop orbit/zoom/reentry."""
from pathlib import Path
import hashlib,json,struct
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
before=json.loads(retain('mouse-audit-solid157-cube-baseline.retropaint'));after=json.loads(retain('mouse-audit-solid157-after-camera.retropaint'));paint=json.loads((downloads/'mouse-audit-enhance148-baseline.retropaint').read_text());assert before==after and before['layers'][0]==paint['layers'][0] and len(before['layers'])==2 and before['active']==before['layers'][0]['id']
cad=before['layers'][1]['cad'];assert cad['units']=='mm' and len(cad['bodies'])==1;body=cad['bodies'][0];assert body['solid']['size']==[20,20,20] and body['scale']==[1,1,1] and body['position']==[0,0,10]
data=retain('mouse-audit-solid157-after-camera-3d-mm.stl');count=struct.unpack_from('<I',data,80)[0];assert count==12 and len(data)==84+count*50;triangles=np.array([struct.unpack_from('<12fH',data,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3);lo=triangles.min(axis=(0,1));hi=triangles.max(axis=(0,1));volume=float(np.einsum('ij,ij->i',triangles[:,0],np.cross(triangles[:,1],triangles[:,2])).sum()/6);assert np.array_equal(hi-lo,[20,20,20]) and volume==8000 and lo[2]==0
edges={}
for triangle in triangles:
    for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
        key=tuple(sorted((tuple(a),tuple(b))));edges[key]=edges.get(key,0)+1
assert set(edges.values())=={2}
a=np.array(Image.open(out/'solid157-before-orbit.png'));b=np.array(Image.open(out/'solid157-after-orbit-zoom.png'));changed=int(np.count_nonzero(np.any(a[130:580,300:1380,:3]!=b[130:580,300:1380,:3],axis=2)));assert changed>10000
ui=json.loads((out/'solid157-ui.json').read_text());assert ui['afterCamera']['canvases']==1 and '20.00 × 20.00 × 20.00 mm' in ui['printCheck'];report=dict(status='Pass',whole_project_exact_after_camera=True,original_paint_layer_exact=True,one_workshop_canvas=True,one_cad_layer=True,bounds_mm=(hi-lo).tolist(),signed_volume_mm3=volume,closed_edges=True,changed_view_pixels=changed,hashes=hashes);(out/'solid157-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
