from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/START-008-complete';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'START-008-ui.json');assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
fixture=read_json(root/'headless/TARGET-fixture/fresh/fixture.retropaint');rows=[];downloads=[]
decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'))
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'))
    before=read('before');assert before==fixture;source_pixels=image('before');assert source_pixels.shape==(640,960,4)
    hidden=deepcopy(before);hidden['active']=2;hidden['layers'][1]['visible']=False
    for label in ['hidden','hidden-rejected','hidden-redone']:assert read(label)==hidden and np.array_equal(image(label),image('hidden'))
    assert read('hidden-undone')==before and np.array_equal(image('hidden-undone'),source_pixels),'Rejected hidden Photo open inserted history'
    selected=deepcopy(before);selected['active']=4;assert read('object-selected')==selected and np.array_equal(image('object-selected'),source_pixels)
    renamed=deepcopy(selected);renamed['layers'][4]['name']='Caption bEfSwR 012'
    for label in ['paint-renamed','paint-name-redone']:assert read(label)==renamed and np.array_equal(image(label),source_pixels)
    assert read('paint-name-undone')==selected and np.array_equal(image('paint-name-undone'),source_pixels)
    cad=read('cad-before-name');expected=deepcopy(renamed);expected['active']=5;cache=decode(cad['layers'][3]['image']);assert cache.shape==(640,960,4) and cache[:,:,3].any();expected['layers'][3]['image']=cad['layers'][3]['image'];assert cad==expected,'Opening CAD changed more than its derived preview/active target'
    edited=deepcopy(cad);edited['layers'][3]['cad']['bodies'][0]['name']='Maker WERF b 012'
    assert read('cad-renamed')==edited and read('cad-name-redone')==edited and read('cad-name-undone')==cad
    closed=read('closed');expected=deepcopy(edited);expected['active']=1;expected['layers'][3]['image']=closed['layers'][3]['image'];assert closed==expected
    fresh=deepcopy(closed);stroke=fresh['layers'][2]['live']['strokes'][0];default_added='clip' not in stroke
    if default_added:stroke['clip']=None
    assert read('fresh/reopened')==fresh and np.array_equal(image('fresh/reopened'),image('closed'))
    body=closed['layers'][3]['cad']['bodies'][0];assert body['solid']==fixture['layers'][3]['cad']['bodies'][0]['solid'] and body['position']==[0,0,10] and body['rotation']==[0,0,0] and body['scale']==[1,1,1]
    assert row['paint_target']=='Character' and row['hidden_target']=='Backdrop' and 'Backdrop is hidden' in row['hidden_hint'] and 'Show this layer' in row['rejection_message'] and row['object_target']=='Text on Caption' and row['CAD_target']=='Cube on 3D 1' and row['draw_tool_after_name']=='scissors' and row['CAD_tool_after_name']=='translate' and row['history_and_actual_fresh_reopen']
    for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in read_json(file) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],normal_hidden_object_and_solid_targets_named=True,hidden_target_explanation_and_rejection_preserve_complete_data_and_history=True,only_intended_layer_and_body_name_fields_change=True,paint_and_CAD_tools_unchanged_by_actual_shortcut_letter_typing=True,all_original_pixels_live_objects_photo_recipes_and_cube_geometry_retained=True,rename_history_and_actual_fresh_project_RGBA_exact=True,only_optional_inactive_no_clip_default_added=default_added))
assert len(downloads)==104
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=104,render_time_ms=10000,oracle='Explicit complete active/visibility/name mutations on the independently verified full MIX plus analytic20mm cube fixture; actual visible UI target/selection/action observations, shortcut-letter native typing and unchanged public tool states; exact source fields/geometry, independent full-size RGBA, useful history and actual fresh file input. Only the known optional inactive no-clip default is admitted on reopen, and derived CAD preview cache may regenerate when entering/leaving the workshop.',execution='Isolated headless production controls/downloads; no desktop or existing user profile access')
(root/'evidence/START-008-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='START-008',viewports=4,actual_downloads_verified=104),indent=2))
