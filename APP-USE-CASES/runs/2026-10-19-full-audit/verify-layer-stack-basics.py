from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io,sys
import numpy as np
root=Path(__file__).resolve().parent;kind=sys.argv[1];assert kind in ['add','remove'];number='001' if kind=='add' else '008';folder=root/('headless/LAYER-'+number+'-complete')
ui=json.loads((folder/'LAYER-stack-basics-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));rows=[];downloads=[]
decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'))
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');assert before==fixture;source=image('before');assert source.shape==(640,960,4)
    if kind=='add':
        empty=read('added-empty');assert len(empty['layers'])==5;new=empty['layers'][3];expected=deepcopy(before);expected['layers'].insert(3,new);expected['active']=new['id'];assert empty==expected
        assert new['id'] not in {l['id'] for l in before['layers']} and new['name']=='Layer 1' and new['paper'] is None and new['visible'] and new['opacity']==1
        assert not new.get('photo') and not new.get('objects') and not new.get('cad') and not any(new['live'].values()) and not decode(new['image']).any()
        assert np.array_equal(image('added-empty'),source)
        painted=read('painted');expected=deepcopy(empty);expected['layers'][3]['image']=painted['layers'][3]['image'];assert painted==expected
        raw=decode(painted['layers'][3]['image']);assert np.array_equal(raw[150,700],[67,160,71,255]);ys,xs=np.where(raw[:,:,3]>0);assert len(xs)>1000 and xs.min()>=588 and xs.max()<=812 and ys.min()>=138 and ys.max()<=162
        assert np.array_equal(image('painted')[150,700],[67,160,71,255])
        picked=read('picked-caption');expected=deepcopy(painted);expected['active']=before['layers'][3]['id'];assert picked==expected and np.array_equal(image('picked-caption'),image('painted'))
        # Undo captured its future after Caption was selected; Redo therefore
        # restores that complete target state too, without an extra edit step.
        for label,reference in {'paint-undone':'added-empty','add-undone':'before','add-redone':'added-empty','paint-redone':'picked-caption','final-picked':'picked-caption'}.items():assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),label
        reopened_expected=deepcopy(picked)
        assert 'clip' not in reopened_expected['layers'][2]['live']['strokes'][0]
        reopened_expected['layers'][2]['live']['strokes'][0]['clip']=None
        assert read('fresh/reopened')==reopened_expected and np.array_equal(image('fresh/reopened'),image('picked-caption'))
        assert row['target_named_before_edit'] and row['compact_add_and_pick_close_palette']==(row['width']<=1000 or row['height']<=550)
        paths=[location/'events.json',location/'fresh/events.json'];details=dict(new_layer_id=new['id'],adjacent_new_layer_is_empty_transparent_and_unique=True,green_pixels_confined_to_new_layer=True,old_layers_all_exact_before_reopen=True,ordinary_compact_add_and_pick_behavior_verified=True,reopen_only_canonicalises_absent_inactive_stroke_clip_to_null=True)
    else:
        removed=read('removed');expected=deepcopy(before);del expected['layers'][2];expected['active']=before['layers'][1]['id'];assert removed==expected
        assert read('remove-undone')==before and np.array_equal(image('remove-undone'),source)
        for label in ['remove-redone','fresh-middle/reopened']:assert read(label)==removed and np.array_equal(image(label),image('removed'))
        # The requested middle layer's red/green and live strips disappear.
        assert not np.array_equal(image('removed'),source)
        last=read('last-before-attempt');expected=deepcopy(before);expected['layers']=[deepcopy(before['layers'][0])];expected['active']=before['layers'][0]['id'];assert last==expected and (image('last-before-attempt')==255).all()
        assert read('last-after-attempt')==last and np.array_equal(image('last-after-attempt'),image('last-before-attempt'))
        painted=read('last-painted');expected=deepcopy(last);expected['layers'][0]['image']=painted['layers'][0]['image'];assert painted==expected
        raw=decode(painted['layers'][0]['image']);assert np.array_equal(raw[150,700],[67,160,71,255])
        assert read('last-paint-undone')==last and np.array_equal(image('last-paint-undone'),image('last-before-attempt'))
        for label in ['last-paint-redone','fresh-last/reopened']:assert read(label)==painted and np.array_equal(image(label),image('last-painted'))
        assert row['last_layer_disabled_and_still_drawable'];paths=[location/'events.json',location/'fresh-middle/events.json',location/'fresh-last/events.json'];details=dict(only_requested_middle_sheet_removed=True,remaining_backdrop_active=True,complete_middle_layer_undo_redo_and_reopen_exact=True,last_layer_attempt_retains_exact_ready_document=True,last_sheet_drawing_and_one_step_history_usable=True)
    assert row['history_and_fresh_reopen_complete']
    for path in paths:downloads += [e for e in json.loads(path.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],complete_project_fields_and_controlled_rgba_verified=True,**details))
assert len(downloads)==(80 if kind=='add' else 88)
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,kind=kind,rows=rows,actual_downloads_verified=len(downloads),render_time_ms=10000,oracle='Complete expected project layer/identity/order changes, independently decoded raw/full-size RGBA, known green stroke and confined source mask, exact white ready Paper, full Undo/Redo and actual fresh chooser input/downloads. No app serializer or renderer supplies expected data.',add_case_canonicalisation='Reopen adds only layers[2].live.strokes[0].clip=null where the saved inactive stroke omitted clip. Both mean no clipping polygon; the exact one field is asserted, not broadly normalised. All points, source pixels and full rendered RGBA are exact.' if kind=='add' else None,execution='Isolated headless public UI; no desktop/existing user profile access')
(root/('evidence/LAYER-'+number+'-independent-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
