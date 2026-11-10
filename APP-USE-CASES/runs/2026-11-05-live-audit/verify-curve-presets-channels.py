"""Independent known patch, preset, channel-isolation and actual-file checks."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(prefix,name,ext='retropaint'):
    filename=f'mouse-audit-curve{prefix}-{name}.{ext}';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest()
    return json.loads(data) if ext=='retropaint' else np.array(Image.open(io.BytesIO(data)).convert('RGBA')).astype(int)
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA')).astype(int)
defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings']
line=[dict(x=0,y=0),dict(x=1,y=1)]
base=load(112,'baseline');raw=pixels(base)
presets={'gentle':[(0,0),(.25,.18),(.75,.82),(1,1)],'fade':[(0,.12),(.5,.5),(1,.95)],'shadows':[(0,0),(.25,.38),(1,1)],'reset':[(0,0),(1,1)]}
pd={};pa={}
for name,points in presets.items():
    d=load(114,name);a=load(114,name,'png');pd[name]=d;pa[name]=a;s=copy.deepcopy(defaults);s['curves']['rgb']=[dict(x=x,y=y) for x,y in points];expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected,name
    assert np.array_equal(a[:,:,3],raw[:,:,3]);ramp=a[20,::4,:3];assert np.all(np.diff(ramp[:,0])>=0) and np.array_equal(ramp[:,0],ramp[:,1]) and np.array_equal(ramp[:,1],ramp[:,2])
assert load(114,'gentle-repeat')==pd['gentle'] and np.array_equal(load(114,'gentle-repeat','png'),pa['gentle'])
assert np.array_equal(pa['reset'],raw)
assert pa['gentle'][20,64*4,0]<64 and pa['gentle'][20,192*4,0]>192
assert pa['fade'][20,0,0]>0 and pa['fade'][20,-1,0]<255
assert pa['shadows'][20,64*4,0]>64 and pa['shadows'][20,0,0]==0 and pa['shadows'][20,-1,0]==255
base=load(115,'baseline');raw=pixels(base);s=copy.deepcopy(defaults);images={};docs={}
for name,value in [('red',180),('green',100),('blue',160),('switched',None)]:
    if value is not None:s['curves'][name]=[dict(x=0,y=0),dict(x=128/255,y=value/255),dict(x=1,y=1)]
    d=load(115,name);a=load(115,name,'png');docs[name]=d;images[name]=a;expected=copy.deepcopy(base);expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected,name
    assert np.array_equal(a[:,:,3],raw[:,:,3]) and np.array_equal(a[raw[:,:,3]==0],raw[raw[:,:,3]==0])
opaque=raw[:,:,3]==255
assert np.array_equal(images['red'][:,:,1:][opaque],raw[:,:,1:][opaque])
assert np.array_equal(images['green'][:,:,0][opaque],images['red'][:,:,0][opaque]) and np.array_equal(images['green'][:,:,2][opaque],raw[:,:,2][opaque])
assert np.array_equal(images['blue'][:,:,:2][opaque],images['green'][:,:,:2][opaque])
assert docs['switched']==docs['blue'] and np.array_equal(images['switched'],images['blue'])
grey=opaque & np.all(raw[:,:,:3]==128,axis=2);assert grey.sum()>100
assert np.all(images['red'][grey,:3]==[180,128,128]) and np.all(images['green'][grey,:3]==[180,100,128]) and np.all(images['blue'][grey,:3]==[180,100,160])
ui=json.loads((out/'curve115-ui.json').read_text(encoding='utf-8'));assert [r['channel'] for r in ui]==['red','green','blue','rgb']
report=dict(status='Pass',three_named_preset_tonal_characters=True,preset_replacement_project_and_PNG_exact=True,reset_every_RGBA_exact=True,visible_channel_selection_and_all_definitions_retained=True,independent_known128_RGB_patch_outputs=[[180,128,128],[180,100,128],[180,100,160]],unaffected_opaque_channels_every_pixel_exact=True,source_alpha_other_settings_whole_document_exact=True,sha256=hashes)
(out/'curve114-115-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native presets, exact replacement/reset and separate combined RGB channels')
