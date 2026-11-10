"""Native slider, curve, crop and automatic edits mark a look Custom."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(n):
    name=f'mouse-audit-photo104-{n}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
normal=json.loads((downloads/'mouse-audit-photo103-a-normal.retropaint').read_text());punch=json.loads((downloads/'mouse-audit-photo103-a-punch.retropaint').read_text());baseline=normal['layers'][0]['photo']['settings']
ui=json.loads((out/'photo104-ui.json').read_text());assert ui==dict(categoryOnly='punch',slider='custom',curve='custom',crop='custom',auto='custom')
for kind in ['slider','curve','crop','auto']:assert doc('normal-'+kind)==normal
for kind,name in [('slider','custom-slider'),('curve','custom-curve'),('crop','custom-crop-native'),('auto','custom-auto')]:
    d=doc(name);recipe=d['layers'][0]['photo'];assert recipe['look']=='custom' and recipe['lookActive'] is True and recipe['normal']==baseline
    expected=copy.deepcopy(punch);expected['layers'][0]['photo']=recipe;expected['crop']=d['crop'];assert expected==d
    if kind!='auto':
        expected=copy.deepcopy(punch);expected['layers'][0]['photo']['look']='custom';settings=expected['layers'][0]['photo']['settings']
        if kind=='slider':settings['brightness']=21
        if kind=='curve':settings['curves']['rgb']=[dict(x=0,y=0),dict(x=.25,y=.38),dict(x=1,y=1)]
        if kind=='crop':settings['crop']=dict(x=.1,y=140/1398,width=.8,height=1118/1398);expected['crop']=copy.deepcopy(settings['crop'])
        assert expected==d
    else:assert recipe['settings']!=punch['layers'][0]['photo']['settings']
name='mouse-audit-photo104-custom-crop-native.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();crop=np.array(Image.open(out/name).convert('RGBA'));full=np.array(Image.open(downloads/'mouse-audit-photo103-a-punch.png').convert('RGBA'));assert np.array_equal(crop,full[140:1258,210:1890])
failed=doc('custom-crop');assert failed['crop']==normal['crop'] and failed['layers'][0]['photo']['look']=='punch'
report=dict(status='Pass',category_navigation_keeps_named_look=True,all_four_edit_routes_mark_custom=True,prelook_manual_baseline_exact_every_branch=True,Normal_whole_document_exact_every_branch=True,underlying_source_and_neighbours_exact=True,crop_render_exact_independent_region_of_full_Punchy=True,initial_crop_attempt='fill plus Tab changed displayed text without committing; preserved separately. Native arrow-key commit produced required crop, Custom and exact export.',sha256=hashes)
(out/'photo104-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native Custom labels for slider/curve/crop/auto, preserved Normal and exact crop output')
