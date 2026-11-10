"""Preserved1024x768 DETAIL clean/noisy pair, seeded LCG12345 and regions."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';a=np.zeros((768,1024,4),dtype=np.uint8)
def grey(box,values):
    x0,y0,x1,y1=box;a[y0:y1,x0:x1,:3]=np.asarray(values,dtype=np.uint8)[...,None];a[y0:y1,x0:x1,3]=255
grey((32,32,480,224),np.broadcast_to(np.where(np.arange(448)<224,32,224),(192,448)))
grey((544,32,992,120),np.broadcast_to(np.where(np.arange(448)%2,160,96),(88,448)))
x=np.arange(448);t=np.clip((x-184)/80,0,1);grey((544,136,992,224),np.broadcast_to(np.rint(32+192*t*t*(3-2*t)),(88,448)))
grey((32,256,480,448),np.full((192,448),128));grey((544,256,992,448),np.full((192,448),128))
grey((32,480,480,640),np.broadcast_to(np.rint(128+24*np.sin(2*np.pi*x/128)),(160,448)))
grey((544,480,992,640),np.broadcast_to(np.rint(128+24*np.sin(2*np.pi*x/8)),(160,448)))
a[672:736,32:256]=[200,40,20,128];a[672:736,256:480]=[20,80,220,128]
clean=a.copy();seed=12345
def noise():
    global seed
    seed=(1664525*seed+1013904223)&0xffffffff;return ((seed>>24)%41)-20
for y in range(256,448):
    for x in range(32,480):a[y,x,:3]=128+noise()
for y in range(256,448):
    for x in range(544,992):
        r,b=noise(),noise();g=round(-(.2126*r+.0722*b)/.7152);a[y,x,:3]=[128+r,128+g,128+b]
files={}
for name,data in [('detail121-clean',clean),('detail121-noisy',a)]:
    p=out/(name+'.png');Image.fromarray(data).save(p);files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
hazy=a.copy();visible=hazy[:,:,3]>0;hazy[:,:,:3][visible]=np.rint(64+hazy[:,:,:3][visible].astype(float)*.5).astype('uint8');p=out/'detail121-hazy.png';Image.fromarray(hazy).save(p);files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(size=[1024,768],PRNG='LCG32 seed12345; state=(1664525*state+1013904223)mod2^32; delta=((state>>24)%41)-20; row-major luminance then chroma',luminance_noise_region=[48,272,464,432],chroma_noise_region=[560,272,976,432],sharp_edge_x=256,sharp_edge_region=[32,32,480,224],fine_alternating_region=[544,32,992,120],soft_edge_region=[544,136,992,224],broad_wave_region=[32,480,480,640],fine_wave_region=[544,480,992,640],transparent_coloured_edge=[32,672,480,736],hazy_mapping='Visible RGB=round(64+0.5*noisyRGB);alphaunchanged',files=files)
(out/'detail121-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared deterministic DETAIL clean/noisy/hazy, sharp/fine/broad/alpha features')
