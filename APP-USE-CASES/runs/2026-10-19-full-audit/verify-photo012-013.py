from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io,re,math
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PHOTO-012-013-complete'
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/(name+'.png')).convert('RGBA'))
decode=lambda layer:np.asarray(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
ui=json.loads((folder/'PHOTO-tone-regions-ui.json').read_text(encoding='utf-8'))
assert ui['status']=='Pass' and not ui['errors'] and ui['fresh_reopen_complete'] and len(ui['rows'])==20
source=image('source');assert source.shape==(256,1024,4)
assert np.array_equal(source,np.asarray(Image.open(root/'fixtures/TONAL.png').convert('RGBA')))
source_doc=read('source');rows=[];new_ids=[]
defaults={key:0 for key in ['exposure','brightness','contrast','highlights','shadows','whites','blacks','temperature','tint','saturation','vibrance','hue','sharpness','threshold','texture','clarity','pop','dehaze','noise','colourNoise','vignette','roundness','grain','distortion','aberration','vertical','horizontal','angle']}
defaults.update(balance=[1,1,1],radius=1,midpoint=50,feather=75,grainSize=1.2,grainRoughness=50,zoom=100,flipX=False,flipY=False,crop=dict(x=0,y=0,width=1,height=1),mixer=[dict(hue=0,saturation=0,luminance=0)]*8,curves={key:[dict(x=0,y=0),dict(x=1,y=1)] for key in ['rgb','red','green','blue']})
# Declare geometric tone regions from the fixture's known input values. These
# acceptance properties do not copy or call the app's adjustment formula.
dark=slice(16*4,64*4);mid=slice(120*4,136*4);bright=slice(192*4,240*4)
for row in ui['rows']:
    key,value,label=row['key'],row['value'],row['label'];doc=read(label);pixels=image(label);new_ids.append(doc['active'])
    assert len(doc['layers'])==1 and doc['active']==doc['layers'][0]['id']
    assert np.array_equal(decode(doc['layers'][0]),source),'Original ramp changed'
    # Each independently imported image legitimately gets a new layer ID. Check
    # it explicitly; only that identity and the intended recipe may differ.
    expected=deepcopy(source_doc);expected['active']=doc['active'];expected['layers'][0]['id']=doc['active']
    # Home plus arrow keys genuinely changes the draft even when its final
    # value is zero, so the saved indicator is Custom with default settings.
    recipe=doc['layers'][0]['photo'];expected_settings=deepcopy(defaults);expected_settings[key]=value
    assert recipe==dict(settings=expected_settings,normal=expected_settings,look='custom',lookActive=False)
    expected['layers'][0]['photo']=recipe
    assert doc==expected,'Unrelated saved fields changed'
    assert row['controls']=={k:(value if k==key else 0) for k in ['highlights','shadows','whites','blacks']}
    assert pixels.shape==source.shape and np.array_equal(pixels[:,:,3],source[:,:,3])
    assert np.array_equal(pixels[:,:,0],pixels[:,:,1]) and np.array_equal(pixels[:,:,1],pixels[:,:,2])
    delta=pixels[:,:,0].astype(float)-source[:,:,0].astype(float)
    if value==0:assert not delta.any()
    else:
        assert (delta>=0).all() if value>0 else (delta<=0).all()
        means={name:float(np.abs(delta[:,region]).mean()) for name,region in [('dark',dark),('mid',mid),('bright',bright)]}
        intended='bright' if key in ['highlights','whites'] else 'dark';opposite='dark' if intended=='bright' else 'bright'
        assert means[intended]>means[opposite]*2+1,(key,value,means)
        assert means[intended]>means['mid'],(key,value,means)
    black=(pixels[:,:,:3].min(axis=2)<=1).mean()*100;white=(pixels[:,:,:3].max(axis=2)>=254).mean()*100
    expected_clip=tuple(math.floor(n+.5) for n in [black,white]);actual=tuple(map(int,re.search(r'(\d+)% shadow clipping; (\d+)% highlight clipping',row['histogram']).groups()))
    assert all(abs(a-b)<=1 for a,b in zip(expected_clip,actual)),(label,expected_clip,actual)
    # The exact clipped source patches remain spatially constant: tone changes
    # cannot invent recovered detail in an already uniform 0 or 255 patch.
    assert np.ptp(pixels[:,:4,:3],axis=(0,1)).max()==0 and np.ptp(pixels[:,-4:,:3],axis=(0,1)).max()==0
    rows.append(dict(control=key,value=value,intended_tone_region_dominates=True,region_mean_absolute_change_255=means if value else dict(dark=0,mid=0,bright=0),other_controls_unchanged=True,source_exact=True,full_size_clipping_percent=expected_clip,preview_clipping_percent=actual))
assert len(set(new_ids))==20
combined=read('combined');settings=combined['layers'][0]['photo']['settings'];assert {k:settings[k] for k in ['highlights','shadows','whites','blacks']}==dict(highlights=-30,shadows=30,whites=30,blacks=-30)
for name in ['reset-cancelled','reset-undone']:
    assert read(name)==combined and np.array_equal(image(name),image('combined'))
reset=read('reset-done');recipe=reset['layers'][0]['photo'];assert recipe['settings']==recipe['normal'] and all(recipe['settings'][k]==0 for k in ['highlights','shadows','whites','blacks'])
copy=deepcopy(combined);copy['layers'][0]['photo']=reset['layers'][0]['photo'];assert copy==reset
assert np.array_equal(image('reset-done'),source)
for name in ['reset-redone','fresh/reopened']:
    assert read(name)==reset and np.array_equal(image(name),source)
hist=json.loads((root/'evidence/PHOTO-017-independent-verification.json').read_text(encoding='utf-8'));assert hist['nearly_transparent_clipping_after_percent']==0 and hist['empty_histogram_and_warnings_zero']
events=json.loads((folder/'events.json').read_text(encoding='utf-8'))+json.loads((folder/'fresh/events.json').read_text(encoding='utf-8'));downloads=[e for e in events if e['action']=='download']
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
assert len(downloads)==54
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source_dimensions=[1024,256],values_per_control=[-100,-30,0,30,100],tone_regions_input_levels=dict(dark=[16,63],mid=[120,135],bright=[192,239]),oracle='Independent spatial pixel differences, intended/opposite/midtone regional dominance, sign, channel neutrality, alpha, constant clipped source patches and independently counted rendered clipping. No app function or copied tone equation supplies expected results.',rows=rows,complete_original_and_unrelated_data_preserved=True,group_reset_cancel_commit_undo_redo_fresh_reopen_exact=True,clipped_uniform_source_patches_do_not_invent_recovered_detail=True,transparent_and_empty_branch_evidence='evidence/PHOTO-017-independent-verification.json',declared_preview_clipping_tolerance_percentage_points=1,actual_downloads_verified=len(downloads),execution='Isolated headless production UI; no desktop control')
(root/'evidence/PHOTO-012-013-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
