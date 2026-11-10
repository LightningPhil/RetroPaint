"""Independent mixed-document and screenshot oracles for ACCESS-013."""
import base64, hashlib, io, json, math
from pathlib import Path
from PIL import Image, ImageChops

root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(stage):
    name='mouse-audit-redraw-'+stage+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes()
    (out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def image(layer):return Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
before=doc('mix-before')
for stage in ['mix-cursor','preview-cancelled','live-undone','short-undone']:assert doc(stage)==before,stage
live=doc('live');assert live==doc('live-redone')
short=doc('short');assert short==doc('short-redone')==doc('short-reopened')
assert doc('fixed-before')==doc('fixed-cancelled')
assert before['active']==live['active']==short['active']==103 and len(short['layers'])==4
for initial,animated,marked in zip(before['layers'],live['layers'],short['layers']):
    if initial['id']!=103:assert initial==animated==marked
    else:
        for key in initial:
            if key!='live':assert initial[key]==animated[key],key
            if key!='image':assert initial[key]==marked[key],key
        stroke=animated['live']['strokes'];assert len(stroke)==1
        assert stroke[0]['spec']['kind']=='conveyor' and stroke[0]['spec']['colors']==['#E53935','#FFD166']
        assert max(abs(p['y']-486.4937387501233) for p in stroke[0]['points'])<1e-8
        assert abs(stroke[0]['points'][0]['x']-509.47574940988403)<1e-8
        assert abs(stroke[0]['points'][-1]['x']-696.9644538786459)<1e-8
        old,new=image(initial),image(marked)

events=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines()]
pointer=[r['event']['detail'] for r in events if r.get('event',{}).get('type')=='native pointer' and r['at'].startswith('2026-11-05T20:45:27.')]
down=next(e for e in pointer if e['phase']=='pointerdown');up=next(e for e in pointer if e['phase']=='pointerup')
assert down['buttons']==1 and up['buttons']==0 and abs(up['clientX']-down['clientX']-3/1.1)<.001
r=down['rect'];start=((down['clientX']-r['x'])/r['width']*960,(down['clientY']-r['y'])/r['height']*640)
end=((up['clientX']-r['x'])/r['width']*960,(up['clientY']-r['y'])/r['height']*640)
inside=outside=0
for y in range(640):
    for x in range(960):
        nearest=min(max(x+.5,start[0]),end[0]);distance=math.hypot(x+.5-nearest,y+.5-start[1])
        if distance<9:
            assert new.getpixel((x,y))==(26,26,26,255),(x,y,new.getpixel((x,y)));inside+=1
        elif distance>13:
            assert old.getpixel((x,y))==new.getpixel((x,y)),(x,y);outside+=1
visible=Image.open(out/'redraw-short-visible.png').convert('RGB')
# The viewport applies its paper texture over the canvas; exact source RGB is
# verified above. Display evidence checks the small dark stroke against blue
# neighbouring paper, avoiding the light cursor-outline ring.
for x,y in [(908,473),(910,475),(912,477)]:
    assert max(visible.getpixel((x,y)))<65,'Final short stroke missing from displayed canvas'
assert visible.getpixel((909,450))[2]>180,'Surrounding blue paper changed'
frames={}
for kind,box in [('preview',(680,240,870,410)),('fixed-preview',(680,240,870,410)),('live',(900,465,1055,486))]:
    a=Image.open(out/f'redraw-{kind}-t0.png').convert('RGB').crop(box)
    b=Image.open(out/f'redraw-{kind}-t1.png').convert('RGB').crop(box)
    changed=sum(any(pixel) for pixel in ImageChops.difference(a,b).get_flattened_data())
    if kind=='preview':assert changed==0,'Pre-fix frozen-preview reproduction changed'
    else:assert changed>100,(kind,changed)
    frames[kind]=changed
measurements={}
for e in json.loads((out/'redraw-evidence.json').read_bytes()):
    lines=[line for line in e.get('trace','').splitlines() if line.startswith('canvas measurement: {')]
    if lines:measurements[e['stage']]=json.loads(lines[-1].split(': ',1)[1])
assert measurements['static']['view']<=10 and measurements['static']['ui']<=3
assert measurements['cursor']['view']<=10 and measurements['cursor']['ui']>measurements['static']['ui']
assert measurements['live-polyline-preview']['view']>1000 and measurements['live-stroke']['view']>1000
assert measurements['fixed-live-polyline-preview']['ui']>100
report={'status':'Pass','whole_mixed_document_cancel_cursor_history_and_native_reopen_exact':True,'measurements_five_seconds':measurements,'displayed_preview_and_live_stroke_changed_pixels':frames,'native_short_drag_physical_pixels':3,'short_stroke_independent_solid_interior_pixels':inside,'short_stroke_unchanged_outside_pixels':outside,'sha256':hashes}
(out/'redraw-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
