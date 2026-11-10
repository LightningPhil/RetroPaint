"""Native TONAL outputs against independent sRGB and patch arithmetic."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name=f'mouse-audit-photo99-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def png(n):
    name=f'mouse-audit-photo99-{n}.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return np.array(Image.open(out/name).convert('RGBA')).astype(int)
baseline=doc('tonal-baseline');source=np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/TONAL-alpha.png').convert('RGBA')).astype(int)
raw=np.array(Image.open(io.BytesIO(base64.b64decode(baseline['layers'][0]['image'].split(',')[1]))).convert('RGBA'));assert np.array_equal(raw,source)
mask=source[:,:,3]>0;v=source[:,:,:3]/255;linear=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);errors={};outputs={}
for name,key,value in [('exposure-plus1','exposure',1),('exposure-minus1','exposure',-1),('brightness-plus30','brightness',30),('contrast-plus50','contrast',50),('contrast-minus50','contrast',-50),('contrast-maximum','contrast',100),('contrast-minimum','contrast',-100),('brightness-reset','brightness',0),('contrast-reset','contrast',0)]:
    d=doc(name);a=png(name);outputs[name]=a;assert np.array_equal(a[:,:,3],source[:,:,3]);assert np.array_equal(a[:,:,0],a[:,:,1]) and np.array_equal(a[:,:,1],a[:,:,2]);expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=d['layers'][0]['photo'];assert expected==d
    for kind in ['settings','normal']:assert d['layers'][0]['photo'][kind][key]==value
    if name.startswith('exposure'):
        lin=np.clip(linear*2**value,0,1);expected=np.rint(255*np.where(lin<=.0031308,lin*12.92,1.055*lin**(1/2.4)-.055));errors[name]=int(np.max(abs(a[:,:,:3][mask]-expected[mask])));assert errors[name]<=1
    if name.endswith('reset'):assert np.array_equal(a,source)
patches=[123,315,507,699,891];brightness=[int(outputs['brightness-plus30'][192,x,0]) for x in patches];assert all(a>b for a,b in zip(brightness,[32,64,128,192,224]));assert not np.array_equal(outputs['brightness-plus30'],outputs['exposure-plus1'])
sep=lambda a:int(a[80,640,0]-a[80,384,0]) # Source neutral160 vs96.
assert sep(outputs['contrast-plus50'])>64>sep(outputs['contrast-minus50'])
report=dict(status='Pass',all_ramp_and_patch_pixels_independent_exposure_max_errors=errors,brightness_patch_values=brightness,brightness_distinct_from_exposure=True,neutral_rgb_and_alpha_exact_every_variant=True,contrast_separation={'baseline':64,'plus50':sep(outputs['contrast-plus50']),'minus50':sep(outputs['contrast-minus50'])},extreme_contrast_valid_RGBA=True,brightness_and_contrast_reset_pixels_exact=True,all_source_document_data_preserved=True,sha256=hashes)
(out/'photo99-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native exposure arithmetic, brightness, contrast extremes, exact alpha and resets')
