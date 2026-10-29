from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
from datetime import datetime,timezone
root=Path(__file__).resolve().parent
images={}
for name,rgba in [('nearly-black',(0,0,0,1)),('nearly-white',(255,255,255,1)),('clear-half',(0,0,0,0))]:
    image=Image.new('RGBA',(1024,256),(128,128,128,255));ImageDraw.Draw(image).rectangle((512,0,1023,255),fill=rgba);images[name]=image
images['empty']=Image.new('RGBA',(1024,256),(0,0,0,0))
images['rgb-flat']=Image.new('RGBA',(1024,256),(64,128,192,255))
rows=[]
for name,image in images.items():
    path=root/'fixtures'/('HIST-'+name+'.png')
    assert not path.exists(),'Do not overwrite retained fixtures'
    image.save(path);rows.append(dict(name=name,file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),size=image.size))
(root/'fixtures/HIST-manifest.json').write_text(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),generator=Path(__file__).name,fixtures=rows,nearly_transparent_oracle='Equal areas of opaque neutral and alpha 1/255 black/white. Opacity-weighted clipping is 1/256 = 0.390625%, which rounds to 0%; it must not dominate the histogram.'),indent=2)+'\n',encoding='utf-8')
print('Created five independent RGBA histogram fixtures.')
