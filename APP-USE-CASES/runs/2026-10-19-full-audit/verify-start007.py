from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/START-007-complete'
ui=json.loads((folder/'START-007-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'))
rows=[];downloads=[]
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');pixels=image('before');assert before==fixture and pixels.shape==(640,960,4)
    for label in ['advanced-on','advanced-off','advanced-again','persisted-off-source','fresh-on/reopened','fresh-off/reopened','modes-redone']:
        assert read(label)==before and np.array_equal(image(label),pixels),'Mode navigation or reopen changed MIX data/controlled-time composition'
    assert (image('modes-undone')==255).all(),'Mode changes inserted an unexplained document history step'
    returned=read('cad-returned');assert len(returned['layers'])==5
    # New layers are inserted above the active Character sheet, preserving
    # Caption above them. They are not unconditionally appended to the stack.
    index=next(i for i,l in enumerate(before['layers']) if l['id']==before['active'])+1
    cad=returned['layers'][index];expected=deepcopy(before);expected['layers'].insert(index,cad);assert returned==expected
    assert cad['id'] not in {l['id'] for l in before['layers']} and cad['cad']['units']=='mm' and cad['cad']['bodies']==[] and cad['visible'] and cad['opacity']==1
    raw=np.asarray(Image.open(io.BytesIO(base64.b64decode(cad['image'].split(',',1)[1]))).convert('RGBA'));assert not raw[:,:,3].any()
    assert np.array_equal(image('cad-returned'),pixels),'Empty CAD workshop or guide hide/show left visible output fragments'
    assert row['main_modes']==[True,False,True] and row['persisted_modes']==[True,False] and all(row[key] for key in ['history_exercised','basic_workshop_layers_visible','backdrop_hide_show','layers_remain_on_return','paint_layer_selectable'])
    for path in [location/'events.json',location/'fresh-on/events.json',location/'fresh-off/events.json']:
        downloads += [e for e in json.loads(path.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],render_time_ms=10000,all_mode_changes_and_both_persisted_preferences_verified=True,complete_mixed_content_and_controlled_rgba_exact=True,navigation_adds_no_document_history_step=True,basic_workshop_exposes_layers_and_guide_visibility=True,layers_remain_after_workshop_close_and_paint_sheet_selectable=True,empty_created_cad_layer_only_expected_document_addition=True))
assert len(downloads)==80
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),fixture='fixtures/MIX-manifest.json',clock_scope='Browser performance.now and RAF callback timestamps held at10000ms; timers/Date/native UI unaffected. Explicit controlled animation comparison, not real elapsed-time/performance evidence.',oracle='Complete real project comparisons, raw original PNG/objects/live/recipe identity, independently decoded controlled-time full-size exports, expected white history predecessor, and explicit empty CAD layer check. UI observations verify visibility, focus-ready workshop, guide hide/show, return and paint target.',execution='Isolated headless Chrome; no desktop or existing user browser interaction')
(root/'evidence/START-007-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
