from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/LAYER-009-complete'
ui=json.loads((folder/'LAYER-009-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==12
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));backup=json.loads((root/'backups/artwork-before-acceptance-audit.retropaint').read_text(encoding='utf-8'));rows=[];downloads=[]
decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'))
for row in ui['rows']:
    variant=row['variant'];location=folder/f"{row['width']}x{row['height']}"/variant;read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');assert image('before').shape==(640,960,4)
    if variant=='CAD-rejection':
        assert before==backup
        neighbour=read('neighbour-attempt');expected=deepcopy(before);expected['active']=before['layers'][3]['id'];assert neighbour==expected and np.array_equal(image('neighbour-attempt'),image('before'))
        after=read('cad-attempt');expected=deepcopy(before);expected['active']=before['layers'][0]['id'];expected['layers'][2]['image']=after['layers'][2]['image'];assert after==expected
        assert after['layers'][2]['cad']==before['layers'][2]['cad'] and len(after['layers'][2]['cad']['bodies'])>0
        assert read('fresh/reopened')==after and np.array_equal(image('fresh/reopened'),image('cad-attempt'))
        assert row['merge_into_CAD_disabled'] and row['merge_CAD_unavailable'] in ['hidden','disabled native attempt']
        detail=dict(merge_into_CAD_native_disabled_attempt_preserves_complete_document=True,CAD_merge_unavailable=row['merge_CAD_unavailable'],all_editable_CAD_recipe_body_ids_and_saved_view_exact=True,CAD_close_only_regenerates_cached_preview_image=True,valid_paint_return_target=after['active'],fresh_project_and_pixels_exact=True)
    else:
        index=2 if variant=='Character' else 3;expected=deepcopy(fixture);expected['active']=fixture['layers'][index]['id'];assert before==expected
        after=read('merged');expected=deepcopy(before);del expected['layers'][index];lower=expected['layers'][index-1];lower['image']=after['layers'][index-1]['image'];lower['opacity']=1;lower['visible']=True;lower['live']={key:[] for key in ['strokes','fills','sparkles']};lower.pop('photo',None);lower.pop('objects',None);expected['active']=lower['id'];assert after==expected
        max_error=int(np.abs(image('merged').astype(int)-image('before').astype(int)).max());assert max_error<=2
        assert read('undone')==before and np.array_equal(image('undone'),image('before'))
        assert read('redone')==after and np.array_equal(image('redone'),image('merged'))
        assert read('fresh/reopened')==after and np.array_equal(image('fresh/reopened'),image('merged'))
        raw=decode(after['layers'][index-1]['image']);assert raw.shape==(640,960,4)
        if variant=='Character':assert np.array_equal(raw[600,900],image('before')[600,900]) and raw[140,150,3]==255
        else:assert raw[140,150,3]==128 and (raw[580:630,850:940,3]==0).all()
        assert any(before['layers'][2]['live'].values()) and before['layers'][3]['objects'] and before['layers'][1]['photo']
        detail=dict(only_adjacent_two_sheets_combined=True,lower_identity_name_and_paper_retained=True,combined_scope_static_pixels_with_unit_opacity=True,captured_frame_rgba_max_error=max_error,complete_separate_originals_live_photo_and_objects_restored_by_undo=True,redo_and_actual_fresh_reopen_exact=True)
    for path in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in json.loads(path.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],variant=variant,**detail))
assert len(downloads)==112
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),render_time_ms=10000,oracle='Explicit adjacent-layer scope and every retained metadata/pixel/identity field; independent Pillow RGBA and predeclared2/255 alpha-flattening tolerance; known opaque and half-alpha probes; exact full Undo/Redo and fresh project input. CAD rejection retains every body/recipe/view and all other sheets; closing CAD may regenerate its raster preview cache.',execution='Actual public controls in isolated headless production sessions; no desktop interaction')
(root/'evidence/LAYER-009-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
