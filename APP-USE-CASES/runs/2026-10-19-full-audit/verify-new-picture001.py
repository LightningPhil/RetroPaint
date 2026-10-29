from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import numpy as np
import json,base64,io,hashlib,sys
root=Path(__file__).resolve().parent;base=root/'headless/FILE-001-fixed';read_json=lambda p:json.loads(p.read_text(encoding='utf-8'));plan=read_json(root/'fixtures/FILE-001-plan.json');prefix='--completed-prefix' in sys.argv
if prefix:
    completed=[r for r in plan['positive_rows'] if (base/r['id']/'native-input.json').exists() and (base/r['id']/'fresh/reopened.png').exists()];assert completed;ui=dict(rows=completed,rejections=[])
else:
    ui=read_json(base/'FILE-001-ui.json');assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==20 and len(ui['rejections'])==4
downloads=[];rows=[];rejections=[]
def rgba(file):
    with Image.open(file) as im:return np.asarray(im.convert('RGBA'))
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
def files(location):
    for file in [location/'events.json',location/'fresh/events.json']:
        for event in read_json(file):
            if event['action']=='download':
                data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
def white_paper(doc,pixels,size):
    width,height=size;assert [doc['width'],doc['height']]==size and pixels.shape==(height,width,4) and (pixels==255).all();assert doc['format']=='RetroPaint' and doc['drawingMode']=='raster' and doc['crop']==dict(x=0,y=0,width=1,height=1);assert len(doc['layers'])==1;layer=doc['layers'][0];assert set(layer)=={'id','name','visible','opacity','paper','image','live'} and layer['name']=='Paper' and layer['visible'] is True and layer['opacity']==1 and layer['paper']=='#ffffff' and layer['live']==dict(strokes=[],fills=[],sparkles=[]) and doc['active']==layer['id'];assert np.array_equal(decoded(doc),pixels)
for row,planned in zip(ui['rows'],plan['positive_rows']):
    assert all(row[k]==v for k,v in planned.items());location=base/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:rgba(location/(label+'.png'));old=read('before');old_image=image('before');assert old_image.shape==(640,960,4) and (old_image!=255).any();new=read('new');blank=image('new');white_paper(new,blank,row['size']);assert new['layers'][0]['id']!=old['layers'][0]['id'];marked=read('marked');expected=deepcopy(new);expected['layers'][0]['image']=marked['layers'][0]['image'];assert marked==expected;pixels=image('marked');assert np.array_equal(pixels,decoded(marked)) and (pixels[:,:,3]==255).all();mask=(pixels!=blank).any(axis=2);ys,xs=np.where(mask);assert len(xs)>0;width,height=row['size'];maximum=float(np.hypot(xs+.5-width/2,ys+.5-height/2).max());assert maximum<=13,'New paper paint lands outside the declared22px centre nib';assert np.abs(pixels[min(height-1,height//2),min(width-1,width//2),:3].astype(int)-[229,57,53]).max()<=1,'New target has the wrong selected Red or position'
    for label,reference in [('marked-undone','new'),('marked-redone','marked'),('creation-undone','before'),('creation-redone','new'),('mark-redone-after-creation','marked'),('fresh/reopened','marked')]:assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),(row['id'],label,'Complete source/history/fresh pixels differ')
    native=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in native) and len([e for e in native if e['type']=='pointerdown'])==len([e for e in native if e['type']=='pointerup'])==2
    for event in native:assert np.linalg.norm(np.array(event['source'])-[event['width']/2,event['height']/2])<.001,'Native tap misses the unchanged source centre'
    files(location);rows.append(dict(id=row['id'],viewport=row['viewport'],size=row['size'],new_single_opaque_white_Paper_exact=True,valid_unique_active_target=True,changed_pixels=len(xs),maximum_paint_distance=maximum,all_old_new_mark_history_and_fresh_source_RGBA_exact=True))
for index,row in enumerate(ui['rejections']):
    location=base/('rejections-v'+str(index+1));read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:rgba(location/(label+'.png'));before=read('before');before_image=image('before');assert len(row['invalid_rows'])==len(plan['invalid_sizes'])==9
    for label in ['cancelled','escaped',*['invalid-'+str(i) for i in range(9)]]:assert read(label)==before and np.array_equal(image(label),before_image),'Cancel/Escape/rejection changed previous source or pixels'
    for label in ['cancel-pending-public',*['invalid-'+str(i)+'-pending-public' for i in range(9)]]:assert np.array_equal(rgba(location/(label+'.png')),before_image),'Picture changes while invalid/cancel draft is still open'
    for observation,planned in zip(row['invalid_rows'],plan['invalid_sizes']):assert observation['requested']==planned and observation['actual_fields']==planned and 'whole-pixel' in observation['message'] and '1' in observation['message'] and '4096' in observation['message']
    assert read('navigation-undone')==read('blank') and np.array_equal(image('navigation-undone'),image('blank'));assert read('navigation-redone')==before and np.array_equal(image('navigation-redone'),before_image),'Dialog navigation/rejection introduces history or damages Redo'
    corrected=read('corrected');corrected_image=image('corrected');white_paper(corrected,corrected_image,[320,240]);assert read('corrected-undone')==before and np.array_equal(image('corrected-undone'),before_image)
    for label in ['corrected-redone','fresh/reopened']:assert read(label)==corrected and np.array_equal(image(label),corrected_image),'Corrected valid retry/history/fresh data differ'
    files(location);rejections.append(dict(viewport=row['viewport'],invalid_categories=9,cancel_and_native_Escape_preserve_complete_source_RGBA=True,all_pending_public_pixels_exact=True,no_navigation_history_and_previous_Redo_exact=True,corrected_valid_retry_and_complete_history_fresh_exact=True))
assert len(downloads)==(18*len(rows) if prefix else 512)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='FILE-001',decoder='Pillow '+Image.__version__,rows=rows,rejections=rejections,actual_downloads_verified=len(downloads),all20_positive_and_four_full_failure_workflows_verified=not prefix,oracle=plan['oracle'],source='Actual controls/downloads only. Independent white-paper/known-Red/affected-mask/full-source comparisons. Thin/minimum sources use actual100% view to reach their original centre, with source dimensions unchanged. No app new/reset/serializer/renderer computes expected output.',scope='Completed positive prefix only; no case Pass.' if prefix else 'Complete planned positive and rejection/cancellation/history/retry scope.')
(root/('evidence/FILE-001-completed-prefix-verification.json' if prefix else 'evidence/FILE-001-independent-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='FILE-001',positive_rows=len(rows),rejection_workflows=len(rejections),actual_downloads=len(downloads),acceptance_complete=not prefix)))
