"""Create the catalogue's labelled PATCH without depending on app rendering."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';out.mkdir(exist_ok=True)
patches=[{'name':'Red: opaque','xywh':[100,100,100,80],'rgba':[255,0,0,255]}, {'name':'Blue: opaque','xywh':[400,100,100,80],'rgba':[0,0,255,255]}, {'name':'Green: opaque','xywh':[100,300,100,80],'rgba':[0,255,0,255]}, {'name':'Red: 50% alpha','xywh':[400,300,100,80],'rgba':[255,0,0,128]}]
image=Image.new('RGBA',(960,640));draw=ImageDraw.Draw(image);font=ImageFont.load_default(size=14)
for patch in patches:
 x,y,w,h=patch['xywh'];draw.rectangle((x,y,x+w-1,y+h-1),fill=tuple(patch['rgba']));draw.text((x,y+h+8),patch['name'],font=font,fill=(0,0,0,255))
image.save(out/'patch-labelled.png');border=image.copy();ImageDraw.Draw(border).rectangle((0,0,959,639),outline=(0,0,0,255),width=1);border.save(out/'patch-labelled-border.png')
for colour in ['white','black']:
 backing=Image.new('RGBA',image.size,colour);backing.alpha_composite(image);backing.save(out/('patch-labelled-'+colour+'.png'))
files={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['patch-labelled.png','patch-labelled-border.png','patch-labelled-white.png','patch-labelled-black.png']}
(out/'patch-labelled-provenance.json').write_text(json.dumps({'size':[960,640],'mode':'RGBA','patches':patches,'labels':'Pillow default 14px font; x=patch x, y=patch bottom+8, outside each rectangle','sha256':files},indent=2)+'\n',encoding='utf-8');print(files)
