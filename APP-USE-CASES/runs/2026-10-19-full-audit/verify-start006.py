from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/START-006-complete'
ui=json.loads((folder/'START-006-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==2
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));rows=[];downloads=[]
for row in ui['rows']:
    mode=row['mode'];location=folder/mode;read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');pixels=image('before');assert before==fixture
    if mode=='aged':assert row['real_elapsed_ms']>=121000 and row['native_elapsed_ms']>=120000 and row['confirmation_shown']
    else:assert row['real_elapsed_ms']<120000 and row['native_elapsed_ms']<120000 and not row['confirmation_shown']
    cleared=read('cleared');assert len(cleared['layers'])==1 and cleared['layers'][0]['name']=='Paper' and cleared['layers'][0]['paper']=='#ffffff'
    layer=cleared['layers'][0];assert layer['visible'] and layer['opacity']==1 and not layer.get('photo') and not layer.get('objects') and not layer.get('cad') and not any(layer['live'].values())
    assert cleared['crop']==dict(x=0,y=0,width=1,height=1) and cleared['width']==960 and cleared['height']==640
    assert (image('cleared')==255).all() and read('redone')==cleared and np.array_equal(image('redone'),image('cleared'))
    for label in ['undone','fresh/restored-reopened']:
        assert read(label)==before and np.array_equal(image(label),pixels),'Undo/fresh reopen did not restore every mixed-content field and controlled-time pixel'
    assert row['undo_redo_complete'] and row['actual_fresh_restored_project_reopen']
    for path in [location/'events.json',location/'fresh/events.json']:
        downloads += [e for e in json.loads(path.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(mode=mode,real_elapsed_ms=row['real_elapsed_ms'],native_elapsed_ms=row['native_elapsed_ms'],render_comparison_time_ms=row['render_time_ms'],confirmation=row['confirmation_shown'],single_white_paper_clear_outcome=True,all_layers_originals_objects_photo_and_live_definitions_restored=True,controlled_full_size_undo_and_reopen_rgba_exact=True,redo_complete_data_and_rgba_exact=True))
assert len(downloads)==20
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),fixture='fixtures/MIX-manifest.json',oracle='Complete saved MIX and restored project data, independently decoded RGBA at identical declared live rendering time, exact known white clear pixels, explicit absence of live/object/photo/CAD remnants and measured real/native elapsed age.',clock_scope='No clock substitution during real ageing or Clear animation. Only completed artwork renders use the declared phase timestamp for exact live-ink comparisons. Native Date elapsed and unfixed performance elapsed both independently recorded before freezing.',execution='Actual headless controls and downloaded files; no desktop or existing user browser access')
(root/'evidence/START-006-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
