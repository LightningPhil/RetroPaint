"""Full-source image import oracle using independent Pillow decoders and geometry."""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image,ImageOps
import numpy as np
import json,hashlib,base64,io,sys
root=Path(__file__).resolve().parent;base=root/'headless/FILE-002-complete';read_json=lambda p:json.loads(p.read_text(encoding='utf-8'));plan=read_json(root/'fixtures/FILE-002-plan.json');prefix='--completed-prefix' in sys.argv
def ready(row):
    location=base/row['id'];event_file=location/'fresh/events.json'
    if not (location/'native-input.json').exists() or not event_file.exists():return False
    return len([e for e in read_json(event_file) if e['action']=='download'])==2
if prefix:
    complete=[r for r in plan['positive_rows'] if ready(r)];assert complete;ui=dict(rows=complete,rejections=[],cancellations=[])
else:
    ui=read_json(base/'FILE-002-ui.json');assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==48 and len(ui['rejections'])==28 and len(ui['cancellations'])==4
downloads=[];rows=[];rejected=[];cancelled=[]
def rgba(file):
    with Image.open(file) as image:return np.asarray(image.convert('RGBA'))
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
def files(location):
    for file in [location/'events.json',location/'fresh/events.json']:
        for event in read_json(file):
            if event['action']=='download':
                data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
def imported(doc,pixels,fixture):
    file=Path(fixture['path']);data=file.read_bytes();assert hashlib.sha256(data).hexdigest()==fixture['sha256'];original=np.asarray(ImageOps.exif_transpose(Image.open(file)).convert('RGBA'));assert hashlib.sha256(original.tobytes()).hexdigest()==fixture['decoded_rgba_sha256'];assert pixels.shape==original.shape==(fixture['size'][1],fixture['size'][0],4) and [doc['width'],doc['height']]==fixture['size'];assert np.array_equal(decoded(doc),pixels),'Actual PNG disagrees with saved source raster'
    assert doc['format']=='RetroPaint' and doc['drawingMode']=='raster' and doc['crop']==dict(x=0,y=0,width=1,height=1) and len(doc['layers'])==1;layer=doc['layers'][0];assert set(layer)=={'id','name','visible','opacity','paper','image','live'} and layer['name']=='Layer 1' and layer['paper'] is None and layer['visible'] is True and layer['opacity']==1 and doc['active']==layer['id'] and layer['live']==dict(strokes=[],fills=[],sparkles=[])
    assert np.array_equal(pixels[:,:,3],original[:,:,3]),'Imported source alpha changed';nonzero=original[:,:,3]>0;error=np.abs(pixels[:,:,:3].astype(int)-original[:,:,:3].astype(int));maximum=int(error[nonzero].max());tolerance=1 if fixture['file']=='Laukka sunset.jpg' else 2 if fixture['decoder_format'] in ['JPEG','WEBP'] else 1 if fixture['alpha_minimum']<255 else 0;assert maximum<=tolerance,(fixture['file'],'Independent decoded RGB mismatch',maximum,tolerance)
    return dict(source_sha256=fixture['sha256'],decoder_format=fixture['decoder_format'],oriented_size=fixture['size'],maximum_independent_RGB_error=maximum,declared_tolerance=tolerance,alpha_exact=True,source_RGBA_equals_actual_PNG=True,independent_decoded_source_and_orientation_verified=True)
for row,planned in zip(ui['rows'],plan['positive_rows']):
    assert all(row[k]==v for k,v in planned.items());location=base/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:rgba(location/(label+'.png'));fixture=next(f for f in plan['fixtures'] if f['file']==row['fixture']);before=read('before');before_pixels=image('before');assert before_pixels.shape==(640,960,4) and (before_pixels!=255).any();doc=read('imported');pixels=image('imported');source_metrics=imported(doc,pixels,fixture);assert doc['active']!=before['active'];marked=read('marked');expected=deepcopy(doc);expected['layers'][0]['image']=marked['layers'][0]['image'];assert marked==expected;painted=image('marked');assert np.array_equal(painted,decoded(marked));mask=(painted!=pixels).any(axis=2);ys,xs=np.where(mask);assert len(xs)>0;point=row['mark'];maximum=float(np.hypot(xs+.5-point[0],ys+.5-point[1]).max());assert maximum<=13,'Image mark is misaligned or changes pixels beyond its declared22px nib';x,y=int(point[0]),int(point[1]);assert np.abs(painted[y,x].astype(int)-[229,57,53,255]).max()<=1,'The centre mark missed its imported source target or pigment'
    for label,reference in [('marked-undone','imported'),('marked-redone','marked'),('import-undone','before'),('import-redone','imported'),('mark-redone-after-import','marked'),('fresh/reopened','marked')]:assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),(row['id'],label,'Complete import/mark/history/fresh source or RGBA differs')
    native=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in native);downs=[e for e in native if e['type']=='pointerdown'];ups=[e for e in native if e['type']=='pointerup'];assert len(downs)==len(ups)==2
    for events in [downs,ups]:assert np.linalg.norm(np.array(events[0]['source'])-[480,320])<.001 and np.linalg.norm(np.array(events[1]['source'])-point)<.001 and [events[1]['width'],events[1]['height']]==row['size']
    files(location);rows.append(dict(id=row['id'],viewport=row['viewport'],fixture=row['fixture'],**source_metrics,native_paint_target=point,changed_pixels=len(xs),maximum_paint_distance=maximum,untouched_pixels_alpha_and_unrelated_data_exact=True,all_import_mark_history_and_fresh_source_RGBA_exact=True))
