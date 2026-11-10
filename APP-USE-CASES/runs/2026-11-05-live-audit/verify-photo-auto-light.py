"""Native repeatable Auto light and constant/clear input safety."""
from pathlib import Path
import base64,hashlib,io,json,math
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';fixtures=root/'test-results/audit-2026-11-05/fixtures';hashes={}
def doc(n):
    name=f'mouse-audit-photo102-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def png(n):
    name=f'mouse-audit-photo102-{n}.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return np.array(Image.open(out/name).convert('RGBA')).astype(int)
first=doc('auto-first');assert doc('auto-repeat')==first
source=np.array(Image.open(fixtures/'photo-underexposed.png').convert('RGBA')).astype(int);raw=np.array(Image.open(io.BytesIO(base64.b64decode(first['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int);assert np.array_equal(raw,source)
result=png('auto-first');assert result.shape==source.shape and np.array_equal(result[:,:,3],source[:,:,3]);assert result[:,:,:3].mean()>source[:,:,:3].mean()+10;assert np.mean(np.max(result[:,:,:3],axis=2)>=254)<.01
def finite(value):
    if isinstance(value,dict):return all(finite(v) for v in value.values())
    if isinstance(value,list):return all(finite(v) for v in value)
    return not isinstance(value,(int,float)) or math.isfinite(value)
assert finite(first)
for name in ['constant','clear']:
    d=doc(name);assert finite(d);a=png(name);expected=np.array(Image.open(fixtures/f'tonal-{name}.png').convert('RGBA'));assert np.array_equal(a,expected)
ui=json.loads((out/'photo102-ui.json').read_text());assert ui['first']==ui['repeat'];assert all(float(x['value'])==0 for name in ['constant','clear'] for x in ui[name])
region=(slice(180,650),slice(420,1200));before=np.array(Image.open(out/'photo102-auto-before-settled.jpg')).astype(int)[region];after=np.array(Image.open(out/'photo102-auto-after-settled.jpg')).astype(int)[region];assert after.mean()>before.mean()+8
report=dict(status='Pass',repeat_after_reset_whole_document_exact=True,source_pixels_exact=True,natural_underexposed_mean_before=float(source[:,:,:3].mean()),natural_auto_mean_after=float(result[:,:,:3].mean()),highlight_clipping_fraction=float(np.mean(np.max(result[:,:,:3],axis=2)>=254)),clear_and_constant_inputs_finite_and_pixels_exact=True,visible_controls_repeat=True,settled_Before_After_expected_luminance_direction=True,early_frame_lag_screenshots_retained_but_excluded=True,sha256=hashes)
(out/'photo102-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native repeatable Auto light, natural tone improvement and clear/constant source safety')
