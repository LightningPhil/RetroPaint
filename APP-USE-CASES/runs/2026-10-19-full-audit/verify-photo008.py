from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
import json,base64,io,sys
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent
folder=root/'evidence'
headless=Path(sys.argv[sys.argv.index('--headless')+1]) if '--headless' in sys.argv else None
location=lambda label:folder if label=='all-settings-saved-before' or headless is None else headless
read=lambda label:json.loads((location(label)/('PHOTO-008-'+label+'.retropaint')).read_text(encoding='utf-8'))
image=lambda label:np.asarray(Image.open(location(label)/('PHOTO-008-'+label+'.png')).convert('RGBA'))
decode=lambda layer:Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
before=read('all-settings-saved-before')
old=json.loads((folder/'PHOTO-004-saved-before.retropaint').read_text(encoding='utf-8'))
assert (before['width'],before['height'])==(3896,2586)
assert image('all-settings-saved-before').shape==(2000,3500,4)
expected_crop=dict(x=100/3896,y=100/2586,width=3500/3896,height=2000/2586)
assert before['crop']==expected_crop
settings=before['layers'][0]['photo']['settings']
assert settings['crop']==expected_crop
prepared=dict(exposure=1,brightness=-15,contrast=20,highlights=-20,shadows=20,whites=-10,blacks=10,temperature=15,tint=-10,saturation=20,vibrance=25,hue=15,sharpness=35,radius=1.5,threshold=5,texture=20,clarity=15,pop=10,dehaze=10,noise=20,colourNoise=15,vignette=-20,midpoint=30,feather=50,roundness=20,grain=30,grainSize=1.8,grainRoughness=70,distortion=20,aberration=15,vertical=10,horizontal=-10,angle=5,zoom=110,flipX=True,flipY=True)
assert all(settings[k]==v for k,v in prepared.items())
assert settings['balance']!=[1,1,1]
assert settings['mixer']==[dict(hue=10,saturation=20,luminance=5)]*8
fade=[dict(x=0,y=.12),dict(x=.5,y=.5),dict(x=1,y=.95)]
assert all(value==fade for value in settings['curves'].values())
copy=deepcopy(before);copy['layers'][0]['photo']=old['layers'][0]['photo'];copy['crop']=old['crop'];assert copy==old
assert read('all-settings-reset-cancelled')==before
if '--setup-only' in sys.argv:
    report=dict(at=datetime.now(timezone.utc).isoformat(),status='Partial',saved_setup_has_every_group_nondefault=True,saved_crop_pixels=[100,100,3500,2000],full_source_and_neighbour_preserved=True,reset_cancel_complete_project_exact=True,remaining=['Actual cancelled full-size PNG','Done and complete default recipe','Undo/Redo full data and pixels','Actual fresh project reopen'])
    (folder/'PHOTO-008-progress-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2));sys.exit(0)
assert np.array_equal(image('all-settings-reset-cancelled'),image('all-settings-saved-before'))
if headless:
    ui=json.loads((headless/'PHOTO-008-headless-ui.json').read_text(encoding='utf-8'))
    assert ui['status']=='Pass' and len(ui['downloads'])==12 and not ui['errors']
    assert json.loads((headless/'PHOTO-008-headless-before.retropaint').read_text(encoding='utf-8'))==before
    assert np.array_equal(np.asarray(Image.open(headless/'PHOTO-008-headless-before.png').convert('RGBA')),image('all-settings-saved-before'))
done=read('all-settings-reset-done')
defaults={k:0 for k in prepared}
defaults.update(radius=1,midpoint=50,feather=75,grainSize=1.2,grainRoughness=50,zoom=100,flipX=False,flipY=False,balance=[1,1,1],mixer=[dict(hue=0,saturation=0,luminance=0)]*8,curves={k:[dict(x=0,y=0),dict(x=1,y=1)] for k in ['rgb','red','green','blue']},crop=dict(x=0,y=0,width=1,height=1))
assert done['layers'][0]['photo']==dict(settings=defaults,normal=defaults,look='normal',lookActive=False),'Reset did not restore every defined group/default'
assert done['crop']==defaults['crop']
copy=deepcopy(done);copy['layers'][0]['photo']=before['layers'][0]['photo'];copy['crop']=before['crop'];assert copy==before
composite=Image.new('RGBA',(3896,2586))
for layer in done['layers']:
    assert layer['visible'] and layer['opacity']==1
    composite=Image.alpha_composite(composite,decode(layer))
result=image('all-settings-reset-done')
assert result.shape==(2586,3896,4)
error=int(np.abs(np.asarray(composite).astype(np.int16)-result.astype(np.int16)).max())
assert error<=1,error
assert read('all-settings-reset-undone')==before
assert np.array_equal(image('all-settings-reset-undone'),image('all-settings-saved-before'))
assert read('all-settings-reset-redone')==done
assert np.array_equal(image('all-settings-reset-redone'),result)
assert read('all-settings-reset-reopened')==done
assert np.array_equal(image('all-settings-reset-reopened'),result)
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source_dimensions=[3896,2586],initial_crop_pixels=[100,100,3500,2000],every_scalar_nondefault_in_saved_setup=True,auto_white_balance_nondefault=True,all_eight_mixer_bands_nondefault=True,all_four_curves_nondefault=True,cancel_restores_complete_saved_recipe_and_full_size_rgba=True,all_groups_and_normal_look_defaults_exact=True,originals_neighbour_and_unrelated_fields_exact=True,full_original_frame_and_hidden_margins_recovered=True,independent_raw_layer_composite_max_error_255=error,declared_composite_tolerance_255=1,undo_restores_complete_recipe_frame_and_exact_rgba=True,redo_reproduces_complete_recipe_frame_and_exact_rgba=True,actual_fresh_project_reopen_full_json_and_rgba_exact=True,setup_notes='Initial numeric fill did not produce the intended saved crop; retained setup output was inspected. Actual keyboard typing plus group return exposed that offsets clamp while the full frame fills the source. Width/height were reduced first, then x/y were typed and verified on return before the final saved fixture. Earlier setup attempts remain preserved and are not used as the all-settings fixture.')
if headless:report.update(execution='Isolated headless production UI; no desktop control',headless_evidence_directory=str(headless),actual_downloads_verified=12)
(folder/'PHOTO-008-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
