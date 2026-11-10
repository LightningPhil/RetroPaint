"""Native source-coordinate crop gestures, clamping and exact actual outputs."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-crop129-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA'))
base=json.loads((downloads/'mouse-audit-photo105-expanded.retropaint').read_text());d=load('moved-resized');assert load('cancelled')==d
c=d['crop'];assert np.allclose([c['x'],c['y'],c['width'],c['height']],[.3,.25,.6,.55],atol=1e-6,rtol=0)
expected=copy.deepcopy(base);expected['crop']=c
for key in ['settings','normal']:expected['layers'][0]['photo'][key]['crop']=c
expected['layers'][0]['photo']['look']='custom';assert d==expected
raw=np.array(Image.open(downloads/'mouse-audit-photo105-expanded.png').convert('RGBA'));x=round(c['x']*2100);y=round(c['y']*1398);w=round(c['width']*2100);h=round(c['height']*1398);assert np.array_equal(load('moved-resized','png'),raw[y:y+h,x:x+w])
ui=json.loads((out/'crop129-ui.json').read_text());rows={r['name']:r['crop'] for r in ui};assert rows['new']['width']==rows['moved']['width']==1050 and rows['new']['height']==rows['moved']['height']==629;assert abs(rows['new']['x']-420)<=1 and abs(rows['new']['y']-280)<=1;assert rows['moved']['x']-rows['new']['x']==210 and abs(rows['moved']['y']-rows['new']['y']-70)<=1
assert rows['zero-attempt']['width']>0 and rows['zero-attempt']['height']>0
outside=rows['outside-clamped'];assert outside['x']+outside['width']==2100 and outside['y']+outside['height']==1398
report=dict(status='Pass',native_source_area_new_move_resize_expected=True,move_preserves_size=True,export_every_RGBA_exact_independent_source_slice=True,zero_area_never_created=True,outside_drag_clamps_both_source_edges=True,Cancel_entire_saved_document_exact=True,source_and_all_other_settings_preserved=True,sha256=hashes)
(out/'crop129-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native crop draw/move/resize, exact source extent, nonzero/clamps and Cancel')
