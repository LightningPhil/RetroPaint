"""Wide source to expose preview/source letterbox coordinate mismatches."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';image=Image.new('RGBA',(960,240));draw=ImageDraw.Draw(image)
colours=[('cast-grey',(154,123,109)),('red',(255,0,0)),('blue',(0,0,255)),('green',(0,255,0)),('grey',(128,128,128)),('white',(255,255,255)),('black',(0,0,0))]
patches=[]
for i,(name,rgb) in enumerate(colours):draw.rectangle((i*120,0,i*120+119,239),fill=(*rgb,255));patches.append(dict(name=name,rgb=rgb,centre=[i*120+60,120]))
path=out/'colour109-wide.png';image.save(path);(out/'colour109-wide.json').write_text(json.dumps(dict(dimensions=[960,240],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),patches=patches,clear='Final120columns',oracle='Known opaque source strips, cast-grey centre60,120. The displayed bitmap is400x180 and CSS object-fit:contain; account for both nested letterboxes when choosing visible source coordinates.'),indent=2)+'\n');print('Prepared wide cast-grey and saturated neighbours')
