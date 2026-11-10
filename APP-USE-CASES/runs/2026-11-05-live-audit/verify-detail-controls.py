"""Independent edge/scale/variance observations from native actual downloads."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(name,ext='retropaint'):
    filename=f'mouse-audit-detail121-{name}.{ext}';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/filename).convert('RGBA')).astype(int)
base=load('baseline');raw=np.array(Image.open(io.BytesIO(base64.b64decode(base['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int);defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];ui=json.loads((out/'detail121-ui.json').read_text());settings={r['name']:r['values'] for r in ui};settings['texture-clarity']={**settings['clarity'],**settings['texture-clarity']};settings['texture-only-reset']=settings['clarity'];settings['sharp-reset']={};settings['noise-reset']={};images={}
assert settings['sharp150-narrow']==dict(sharpness=150,radius=.5)
assert settings['sharp150-wide']==dict(sharpness=150,radius=3)
assert settings['noise100-both']==dict(noise=100,colourNoise=100)
for name,values in settings.items():
    d=load(name);a=load(name,'png');images[name]=a;s=copy.deepcopy(defaults);s.update(values);expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected,name
    assert a.shape==raw.shape and np.array_equal(a[:,:,3],raw[:,:,3]) and np.array_equal(a[raw[:,:,3]==0],raw[raw[:,:,3]==0]),name
assert np.array_equal(images['sharp-reset'],raw) and np.array_equal(images['noise-reset'],raw)
assert np.array_equal(images['texture-only-reset'],images['clarity'])
def region(a,box):x0,y0,x1,y1=box;return a[y0:y1,x0:x1,:3]
def change(name,box):return float(np.mean(abs(region(images[name],box)-region(raw,box))))
noise=[48,272,464,432];fine=[560,496,976,624];broad=[48,496,464,624]
assert change('sharp-high',noise)>change('sharp-low',noise)*1.5
assert change('threshold-high',noise)<change('sharp-high',noise)*.1
assert np.count_nonzero(np.any(images['radius-wide'][:,:,:3]!=raw[:,:,:3],axis=2))>np.count_nonzero(np.any(images['sharp-high'][:,:,:3]!=raw[:,:,:3],axis=2))
texture_fine=change('texture',fine);texture_broad=change('texture',broad);clarity_fine=change('clarity',fine);clarity_broad=change('clarity',broad)
assert texture_fine>texture_broad*2 and clarity_broad>texture_broad*2
assert not np.array_equal(images['texture'],images['clarity'])
luma=lambda a:a@np.array([.2126,.7152,.0722]);variance=lambda a:float(np.var(luma(region(a,noise))))
before_var=variance(raw);after_var=variance(images['noise-luma']);assert after_var<before_var*.5
colour_box=[560,272,976,432];chroma=lambda a:float(np.mean(np.ptp(region(a,colour_box),axis=2)**2));before_chroma=chroma(raw);after_chroma=chroma(images['noise-colour']);assert after_chroma<before_chroma*.5
assert np.array_equal(region(images['noise-colour'],noise),region(raw,noise))
assert np.max(abs(region(images['noise-colour'],[48,688,240,720])-region(raw,[48,688,240,720])))<=1
assert np.max(abs(region(images['noise-colour'],[272,688,464,720])-region(raw,[272,688,464,720])))<=1
assert np.mean(np.ptp(region(images['noise-colour'],[48,688,240,720]),axis=2))>150
for name in ['noise-luma','noise-colour','noise-both']:
    profile=images[name][100,32:480,0];assert np.argmax(np.diff(profile))==223 and profile[100]==32 and profile[300]==224,name
report=dict(status='Pass',amount_increases_strength=True,radius_increases_neighbourhood=True,threshold_protects_flat_noise=True,fine_and_broad_scale_separated=dict(texture_fine=texture_fine,texture_broad=texture_broad,clarity_fine=clarity_fine,clarity_broad=clarity_broad),texture_only_reset_retains_clarity_every_pixel_exact=True,luminance_variance=dict(before=before_var,after=after_var),colour_spread_squared=dict(before=before_chroma,after=after_chroma),colour_only_keeps_neutral_noise_exact=True,strong_edge_position_and_levels_preserved=True,source_alpha_dimensions_clear_padding_and_all_other_settings_exact=True,group_resets_every_RGBA_exact=True,sha256=hashes)
(out/'detail121-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native detail amount/radius/threshold, distinct texture/clarity and seeded noise metrics')
