"""Actual grain redraw/reopen determinism and common luminance-gain colour oracle."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-grain127-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=json.loads((downloads/'mouse-audit-photo105-expanded.retropaint').read_text());raw=np.array(Image.open(downloads/'mouse-audit-photo105-expanded.png').convert('RGBA')).astype(int);ui=json.loads((out/'grain127-ui.json').read_text());images={}
for name,key in [('low','amount'),('high','high')]:
    d=load(name);a=load(name,'png');images[name]=a;expected=copy.deepcopy(base)
    for kind in ['settings','normal']:expected['layers'][0]['photo'][kind]['grain']=ui[key]
    expected['layers'][0]['photo']['look']='custom';assert d==expected
    assert a.shape==raw.shape and np.array_equal(a[:,:,3],raw[:,:,3]);source=raw[:,:,:3].astype(float);result=a[:,:,:3];nonzero=source>0;denom=np.maximum(source,1);lower=np.where(nonzero,(result-.50001)/denom,-np.inf).max(axis=2);upper=np.where(nonzero,(result+.50001)/denom,np.inf).min(axis=2);assert np.all(lower<=upper),'No common achromatic gain could produce some pixel';assert np.all(result[~nonzero]==0)
high=images['high'];assert np.array_equal(load('redraw','png'),high) and np.array_equal(load('reopened','png'),high)
low_difference=images['low'][:,:,:3]-raw[:,:,:3];high_difference=high[:,:,:3]-raw[:,:,:3];low_variation=float(np.mean(abs(low_difference)));high_variation=float(np.mean(abs(high_difference)));assert high_variation>low_variation*1.8 and low_variation>.1
assert np.corrcoef(low_difference.ravel(),high_difference.ravel())[0,1]>.98
report=dict(status='Pass',same_recipe_zoom_BeforeAfter_redraw_and_actual_project_reopen_fullPNG_every_RGBA_exact=True,natural_full2100x1398_source_and_other_recipe_fields_exact=True,all_RGB_pixels_admit_one_common_luminance_gain_within8bitrounding=True,zero_channels_and_alpha_preserved=True,low_mean_variation=low_variation,high_mean_variation=high_variation,higher_amount_increases_fixed_pattern=True,sha256=hashes)
(out/'grain127-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS natural grain fixed pattern across redraw/zoom/reopen, achromatic gain and amount')
