from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/LAYER-003-final'
ui=json.loads((folder/'LAYER-003-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));rows=[];downloads=[]
decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'))
encoded=np.array([30,136,229],dtype=float)/255;linear=np.where(encoded<=.04045,encoded/12.92,((encoded+.055)/1.055)**2.4)*2**.5;linear=np.clip(linear,0,1);blue=np.rint(np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)*255)
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');assert before==fixture
    hidden=read('hidden');expected=deepcopy(before);expected['layers'][1]['visible']=False;assert hidden==expected
    painted=read('hidden-painted');expected=deepcopy(hidden);expected['layers'][2]['image']=painted['layers'][2]['image'];assert painted==expected,'Foreground gesture changed unrelated source/layer/live/recipe/object data'
    original=decode(hidden['layers'][2]['image']);actual=decode(painted['layers'][2]['image']);changed=np.any(original!=actual,axis=2);ys,xs=np.where(changed);assert changed.sum()>1000 and xs.min()>=588 and xs.max()<=812 and ys.min()>=138 and ys.max()<=162
    assert np.array_equal(actual[150,700],[67,160,71,255])
    shown=read('shown-painted');expected=deepcopy(painted);expected['layers'][1]['visible']=True;assert shown==expected
    states={'show-undone':'hidden-painted','paint-undone':'hidden','hide-undone':'before','hide-redone':'hidden','paint-redone':'hidden-painted','show-redone':'shown-painted','fresh/reopened':'shown-painted'}
    for label,reference in states.items():assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),'Visibility/paint history or actual file reopen differs: '+label
    assert np.array_equal(image('hidden')[600,900],[255,255,255,255])
    assert np.abs(image('before')[600,900,:3].astype(float)-blue).max()<=1
    assert np.abs(image('hidden-painted')[150,700,:3].astype(float)-(.5*np.array([67,160,71])+.5*255)).max()<=1
    assert np.abs(image('shown-painted')[150,700,:3].astype(float)-(.5*np.array([67,160,71])+.5*blue)).max()<=1
    assert row['hidden_background_picker']=='#FFFFFF' and row['visibility_and_paint_history_separate'] and row['fresh_reopen_complete']
    for path in [location/'events.json',location/'fresh/events.json']:
        downloads += [e for e in json.loads(path.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],hidden_guide_excluded_from_export_and_actual_colour_pick=True,guide_original_bytes_and_all_non_target_data_exact=True,new_green_stroke_changed_pixels=int(changed.sum()),new_foreground_raw_change_bounds=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],independent_opacity_probes_match=True,three_separate_undo_redo_states_and_actual_fresh_reopen_exact=True))
assert len(downloads)==88
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=88,render_time_ms=10000,declared_blend_probe_tolerance_255=1,oracle='Independent full-size RGBA/raw-layer change masks, known green/white/blue patches, published sRGB +0.5EV and elementary alpha blending, complete parsed project fields, exact separate history states and actual saved-file reopen.',execution='Isolated headless production UI; no existing user browser or desktop interaction')
(root/'evidence/LAYER-003-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
