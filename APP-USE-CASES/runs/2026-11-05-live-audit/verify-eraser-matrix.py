"""Verify Paper versus alpha erasing, layer isolation, history and round trips."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(name,ext='retropaint'):
    filename='mouse-audit-eraser57-'+name+'.'+ext;data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(actual(name))
def pixels(layer):return np.array(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
evidence=json.loads((out/'eraser57-evidence.json').read_bytes());results=[];yy,xx=np.mgrid[:640,:960]
for row in evidence['rows']:
    variant=row['variant'];before=doc(variant+'-before');after=doc(variant+'-after');target=0 if variant=='paper' else 2
    assert before['active']==after['active']==before['layers'][target]['id']
    assert before['layers'][0]['paper']=='#ffffff'
    assert all(a==b for i,(a,b) in enumerate(zip(before['layers'],after['layers'])) if i!=target)
    a=pixels(before['layers'][target]);b=pixels(after['layers'][target]);patch=b[395:405,230:250]
    if variant=='paper':assert np.all(patch==[255,255,255,255])
    else:assert np.all(patch[:,:,3]==0)
    rect=row['rect'];x0=(row['from'][0]-rect['x'])*960/rect['width'];x1=(row['to'][0]-rect['x'])*960/rect['width'];y=(row['to'][1]-rect['y'])*640/rect['height']
    changed=np.any(a!=b,axis=2);distance=np.hypot(xx+.5-np.clip(xx+.5,x0,x1),yy+.5-y)
    assert changed.any() and not np.any(changed & (distance>20))
    assert doc(variant+'-undone')==before and doc(variant+'-redone')==after
    if variant=='hidden':assert not before['layers'][target]['visible'] and after['layers'][target]['visible']
    results.append({'variant':variant,'changed_pixels':int(changed.sum()),'all_other_layers_exact':True,'whole_Undo_Redo_exact':True,'outside_declared_radius20_tube_exact':True})
png=np.array(Image.open(io.BytesIO(actual('transparent-after','png'))).convert('RGBA'))
assert np.all(png[395:405,230:250]==[30,136,229,255])
assert doc('project-reopened')==doc('transparent-after')
assert np.array_equal(png,pixels(doc('png-reopened')['layers'][0]))
report={'status':'Pass','rows':results,'transparent_hole_reveals_exact_Backdrop_RGB':True,'project_and_PNG_roundtrips_exact':True,
        'hidden_policy':'Gesture makes the active Character layer visible and erases that same layer. Every neighbouring layer remains exact; Undo restores hidden visibility and original pixels together.',
        'fixture_correction':'eraser56 exposed boolean paper metadata in synthetic MIX. Original evidence retained. eraser57 uses corrected #ffffff/null schema, and asserts Paper colour before checking its erase result.', 'sha256':hashes}
(out/'eraser57-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS Paper white, transparent alpha0/backdrop, hidden-neighbour isolation, exact history and round trips')
