"""Native relative Temperature/Tint, independent controls, skin and alpha."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(n):
    name=f'mouse-audit-colour107-{n}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def png(n):
    name=f'mouse-audit-colour107-{n}.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return np.array(Image.open(out/name).convert('RGBA')).astype(int)
baseline=doc('baseline');source=np.array(Image.open(io.BytesIO(base64.b64decode(baseline['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int);original=np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/colour107-patches.png').convert('RGBA')).astype(int);assert np.array_equal(source[:,:,3],original[:,:,3])
for alpha in [64,128,192,255]:assert np.max(abs(source[:,:,:3][source[:,:,3]==alpha]-original[:,:,:3][source[:,:,3]==alpha]))<=np.ceil(255/(2*alpha))
images={};defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'] # Explicit defaults independently checked by verify-photo-resets.py.
for name,temperature,tint in [('temperature-warm50',50,0),('temperature-cool50',-50,0),('temperature-reset',0,0),('temperature20',20,0),('tint-magenta50',20,50),('tint-green50',20,-50),('tint-reset',20,0)]:
    d=doc(name);a=png(name);images[name]=a;settings=copy.deepcopy(defaults);settings.update(temperature=temperature,tint=tint);expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False);assert expected==d
    for kind in ['settings','normal']:assert d['layers'][0]['photo'][kind]['temperature']==temperature and d['layers'][0]['photo'][kind]['tint']==tint
    assert np.array_equal(a[:,:,3],source[:,:,3]);assert np.array_equal(a[source[:,:,3]==0],source[source[:,:,3]==0])
for x in [680,760,840]:
    warm=images['temperature-warm50'][72,x,:3];cool=images['temperature-cool50'][72,x,:3];assert warm[0]>warm[1]>warm[2] and cool[0]<cool[1]<cool[2]
assert np.array_equal(images['temperature-reset'],source);assert np.array_equal(images['tint-reset'],images['temperature20'])
for x in [760,920]:
    cast=lambda a:float(a[72,x,1]-(a[72,x,0]+a[72,x,2])/2)
    assert cast(images['tint-magenta50'])<cast(images['temperature20'])<cast(images['tint-green50'])
assert np.ptp(images['tint-magenta50'][72,920,:3])>50 and np.ptp(images['tint-green50'][72,920,:3])>50
report=dict(status='Pass',relative_warm_cool_opposite_shifts=True,neutral_and_skin_samples_checked=True,tint_labels_match_green_magenta_direction=True,temperature20_independent_of_tint=True,not_global_desaturation=True,all_alpha_and_clear_margins_exact=True,temperature_reset_pixels_exact=True,tint_reset_exact_temperature20_reference=True,underlying_source_and_other_document_data_exact=True,sha256=hashes)
(out/'colour107-balance-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native relative Temperature/Tint, skin direction, independent settings, exact alpha and resets')
