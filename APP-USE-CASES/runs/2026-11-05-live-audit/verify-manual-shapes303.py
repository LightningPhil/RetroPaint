from pathlib import Path
from PIL import Image
import json
root=Path(__file__).resolve().parents[3]
mouse=root/'test-results/audit-2026-11-05/mouse'
def image(name):return Image.open(mouse/name).convert('RGBA')
def bbox(img,x0=0,x1=None):
 x1=x1 or img.width;pix=img.load();p=[(x,y) for y in range(img.height) for x in range(x0,x1) if pix[x,y]!=(255,255,255,255)];assert p;return (min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p))
def square(b,tolerance=1):
 x0,y0,x1,y1=b;assert abs((x1-x0)-(y1-y0))<=tolerance,b
line=image('manual-shift-line303.png');after=image('manual-shift-line303-after-undo.png');assert line.size==after.size and line.tobytes()==after.tobytes();square(bbox(line),0)
for name in ['manual-shift-square303.png','manual-shift-square-reverse303.png']:square(bbox(image(name)))
for name in ['manual-shift-circles303.png','manual-shift-ovals303.png']:
 im=image(name);square(bbox(im,0,500));square(bbox(im,500,960))
events=[]
for s in (mouse/'manual-shape-events303.jsonl').open(encoding='utf8'):
 e=json.loads(s).get('event',{});d=e.get('detail',{})
 if e.get('type')=='native pointer' and '2026-11-08T12:07:00'<=e.get('at','')<'2026-11-08T12:16:00' and d.get('target')=='view':events.append((e['at'],d))
for start,end in [('12:08:00','12:08:10'),('12:09:45','12:09:55'),('12:10:35','12:10:45'),('12:11:40','12:11:50'),('12:13:00','12:13:10'),('12:14:55','12:15:25')]:
 subset=[d for t,d in events if start<=t[11:19]<=end and d['phase'] in ['pointerdown','pointerup'] and d['shiftKey']];assert len(subset)>=2,(start,subset)
print('PASS: 45-degree line, exact undo, both square directions, both circle/oval directions, and physical Shift events')
