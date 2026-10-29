from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/MIX-final'
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'))
decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'))
ui=json.loads((folder/'MIX-producer-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and ui['fresh_reopen_complete']
basic=read('MIX-basic');enriched=read('MIX-enriched');assert read('fresh/MIX-reopened')==enriched
assert (enriched['width'],enriched['height'])==(960,640) and len(enriched['layers'])==4 and len({l['id'] for l in enriched['layers']})==4
assert [l['name'] for l in enriched['layers']]==['Paper','Backdrop','Character','Caption']
paper,backdrop,character,caption=enriched['layers'];assert all(l['visible'] for l in enriched['layers']) and [l['opacity'] for l in enriched['layers']]==[1,1,.5,1]
assert (decode(paper['image'])==255).all()
assert (decode(backdrop['image'])==np.array([30,136,229,255])).all()
raw=decode(character['image']);assert (raw[110:170,110:190]==[229,57,53,255]).all() and (raw[310:370,410:490]==[67,160,71,255]).all() and raw[600,900,3]==0
assert len(caption['objects'])==2 and [o['kind'] for o in caption['objects']]==['text','stamp']
text,stamp=caption['objects'];assert [line['text'] for line in text['lines']]==['MIX caption'] and text['size']==36 and 'Arial' in text['font'] and stamp['emoji']=='\U0001f431'
assert not decode(caption['image'])[:,:,3].any()
for original,current in zip(basic['layers'],enriched['layers']):
    assert original['image']==current['image'] and original.get('objects')==current.get('objects')
    assert not original['live']['strokes'] and not original['live']['fills'] and not original['live']['sparkles']
recipe=backdrop['photo'];assert recipe['settings']['exposure']==.5 and recipe['settings']==recipe['normal'] and recipe['look']=='custom' and not recipe['lookActive']
assert len(character['live']['fills'])==1 and len(character['live']['strokes'])==1 and not character['live']['sparkles']
water=character['live']['fills'][0];assert water['spec']==dict(kind='texture',colors=[],speed=1,mode='snap',along=False,texture='water') and water['opacity']==1 and water['gradient'] is None
mask=decode(water['mask']);assert mask.shape==(640,960,4) and mask[420,300,3]==255
ys,xs=np.where(mask[:,:,3]>0);assert xs.min()>=80 and xs.max()<=520 and ys.min()>=400 and ys.max()<=440
belt=character['live']['strokes'][0];assert belt['spec']==dict(kind='conveyor',colors=['#E53935','#1E88E5'],speed=3,mode='ooze',along=True,texture=None)
assert len(belt['points'])>20 and abs(belt['points'][0]['x']-100)<.01 and abs(belt['points'][-1]['x']-500)<.01
assert all(abs(p['y']-560)<.01 and 0<p['w']<=35 for p in belt['points'])
assert enriched['active']==character['id'] and enriched['drawingMode']=='raster'
events=json.loads((folder/'events.json').read_text(encoding='utf-8'))+json.loads((folder/'fresh/events.json').read_text(encoding='utf-8'));downloads=[e for e in events if e['action']=='download'];assert len(downloads)==6
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,status='Verified fixture; not an acceptance case result',source='Entirely real public UI creation and actual saved-file fresh-context reopen',basic_file='headless/MIX-final/MIX-basic.retropaint',enriched_file='headless/MIX-final/MIX-enriched.retropaint',layers=[dict(id=l['id'],name=l['name'],opacity=l['opacity'],raw_rgba_sha256=hashlib.sha256(decode(l['image']).tobytes()).hexdigest()) for l in enriched['layers']],white_paper_blue_backdrop_red_green_character_verified=True,editable_text_and_stamp_preserved=True,live_water_mask_bounds=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],live_conveyor_point_count=len(belt['points']),photo_exposure=.5,complete_fresh_project_reopen_exact=True,actual_downloads_verified=6,composition_note='Live export pixels are time-dependent. Later acceptance workflows must compare at controlled display time or explicitly measure static/live scopes; arbitrary-time PNG equality is not assumed.',setup_notes='Earlier fixture attempts are retained as failed setup: New layer is unavailable while the Layer options page is shown; Shape fill is inside More shapes & fill. Corrected producer uses the actual Back to layers and More shapes controls. Caption uses the centred Place default; an occluded attempted paper click did not set its anchor. MIX does not prescribe caption coordinates; this fixture certifies text content/editability, not the separate text-positioning case.')
(root/'fixtures/MIX-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
