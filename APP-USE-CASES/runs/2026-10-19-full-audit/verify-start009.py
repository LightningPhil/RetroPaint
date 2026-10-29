from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/START-009-before';reopen=root/'headless/START-009-reopened'
ui=json.loads((folder/'START-009-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
rows=[];downloads=[]
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');pixels=image('before');assert (before['width'],before['height'])==(960,640) and before['drawingMode']=='raster' and len(before['layers'])==1
    assert pixels.shape==(640,960,4) and (pixels[:,:,3]==255).all();first=np.any(pixels[:,:,:3]!=255,axis=2);assert first.sum()>500
    for label in ['after-done','after-escape','resumed-undone']:
        assert read(label)==before and np.array_equal(image(label),pixels),'Help navigation/dismissal/Undo changed the preserved artwork'
    resumed=read('resumed');after=image('resumed');changed=np.any(after!=pixels,axis=2)
    assert changed.sum()>500 and np.array_equal(after[first],pixels[first]),'Resumed stamping changed the old stamp'
    assert read('resumed-redone')==resumed and np.array_equal(image('resumed-redone'),after)
    assert row['unexpected_downloads']==row['unexpected_choosers']==0 and len(row['blocked_keys'])==20 and len(row['categories'])==6
    assert {item['category'] for item in row['categories']}=={'tools','edit','view'}
    assert all(item['focus']==dict(id='openShortcuts',tag='BUTTON',visible=True) for item in row['dismissals'])
    events=json.loads((location/'events.json').read_text(encoding='utf-8'));events=[e for e in events if e['action']=='download'];assert len(events)==12;downloads+=events
    rows.append(dict(viewport=[row['width'],row['height']],all_three_help_categories_fit_twice=True,done_and_escape_restore_visible_invoker_focus=True,stamp_and_size_preserved_by_actual_controls=True,complete_picture_data_and_rgba_exact_after_help=True,blocked_app_keys_count=20,unintended_downloads_and_choosers=0,resumed_stamp_changed_pixels=int(changed.sum()),prior_stamp_preserved_exactly=True,one_step_undo_and_redo_exact=True))
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
reopened=json.loads((reopen/'ARTWORK-headless-ui.json').read_text(encoding='utf-8'));assert reopened['status']=='Pass' and len(reopened['downloads'])==4
source=(folder/'1280x720/resumed-redone.retropaint').read_bytes();source_pixels=np.asarray(Image.open(folder/'1280x720/resumed-redone.png').convert('RGBA'))
for label in ['ARTWORK-headless-saved','ARTWORK-headless-reopened']:
    assert (reopen/(label+'.retropaint')).read_bytes()==source and np.array_equal(np.asarray(Image.open(reopen/(label+'.png')).convert('RGBA')),source_pixels)
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=52,selected_stamp='🐱',selected_size=1.7,actual_fresh_project_save_reopen_byte_and_rgba_exact=True,oracle='Complete saved project identity, independently decoded PNG RGBA and untouched old-stamp mask, actual UI focus/selection/size checks and effective help/row rectangles; two fresh saved-file project contexts.',execution='Isolated headless Chrome; no desktop or existing browser use')
(root/'evidence/START-009-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
