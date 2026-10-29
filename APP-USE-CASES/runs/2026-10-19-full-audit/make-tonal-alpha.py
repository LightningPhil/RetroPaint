from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import json,hashlib
root=Path(__file__).resolve().parent
image=Image.new('RGBA',(1024,256),(0,0,0,0))
draw=ImageDraw.Draw(image)
for value in range(256):draw.rectangle((value*4,16,value*4+3,143),fill=(value,value,value,255))
patches=[]
for n,value in enumerate([32,64,128,192,224]):
    box=(32+n*192,160,215+n*192,223)
    draw.rectangle(box,fill=(value,value,value,255));patches.append(dict(value=value,box=box,centre=[(box[0]+box[2])//2,192]))
path=root/'fixtures/TONAL-alpha.png'
assert not path.exists(),'Do not overwrite retained fixture bytes'
image.save(path)
report=dict(at=datetime.now(timezone.utc).isoformat(),generator=Path(__file__).name,decoder='Pillow '+Image.__version__,file=path.name,size=image.size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),ramp='Four columns per neutral value 0..255, rows 16..143 inclusive',patches=patches,transparent_padding='Rows 0..15 and 224..255, plus non-patch portions below row 143; RGBA zero')
(root/'fixtures/TONAL-alpha-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
