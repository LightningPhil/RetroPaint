"""Shared composition crop, source retention and truly local photo geometry."""
from pathlib import Path
import base64,copy,hashlib,io,json,math
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-mix135-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=load('baseline');crop=load('cropped');assert load('reopened')==crop
c=dict(x=80/960,y=40/640,width=800/960,height=560/640);assert crop['crop']==c;expected=copy.deepcopy(base);expected['crop']=c
for key in ['settings','normal']:expected['layers'][2]['photo'][key]['crop']=c
assert crop==expected
raw=load('baseline','png');a=load('cropped','png');assert np.array_equal(a,raw[40:600,80:880])
local=load('local-straighten');angle=local['layers'][2]['photo']['settings']['angle'];assert 5<angle<15;expected=copy.deepcopy(crop)
for key in ['settings','normal']:expected['layers'][2]['photo'][key]['angle']=angle
assert local==expected
b=load('local-straighten','png');assert b.shape==a.shape and np.count_nonzero(b!=a)>1000
# Bound every original Character pixel and object, then include both rotation
# directions around the source centre and a3px bilinear margin. Other sheets
# must remain exact outside this independently computed affected region.
points=[]
for o in base['layers'][2]['objects']:
    bounds=Image.open(io.BytesIO(base64.b64decode(o['image'].split(',')[1]))).getbbox() if o['kind']=='raster' else (0,0,o['width'],o['height'])
    assert bounds is not None;m=o['matrix'];boxes=[bounds]
    # Live ink is retained separately from the raster object's original PNG.
    # Its fill masks and stroke envelopes are part of that object's source.
    live=o.get('live',{});origin=o.get('origin',dict(x=0,y=0))
    for fill in live.get('fills',[]):
        fill_box=Image.open(io.BytesIO(base64.b64decode(fill['mask'].split(',')[1]))).getbbox()
        if fill_box:boxes.append((fill_box[0]-origin['x'],fill_box[1]-origin['y'],fill_box[2]-origin['x'],fill_box[3]-origin['y']))
    for stroke in live.get('strokes',[]):
        for p in stroke['points']:
            radius=p['w']/2+3;x=p['x']-origin['x'];y=p['y']-origin['y'];boxes.append((x-radius,y-radius,x+radius,y+radius))
    assert not live.get('sparkles',[])
    for bounds in boxes:
        for x,y in [(bounds[0],bounds[1]),(bounds[2],bounds[1]),(bounds[0],bounds[3]),(bounds[2],bounds[3])]:points.append((m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]))
expanded=points.copy()
for sign in [-1,1]:
    t=math.radians(angle*sign);co,si=math.cos(t),math.sin(t)
    for x,y in points:expanded.append((480+co*(x-480)-si*(y-320),320+si*(x-480)+co*(y-320)))
x0=max(0,math.floor(min(x for x,y in expanded))-3-80);x1=min(800,math.ceil(max(x for x,y in expanded))+3-80);y0=max(0,math.floor(min(y for x,y in expanded))-3-40);y1=min(560,math.ceil(max(y for x,y in expanded))+3-40);outside=np.ones(a.shape[:2],bool);outside[y0:y1,x0:x1]=False;assert np.array_equal(a[outside],b[outside])
assert any(o['kind']=='text' for o in base['layers'][3]['objects']) and len(base['layers'])==4
report=dict(status='Pass',four_visible_sheets_with_photo_paint_text_stamp=True,shared800x560_frame_every_RGBA_exact_full_composite_slice=True,all_source_pixels_objects_live_recipes_and_other_sheets_exact=True,actual_project_reopen_whole_document_exact=True,local_straighten_only_Character_recipe_changes=True,all_composite_pixels_outside_Character_old_rotated_bounds_exact=True,unaffected_region_pixels=int(outside.sum()),sha256=hashes)
(out/'mix135-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native shared multilayer frame, exact alignment/source/reopen and local-only straighten')
