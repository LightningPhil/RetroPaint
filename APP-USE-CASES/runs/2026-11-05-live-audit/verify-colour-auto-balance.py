"""Native bounded Auto WB, neutral cast, exact reversal and safe alternatives."""
from pathlib import Path
import base64,copy,hashlib,io,json,math
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(n):
    name=f'mouse-audit-colour108-{n}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def png(n):
    name=f'mouse-audit-colour108-{n}.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return np.array(Image.open(out/name).convert('RGBA')).astype(int)
def raw(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int)
defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];cast=doc('cast-baseline');balanced=doc('cast-balanced');art=doc('art-baseline');artbalanced=doc('art-balanced')
for before,after in [(cast,balanced),(art,artbalanced)]:
    gains=after['layers'][0]['photo']['settings']['balance'];assert len(gains)==3 and all(isinstance(v,(int,float)) and math.isfinite(v) and .25<=v<=4 for v in gains)
    assert abs(math.prod(gains)-1)<1e-9
    settings=copy.deepcopy(defaults);settings['balance']=gains;expected=copy.deepcopy(before);expected['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False);assert after==expected
result=png('cast-balanced');source=raw(cast);assert np.array_equal(result[:,:,3],source[:,:,3]);assert np.ptp(source[300,500,:3])==45 and np.ptp(result[300,500,:3])<=1;assert abs(result[300,500,:3].mean()-127)<=1
assert doc('cast-undone')==cast and doc('cast-redone')==balanced
empty=doc('empty-balanced');assert empty['layers'][0]['photo']['settings']['balance']==[1,1,1];assert np.array_equal(png('empty-balanced'),np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/tonal-clear.png').convert('RGBA')))
reset=doc('art-reset');expected=copy.deepcopy(art);expected['layers'][0]['photo']=dict(settings=defaults,normal=defaults,look='normal',lookActive=False);assert reset==expected;assert np.array_equal(png('art-reset'),raw(art))
ui=json.loads((out/'colour108-ui.json').read_text(encoding='utf-8'));assert ui['before']==ui['artBefore']=='Before · original pixels';assert ui['artReset']=='normal';assert all(float(v['value'])==0 for v in ui['emptyControls'])
region=(slice(300,500),slice(650,1000));before=np.array(Image.open(out/'colour108-cast-before.jpg')).astype(int)[region];after=np.array(Image.open(out/'colour108-cast-after.jpg')).astype(int)[region];assert np.median(np.ptp(before,axis=2))>35 and np.median(np.ptp(after,axis=2))<3
report=dict(status='Pass',finite_bounded_gains_and_unit_product=True,known_cast154_123_109_becomes=result[300,500,:3].tolist(),alpha_exact=True,underlying_originals_and_other_fields_exact=True,Undo_Redo_whole_document_exact=True,empty_input_neutral_gains_and_pixels_exact=True,strong_artistic_scene_Before_and_Reset_available=True,artistic_reset_pixels_exact=True,settled_comparison_shows_original_and_balanced_cast=True,sha256=hashes)
(out/'colour108-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native Auto WB bounded gains, neutral cast, exact history/source, empty and artistic alternatives')
