from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import components,distances
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PAINT-009-complete';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'PAINT-009-ui.json');plan=read_json(root/'fixtures/PAINT-009-plan.json');assert ui['status']=='Pass' and not ui['errors'] and [r['viewport'] for r in ui['rows']]==plan['viewports']
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
rows=[];downloads=[];red=np.array([229,57,53],float);blue=np.array([30,136,229],float)
for row in ui['rows']:
    location=folder/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and (blank==255).all() and before['drawingMode']=='raster' and len(before['layers'])==1
    paths=[dict(label='blue-left',centre=[200,440],strength=1,half=100,width=96),dict(label='blue-right',centre=[700,440],strength=1,half=100,width=96),*[dict(g,half=60,width=22) for g in plan['gestures']]];previous=blank;source_previous=before;stage={};patches={};metrics={}
    for item in paths:
        label=item['label'];doc=read(label);expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected;pixels=image(label);assert np.array_equal(pixels,decoded(doc)) and (pixels[:,:,3]==255).all();mask=(pixels!=previous).any(axis=2);assert components(mask)==1,label+' is disconnected';ys,xs=np.where(mask);x,y=item['centre'];distance=distances([[x-item['half'],y],[x+item['half'],y]],xs,ys);assert distance.max()<=item['width']/2+2,'Strength change affects unrelated source pixels'
        patch=previous[y-5:y+6,x-5:x+6,:3].astype(float);colour=blue if label.startswith('blue-') else red;expected_patch=np.rint(patch*(1-item['strength'])+colour*item['strength']);actual_patch=pixels[y-5:y+6,x-5:x+6,:3].astype(float);error=int(np.abs(actual_patch-expected_patch).max());assert error<=2,label+' disagrees with independently computed source-over Strength';assert np.all(actual_patch==actual_patch[0,0]),'Known centre patch is not uniform'
        patches[label]=actual_patch[0,0].astype(int).tolist();metrics[label]=dict(changed_pixels=int(mask.sum()),maximum_path_distance=float(distance.max()),known_centre_patch_max_error=error);previous=pixels;source_previous=doc;stage[label]=pixels
    assert read('spray-selected')==read('colour-full') and read('biro-selected')==read('colour-full') and read('marker-restored')==read('colour-full'),'Tool/drawer transitions mutate previous marks'
    assert np.linalg.norm(np.array(patches['white-weak'])-255)<np.linalg.norm(np.array(patches['white-full'])-255)
    assert np.linalg.norm(np.array(patches['colour-weak'])-blue)<np.linalg.norm(np.array(patches['colour-full'])-blue)
    for name,backing in [('white',np.full(3,255.)),('colour',blue)]:assert np.linalg.norm(np.array(patches[name+'-overlap'])-red)<np.linalg.norm(np.array(patches[name+'-weak'])-red),'Second weak pass fails to accumulate'
    labels=[p['label'] for p in paths]
    for index,label in enumerate(labels):assert read(label+'-undone')==read('before' if index==0 else labels[index-1]) and read(label+'-redone')==read(label),label+' history loses exact previous source state'
    assert read('fresh/reopened')==read(labels[-1]) and np.array_equal(image('fresh/reopened'),previous)
    inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==8
    events=read_json(location/'events.json');checks=[e for e in events if e['action']=='visible-strength-and-range-agree'];assert len(checks)==10 and all((str(round(e['value']*100))+'%') in e['label'] for e in checks)
    for file in [location/'events.json',location/'fresh/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
    rows.append(dict(viewport=row['viewport'],patch_RGB=patches,independent_blend_metrics=metrics,range_and_visible_strength_label_checks=len(checks),all_selection_only_data_exact=True,every_eight_gesture_undo_redo_exact=True,actual_fresh_source_RGBA_exact=True))
assert len(downloads)==156
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),all_planned_rows_verified=True,oracle=plan['oracle'],execution=ui['execution']);(root/'evidence/PAINT-009-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-009',rows=len(rows),downloads=len(downloads))))
