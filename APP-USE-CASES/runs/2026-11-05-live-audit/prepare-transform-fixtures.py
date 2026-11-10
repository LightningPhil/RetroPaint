"""Separate PATCH/MIX copies with asymmetric corner labels for EDIT-019."""
from pathlib import Path
from PIL import Image,ImageDraw
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures';downloads=Path.home()/'Downloads';provenance={}
def corners(im,index):
 d=ImageDraw.Draw(im);w,h=im.size;k=64+index*40
 for label,x,y,color in [('TL',8,8,(k,32,16,255)),('TR',w-96,8,(16,k,32,255)),('BL',8,h-48,(32,16,k,255)),('BR',w-96,h-48,(k,k,16,255))]:
  d.rectangle((x,y,x+23,y+23),fill=color);d.text((x+27,y+6),f'{label} L{index+1}',fill=(0,0,0,255))
 return im
source=folder/'patch-labelled.png';im=corners(Image.open(source).convert('RGBA'),0);path=folder/'patch-transform-corners.png';im.save(path);provenance['PATCH']={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
source=downloads/'mouse-audit-edit-crop39-before.retropaint';d=json.loads(source.read_bytes())
for i,layer in enumerate(d['layers']):
 im=Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))).convert('RGBA');corners(im,i);b=io.BytesIO();im.save(b,format='PNG');layer['image']='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
path=folder/'mix-transform-corners.retropaint';path.write_text(json.dumps(d,separators=(',',':'),ensure_ascii=False),encoding='utf-8');provenance['MIX']={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
provenance['recipe']='Each 960x640 layer gets24x24corner blocks at8,8 /864,8 /8,592 /864,592. Corner RGB TL(k,32,16),TR(16,k,32),BL(32,16,k),BR(k,k,16), k=64+40*layerIndex. Black TL/TR/BL/BR L1..L4 labels atblockx+27,y+6. Original four PATCH rectangles and all MIX object definitions retained.'
(folder/'transform-corners-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8');print(json.dumps(provenance,indent=2))
