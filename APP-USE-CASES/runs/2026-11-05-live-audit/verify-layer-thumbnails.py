"""Verify native screenshots, saved marks and API repaint observations."""
from pathlib import Path
import base64,hashlib,io,json,re
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name=f'mouse-audit-layer92-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def rgba(url):return np.array(Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGBA'))
stroke=doc('stroke');live=doc('live');hidden=doc('hidden-paint')
for i in [0,1,3]:assert stroke['layers'][i]==live['layers'][i]==hidden['layers'][i]
assert stroke['layers'][2]['image']==live['layers'][2]['image']
assert len(live['layers'][2]['live']['strokes'])==1 and live['layers'][2]['live']==hidden['layers'][2]['live']
a=rgba(live['layers'][2]['image']);b=rgba(hidden['layers'][2]['image']);changed=np.any(a!=b,axis=2);allowed=np.zeros(changed.shape,dtype=bool);allowed[249:352,249:652]=True;assert changed.any() and not np.any(changed&~allowed)
assert tuple(b[300,450])==(30,136,229,255)
def shot(n):return np.array(Image.open(out/f'layer92-{n}.jpg')).astype(int)
static=shot('stroke-settled');thumb=static[380:385,1545:1560]
# The 22px source line becomes ~1px in the 52px JPEG thumbnail: downsampling
# and chroma subsampling reduce its green channel separation to 31/255.
# Use location, colour direction and exact saved source pixels together.
green=(thumb[:,:,1]>thumb[:,:,0]+20)&(thumb[:,:,1]>thumb[:,:,2]+15);assert green.any()
original=shot('before')[380:385,1545:1560];assert np.mean(thumb[:,:,0]-original[:,:,0]) < -10
assert tuple(rgba(stroke['layers'][2]['image'])[450,400])==(67,160,71,255)
ta=shot('live-a')[355:395,1530:1582];tb=shot('live-b')[355:395,1530:1582];temporal=int(np.count_nonzero(np.max(abs(ta-tb),axis=2)>20));assert temporal>=20
thumb=shot('reopened-palette-settled')[355:395,1530:1582];blue=(thumb[:,:,2]>thumb[:,:,0]+70)&(thumb[:,:,2]>thumb[:,:,1]+25);assert blue.sum()>=35
measure=lambda name:[json.loads(s) for s in re.findall(r'canvas measurement: (\{[^\n]+\})',(out/name).read_text())][-1]
static_calls=measure('layer92-static-settled-log.txt');live_calls=measure('layer92-live-log.txt');assert static_calls['view']<=5 and live_calls['view']>static_calls['view']*5
report=dict(status='Pass',correct_row_committed_green_mark=True,animated_thumbnail_changed_pixels=temporal,closed_palette_next_blue_mark_visible=True,only_active_layer_and_declared_blue_gesture_region_changes=True,live_definition_retained=True,static_five_second_canvas_API_calls=static_calls,live_five_second_canvas_API_calls=live_calls,scope='Counters observe standard Canvas APIs, not application state. Static measurement includes one input-triggered repaint. Initial frozen-clock screenshot preceded resumed thumbnail refresh; settled native-time screenshot used.',sha256=hashes)
(out/'layer92-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native correct row, animated thumbnail, bounded static repaint and closed-palette update')
