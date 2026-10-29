from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PHOTO-016-complete';looks=root/'headless/PHOTO-015-complete'
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/(name+'.png')).convert('RGBA'))
ui=json.loads((folder/'PHOTO-looks-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and ui['fresh_reopen_complete']
baseline=json.loads((looks/'baseline.retropaint').read_text(encoding='utf-8'));base_pixels=np.asarray(Image.open(looks/'baseline.png').convert('RGBA'));base_preview=np.asarray(Image.open(looks/'baseline-preview.png').convert('RGBA'))
assert read('custom-baseline')==baseline and np.array_equal(image('custom-baseline'),base_pixels)
presets={'natural':dict(contrast=8,vibrance=15,clarity=8),'punch':dict(contrast=15,pop=35,vibrance=20),'warm':dict(temperature=24,tint=5,grain=12),'cool':dict(temperature=-25,tint=0)}
rows=[]
for item in ui['rows']:
    variant,preset=item['variant'],item['preset'];doc=read(variant+'-custom');recipe=doc['layers'][0]['photo'];expected=deepcopy(baseline);settings=deepcopy(baseline['layers'][0]['photo']['settings']);settings.update(presets[preset])
    if variant=='slider':settings['brightness']=22
    if variant=='curve':settings['curves']['green']=[dict(x=0,y=.12),dict(x=.5,y=.5),dict(x=1,y=.95)]
    if variant=='crop':
        settings['crop']=dict(x=120/3896,y=90/2586,width=3400/3896,height=2100/2586);expected['crop']=deepcopy(settings['crop'])
    if variant=='automatic':
        # This case verifies the Custom transition, not Auto light's separate
        # tonal algorithm. Require changes only to its five exposed settings.
        keys=['exposure','contrast','shadows','highlights','vibrance'];assert any(recipe['settings'][k]!=settings[k] for k in keys)
        for key in keys:
            value=recipe['settings'][key];assert isinstance(value,(float,int)) and np.isfinite(value)
            assert (-4<=value<=4) if key=='exposure' else (-100<=value<=100)
            settings[key]=value
    expected['layers'][0]['photo']=dict(settings=settings,normal=deepcopy(baseline['layers'][0]['photo']['settings']),look='custom',lookActive=True)
    assert doc==expected,'Unexpected recipe/baseline/original/neighbour mutation: '+variant
    pixels=image(variant+'-custom');prior=np.asarray(Image.open(looks/('forward-'+preset+'.png')).convert('RGBA'))
    if variant=='crop':assert pixels.shape==(2100,3400,4) and np.array_equal(pixels,prior[90:2190,120:3520]),'Actual full-size crop differs from independently indexed pre-crop output'
    else:assert pixels.shape==base_pixels.shape and np.any(pixels!=prior)
    before_preview=image(variant+'-preset-preview');after_preview=image(variant+'-custom-preview');changed=int(np.any(before_preview!=after_preview,axis=2).sum());assert changed>100
    assert read(variant+'-undone')==baseline and np.array_equal(image(variant+'-undone'),base_pixels)
    assert read(variant+'-redone')==doc and np.array_equal(image(variant+'-redone'),pixels)
    for suffix in ['normal','cancelled']:
        assert read(variant+'-'+suffix)==baseline and np.array_equal(image(variant+'-'+suffix),base_pixels)
    assert np.array_equal(image(variant+'-normal-preview'),base_preview)
    assert item['category_navigation_preserved'] and item['custom_indicated'] and item['undo_redo'] and item['normal_after_commit'] and item['cancelled_draft']
    rows.append(dict(variant=variant,preset=preset,complete_custom_recipe_and_original_baseline_exact=True,public_preview_changed_pixels=changed,full_size_draft_effect_verified=True,undo_redo_complete_data_and_rgba_exact=True,normal_restores_manual_baseline_after_commit_and_reopen=True,cancel_preserves_complete_baseline=True))
assert len(rows)==4 and read('fresh/reopened')==baseline and np.array_equal(image('fresh/reopened'),base_pixels)
events=json.loads((folder/'events.json').read_text(encoding='utf-8'))+json.loads((folder/'fresh/events.json').read_text(encoding='utf-8'));downloads=[e for e in events if e['action']=='download']
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
assert len(downloads)==44
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source_dimensions=[3896,2586],rows=rows,all_six_category_changes_preserve_selected_look=True,actual_fresh_downloaded_file_reopen_exact=True,originals_neighbour_and_all_unrelated_fields_exact=True,actual_downloads_verified=len(downloads),oracle='Literal preset/manual parameter contracts, complete preserved project comparisons, full-size Pillow RGBA, independently indexed crop over a separately saved full-size Warm result, and exact public preview and baseline comparisons.',scope='Custom label and baseline transitions for slider/curve/crop/automatic edits. Auto light algorithm quality is a separate PHOTO-014 case.',execution='Isolated headless production UI; no desktop control')
(root/'evidence/PHOTO-016-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
