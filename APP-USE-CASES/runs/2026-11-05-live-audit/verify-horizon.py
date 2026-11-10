"""Known horizon slope, both surfaces, repaired landscape and safe short input."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(prefix,n,ext='retropaint'):
    name=f'mouse-audit-horizon{prefix}-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=load(137,'baseline');defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];expected=copy.deepcopy(base);s=copy.deepcopy(defaults);s['angle']=-11.3;expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);reference=None
for name in ['paper','phone390','phone320','landscape-fixed']:
    assert load(137,name)==expected;image=load(137,name,'png');assert image.shape==(640,960,4)
    if reference is None:reference=image
    else:assert np.array_equal(image,reference)
raw=np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/geometry136-horizon.png').convert('RGBA')).astype(int)
def slope(a):
    ys,xs=np.where((a[:,:,0]<30)&(a[:,:,1]>145)&(a[:,:,2]>165)&(a[:,:,3]>128));assert len(xs)>1000;return float(np.polyfit(xs,ys,1)[0])
original_slope=slope(raw);fixed_slope=slope(reference);assert abs(original_slope-.2)<.002 and abs(fixed_slope)<.003
vertical=load(138,'vertical');vs=copy.deepcopy(defaults);vs['angle']=-45;vexpected=copy.deepcopy(base);vexpected['layers'][0]['photo']=dict(settings=vs,normal=vs,look='custom',lookActive=False);assert vertical==vexpected;vimage=load(138,'vertical','png');assert vimage.shape==reference.shape
for a,angle in [(reference,-11.3),(vimage,-45)]:
    y,x=np.mgrid[:640,:960];t=np.deg2rad(-angle);sx=np.cos(t)*(x+.5-480)-np.sin(t)*(y+.5-320)+479.5;sy=np.sin(t)*(x+.5-480)+np.cos(t)*(y+.5-320)+319.5;outside=(sx<-.5)|(sx>959.5)|(sy<-.5)|(sy>639.5);assert np.all(a[outside]==0)
before=load(138,'zero-before');assert 'photo'in before['layers'][0] and 'photo'not in base['layers'][0];assert load(138,'zero-fixed')==base;assert load(138,'short-fixed')==base
ui=json.loads((out/'horizon137-ui.json').read_text());fixed=next(r for r in ui if r['name']=='landscape844-fixed');assert fixed['paper']['right']<fixed['panelLeft']-8 and fixed['viewport']==dict(width=844,height=390);assert fixed['angle']==-11.3
short=json.loads((out/'horizon138-ui.json').read_text());assert short['zeroAfter']['look']=='normal' and short['shortAfter']['look']=='normal';assert any('longer line' in m for m in short['zeroAfter']['messages'])
report=dict(status='Pass',known_source_horizon_slope=original_slope,corrected_export_slope=fixed_slope,paper_phone390_phone320_repaired_landscape_same_angle_recipe_and_PNG_exact=True,LIVE058_short_landscape_full_paper_accessible=True,LIVE059_zero_and_short_samples_create_no_recipe_or_history_and_explain_longer_line=True,near_vertical_clamped_visible_minus45_safe=True,no_wrap_or_opaque_garbage_outside_source=True,source_other_settings_dimensions_exact=True,sha256=hashes)
(out/'horizon137-138-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native measured horizon, paper/mini/landscape mapping, safe zero/short/vertical and source')
