"""Native angle/scale bounds, full-source mapping, clear corners and reset."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
from geometry_oracle import verify_geometry
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-align139-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=load('baseline');canvas=np.array(Image.open(io.BytesIO(base64.b64decode(base['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int)
assert np.all(canvas[:,:,3]==0);objects=base['layers'][0]['objects'];assert len(objects)==1;obj=objects[0];assert obj['kind']=='raster' and obj['matrix']==[1,0,0,1,0,0] and obj['opacity']==1 and not obj.get('live');raw=np.array(Image.open(io.BytesIO(base64.b64decode(obj['image'].split(',')[1]))).convert('RGBA')).astype(int);assert np.array_equal(raw,np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/geometry136-grid.png').convert('RGBA')))
defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];ui=json.loads((out/'align139-ui.json').read_text());values={r['name']:r['values'] for r in ui};values['reset']={};images={};metrics={}
assert values['plus45']==dict(angle=45) and values['minus45']==dict(angle=-45);assert values['plus45-scale200']==dict(angle=45,zoom=200) and values['plus45-scale50']==dict(angle=45,zoom=50)
for name,changes in values.items():
    d=load(name);a=load(name,'png');images[name]=a;s=copy.deepcopy(defaults);s.update(changes);expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected
    metrics[name]=verify_geometry(a,raw,s)
assert np.all(images['plus45-scale200'][:,:,3]==255);assert np.count_nonzero(images['plus45-scale50'][:,:,3]==0)>np.count_nonzero(images['plus45'][:,:,3]==0)*2;assert images['plus45'][0,0,3]==0
assert np.array_equal(images['reset'],raw)
report=dict(status='Pass',native_angle_exact_minus45_plus45_and_scale50_200=True,source960x640_dimensions_frame_and_every_underlying_field_exact=True,independent_homogeneous_coordinate_and_premultiplied_alpha_mapping=True,scale200_intentionally_covers_all_rotated_clear_corners=True,scale50_exposes_more_clear_source_surrounding=True,no_wrap_or_colour_in_clear_pixels=True,group_reset_every_RGBA_exact=True,metrics=metrics,sha256=hashes)
(out/'align139-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native angle/scale endpoints, independent geometry, clear corners and exact source/reset')
