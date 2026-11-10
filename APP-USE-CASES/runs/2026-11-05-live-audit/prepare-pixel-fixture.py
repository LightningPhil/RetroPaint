"""Independently encode the prescribed 32x32 PIXEL fixture."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';im=Image.new('RGB',(32,32),'white');d=ImageDraw.Draw(im)
for i in range(2,15):im.putpixel((i,i),(0,0,0));im.putpixel((i+1,i),(0,0,0))
im.putpixel((15,15),(0,0,0));d.line((22,2,22,21),fill='red',width=1)
for y in range(22,26):
 for x in range(2,6):im.putpixel((x,y),(0,0,0) if (x+y)%2==0 else (0,0,255))
d.rectangle((25,25,29,29),fill='blue');path=out/'pixel-32.png';im.save(path);manifest={'size':[32,32],'mode':'RGB','recipe':'Opaque white32x32; one-pixel black staircase from2,2 via alternating horizontal/vertical steps to15,15; red vertical one-pixel line22,2..22,21; four-by-four black/blue checker at2,22; blue5x5block25,25..29,29. Palette exactly black,white,red,blue.','sha256':hashlib.sha256(path.read_bytes()).hexdigest()};(out/'pixel-32-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(manifest['sha256'])
