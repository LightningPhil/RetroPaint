from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PHOTO-019-verified';setup=root/'headless/PHOTO-019-complete';looks=root/'headless/PHOTO-015-complete'
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/(name+'.png')).convert('RGBA'))
ui=json.loads((folder/'PHOTO-019-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and ui['fresh_reopen_complete'] and len(ui['rows'])==3
baseline=json.loads((looks/'baseline.retropaint').read_text(encoding='utf-8'));base_pixels=np.asarray(Image.open(looks/'baseline.png').convert('RGBA'));warm_pixels=np.asarray(Image.open(looks/'forward-warm.png').convert('RGBA'))
fixture=json.loads((setup/'look-cropped.retropaint').read_text(encoding='utf-8'));crop=dict(x=120/3896,y=90/2586,width=3400/3896,height=2100/2586)
cropped_settings=deepcopy(baseline['layers'][0]['photo']['settings']);cropped_settings['crop']=crop;expected=deepcopy(baseline);expected['crop']=crop;warm=deepcopy(cropped_settings);warm.update(temperature=24,tint=5,grain=12);expected['layers'][0]['photo']=dict(settings=warm,normal=cropped_settings,look='warm',lookActive=True)
assert fixture==expected,'Original real UI fixture does not contain the intended baseline/curve/crop/look'
assert np.array_equal(np.asarray(Image.open(setup/'look-cropped.png').convert('RGBA')),warm_pixels[90:2190,120:3520])
assert read('fresh-cropped')==fixture and np.array_equal(image('fresh-cropped'),warm_pixels[90:2190,120:3520])
normal=read('normal-cropped');expected['layers'][0]['photo']=dict(settings=cropped_settings,normal=cropped_settings,look='normal',lookActive=False)
assert normal==expected and np.array_equal(image('normal-cropped'),base_pixels[90:2190,120:3520])
whole=read('whole-restored');expected=deepcopy(baseline);expected['layers'][0]['photo']['look']='custom'
assert whole==expected and np.array_equal(image('whole-restored'),base_pixels)
assert read('whole-undone')==normal and np.array_equal(image('whole-undone'),image('normal-cropped'))
for label in ['whole-redone','final-reopened']:
    assert read(label)==whole and np.array_equal(image(label),base_pixels)
rows=[]
for kind in ['numeric','curve','look']:
    invalid=read('invalid-'+kind);expected=deepcopy(fixture)
    if kind=='numeric':expected['layers'][0]['photo']['settings']['exposure']='1'
    if kind=='curve':expected['layers'][0]['photo']['settings']['curves']['red']=[dict(x=0,y=0),dict(x=.8,y=.5),dict(x=.5,y=.6),dict(x=1,y=1)]
    if kind=='look':expected['layers'][0]['photo']['look']='unrecognised-look'
    assert invalid==expected,'Malformed fixture changed more than its deliberate one property'
    assert read('rejected-'+kind)==whole and np.array_equal(image('rejected-'+kind),base_pixels)
    assert read('valid-retry-'+kind)==whole
    rows.append(dict(kind=kind,only_deliberate_fixture_property_changed=True,actual_explained_rejection=True,complete_open_document_and_full_size_rgba_preserved=True,valid_retry_exact=True))
events=json.loads((folder/'events.json').read_text(encoding='utf-8'));downloads=[e for e in events if e['action']=='download'];assert len(downloads)==21
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source_dimensions=[3896,2586],saved_crop_pixels=[120,90,3400,2100],named_look='warm',nondefault_manual_baseline_and_red_curve=True,fresh_project_recipe_and_render_exact=True,normal_uses_exact_saved_cropped_baseline=True,hidden_margins_recovered_with_exact_full_size_rgba=True,original_neighbour_and_unrelated_fields_exact=True,whole_frame_undo_redo_and_actual_second_reopen_exact=True,negative_rows=rows,actual_downloads_verified=len(downloads),oracle='Complete expected project data and independently indexed full-size crops of the separately saved baseline/Warm outputs; Pillow decoded RGBA and actual fresh project chooser downloads.',harness_correction='The original setup run overwrote its event list when creating a fresh context. It is retained as the actual UI fixture producer, with its source copy and screenshots. The corrected complete fresh-session run preserves a continuous log of all 21 downloads; no acceptance outcome was recorded from the deficient log.',execution='Isolated headless production UI; no desktop control')
(root/'evidence/PHOTO-019-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
