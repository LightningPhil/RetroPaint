"""Native same-source neutral picking, wide-preview regression and safe samples."""
from pathlib import Path
import base64,copy,hashlib,io,json,math
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(n):
    name=f'mouse-audit-colour109-{n}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def png(n):
    name=f'mouse-audit-colour109-{n}.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return np.array(Image.open(out/name).convert('RGBA')).astype(int)
def raw(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int)
baseline=json.loads((downloads/'mouse-audit-colour107-baseline.retropaint').read_text());wide=doc('wide-baseline');defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];paper=doc('paper');assert doc('mini')==paper;assert np.array_equal(png('paper'),png('mini'))
widepaper=doc('wide-paper');assert doc('wide-mini-fixed')==doc('wide-mini320-fixed')==widepaper
assert np.array_equal(png('wide-paper'),png('wide-mini-fixed')) and np.array_equal(png('wide-paper'),png('wide-mini320-fixed'))
for source,d,image in [(baseline,paper,png('paper')),(wide,widepaper,png('wide-paper'))]:
    gains=d['layers'][0]['photo']['settings']['balance'];settings=copy.deepcopy(defaults);settings['balance']=gains;expected=copy.deepcopy(source);expected['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False);assert d==expected
    assert all(math.isfinite(v) and .25<=v<=4 for v in gains);assert np.array_equal(image[:,:,3],raw(source)[:,:,3])
assert paper['layers'][0]['photo']['settings']['balance']==widepaper['layers'][0]['photo']['settings']['balance'];assert np.ptp(png('paper')[576,240,:3])==0 and np.ptp(png('wide-paper')[120,60,:3])==0
failed=doc('wide-mini-before');failedpng=png('wide-mini-before');assert failed['layers'][0]['photo']['settings']['balance']==[.25,4,4];assert failedpng[120,60,:3].tolist()==[80,230,205]
assert doc('wide-padding-safe')==wide
for name in ['transparent','outside']:assert doc(name+'-safe')==baseline and np.array_equal(png(name+'-safe'),raw(baseline))
for name in ['black','white']:
    d=doc(name+'-safe');gains=d['layers'][0]['photo']['settings']['balance'];assert all(math.isfinite(v) and abs(v-1)<1e-12 for v in gains)
    settings=copy.deepcopy(defaults);settings['balance']=gains;expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False);assert d==expected;assert np.array_equal(png(name+'-safe'),raw(baseline))
safety=json.loads((out/'colour109-safety-ui.json').read_text(encoding='utf-8'));assert {s['name'] for s in safety}=={'wide-padding','black','white','transparent','outside'}
for row in safety:
    if row['name'] in ['transparent','wide-padding']:assert row['look']=='normal' and any('Choose a painted grey or white area.' in s for s in row['messages'])
points=json.loads((out/'colour109-wide-fixed-points.json').read_text());assert points['phone320']['viewport']==dict(width=320,height=568)
report=dict(status='Pass',standard_paper_and_phone_preview_whole_project_and_PNG_exact=True,wide_phone390_and320_match_paper_exactly=True,same_known_cast_neutralised=True,no_paint_dot_original_source_and_other_fields_exact=True,black_and_clipped_white_finite_neutral_and_pixels_exact=True,clear_outside_and_preview_padding_rejected_without_document_changes=True,before_fix_failure={'gains':[.25,4,4],'cast_rgb':[80,230,205]},fix='LIVE-055 accounts for source-to-bitmap and bitmap-to-CSS contain scaling; rejects neutral samples outside the rendered image; crop handle distance uses same display scale.',sha256=hashes)
(out/'colour109-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native neutral sampling paper/standard+wide phone previews, source preservation and safe rejected samples')
