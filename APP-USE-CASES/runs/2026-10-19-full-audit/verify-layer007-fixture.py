from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/LAYER-007-fixture';read=lambda file:json.loads((folder/file).read_text(encoding='utf-8'))
ui=read('duplicate-fixture-ui.json');assert ui['status']=='Pass' and not ui['errors'] and ui['fresh_reopen_complete']
before=read('producer/before.retropaint');source=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));assert before==source
made=read('producer/enriched.retropaint');fresh=read('fresh/fixture.retropaint');expected=deepcopy(made);assert 'clip' not in expected['layers'][2]['objects'][0]['live']['strokes'][0];expected['layers'][2]['objects'][0]['live']['strokes'][0]['clip']=None;assert fresh==expected
decode=lambda data:np.asarray(Image.open(io.BytesIO(base64.b64decode(data.split(',',1)[1]))).convert('RGBA'))
layer=fresh['layers'][2];raster,text=layer['objects'];assert raster['kind']=='raster' and raster['name']=='Existing artwork' and raster['matrix']==[1,0,0,1,0,0] and raster['opacity']==1 and raster['width']==960 and raster['height']==640
assert np.array_equal(decode(raster['image']),decode(source['layers'][2]['image']))
live=deepcopy(source['layers'][2]['live']);live['strokes'][0]['clip']=None;assert raster['live']==live and not any(layer['live'].values()) and not decode(layer['image']).any()
assert text['kind']=='text' and text['font']=='24px "Arial"' and text['matrix']==[1,0,0,1,300,300] and [line['text'] for line in text['lines']]==['Copy source'] and text['color']=='#E53935'
assert layer['photo']['settings']['brightness']==10 and layer['photo']['settings']['exposure']==.25 and layer['photo']['normal']==layer['photo']['settings'] and layer['photo']['look']=='custom'
expected=deepcopy(source);expected['drawingMode']='vector';expected['layers'][2]=layer;assert fresh==expected
a=np.asarray(Image.open(folder/'producer/enriched.png').convert('RGBA'));b=np.asarray(Image.open(folder/'fresh/fixture.png').convert('RGBA'));assert np.array_equal(a,b)
reference=np.asarray(Image.open(root/'headless/LAYER-001-complete/1280x720/before.png').convert('RGBA'));changed=(a!=reference).any(axis=2);allowed=np.zeros(changed.shape,dtype=bool);allowed[70:600,60:550]=True;allowed[299:342,299:662]=True;assert changed.any() and not (changed&~allowed).any()
events=[event for file in ['producer/events.json','fresh/events.json'] for event in read(file) if event['action']=='download'];assert len(events)==5
for event in events:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),project=str(folder/'fresh/fixture.retropaint'),sha256=hashlib.sha256((folder/'fresh/fixture.retropaint').read_bytes()).hexdigest(),decoder='Pillow '+Image.__version__,actual_downloads_verified=5,original_MIX_source_pixels_and_live_definitions_retained_in_editable_raster_object=True,new_text_content_and_default_centred_position_verified=True,independent_saved_photo_recipe=dict(exposure=.25,brightness=10),all_other_sheets_exact=True,fresh_rgba_exact=True,only_reopen_representation_change='objects[0].live.strokes[0].clip absent -> null, the known optional no-clipping default',scope='Fixture preparation only, not an acceptance case Pass. All content created through actual public controls; no application serializer/renderer supplied the expected saved data.')
(root/'fixtures/LAYER-007-combined-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
