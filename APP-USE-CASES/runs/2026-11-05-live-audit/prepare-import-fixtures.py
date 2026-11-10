"""Independent Pillow encoding for all IMPORT formats and EXIF orientation."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import hashlib,json,numpy as np
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures/import-formats';folder.mkdir(exist_ok=True);im=Image.new('RGBA',(320,240));d=ImageDraw.Draw(im)
for label,box,color in [('TL',(6,6,29,29),'red'),('TR',(280,6,303,29),'green'),('BL',(6,200,29,223),'blue'),('BR',(280,200,303,223),'yellow')]:d.rectangle(box,fill=color);d.text((box[0]+2,box[1]+5),label,fill='black')
d.rectangle((60,60,99,99),fill=(255,0,0,255));d.rectangle((160,60,199,99),fill=(0,255,0,128));white=Image.new('RGBA',im.size,'white');white.alpha_composite(im);rgb=white.convert('RGB');files=[]
for fmt,ext in [('PNG','png'),('JPEG','jpg'),('WEBP','webp'),('BMP','bmp'),('GIF','gif'),('TIFF','tif')]:
 path=folder/('source.'+ext);source=rgb if fmt in ('JPEG','BMP') else im.copy();options={'quality':95,'subsampling':0} if fmt=='JPEG' else {'lossless':True} if fmt=='WEBP' else {'compression':'raw'} if fmt=='TIFF' else {}
 if fmt=='GIF':
  a=np.array(source);a[:,:,3]=np.where(a[:,:,3]<128,0,255);source=Image.fromarray(a)
 source.save(path,format=fmt,**options);files.append({'file':str(path),'format':fmt,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':list(Image.open(path).size)})
path=folder/'orientation6.jpg';exif=Image.Exif();exif[274]=6;rgb.save(path,'JPEG',quality=95,subsampling=0,exif=exif);files.append({'file':str(path),'format':'JPEG','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'EXIF_orientation':6,'size':[240,320]});(folder/'corrupt.png').write_bytes(b'\x89PNG\r\n\x1a\ncorrupt-disposable-audit-data')
plan={'encoder':'Pillow '+Image.__version__,'files':files,'corrupt':str(folder/'corrupt.png'),'source_recipe':'320x240clear; labelled24x24corner blocks at6,6 /280,6 /6,200 /280,200. Red40square60,60 andgreen alpha128square160,60. JPEG/BMP white matte; GIF binary alpha; WebP lossless; TIFF rawRGBA.','decoder_oracle':'Independent Pillow decode; EXIF6 transposed before comparing. Exact RGBA for PNG/WebP/BMP/GIF/TIFF. JPEG decoder comparison: meanRGBerror<=1,max<=5, dimensions/orientation exact. Mark line around centre120row (EXIFportrait160row) must align with expected pixels; outside delivered gesture footprint exact, each Undo/Redo exact.','recorded_before_import_execution':True};(folder/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8');print(json.dumps({'files':len(files),'encoder':plan['encoder']},indent=2))
