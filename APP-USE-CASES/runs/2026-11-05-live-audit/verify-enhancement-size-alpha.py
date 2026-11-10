"""Decode native neural exports; independently check dimensions and bilinear alpha."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
from geometry_oracle import project_source
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};metrics={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return out/name
base=json.loads(retain('mouse-audit-enhance148-baseline.retropaint').read_text());after=json.loads(retain('mouse-audit-enhance148-after.retropaint').read_text());assert base==after
source=project_source(base);h,w,_=source.shape;assert (w,h)==(160,120)
for scale in [2,4]:
    actual=np.array(Image.open(retain(f'mouse-audit-enhance148-baseline-{scale}x-enhanced.png')).convert('RGBA')).astype(int);assert actual.shape==(h*scale,w*scale,4)
    yy,xx=np.mgrid[:h*scale,:w*scale];x=(xx+.5)/scale-.5;y=(yy+.5)/scale-.5;ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=x-ix;fy=y-iy;alpha=np.zeros(x.shape)
    for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:alpha+=source[np.clip(iy+dy,0,h-1),np.clip(ix+dx,0,w-1),3]*weight
    assert np.array_equal(actual[:,:,3],np.rint(alpha));assert np.all(actual[alpha==0]==0)
    for edge in [actual[:16*scale],actual[-16*scale:],actual[:,:20*scale],actual[:,-20*scale:]]:assert np.any(edge[:,:,3]==0)
    # Neural detail must differ from a mere enlarged source.
    enlarged=np.array(Image.fromarray(source.astype('uint8')).resize((w*scale,h*scale),Image.Resampling.BICUBIC)).astype(int);opaque=actual[:,:,3]==255;changed=int(np.count_nonzero(np.any(abs(actual[:,:,:3]-enlarged[:,:,:3])>4,axis=2)&opaque));assert changed>100
    metrics[str(scale)]=dict(dimensions=[w*scale,h*scale],exact_alpha=True,clear_RGBA_zero=True,opaque_pixels_different_from_bicubic=changed)
# The opaque twin has identical neural RGB input after clear-padding colour extension.
twin=source.copy();twin[twin[:,:,3]==0,:3]=source[16,20,:3];twin[:,:,3]=255
Image.fromarray(twin.astype('uint8')).save(root/'test-results/audit-2026-11-05/fixtures/enhance148-opaque-twin.png')
report=dict(status='Pass',original_project_exact=True,metrics=metrics,hashes=hashes,remaining='Opaque twin comparison for independent matte-contamination proof; multilayer whole-image and seam fixture remain separate.')
(out/'enhance148-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
