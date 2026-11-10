"""Independent full-source radial vignette and cropped-frame policy."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-vignette125-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=json.loads((downloads/'mouse-audit-photo105-expanded.retropaint').read_text());source=np.array(Image.open(downloads/'mouse-audit-photo105-expanded.png').convert('RGBA')).astype(int);ui=json.loads((out/'vignette125-ui.json').read_text());images={}
def predicted(s):
    h,w,_=source.shape;y,x=np.mgrid[:h,:w];c=s['crop'];cx=(c['x']+c['width']/2)*w;cy=(c['y']+c['height']/2)*h;rx=c['width']*w/2;ry=c['height']*h/2;r=s['roundness']/100;distance=np.hypot((x+.5-cx)/(rx*(1-r)+min(rx,ry)*r),(y+.5-cy)/(ry*(1-r)+min(rx,ry)*r))/2**.5;start=s['midpoint']/100*.8;end=start+.08+s['feather']/100*(1-start);t=np.clip((distance-start)/(end-start),0,1);v=t*t*(3-2*t)*s['vignette']/100;rgb=source[:,:,:3];rgb=rgb*(1+v[:,:,None]*.85) if s['vignette']<0 else rgb+(255-rgb)*v[:,:,None]*.85;a=source.copy();a[:,:,:3]=np.rint(rgb).astype(int);xx=round(c['x']*w);yy=round(c['y']*h);return a[yy:yy+round(c['height']*h),xx:xx+round(c['width']*w)]
for name in ['dark','light','reset','cropped']:
    d=load(name);a=load(name,'png');images[name]=a;foundation=copy.deepcopy(base) if name!='cropped' else json.loads((downloads/'mouse-audit-photo105-fresh-normal.retropaint').read_text());expected=copy.deepcopy(foundation);value=0 if name=='reset' else ui[name]
    for key in ['settings','normal']:expected['layers'][0]['photo'][key]['vignette']=value
    expected['layers'][0]['photo']['look']='custom';assert d==expected
    p=predicted(d['layers'][0]['photo']['settings']);assert a.shape==p.shape and np.max(abs(a-p))<=1
    assert np.array_equal(a[:,:,3],p[:,:,3])
assert np.array_equal(images['reset'],source);assert np.array_equal(load('panel-reopened','png'),images['cropped'])
centre=(slice(500,900),slice(800,1300));assert np.array_equal(images['dark'][centre],source[centre]) and np.array_equal(images['light'][centre],source[centre]);assert np.mean(images['dark'][:100,:100,:3])<np.mean(source[:100,:100,:3])<np.mean(images['light'][:100,:100,:3])
report=dict(status='Pass',natural_dark_light_corner_directions=True,central_subject_exactly_protected=True,independent_radial_formula_max1RGBA=True,cropped1680x1118_frame_anchor_verified=True,panel_navigation_reopen_export_every_RGBA_exact=True,source_and_other_recipe_document_exact=True,reset_every_RGBA_exact=True,sha256=hashes)
(out/'vignette125-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS natural vignette directions/centre, independent crop anchor and stable output/reset')
