"""Independent coordinate chart and mathematically declared input distortions."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';w,h=960,640;chart=Image.new('RGBA',(w,h));d=ImageDraw.Draw(chart);d.rectangle((16,16,943,623),fill=(240,240,240,255))
for x in range(80,881,80):d.line((x,32,x,607),fill=(50,50,50,255),width=3);d.text((x+5,38),str(x),fill=(20,20,20,255))
for y in range(80,561,80):d.line((32,y,927,y),fill=(70,70,70,255),width=3);d.text((38,y+5),str(y),fill=(20,20,20,255))
d.rectangle((240,160,720,480),outline=(120,30,180,255),width=5)
for box,color,text in [((24,24,71,71),(230,30,30,255),'TL'),((888,24,935,71),(20,180,40,255),'TR'),((24,568,71,615),(20,80,230,255),'BL'),((888,568,935,615),(240,190,20,255),'BR')]:d.rectangle(box,fill=color);d.text((box[0]+8,box[1]+18),text,fill=(0,0,0,255))
horizon=chart.copy();ImageDraw.Draw(horizon).line((100,250,800,390),fill=(0,180,200,255),width=5)
src=np.array(chart).astype(float);yy,xx=np.mgrid[:h,:w];cx=(w-1)/2;cy=(h-1)/2;unit=320;px=(xx-cx)/unit;py=(yy-cy)/unit
def sample(x,y):
    valid=(x>=0)&(x<=w-1)&(y>=0)&(y<=h-1);x=np.clip(x,0,w-1);y=np.clip(y,0,h-1);ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=x-ix;fy=y-iy;result=np.zeros((h,w,4));alpha=np.zeros((h,w));premul=np.zeros((h,w,3))
    for dx,dy,weight in [(0,0,(1-fx)*(1-fy)),(1,0,fx*(1-fy)),(0,1,(1-fx)*fy),(1,1,fx*fy)]:
        p=src[np.minimum(iy+dy,h-1),np.minimum(ix+dx,w-1)];a=p[:,:,3]*weight;alpha+=a;premul+=p[:,:,:3]*a[:,:,None]
    result[:,:,3]=alpha;np.divide(premul,alpha[:,:,None],out=result[:,:,:3],where=alpha[:,:,None]>0);result[~valid]=0;return Image.fromarray(np.rint(result).clip(0,255).astype('uint8'))
images={'geometry136-grid':chart,'geometry136-horizon':horizon};mappings={}
for axis in ['vertical','horizontal']:
    for sign in [-1,1]:
        k=sign*.2;den=1+k*(py if axis=='vertical' else px);name=f'geometry136-{axis}-'+('positive' if sign>0 else 'negative');images[name]=sample(px/den*unit+cx,py/den*unit+cy);mappings[name]=dict(mapping='Input samples ideal at p/(1+k*pAxis), normalized around pixel centre; independent inverse projective map.',k=k,intended_correction=sign*50)
for value in [70,-35]:
    a=value/350;radius=np.hypot(px,py);upper=4 if a>0 else (-1/(3*a))**.5;valid=radius<=upper*(1+a*upper*upper);lo=np.zeros_like(radius);hi=np.full_like(radius,upper)
    for _ in range(48):
        mid=(lo+hi)/2;less=mid*(1+a*mid*mid)<radius;lo=np.where(less,mid,lo);hi=np.where(less,hi,mid)
    r=(lo+hi)/2;scale=np.divide(r,radius,out=np.ones_like(r),where=radius>0);im=sample(px*scale*unit+cx,py*scale*unit+cy);arr=np.array(im);arr[~valid]=0;name='geometry136-radial-'+str(value);images[name]=Image.fromarray(arr);mappings[name]=dict(mapping='Input samples ideal at monotonic-branch inverse of r*(1+a*r^2);48stepbisection; noninvertibleinputpoints clear.',a=a,intended_correction=value)
# Known channel-separated monochrome edges; red stretched and blue contracted.
edge=Image.new('RGBA',(w,h));ed=ImageDraw.Draw(edge);ed.rectangle((16,16,943,623),fill=(240,240,240,255));ed.rectangle((100,96,179,543),fill=(20,20,20,255));ed.rectangle((780,96,859,543),fill=(20,20,20,255));original_src=src;src=np.array(edge).astype(float);fringe=np.array(edge);f=.005
for channel,scale in [(0,1+f),(2,1-f)]:fringe[:,:,channel]=np.array(sample((xx-cx)/scale+cx,(yy-cy)/scale+cy))[:,:,channel]
src=original_src;images['geometry136-fringe']=Image.fromarray(fringe);images['geometry136-fringe-ideal']=edge;mappings['geometry136-fringe']=dict(mapping='InputRed samples ideal at p/1.005;Blue at p/.995;Greenandalphaunchanged.',intended_correction=100,edge_x=[100,180,780,860])
files={}
for name,im in images.items():
    p=out/(name+'.png');im.save(p);files[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(size=[w,h],pixel_centre=[cx,cy],normalization_unit=unit,horizon=dict(start=[100,250],end=[800,390],slope=.2,expected_correction_degrees=-11.309932474020215),grid_x=list(range(80,881,80)),grid_y=list(range(80,561,80)),rectangle=[240,160,720,480],clear_border=16,mappings=mappings,files=files)
(out/'geometry136-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print('Prepared independently mapped GEOMETRY grid/horizon/perspective/radial/channel-offset charts')
