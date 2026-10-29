from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/LAYER-011-before';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'))
ui=read_json(folder/'LAYER-011-ui.json');assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
fixture=read_json(root/'headless/MIX-final/MIX-basic.retropaint');decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'));rows=[];downloads=[]
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'))
    before=read('before');expected=deepcopy(fixture);expected['active']=fixture['layers'][2]['id'];assert before==expected
    brief=read('brief');layer=brief['layers'][2];assert len(layer['objects'])==2 and not decode(layer['image']).any();existing,mark=layer['objects'];assert existing['kind']=='raster' and existing['matrix']==[1,0,0,1,0,0] and np.array_equal(decode(existing['image']),decode(before['layers'][2]['image']))
    expected=deepcopy(before);expected['layers'][2]['image']=layer['image'];expected['layers'][2]['objects']=layer['objects'];assert brief==expected
    def known_green(object,probe,bounds):
        assert object['kind']=='raster' and object['opacity']==1 and object['matrix'][:4]==[1,0,0,1] and not object.get('live') and object['wet'] is False
        raw=decode(object['image']);x,y=object['matrix'][4:];assert x==int(x) and y==int(y);px,py=probe;assert np.array_equal(raw[int(py-y),int(px-x)],[67,160,71,255]);ys,xs=np.where(raw[:,:,3]>0);left,top,right,bottom=bounds;assert (xs+x>=left).all() and (xs+x<=right).all() and (ys+y>=top).all() and (ys+y<=bottom).all()
    known_green(mark,(700,150),(608,138,812,162))
    allowed=np.zeros((640,960),dtype=bool);allowed[138:164,608:814]=True;changed=(image('brief')!=image('before')).any(axis=2);assert changed.any() and not (changed&~allowed).any()
    assert int(np.abs(image('brief')[150,700,:3].astype(int)-(np.array([67,160,71])+np.array([30,136,229]))/2).max())<=1
    hidden=read('hidden-mark');assert len(hidden['layers'][2]['objects'])==3;expected=deepcopy(brief);expected['layers'][2]['objects'].append(hidden['layers'][2]['objects'][-1]);assert hidden==expected;known_green(hidden['layers'][2]['objects'][-1],(625,200),(588,188,662,212))
    allowed=np.zeros((640,960),dtype=bool);allowed[188:214,588:664]=True;changed=(image('hidden-mark')!=image('brief')).any(axis=2);assert changed.any() and not (changed&~allowed).any()
    live=read('live');assert len(live['layers'][2]['objects'])==4;water=live['layers'][2]['objects'][-1];expected=deepcopy(hidden);expected['layers'][2]['objects'].append(water);assert live==expected
    assert water['kind']=='raster' and water['matrix'][:4]==[1,0,0,1] and water['liveSize']==dict(width=960,height=640) and water['wet'] is False
    assert not water['live']['strokes'] and not water['live']['sparkles'] and len(water['live']['fills'])==1 and water['live']['fills'][0]['spec']['texture']=='water' and water['live']['fills'][0]['spec']['speed']==1
    assert read('live-undone')==hidden and np.array_equal(image('live-undone'),image('hidden-mark'));assert read('live-redone')==live and np.array_equal(image('live-redone'),image('live'))
    fresh=deepcopy(live)
    for index in [1,2,3]:assert fresh['layers'][2]['objects'][index]['wet'] is False;del fresh['layers'][2]['objects'][index]['wet']
    assert read('fresh/reopened')==fresh and np.array_equal(image('fresh/reopened'),image('live'))
    thumbs={label:{id:image(label+'-layer-'+str(id)) for id in [1,2,3,4]} for label in ['before','brief','hidden-mark','live-a','live-b']}
    for label in thumbs:
        for id,pixels in thumbs[label].items():
            assert pixels.shape==(48,64,4)
            if id!=3:assert np.array_equal(pixels,thumbs['before'][id]),'Unchanged sheet preview changed'
    def thumb_region(a,b,bounds):
        changed=(a!=b).any(axis=2);left,top,right,bottom=bounds;allowed=np.zeros((48,64),dtype=bool);allowed[top:bottom,left:right]=True;assert changed.any() and not (changed&~allowed).any();return int(changed.sum())
    brief_count=thumb_region(thumbs['before'][3],thumbs['brief'][3],(39,10,56,16));hidden_count=thumb_region(thumbs['brief'][3],thumbs['hidden-mark'][3],(38,14,46,19));live_count=thumb_region(thumbs['live-a'][3],thumbs['live-b'][3],(4,28,36,35))
    mark_thumb=thumbs['brief'][3][10:16,39:56];green=(mark_thumb[:,:,3]>20)&(mark_thumb[:,:,1].astype(int)>mark_thumb[:,:,0].astype(int)+40)&(mark_thumb[:,:,1].astype(int)>mark_thumb[:,:,2].astype(int)+40);assert green.any()
    reopened_thumb=image('fresh/reopened-char-thumbnail');allowed=np.zeros((48,64),dtype=bool);allowed[28:35,4:36]=True;assert not (((reopened_thumb!=thumbs['hidden-mark'][3]).any(axis=2))&~allowed).any() and reopened_thumb[28:35,4:36,3].any()
    for label in ['static-idle','hidden-live','visible-live']:
        observed=read_json(location/(label+'-canvas-calls.json'));assert observed['elapsed_ms']>=1100 and not observed['overflow'] and not observed['enabled'];view=[c for c in observed['calls'] if c['canvas']=='view'];thumbnail=[c for c in observed['calls'] if c['layer']]
        if label=='static-idle':assert not view and not thumbnail
        elif label=='hidden-live':assert view and not thumbnail
        else:assert view and thumbnail
    for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in read_json(file) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],brief_known_green_mark_and_only_correct_thumbnail_verified=True,brief_thumbnail_changed_pixels=brief_count,hidden_mark_thumbnail_changed_pixels=hidden_count,real_live_thumbnail_changed_pixels=live_count,other_three_thumbnails_exact=True,static_idle_view_and_thumbnail_calls=0,hidden_palette_live_picture_updates_without_row_repaints=True,visible_live_thumbnails_update=True,full_document_history_and_reopened_rgba_exact=True,reopen_only_omits_three_explicit_false_transient_wet_flags=True))
assert len(downloads)==56
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=56,oracle='Independent known green source pixels, full-document edit masks and alpha blending (predeclared1/255), explicit untouched source layer/object data, mathematically mapped64x48 thumbnail bounds, independently decoded temporal PNG differences and observational real elapsed Canvas calls. Static idle requires zero full view/thumbnail calls; hidden/live visibility branches and exact phase10000ms history/fresh project PNG are separately checked.',representation_change='Only objects[1,2,3].wet=false is omitted on project input. These are completed dry strokes, with no active drips. The reader excludes the transient wet runtime flag, and all pixels, masks, live definitions, IDs, transforms and rendered PNGs are exact. Exact differences retained in evidence/LAYER-011-reopen-differences.json. No broad normalisation.',execution='Actual public UI in isolated headless production contexts; native time for animation/idle observations, explicit fixed time only for completed save/history comparisons')
(root/'evidence/LAYER-011-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
