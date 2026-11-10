"""Known projective input convergence and independent homogeneous output maps."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
from geometry_oracle import verify_geometry
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};metrics={};convergence={}
def load(name,stage,ext='retropaint'):
    filename=f'mouse-audit-persp141-{name}-{stage}.{ext}';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/filename).convert('RGBA')).astype(int)
def source(d):
    layer=d['layers'][0];canvas=np.array(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))).convert('RGBA')).astype(int)
    if not layer.get('objects'):return canvas
    assert np.all(canvas[:,:,3]==0);objects=layer['objects'];assert len(objects)==1;obj=objects[0];assert obj['kind']=='raster' and obj['matrix']==[1,0,0,1,0,0] and obj['opacity']==1 and not obj.get('live');return np.array(Image.open(io.BytesIO(base64.b64decode(obj['image'].split(',')[1]))).convert('RGBA')).astype(int)
def spread(a,axis):
    purple=(a[:,:,0]>80)&(a[:,:,0]<160)&(a[:,:,1]<70)&(a[:,:,2]>120)&(a[:,:,3]>128);spans=[]
    for position in ([240,400] if axis=='vertical' else [320,640]):
        points=np.flatnonzero(purple[position,:] if axis=='vertical' else purple[:,position]);middle=480 if axis=='vertical' else 320;left=points[points<middle];right=points[points>middle];assert len(left)>1 and len(right)>1;spans.append(float(np.median(right)-np.median(left)))
    return abs(spans[1]-spans[0])
defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];ui=json.loads((out/'persp141-ui.json').read_text());images={}
for axis in ['vertical','horizontal']:
    for sign in ['positive','negative']:
        name=axis+'-'+sign;base=load(name,'baseline');raw=source(base)
        for stage in ['corrected','extreme']:
            row=next(r for r in ui if r['name']==name and r['stage']==stage);value=row['value'];assert value==(49 if sign=='positive' else -49) if stage=='corrected' else value==(75 if sign=='positive' else -75)
            s=copy.deepcopy(defaults);s[axis]=value;d=load(name,stage);a=load(name,stage,'png');images[name+'-'+stage]=a;expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected
            metrics[name+'-'+stage]=verify_geometry(a,raw,s)
            if stage=='corrected':
                original=spread(raw,axis);corrected=spread(a,axis);assert original>20 and corrected<=original*.15 and corrected<=3;convergence[name]=dict(before=original,after=corrected)
name='horizontal-positive';base=load(name,'baseline');raw=source(base)
for stage,changes in [('vertical-only',dict(vertical=49)),('combined',dict(vertical=49,horizontal=49)),('reset',{})]:
    d=load(name,stage);a=load(name,stage,'png');s=copy.deepcopy(defaults);s.update(changes);expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected;metrics[stage]=verify_geometry(a,raw,s)
    if stage=='vertical-only':assert spread(a,'horizontal')>spread(images[name+'-corrected'],'horizontal')+15
    if stage=='reset':assert np.array_equal(a,raw)
report=dict(status='Pass',both_axes_both_signs_known_inverse_projective_fixtures=True,all_exact_plus_minus75_endpoints=True,known_edge_convergence_reduced=convergence,horizontal_compared_to_vertical_only_on_same_source=True,combined_definitions_independent_and_reset_every_RGBA_exact=True,independent_homogeneous_matrix_full_output_pixel_checks=True,source_objects_dimensions_frame_other_settings_exact=True,no_wrap_or_colour_in_clear_pixels=True,metrics=metrics,sha256=hashes)
(out/'persp141-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native both-axis/sign perspective, known convergence, extremes, independence and source/alpha')
