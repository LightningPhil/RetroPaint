"""Native mixed duplication retains source identity and isolates mutable wet pixels."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-vector85-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('long-paused');transformed=doc('copies-transformed');animated=doc('after-animation');undone=doc('move-undone');redone=doc('move-redone');src=before['layers'][0]['objects'];objects=transformed['layers'][0]['objects']
assert len(src)==23 and len(objects)==25 and src[-1]['wet'] is True
assert objects[:22]==src[:22]
# The original wet surface can keep accumulating pigment; only its image may change.
a=copy.deepcopy(src[-1]);b=copy.deepcopy(objects[22]);a.pop('image');b.pop('image');assert a==b
for old,new in [(objects[20],objects[23]),(objects[22],objects[24])]:
    a=copy.deepcopy(old);b=copy.deepcopy(new);assert a.pop('id')!=b.pop('id');a.pop('matrix');b.pop('matrix')
    if a.get('wet'):assert b.get('wet') is False;a.pop('wet');b.pop('wet')
    assert a==b
def bounds(items):
    pts=[]
    for o in items:
        a,b,c,d,e,f=o['matrix'];pts.extend((a*x+c*y+e,b*x+d*y+f)for x,y in [(0,0),(o['width'],0),(0,o['height']),(o['width'],o['height'])])
    xs,ys=zip(*pts);return [min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)]
assert max(abs(a-b)for a,b in zip(bounds(objects[23:]),[100,400,200,160]))<1e-8
changed=[i for i,(a,b)in enumerate(zip(objects,animated['layers'][0]['objects']))if a!=b];assert changed==[22]
a=copy.deepcopy(objects[22]);b=copy.deepcopy(animated['layers'][0]['objects'][22]);assert a.pop('image')!=b.pop('image') and a==b
assert animated['layers'][0]['objects'][23:]==objects[23:]
assert max(abs(a-b)for a,b in zip(bounds(undone['layers'][0]['objects'][23:])[2:],bounds(objects[23:])[2:]))<1e-8
assert undone['layers'][0]['objects'][23:][0]['matrix']!=objects[23]['matrix']
assert redone==animated
report={'status':'Pass','native_wet_source_true':True,'copy_source_pixels_equal_at_capture':True,'copy_has_unique_ID_and_settled_surface':True,'only_original_wet_image_changes_after_resume':True,'copied_group_exact_bounds':[100,400,200,160],'move_Undo_and_entire_project_Redo_exact':True,'sha256':hashes};(out/'vector85-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native wet mixed duplication, independent pixels, exact group transforms and history')
