from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/LAYER-015-final';extra=root/'headless/LAYER-015-landscape-final'
ui=json.loads((folder/'LAYER-015-ui.json').read_text(encoding='utf-8'));supplement=json.loads((extra/'LAYER-015-ui.json').read_text(encoding='utf-8'))
assert ui['status']=='Fail' and not ui['errors'] and len(ui['rows'])==15 and 'element is not visible' in ui['error'] and 'data-photo-category' in ui['error']
assert supplement['status']=='Pass' and not supplement['errors'] and len(supplement['rows'])==5 and supplement['origin']==ui['origin']=='http://127.0.0.1:8098/'
completed=[*(dict(row,evidence_root=folder) for row in ui['rows']),*(dict(row,evidence_root=extra) for row in supplement['rows'])]
assert len({(r['width'],r['height'],r['label']) for r in completed})==20
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));rows=[];downloads=[]
for row in completed:
    label=row['label'];location=row['evidence_root']/f"{row['width']}x{row['height']}"/label;read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');expected=deepcopy(fixture);expected['active']=fixture['layers'][1]['id'];assert before==expected
    source=image('before');assert source.shape==(640,960,4)
    if label=='basic':
        for state in ['basic','advanced-restored']:assert read(state)==before and np.array_equal(image(state),source)
        final=before;pixels=source
    else:
        final=read('after');pixels=image('after')
        if label.endswith('cancel'):
            assert final==before and np.array_equal(pixels,source)
            blank=deepcopy(before);blank['layers']=[deepcopy(before['layers'][0])];blank['active']=before['layers'][0]['id'];assert read('undone')==blank and (image('undone')==255).all(),'Cancel inserted an unexpected document Undo step'
        else:
            expected=deepcopy(before);expected['layers'][1]['photo']['settings']['brightness']=20;expected['layers'][1]['photo']['normal']['brightness']=20;assert final==expected
            assert read('undone')==before and np.array_equal(image('undone'),source)
            assert pixels[600,900,0]>source[600,900,0] and pixels[600,900,1]>source[600,900,1] and pixels[600,900,3]==255
        assert read('redone')==final and np.array_equal(image('redone'),pixels)
        assert row['restored_palette']==row['prior_palette_open']
    reopened_expected=deepcopy(final);assert 'clip' not in reopened_expected['layers'][2]['live']['strokes'][0];reopened_expected['layers'][2]['live']['strokes'][0]['clip']=None
    assert read('fresh/reopened')==reopened_expected and np.array_equal(image('fresh/reopened'),pixels)
    assert row['photo_and_layers_exclusive'] and row['target']=='Backdrop' and row['fresh_reopen_complete']
    for path in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in json.loads(path.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],variant=label,prior_palette_open=row['prior_palette_open'],actual_ui_exclusivity_and_restoration_verified=True,active_target_and_all_original_content_preserved=True,saved_recipe_and_history_coherent=True,full_size_rgba_and_actual_fresh_reopen_verified=True,only_optional_inactive_no_clip_default_added_on_reopen=True))
assert len(downloads)==192
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=192,render_time_ms=10000,oracle='Complete expected MIX/recipe/active state, exact independently decoded full-size PNGs, known white document Undo predecessor for Cancel, actual public visibility/inert/target observations, and saved-file fresh input. Only the precise known absent inactive-stroke clip→null canonicalisation is admitted.',execution='Isolated headless production UI; no desktop/user browser interaction')
report['coverage_chunks']=[dict(folder='headless/LAYER-015-final',completed_variants=15,unfinished='844x390 closed-cancel setup tried the hidden category button; excluded'),dict(folder='headless/LAYER-015-landscape-final',completed_variants=5,route='Actual combined group selector, the existing short-screen UI')]
(root/'evidence/LAYER-015-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
