from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PHOTO-015-complete'
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/(name+'.png')).convert('RGBA'))
ui=json.loads((folder/'PHOTO-looks-headless-ui.json').read_text(encoding='utf-8'))
assert ui['status']=='Pass' and not ui['errors'] and ui['fresh_reopen_complete']
original=json.loads((root/'evidence/PHOTO-004-saved-before.retropaint').read_text(encoding='utf-8'))
baseline=read('baseline');expected=deepcopy(original)
settings=deepcopy(original['layers'][0]['photo']['settings'])
settings.update(brightness=17,temperature=-12)
settings['curves']['red']=[dict(x=0,y=0),dict(x=.25,y=.38),dict(x=1,y=1)]
expected['layers'][0]['photo']=dict(settings=settings,normal=deepcopy(settings),look='normal',lookActive=False)
assert baseline==expected,'Saved baseline does not contain the exact manual edits and preserved original document'
assert baseline['width']==3896 and baseline['height']==2586 and len(baseline['layers'])==2
base_pixels=image('baseline');assert base_pixels.shape==(2586,3896,4)
assert not np.array_equal(base_pixels,np.asarray(Image.open(root/'evidence/PHOTO-004-saved-before.png').convert('RGBA')))
presets={'natural':dict(contrast=8,vibrance=15,clarity=8),'punch':dict(contrast=15,pop=35,vibrance=20),'mono':dict(saturation=-100,contrast=12),'warm':dict(temperature=24,tint=5,grain=12),'cool':dict(temperature=-25,tint=0)}
decode=lambda layer:np.asarray(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
neighbour=decode(baseline['layers'][1]);opaque=neighbour[:,:,3]==255
assert opaque.any()
rows=[]
for name,changes in presets.items():
    doc=read('forward-'+name);expected=deepcopy(baseline);recipe=dict(settings=deepcopy(settings),normal=deepcopy(settings),look=name,lookActive=True);recipe['settings'].update(changes);expected['layers'][0]['photo']=recipe
    assert doc==expected,'Look accumulated settings or modified another field: '+name
    pixels=image('forward-'+name);assert pixels.shape==base_pixels.shape
    changed=int(np.any(pixels!=base_pixels,axis=2).sum());assert changed>1000
    assert np.array_equal(pixels[opaque],neighbour[opaque]),'Photo look changed the separate opaque neighbouring sheet'
    forward=image('forward-'+name+'-preview');reverse=image('reverse-'+name+'-preview')
    assert np.array_equal(forward,reverse),'Preview accumulated preset changes with order: '+name
    rows.append(dict(look=name,complete_saved_recipe_exact=True,normal_baseline_exact=True,original_and_neighbour_exact=True,full_size_changed_pixels=changed,forward_reverse_preview_rgba_exact=True))
assert read('reverse-cancelled')==read('forward-cool')
assert np.array_equal(image('reverse-cancelled'),image('forward-cool'))
for name in ['normal-restored','normal-redone','fresh/reopened']:
    assert read(name)==baseline
    assert np.array_equal(image(name),base_pixels),'Normal/full saved-file reopen differs from actual manual baseline'
assert read('normal-undone')==read('forward-cool')
assert np.array_equal(image('normal-undone'),image('forward-cool'))
assert np.array_equal(image('normal-restored-preview'),image('baseline-preview'))
events=json.loads((folder/'events.json').read_text(encoding='utf-8'))+json.loads((folder/'fresh/events.json').read_text(encoding='utf-8'))
downloads=[event for event in events if event['action']=='download']
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
assert len(downloads)==22
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source_dimensions=[3896,2586],baseline_manual_edits=dict(exposure=1,brightness=17,temperature=-12,red_curve='Lift shadows'),exact_complete_baseline_setup=True,rows=rows,all_actual_selectable_looks_executed=True,normal_restores_exact_manual_baseline_data_and_full_size_rgba=True,cancel_preserves_committed_look_data_and_full_size_rgba=True,undo_redo_and_actual_fresh_saved_file_reopen_exact=True,actual_downloads_verified=len(downloads),preview_comparison='Exact public preview RGBA for each named look across forward committed and reverse draft order. Full-size actual PNG retained for every look; original source and neighbouring layer are exact. No claim that one small preview certifies full-size photographic effects.',execution='Isolated headless production UI; no desktop control')
(root/'evidence/PHOTO-015-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
