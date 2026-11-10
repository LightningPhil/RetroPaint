"""Deterministic clipping-coverage and auto-tone failure inputs."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';files={}
coverage=np.zeros((256,1024,4),dtype=np.uint8);coverage[:,:,3]=1;coverage[:,512:,:3]=255;coverage[64:192,256:768]=[128,128,128,255]
images={'tonal-coverage':Image.fromarray(coverage),'tonal-constant':Image.new('RGBA',(1024,256),(128,128,128,255)),'tonal-clear':Image.new('RGBA',(1024,256),(0,0,0,0))}
source=root/'test-results/audit-2026-11-05/mouse/photo-natural-original.jpg';im=np.array(Image.open(source).convert('RGB'))/255
linear=np.where(im<=.04045,im/12.92,((im+.055)/1.055)**2.4)*.25
images['photo-underexposed']=Image.fromarray(np.rint(255*np.where(linear<=.0031308,12.92*linear,1.055*linear**(1/2.4)-.055)).astype(np.uint8))
for name,image in images.items():
    path=out/(name+'.png');image.save(path);files[path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'dimensions':image.size}
report=dict(files=files,coverage='1024x256: alpha1black left, alpha1white right; opaque128rectangle x256..767,y64..191. Visible coverage predicts ~0.58percent clipping each end, rounded1percent; faint padding must not count as75percent opaque clipping.',underexposed='Public-domain retained natural source, published sRGB decode, linear×0.25, inverse transfer, rounded8bit; no app renderer',natural_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
(out/'tonal-edge-provenance.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared clipping coverage, constant, clear and natural underexposed fixtures')
