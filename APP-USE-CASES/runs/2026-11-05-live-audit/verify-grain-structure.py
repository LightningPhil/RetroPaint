"""Fixed-source grain spatial scale, roughness structure and colour/alpha metrics."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-grain128-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=load('baseline');raw=np.array(Image.open(io.BytesIO(base64.b64decode(base['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int);defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];ui=json.loads((out/'grain128-ui.json').read_text());values={r['name']:r['values'] for r in ui};values['reset']={};images={}
assert values['size-half']==dict(grain=40,grainSize=.5) and values['size-three']==dict(grain=40,grainSize=3);assert values['roughness0']==dict(grain=40,grainRoughness=0) and values['roughness100']==dict(grain=40,grainRoughness=100) and values['amount100']==dict(grain=100)
for name,changes in values.items():
    d=load(name);a=load(name,'png');images[name]=a;s=copy.deepcopy(defaults);s.update(changes);expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected
    assert a.shape==raw.shape and np.array_equal(a[:,:,3],raw[:,:,3]) and np.array_equal(a[raw[:,:,3]==0],raw[raw[:,:,3]==0])
    mask=raw[:,:,3]==255;source=raw[:,:,:3][mask].astype(float);result=a[:,:,:3][mask];nonzero=source>0;denom=np.maximum(source,1);lower=np.where(nonzero,(result-.50001)/denom,-np.inf).max(axis=1);upper=np.where(nonzero,(result+.50001)/denom,np.inf).min(axis=1);assert np.all(lower<=upper);assert np.all(result[~nonzero]==0)
assert np.array_equal(images['reset'],raw)
field=lambda n:images[n][272:432,48:464,0]-raw[272:432,48:464,0]
def correlation(n):
    a=field(n);return float(np.corrcoef(a[:,:-1].ravel(),a[:,1:].ravel())[0,1])
c={name:correlation(name) for name in ['default','size-half','size-three','roughness0','roughness100']};assert c['size-three']>c['size-half']+.3;assert c['roughness100']>c['roughness0']+.1
assert not np.array_equal(field('roughness100'),field('roughness0'));assert np.std(field('amount100'))>np.std(field('default'))*2
report=dict(status='Pass',same_fixed_source_and_Amount40=True,Size_exact_half_to_three_changes_spatial_scale=True,Roughness_exact0_to100_changes_structure=True,neighbour_correlations=c,amount100_variance_greater=True,all_opaque_RGB_admit_common_achromatic_gain=True,alpha_clear_padding_source_other_settings_exact=True,reset_every_RGBA_exact=True,sha256=hashes)
(out/'grain128-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native grain size/roughness/amount endpoints, spatial metrics, hue/alpha and reset')
