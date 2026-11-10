"""Verify actual native curve downloads against known ramp and saved controls."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(prefix,name,ext='retropaint'):
    filename=f'mouse-audit-curve{prefix}-{name}.{ext}';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest()
    return json.loads(data) if ext=='retropaint' else np.array(Image.open(io.BytesIO(data)).convert('RGBA')).astype(int)
baseline=load(112,'baseline');raw=np.array(Image.open(io.BytesIO(base64.b64decode(baseline['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int)
defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings']
docs={n:load(112,n) for n in ['up','down','exact','constrained','neighbour','keyboard','deleted']};docs['repaired']=load(113,'exact')
for n,d in docs.items():
    curves=d['layers'][0]['photo']['settings']['curves'];settings=copy.deepcopy(defaults);settings['curves']=curves;expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False);assert d==expected,n
    for channel,points in curves.items():
        assert points[0]['x']==0 and points[-1]['x']==1 and all(0<=p['y']<=1 for p in points)
        assert all(b['x']-a['x']>=1/255-1e-12 for a,b in zip(points,points[1:]))
        if channel!='rgb':assert points==[dict(x=0,y=0),dict(x=1,y=1)]
assert docs['up']['layers'][0]['photo']['settings']['curves']['rgb'][1]['y']==.75
assert docs['down']['layers'][0]['photo']['settings']['curves']['rgb'][1]['y']==.25
old=docs['exact']['layers'][0]['photo']['settings']['curves']['rgb'][1];assert abs(old['x']-.5)<1e-6 and old['x']!=128/255
point=docs['repaired']['layers'][0]['photo']['settings']['curves']['rgb'][1];assert point==dict(x=128/255,y=160/255)
assert docs['constrained']['layers'][0]['photo']['settings']['curves']['rgb'][1]==point
neighbours=docs['neighbour']['layers'][0]['photo']['settings']['curves']['rgb'];assert len(neighbours)==4 and abs(neighbours[2]['x']-neighbours[1]['x']-1/255)<1e-12
key=docs['keyboard']['layers'][0]['photo']['settings']['curves']['rgb'][1];assert abs(key['x']-(old['x']-9/255))<1e-12 and abs(key['y']-151/255)<1e-12
assert docs['deleted']['layers'][0]['photo']['settings']['curves']['rgb']==[dict(x=0,y=0),dict(x=1,y=1)]
images={n:load(112,n,'png') for n in ['up','down','exact']};images['repaired']=load(113,'exact','png')
for n,a in images.items():
    assert a.shape==raw.shape and np.array_equal(a[:,:,3],raw[:,:,3]);assert np.array_equal(a[raw[:,:,3]==0],raw[raw[:,:,3]==0])
    ramp=a[20,:1024:4,:3];assert np.array_equal(ramp[:,0],ramp[:,1]) and np.array_equal(ramp[:,1],ramp[:,2]);assert np.all(np.diff(ramp[:,0])>=0);assert ramp[0,0]==0 and ramp[-1,0]==255
assert abs(images['up'][20,128*4,0]-191)<=1 and abs(images['down'][20,128*4,0]-64)<=1
assert images['repaired'][20,128*4,0]==160
ui=json.loads((out/'curve112-ui.json').read_text(encoding='utf-8'));assert next(r for r in ui if r['name']=='cannot-cross64')['values']['x']=='65';assert next(r for r in ui if r['name']=='endpoint-protected')['values']['removeDisabled']
report=dict(status='Pass',native_RGB_up_down_neutral_monotone_ramp=True,numeric128_160_exact_normalized_after_LIVE057=True,neighbour_order_and_numeric_constraints=True,keyboard_one_and_ten_unit_axes=True,interior_delete_and_protected_endpoints=True,source_alpha_other_settings_whole_document_exact=True,before_fix_rounded_entry_failure_retained=True,sha256=hashes)
(out/'curve112-113-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native RGB, exact entry, ordering, keyboard and independent saved ramp')
