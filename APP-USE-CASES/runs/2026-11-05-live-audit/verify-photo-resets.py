"""Native individual/group/full photo resets and original-source recovery."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name=f'mouse-audit-photo98-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
rich=doc('rich-recipe');slider=doc('slider-reset');group=doc('group-reset');expected=copy.deepcopy(rich)
for key in ['settings','normal']:expected['layers'][0]['photo'][key]['exposure']=0
assert expected==slider
expected=copy.deepcopy(rich)
for key in ['settings','normal']:
    for field in ['exposure','brightness','contrast']:expected['layers'][0]['photo'][key][field]=0
assert expected==group
assert doc('full-reset-cancelled')==rich
reset=doc('full-reset');recipe=reset['layers'][0]['photo'];s=recipe['settings'];assert s==recipe['normal'] and recipe['look']=='normal' and recipe['lookActive'] is False
special=dict(balance=[1,1,1],mixer=[dict(hue=0,saturation=0,luminance=0) for _ in range(8)],curves={c:[dict(x=0,y=0),dict(x=1,y=1)] for c in ['rgb','red','green','blue']},radius=1,midpoint=50,feather=75,grainSize=1.2,grainRoughness=50,zoom=100,crop=dict(x=0,y=0,width=1,height=1))
for key,value in s.items():assert value==special.get(key,0),(key,value)
expected=copy.deepcopy(rich);expected['layers'][0]['photo']=recipe;assert reset==expected
assert doc('full-reset-undone')==rich and doc('full-reset-redone')==reset
images={}
for n in ['rich-recipe','group-reset','full-reset']:
    name=f'mouse-audit-photo98-{n}.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();images[n]=np.array(Image.open(out/name).convert('RGBA')).astype(int)
assert images['rich-recipe'][:,:,:3].mean()>images['group-reset'][:,:,:3].mean()+30
decode=lambda l:Image.open(io.BytesIO(base64.b64decode(l['image'].split(',')[1]))).convert('RGBA')
original=np.array(Image.alpha_composite(decode(reset['layers'][0]),decode(reset['layers'][1]))).astype(int)
assert np.array_equal(original[:,:,3],images['full-reset'][:,:,3]);error=int(np.max(abs(original-images['full-reset'])));assert error<=1
report=dict(status='Pass',double_click_only_exposure_reset=True,group_reset_only_three_light_fields=True,other_groups_and_source_data_exact=True,full_reset_all_defaults_explicitly_checked=True,cancel_and_undo_restore_whole_saved_document_exact=True,redo_exact=True,reset_render_independent_Pillow_composite_max_error=error,alpha_exact=True,rich_vs_light_reset_mean_drop=float(images['rich-recipe'][:,:,:3].mean()-images['group-reset'][:,:,:3].mean()),sha256=hashes)
(out/'photo98-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native slider/group/full resets, preserved source and exact Cancel/Undo/Redo')
