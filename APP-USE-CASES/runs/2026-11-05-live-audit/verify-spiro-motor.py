"""Verify actual live motor downloads without importing application code."""
import base64, hashlib, io, json, math
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
import numpy as np

root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads'
hashes={}
def actual(stem,ext='retropaint'):
 name='mouse-audit-spiro-motor35-'+stem+'.'+ext
 data=(downloads/name).read_bytes();(out/name).write_bytes(data)
 hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(actual(stem))
before=doc('before');stop=doc('stop');reset=doc('reset');custom=doc('custom-reset');auto=doc('auto');manual=doc('manual')
assert doc('stop-undone')==before and doc('stop-redone')==stop
assert doc('reset-undone')==stop and doc('reset-redone')==reset
assert doc('custom-before')==reset and doc('custom-reset-undone')==reset and doc('custom-reset-redone')==custom
assert doc('auto-undone')==custom and doc('auto-redone')==auto
assert doc('reopened')==manual
documents=[before,stop,reset,custom,auto,manual]
assert [len(d['layers'][0].get('objects',[])) for d in documents]==[0,1,2,3,4,5]
curves=[]
for index,(previous,current) in enumerate(zip(documents,documents[1:])):
 objects=current['layers'][0]['objects'];assert objects[:-1]==previous['layers'][0].get('objects',[])
 expected=json.loads(json.dumps(previous));expected['layers'][0]['objects']=objects;assert expected==current
 obj=objects[-1];assert obj['kind']=='path' and obj['name']=='Spiro' and obj['lineWidth']==3 and obj['stroke']['color']=='#1E88E5' and obj['fill'] is None
 points=np.array([[p['x']+obj['matrix'][4],p['y']+obj['matrix'][5]] for p in obj['paths'][0]['points']])
 R=640/3;outer,inner=(180,53) if index in [2,4] else (96,36)
 r=R*inner/outer;A=R-r;k=-A/r;holes=8 if inner==53 else 7
 initial=[np.array([480+A+r*(.18+.66*h/(holes-1))*math.cos(2.2*h),320+r*(.18+.66*h/(holes-1))*math.sin(2.2*h)]) for h in range(holes)]
 hole=min(range(holes),key=lambda h:np.linalg.norm(points[0]-initial[h]));assert np.linalg.norm(points[0]-initial[hole])<1e-6
 d=r*(.18+.66*hole/(holes-1));phi=2.2*hole
 theta=np.unwrap(np.arctan2(points[:,1]-320,points[:,0]-480))
 def position(t):return np.column_stack((480+A*np.cos(t)+d*np.cos(k*t+phi),320+A*np.sin(t)+d*np.sin(k*t+phi)))
 for _ in range(12):
  error=position(theta)-points
  velocity=np.column_stack((-A*np.sin(theta)-d*k*np.sin(k*theta+phi),A*np.cos(theta)+d*k*np.cos(k*theta+phi)))
  theta-=np.sum(error*velocity,axis=1)/np.sum(velocity*velocity,axis=1)
 error=np.linalg.norm(position(theta)-points,axis=1)
 assert error.max()<1e-6 and abs(theta[0])<1e-7,(index,float(error.max()),float(theta[0]),points[0].tolist())
 if index==3:assert abs(theta[-1]-6*math.pi)<1e-6
 else:assert 0<theta[-1]<2*math.pi*(inner/math.gcd(outer,inner))
 curves.append({'action':['Stop','Reset','custom Reset','automatic finish','Manual switch'][index],'offered_hole_zero_based':hole,'points':len(points),'theta_end':float(theta[-1]),'maximum_curve_error_source_px':float(error.max())})
png=Image.open(io.BytesIO(actual('manual','png'))).convert('RGBA')
assert png.size==(960,640) and png.tobytes()==Image.open(io.BytesIO(actual('reopened','png'))).convert('RGBA').tobytes()
source=Image.open(io.BytesIO(base64.b64decode(manual['layers'][0]['image'].split(',',1)[1]))).convert('RGBA');assert source.getextrema()==((255,255),)*4
allowed=Image.new('L',png.size);draw=ImageDraw.Draw(allowed)
for obj in manual['layers'][0]['objects']:
 pts=[(p['x']+obj['matrix'][4],p['y']+obj['matrix'][5]) for p in obj['paths'][0]['points']]
 draw.line(pts,fill=255,width=7)
 for x,y in [pts[0],pts[-1]]:draw.ellipse((x-3.5,y-3.5,x+3.5,y+3.5),fill=255)
changed=ImageChops.difference(png.convert('RGB'),Image.new('RGB',png.size,'white')).convert('L').point(lambda v:255 if v else 0)
assert changed.getbbox() and ImageChops.subtract(changed,allowed).getbbox() is None
for name in ['stop','reset','custom-reset','auto']:assert Image.open(io.BytesIO(actual(name,'png'))).getbbox()
report={'status':'Pass','curves':curves,'whole_document_undo_redo_exact':True,'native_project_and_png_reopen_exact':True,'original_raster_untouched':True,'capture_loss_live':'Unproved: native omnibox click did not interrupt the browser-held pointer; synthetic regression only.','sha256':hashes}
(out/'spiro-motor35-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