for mode,group,planned_group in [('rejected',ui['rejections'],plan['negative_rows']),('cancelled',ui['cancellations'],plan['cancellation_rows'])]:
    for row,planned in zip(group,planned_group):
        assert all(row[k]==v for k,v in planned.items());location=base/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:rgba(location/(label+'.png'));before=read('before');pixels=image('before');assert (pixels!=255).any() and np.array_equal(image('blank'),np.full((640,960,4),255,dtype=np.uint8));assert read('retained')==before and np.array_equal(image('retained'),pixels),'Rejected/cancelled file partially replaces the document'
        assert read('navigation-undone')==read('blank') and np.array_equal(image('navigation-undone'),image('blank')) and read('navigation-redone')==before and np.array_equal(image('navigation-redone'),pixels),'File rejection/cancel adds history or damages prior Redo'
        retry=read('retry');retry_image=image('retry');fixture=next(f for f in plan['fixtures'] if f['file']=='ORIENT.png');retry_stats=imported(retry,retry_image,fixture);assert read('retry-undone')==before and np.array_equal(image('retry-undone'),pixels)
        for label in ['retry-redone','fresh/reopened']:assert read(label)==retry and np.array_equal(image(label),retry_image),'Actual recovery retry/history/fresh source differs'
        observed=dict(id=row['id'],viewport=row['viewport'],complete_source_and_RGBA_rejection_atomic=True,old_history_and_Redo_exact=True,valid_PNG_retry_history_and_fresh_source_RGBA_exact=True,retry=retry_stats)
        if mode=='cancelled':
            events=read_json(location/'native-chooser-events.json');assert row['native_cancel'] and row['OS_chooser_visual_certification'] is False and len(events)==1 and events[0]['type']=='cancel' and events[0]['trusted'] and events[0]['files']==0;observed['genuine_browser_native_trusted_cancel_observed']=True;cancelled.append(observed)
        else:
            rejected_fixture=next(f for f in plan['rejected_fixtures'] if f['file']==row['fixture']);assert hashlib.sha256(Path(rejected_fixture['path']).read_bytes()).hexdigest()==rejected_fixture['sha256'];assert row['actual_explanation'] and any(s in row['actual_explanation'] for s in ['could not be opened','damaged','unsupported']);observed.update(fixture=row['fixture'],actual_explanation=row['actual_explanation']);rejected.append(observed)
        files(location)
assert len(downloads)==(18*len(rows) if prefix else 1440)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='FILE-002',decoder='Pillow '+Image.__version__,positive_rows=rows,rejections=rejected,cancellations=cancelled,actual_downloads_verified=len(downloads),all48_positive28_rejected_four_native_cancel_rows_verified=not prefix,oracle=plan['oracle'],scope='Completed positive prefix only; no case Pass.' if prefix else 'All preplanned formats/channel models/orientation/transparency/photo/layout, genuine corrupt/unsupported bytes, native browser chooser cancellation, full history and actual fresh input.',limitation='Native browser chooser request cancellation is verified; the operating system file-dialog visual design and physical device are not certified.')
(root/('evidence/FILE-002-completed-prefix-verification.json' if prefix else 'evidence/FILE-002-independent-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='FILE-002',positive_rows=len(rows),rejected_rows=len(rejected),native_cancel_rows=len(cancelled),actual_downloads=len(downloads),acceptance_complete=not prefix)))
