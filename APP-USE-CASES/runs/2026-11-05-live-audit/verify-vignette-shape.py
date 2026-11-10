"""Uniform known patch, independent radial maps and endpoint geometry metrics."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-vignette126-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=load('baseline');raw=np.array(Image.open(io.BytesIO(base64.b64decode(base['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int);defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];ui=json.loads((out/'vignette126-ui.json').read_text());images={};h,w,_=raw.shape;y,x=np.mgrid[:h,:w];visible=raw[:,:,3]>0;opaque=raw[:,:,3]==255
for row in ui:
    name=row['name'];d=load(name);a=load(name,'png');images[name]=a;s=copy.deepcopy(defaults);s.update(row['values']);expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected
    r=s['roundness']/100;rx=w/2*(1-r)+min(w,h)/2*r;ry=h/2;distance=np.hypot((x+.5-w/2)/rx,(y+.5-h/2)/ry)/2**.5;start=s['midpoint']/100*.8;end=start+.08+s['feather']/100*(1-start);t=np.clip((distance-start)/(end-start),0,1);v=t*t*(3-2*t)*s['vignette']/100;predicted=raw[:,:,:3]*(1+v[:,:,None]*.85) if s['vignette']<0 else raw[:,:,:3]+(255-raw[:,:,:3])*v[:,:,None]*.85;error=abs(a[:,:,:3]-np.rint(predicted));assert error[opaque].max()<=1 and error[visible].max()<=2
    assert np.array_equal(a[:,:,3],raw[:,:,3]) and np.array_equal(a[~visible],raw[~visible])
for key in ['midpoint','feather','roundness']:
    for value in [0,100]:assert next(r['values'][key] for r in ui if r['name']==key+str(value))==value
modified=lambda n:int(np.count_nonzero((images[n][:,:,0]<127)&opaque));transition=lambda n:int(np.count_nonzero((images[n][:,:,0]>77)&(images[n][:,:,0]<126)&opaque));protected=lambda n:int(np.count_nonzero((images[n][:,:,0]==128)&opaque))
assert modified('midpoint0')>modified('midpoint100')*2
assert transition('feather100')>transition('feather0')*2
assert protected('roundness0')>protected('roundness100') and np.count_nonzero(images['roundness0']!=images['roundness100'])>10000
assert next(r['values']['vignette'] for r in ui if r['name']=='amount-minus100')==-100 and next(r['values']['vignette'] for r in ui if r['name']=='amount-plus100')==100
report=dict(status='Pass',all_three_shape_controls_both_exact_endpoints=True,amount_both_exact_endpoints=True,independent_radial_formula_matches_known_uniform_patch=True,midpoint_reach_modified_pixels=[modified('midpoint0'),modified('midpoint100')],feather_transition_pixels=[transition('feather0'),transition('feather100')],roundness_protected_pixels=[protected('roundness0'),protected('roundness100')],all_controls_independent_saved_source_alpha_clear_border_exact=True,sha256=hashes)
(out/'vignette126-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native vignette shape/endpoints, independent maps/reach/softness/contour and alpha')
