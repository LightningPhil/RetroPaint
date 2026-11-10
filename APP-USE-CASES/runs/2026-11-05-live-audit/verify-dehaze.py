"""Known haze contrast, opposite directions and independent pixel arithmetic."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-haze122-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=load('baseline');raw=np.array(Image.open(io.BytesIO(base64.b64decode(base['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int);defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];ui=json.loads((out/'haze122-ui.json').read_text());values={r['name']:r['value'] for r in ui};values['reset']=0;images={}
for name,value in values.items():
    d=load(name);a=load(name,'png');images[name]=a;s=copy.deepcopy(defaults);s['dehaze']=value;expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected
    assert a.shape==raw.shape and np.array_equal(a[:,:,3],raw[:,:,3]) and np.array_equal(a[raw[:,:,3]==0],raw[raw[:,:,3]==0])
    prediction=np.rint(np.clip((raw[:,:,:3]/255-.09*value/100)/(1-.18*value/100),0,1)*255);error=abs(a[:,:,:3]-prediction);visible=raw[:,:,3]>0;bounds=np.maximum(1,np.ceil(255/(2*np.maximum(1,raw[:,:,3]))));assert np.all(error.max(axis=2)[visible]<=bounds[visible])
    opaque=raw[:,:,3]==255;assert error[opaque].max()<=1
    grey=(raw[:,:,0]==raw[:,:,1])&(raw[:,:,1]==raw[:,:,2])&visible;assert np.all(a[:,:,0][grey]==a[:,:,1][grey]) and np.all(a[:,:,1][grey]==a[:,:,2][grey])
contrast=lambda a:int(a[100,400,0]-a[100,100,0]);assert contrast(images['negative100'])<contrast(images['negative'])<contrast(raw)<contrast(images['positive'])<contrast(images['positive100']);assert values['positive100']==100 and values['negative100']==-100
assert np.array_equal(images['reset'],raw)
report=dict(status='Pass',positive_negative_opposite_contrast_order=True,extremes_plus_minus100_valid=True,independent_pixel_formula_with_declared_alpha_quantization=True,neutral_patches_remain_neutral=True,alpha_clear_source_other_settings_exact=True,reset_every_RGBA_exact=True,contrast={n:contrast(a) for n,a in images.items()},sha256=hashes)
(out/'haze122-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native dehaze directions/extremes, independent RGB and exact reset/source/alpha')
