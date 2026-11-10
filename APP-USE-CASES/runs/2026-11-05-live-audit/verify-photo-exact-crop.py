"""Native exact source crop, invalid-field atomicity, ratio and history."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(prefix,n):
    name=f'mouse-audit-crop{prefix}-{n}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def png(prefix,n):
    name=f'mouse-audit-crop{prefix}-{n}.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return np.array(Image.open(out/name).convert('RGBA')).astype(int)
baseline=doc(110,'baseline');raw=np.array(Image.open(io.BytesIO(base64.b64decode(baseline['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int);defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];exact=doc(111,'exact');crop=dict(x=100/960,y=50/640,width=200/960,height=100/640)
def expected(frame):
    settings=copy.deepcopy(defaults);settings['crop']=frame;d=copy.deepcopy(baseline);d['crop']=frame;d['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False);return d
assert exact==expected(crop)==doc(110,'exact-native');assert np.array_equal(png(111,'exact'),raw[50:150,100:300]);assert doc(111,'undone')==baseline and doc(111,'redone')==exact
for name in ['zero','negative','outside-position','oversize','empty','overflow','subpixel','phone-zero']:assert doc(111,name+'-rejected')==exact
assert doc(111,'rejections-undone')==baseline and doc(111,'rejections-redone')==exact
square=doc(111,'square-rejected');s=square['crop'];assert np.allclose([s['x']*960,s['y']*640,s['width']*960,s['height']*640],[150,50,100,100],atol=1e-8,rtol=0);assert square==expected(s)
large=doc(111,'square300');s=large['crop'];assert np.allclose([s['x']*960,s['y']*640,s['width']*960,s['height']*640],[150,50,300,300],atol=1e-8,rtol=0);assert large==expected(s);assert np.array_equal(png(111,'square300'),raw[50:350,150:450])
failed=doc(110,'zero-before');assert abs(failed['crop']['width']*960-1)<1e-8;assert png(110,'zero-before').shape==(100,1,4)
ui=json.loads((out/'crop111-ui.json').read_text(encoding='utf-8'));assert len(ui)==10
for row in ui:
    if 'restored' in row:assert any('Choose crop coordinates' in s for s in row['messages'])
    if row['name']=='ratio-incompatible':assert row['before']==row['after'] and any('chosen crop ratio' in s for s in row['messages'])
    if row['name']=='phone-zero':assert row['viewport']==dict(width=320,height=568)
report=dict(status='Pass',source_coordinate100_50_size200_100_PNG_every_RGBA_exact=True,valid_square300_output_exact=True,zero_negative_outside_oversize_empty_overflow_subpixel_whole_document_preserved=True,ratio_incompatible_keeps_current_square=True,all_source_and_other_adjustments_preserved=True,exact_frame_Undo_Redo_and_rejections_add_no_history=True,native_phone320_zero_rejection=True,before_fix_failure='Native width0 silently clamped to1; saved PNG100x1 retained. Initial browser-helper appending/uncommitted attempt excluded; real browser-native Ctrl+A/typeText/Tab route used.',sha256=hashes)
(out/'crop110-111-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native exact crop pixels, saved-frame rejection, ratio, phone and exact history')
