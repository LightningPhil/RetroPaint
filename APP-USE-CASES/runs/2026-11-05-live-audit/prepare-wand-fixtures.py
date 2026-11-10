"""Prepare FILL variants after documenting the observed comparison metric."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures/wand';out.mkdir(exist_ok=True)
base=Image.new('RGBA',(320,240),'white');d=ImageDraw.Draw(base);d.rectangle((20,20,140,140),fill='black');d.rectangle((21,21,139,139),fill='#e8e8e8');d.rectangle((220,40,259,79),fill='#e8e8e8')
variants={'base':base}
gap=base.copy();gap.putpixel((80,20),(255,255,255,255));variants['gap']=gap
variation=base.copy()
for x in range(21,140):
 level=232+(x-21)%17-8
 for y in range(21,140):variation.putpixel((x,y),(level,level,level,255))
variants['variation']=variation
aa=base.copy();d=ImageDraw.Draw(aa);d.rectangle((21,21,139,139),fill='#b8b8b8');d.rectangle((22,22,138,138),fill='#e8e8e8');variants['antialiased']=aa
alpha=base.copy();d=ImageDraw.Draw(alpha);d.rectangle((59,59,100,100),fill=(232,232,232,128));d.rectangle((60,60,99,99),fill=(0,0,0,0));variants['transparent']=alpha
manifest={'metric_documented_before_fixture_tests':'src/fill.ts floodMask: four-connected membership relative to original seed, sum of absolute R,G,B,A differences <= tolerance. Two fully transparent pixels match regardless of hidden RGB. The native oracle implements a separate deque BFS.','recipe':'320x240 white RGBA; inclusive black one-pixel border20,20..140,140; grey232 interior21..139; second grey island220,40 size40x40. Gap80,20 white. Variation column value232+((x-21)%17)-8. AA ring184 at21..139 surrounding232 core22..138. Transparent variant grey232 alpha128 ring59..100 surrounding clear0 RGBA centre60..99.','sha256':{}}
for name,img in variants.items():
 path=out/(name+'.png');img.save(path);manifest['sha256'][path.name]=hashlib.sha256(path.read_bytes()).hexdigest()
(out/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps(manifest,indent=2))
