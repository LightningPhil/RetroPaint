"""Natural photo Pop must equal its three explicit manual contributions."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-pop124-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA'))
base=json.loads((downloads/'mouse-audit-photo105-expanded.retropaint').read_text());ui=json.loads((out/'pop124-ui.json').read_text());assert ui==dict(pop=40,clarity=24,dehaze=6,vibrance=8)
for name,changes in [('moderate',dict(pop=40)),('reset',{}),('manual-equivalent',dict(clarity=24,dehaze=6,vibrance=8))]:
    d=load(name);expected=copy.deepcopy(base)
    for key in ['settings','normal']:expected['layers'][0]['photo'][key].update(changes)
    expected['layers'][0]['photo']['look']='custom';assert d==expected,name
pop=load('moderate','png');manual=load('manual-equivalent','png');reset=load('reset','png');original=np.array(Image.open(downloads/'mouse-audit-photo105-expanded.png').convert('RGBA'));assert pop.shape==(1398,2100,4) and np.array_equal(pop,manual);assert np.array_equal(reset,original);assert np.array_equal(pop[:,:,3],original[:,:,3]);assert np.count_nonzero(pop!=original)>100000
report=dict(status='Pass',native_natural_photo_Before_and_Pop40=True,Pop40_every_RGBA_equals_manual_clarity24_vibrance8_dehaze6=True,reset_every_RGBA_equals_original_manual_baseline=True,source_and_other_recipe_and_document_exact=True,full_source_dimensions_and_alpha_exact=True,initial_small_slider_click_inside_thumb_did_not_change_dehaze_corrected_by_native_drag=True,sha256=hashes)
(out/'pop124-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native Pop40 exact manual equivalence, reset/source/alpha and full-size natural photo')
