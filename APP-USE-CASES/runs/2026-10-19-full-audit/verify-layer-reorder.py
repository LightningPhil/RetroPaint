from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,sys
import numpy as np
root=Path(__file__).resolve().parent;kind=sys.argv[1];assert kind in ['drag','keyboard'];number='005' if kind=='drag' else '006';folder=root/('headless/LAYER-'+number+('-complete' if kind=='drag' else '-final'))
ui=json.loads((folder/'LAYER-reorder-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));rows=[];downloads=[]
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');assert before==fixture;source=image('before')
    def expected(indices,active):
        result=deepcopy(before);result['layers']=[deepcopy(before['layers'][i]) for i in indices];result['active']=before['layers'][active]['id'];return result
    if kind=='drag':
        assert read('below')==expected([0,2,1,3],2) and read('top')==expected([0,1,3,2],2) and read('original')==before
        for label,reference in {'below-undone':'before','below-redone':'below','top-undone':'below','top-redone':'top','original-undone':'top','original-redone':'before','same-position':'before','same-position-undone':'top','same-position-after-undo':'top','same-position-redone':'before','final':'before','fresh/reopened':'before'}.items():assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),label
        removed=np.asarray(Image.open(root/'headless/LAYER-008-complete'/f"{row['width']}x{row['height']}"/'removed.png').convert('RGBA'))
        assert np.array_equal(image('below'),removed),'Opaque guide did not occlude the layer moved below it'
        mask=np.zeros(source.shape[:2],dtype=bool);mask[310:370,410:490]=True;mask &= np.all(source[:,:,:3]==[253,216,53],axis=2);count=int(mask.sum());assert count>50
        predicted=.5*np.array([67,160,71])+.5*np.array([253,216,53]);error=float(np.abs(image('top')[:,:,:3][mask].astype(float)-predicted).max());assert error<=1
        assert row['same_position_history_checked'];details=dict(layer_identity_preserved_for_all_three_drags=True,below_opaque_guide_matches_separately_verified_removal_composite=True,independent_green_over_yellow_text_probe_pixels=count,blend_probe_maximum_error_255=error,same_position_drop_no_extra_history_or_rows=True)
    else:
        base_bottom=expected([0,1,2,3],0);up=expected([1,0,2,3],0);top=expected([0,1,2,3],3)
        assert read('navigation-bottom')==base_bottom and read('bottom-boundary')==base_bottom
        assert read('up')==up and read('down')==base_bottom and read('post-boundary')==base_bottom and read('top-boundary')==top
        for label,reference in {'up-undone':'navigation-bottom','up-redone':'up','down-undone':'up','down-redone':'down','post-boundary-undone':'up','post-boundary-redone':'down','top-boundary-undone':'up','top-boundary-redone':'top-boundary','final':'top-boundary'}.items():assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),label
        assert np.array_equal(image('navigation-bottom'),source) and np.array_equal(image('down'),source) and np.array_equal(image('top-boundary'),source)
        assert np.array_equal(image('up')[600,900],[255,255,255,255]) and not np.array_equal(source[600,900],[255,255,255,255])
        reopened=deepcopy(top);assert 'clip' not in reopened['layers'][2]['live']['strokes'][0];reopened['layers'][2]['live']['strokes'][0]['clip']=None
        assert read('fresh/reopened')==reopened and np.array_equal(image('fresh/reopened'),source)
        assert row['top_and_bottom_boundaries_checked'];details=dict(native_selection_arrows_change_only_target=True,both_alt_reorder_directions_verified=True,opaque_paper_order_probe_exact=True,top_bottom_boundaries_do_not_wrap_or_add_history=True,reopen_only_adds_explicit_null_no_clip_on_inactive_stroke=True)
    assert row['fresh_reopen_complete']
    for path in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in json.loads(path.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],all_original_pixels_live_objects_recipes_and_ids_preserved=True,every_history_state_and_controlled_rgba_verified=True,actual_fresh_saved_file_reopen_verified=True,**details))
assert len(downloads)==(128 if kind=='drag' else 136)
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,kind=kind,rows=rows,actual_downloads_verified=len(downloads),render_time_ms=10000,declared_blend_probe_tolerance_255=1,oracle='Explicit expected layer permutations and active identities; complete saved fields, independent full-size pixels, physical opaque-cover equivalence and elementary green/yellow alpha mixing, exact Undo/Redo and actual fresh project input. No internal reorder/serializer/render function supplies expected outcomes.',execution='Isolated headless native pointer/keyboard UI; no desktop/existing user browser access')
(root/('evidence/LAYER-'+number+'-independent-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
