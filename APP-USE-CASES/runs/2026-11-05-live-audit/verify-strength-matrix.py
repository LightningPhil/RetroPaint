"""Independent source-over arithmetic and exact native history/round trips."""
from pathlib import Path
from PIL import Image
import base64, copy, hashlib, io, json
import numpy as np
root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads'
hashes={}
def actual(name,extension='retropaint'):
    filename='mouse-audit-strength54-'+name+'.'+extension
    data=(downloads/filename).read_bytes();(out/filename).write_bytes(data)
    hashes[filename]=hashlib.sha256(data).hexdigest()
    return data
def doc(name): return json.loads(actual(name))
def pixels(d): return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
baseline=doc('before')
fixture=json.loads((root/'test-results/audit-2026-11-05/fixtures/strength53/white-blue.retropaint').read_bytes())
# Pillow and Chrome encode the same RGBA with different PNG compression.
# The initial whole-JSON fixture comparison failed only on this image string.
assert np.array_equal(pixels(baseline),pixels(fixture))
fixture['layers'][0]['image']=baseline['layers'][0]['image'];assert baseline==fixture
red=np.array([229,57,53]);white=np.array([255,255,255]);blue=np.array([30,136,229])
rows=[('white-full',white,1,1,200,180,647,858,274),('blue-full',blue,1,1,700,180,1053,1265,274),
      ('white-weak',white,.15,1,200,360,647,858,427),('blue-weak',blue,.15,1,700,360,1053,1265,427),
      ('white-overlap',white,.15,2,200,360,647,858,427),('blue-overlap',blue,.15,2,700,360,1053,1265,427)]
previous=baseline;results=[]
yy,xx=np.mgrid[:640,:960]
for name,bg,alpha,passes,x,y,sx,ex,sy in rows:
    current=doc(name);a=pixels(previous);b=pixels(current)
    expected=bg.astype(float)
    for _ in range(passes):expected=red*alpha+expected*(1-alpha)
    patch=b[y-4:y+5,x-4:x+5,:3].astype(float)
    error=float(np.abs(patch-expected).max());assert error<=2,(name,error)
    x0=(sx-562)*960/813;x1=(ex-562)*960/813;y0=(sy-122)*640/542
    distance=np.hypot(xx+.5-np.clip(xx+.5,x0,x1),yy+.5-y0)
    changed=np.any(a!=b,axis=2);assert changed.any() and not np.any(changed & (distance>13)),name
    meta_a=copy.deepcopy(previous);meta_b=copy.deepcopy(current)
    del meta_a['layers'][0]['image'];del meta_b['layers'][0]['image'];assert meta_a==meta_b,name
    results.append({'name':name,'expected_RGB':expected.tolist(),'observed_RGB':b[y,x,:3].tolist(),'maximum_centre_error':error,'changed_pixels':int(changed.sum()),'outside_declared_stroke_tube_exact':True})
    previous=current
assert doc('white-overlap-undone')==doc('blue-weak')
assert doc('white-overlap-redone')==doc('white-overlap')==doc('blue-overlap-undone')
assert doc('blue-overlap-redone')==doc('blue-overlap')==doc('controls')==doc('project-reopened')
png=np.array(Image.open(io.BytesIO(actual('final','png'))).convert('RGBA'))
assert np.array_equal(png,pixels(previous)) and np.array_equal(png,pixels(doc('png-reopened')))
states=json.loads((out/'strength54-states.json').read_bytes())
assert len(states)==5
for s in states:assert str(round(float(s['value'])*100))+'%' in s['label']
report={'status':'Pass','native_input':'Connected Chrome mouse drags; keyboard Home/End on the strength slider','rows':results,'whole_project_overlap_Undo_Redo_exact':True,'control_changes_preserve_whole_document':True,'project_and_PNG_roundtrips_exact':True,'visible_strength_checks':states,'sha256':hashes}
(out/'strength54-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS six source-over cases, both exact overlap histories, control labels and project/PNG round trips')
