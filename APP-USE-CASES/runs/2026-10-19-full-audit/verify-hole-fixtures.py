from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image,ImageColor
import numpy as np
import json,hashlib,base64,io
root=Path(__file__).resolve().parent;base=root/'headless/HOLE-producer';read=lambda p:json.loads(p.read_text(encoding='utf-8'));rgba=lambda p:np.asarray(Image.open(p).convert('RGBA'));decode=lambda layer:rgba(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1])));ui=read(base/'HOLE-producer-ui.json');assert ui['status']=='Pass' and not ui['errors'];clear=read(base/'HOLE-clear.retropaint');paper=read(base/'HOLE-Paper.retropaint');assert [clear['width'],clear['height']]==[960,640] and [paper['width'],paper['height']]==[960,640] and clear['drawingMode']==paper['drawingMode']=='raster' and len(clear['layers'])==2 and len(paper['layers'])==1
guide,paint=clear['layers'];assert [guide['name'],paint['name']]==['Green guide','Paint to erase'] and guide['paper'] is None and paint['paper'] is None and clear['active']==paint['id'];assert guide['visible'] and paint['visible'] and guide['opacity']==paint['opacity']==1;green=decode(guide);actual=decode(paint);assert (green==[67,160,71,255]).all();wanted=np.asarray(Image.open(root/'fixtures/SMUDGE.png').convert('RGBA').resize((960,640),Image.Resampling.NEAREST));assert np.array_equal(actual,wanted),'Actual nearest resize disagrees with independent source/coordinate mapping';assert set(np.unique(actual[:,:,3]))=={0,255} and not actual[:,:,1].any() and (actual[200:440,160:400]==[255,0,0,255]).all() and (actual[200:440,500:760]==[0,0,255,255]).all();expected=np.where(actual[:,:,3,None]>0,actual,green);assert np.array_equal(rgba(base/'HOLE-clear.png'),expected)
layer=paper['layers'][0];assert layer['id']==guide['id'] and paper['active']==layer['id'] and layer['name']=='Paper' and ImageColor.getrgb(layer['paper'])==(255,255,255) and layer['visible'] and layer['opacity']==1;assert np.array_equal(decode(layer),expected) and np.array_equal(rgba(base/'HOLE-Paper.png'),expected);assert (decode(layer)[:,:,3]==255).all()
for kind,doc in [('clear',clear),('Paper',paper)]:
    assert read(base/f'fresh-{kind}/reopened.retropaint')==doc and np.array_equal(rgba(base/f'fresh-{kind}/reopened.png'),expected),'Actual fresh project input changes fixture source/RGBA'
    assert not any(any(l['live'][key] for key in ['strokes','fills','sparkles']) or l.get('photo') or l.get('objects') or l.get('cad') for l in doc['layers'])
downloads=[]
for folder in [base,base/'fresh-clear',base/'fresh-Paper']:
    for event in read(folder/'events.json'):
        if event['action']=='download':data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
assert len(downloads)==8
report=dict(at=datetime.now(timezone.utc).isoformat(),status='Verified native Black Hole fixtures only; not PAINT015 Pass',dimensions=[960,640],source='Real SMUDGE project resized through actual controls with smoothing off; defined white Paper made by actual checkbox/merge. Independent Pillow nearest/elementary opaque composition exact.',records=[dict(kind=kind,path=str((base/f'HOLE-{kind}.retropaint').relative_to(root)),sha256=hashlib.sha256((base/f'HOLE-{kind}.retropaint').read_bytes()).hexdigest(),target_layer_id=doc['active'],layers=len(doc['layers'])) for kind,doc in [('clear',clear),('Paper',paper)]],known_Red_box=[120,160,420,480],known_Blue_box=[480,160,780,480],underlying_Green_RGBA=[67,160,71,255],clear_target_has_no_Green_or_opaque_Black=True,defined_Paper_colour_RGB=[255,255,255],complete_fresh_source_RGBA_exact=True,actual_downloads_verified=8)
(root/'fixtures/HOLE-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
