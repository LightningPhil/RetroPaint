"""Independent accepted numeric bounds, constrained drawings and round trip."""
import base64,hashlib,io,itertools,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageDraw,ImageFilter

root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(name,ext='retropaint'):
 filename='mouse-audit-spiro-'+name+'.'+ext;data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(actual(name))
before=doc('teeth35-before');assert before==doc('teeth35-after-before-fix')==doc('teeth36-after')==doc('limits36-before')
rows=json.loads((out/'spiro-teeth36-fixed.json').read_bytes());assert len(rows)==26
for row in rows[:-1]:
 outer=row['controls']['outerTeeth'];inner=row['controls']['innerTeeth']
 assert outer['valid'] and inner['valid'] and float(inner['max'])==float(outer['value'])-8
 requested=float(row['requested'] or 0)
 field=row['field'];expected=max(40,min(180,math.floor(requested+.5))) if field=='outerTeeth' else max(10,min(float(outer['value'])-8,math.floor(requested+.5)))
 assert float(row['controls'][field]['value'])==expected
assert rows[-1]['incompatibleOrange']=={'max':'32','valid':True,'value':'32'}
low=doc('limits36-low');high=doc('limits36-high');assert doc('limits36-low-undone')==before and doc('limits36-low-redone')==low and doc('limits36-high-undone')==low and doc('limits36-high-redone')==high
assert doc('limits36-reopened')==high
curve_reports=[];analytic=[]
for previous,current,outer,inner,holes in [(before,low,40,32,5),(low,high,180,172,10)]:
 objects=current['layers'][0]['objects'];assert objects[:-1]==previous['layers'][0]['objects']
 expected=json.loads(json.dumps(previous));expected['layers'][0]['objects']=objects;assert expected==current
 obj=objects[-1];assert obj['kind']=='path' and obj['name']=='Spiro' and obj['lineWidth']==3 and obj['stroke']['color']=='#1E88E5' and obj['fill'] is None
 points=np.array([[p['x']+obj['matrix'][4],p['y']+obj['matrix'][5]] for p in obj['paths'][0]['points']])
 R=200;r=R*inner/outer;A=R-r;k=-A/r;d=r*(.18+.66*2/(holes-1));phi=4.4;end=2*math.pi*inner/math.gcd(outer,inner)
 def curve(t):return np.column_stack((480+A*np.cos(t)+d*np.cos(k*t+phi),320+A*np.sin(t)+d*np.sin(k*t+phi)))
 assert np.linalg.norm(points[0]-curve(np.array([0]))[0])<1e-6 and np.linalg.norm(points[-1]-curve(np.array([end]))[0])<1e-6
 # The largest curve is deliberately thinned during drawing, so point index
 # is not uniform in angle. A coarse independent spatial index seeds exact
 # analytic projections; every stored point must still fit the configured curve.
 grid_t=np.linspace(0,end,math.ceil(end/.005)+1);grid=curve(grid_t);bins={}
 for i,key in enumerate(map(tuple,np.floor(grid).astype(int))):bins.setdefault(key,[]).append(i)
 targets={}
 for i,key in enumerate(map(tuple,np.floor(points).astype(int))):targets.setdefault(key,[]).append(i)
 theta=np.empty(len(points))
 for (x,y),ids in targets.items():
  candidates=[i for dx,dy in itertools.product([-1,0,1],repeat=2) for i in bins.get((x+dx,y+dy),[])];assert candidates
  for start in range(0,len(ids),256):
   ix=ids[start:start+256];distance=np.sum((points[ix,None,:]-grid[candidates][None,:,:])**2,axis=2)
   theta[ix]=grid_t[np.array(candidates)[distance.argmin(axis=1)]]
 for _ in range(16):
  error=curve(theta)-points;velocity=np.column_stack((-A*np.sin(theta)-d*k*np.sin(k*theta+phi),A*np.cos(theta)+d*k*np.cos(k*theta+phi)))
  theta-=np.sum(error*velocity,axis=1)/np.maximum(1e-12,np.sum(velocity*velocity,axis=1))
 error=np.linalg.norm(curve(theta)-points,axis=1)
 # At a self-intersection the nearest coarse sample can belong to the other
 # branch. Project all nearby analytic branches for those unresolved points.
 for ix in np.flatnonzero(error>=1e-5):
  x,y=np.floor(points[ix]).astype(int);candidates=[i for dx,dy in itertools.product([-1,0,1],repeat=2) for i in bins.get((x+dx,y+dy),[])]
  t=grid_t[candidates].copy()
  for _ in range(32):
   residual=curve(t)-points[ix];velocity=np.column_stack((-A*np.sin(t)-d*k*np.sin(k*t+phi),A*np.cos(t)+d*k*np.cos(k*t+phi)))
   t-=np.clip(np.sum(residual*velocity,axis=1)/np.maximum(1e-12,np.sum(velocity*velocity,axis=1)),-.02,.02)
  error[ix]=np.linalg.norm(curve(t)-points[ix],axis=1).min()
 assert error.max()<1e-5,(outer,inner,float(error.max()),int((error>=1e-5).sum()))
 analytic.append(curve(np.linspace(0,end,math.ceil(end*max(A,r*abs(k))*25)+1)))
 curve_reports.append({'outer':outer,'inner':inner,'offered_hole_zero_based':2,'stored_points_all_verified':len(points),'maximum_curve_error_source_px':float(error.max())})
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
png=image(actual('limits36-high','png'));assert png.tobytes()==image(actual('limits36-reopened','png')).tobytes()
source=image(base64.b64decode(high['layers'][0]['image'].split(',',1)[1]));assert source.getextrema()==((255,255),)*4
original=image(actual('pair35-orange-120-reopened','png'));allowed=ImageChops.difference(original.convert('RGB'),Image.new('RGB',original.size,'white')).convert('L').point(lambda v:255 if v else 0)
draw=ImageDraw.Draw(allowed)
for samples in analytic:
 pts=[tuple(p) for p in samples];draw.line(pts,fill=255,width=7)
 for x,y in pts[::5]+[pts[-1]]:draw.ellipse((x-3.5,y-3.5,x+3.5,y+3.5),fill=255)
changed=ImageChops.difference(png.convert('RGB'),Image.new('RGB',png.size,'white')).convert('L').point(lambda v:255 if v else 0)
assert ImageChops.subtract(changed,allowed).getbbox() is None
coverage=np.array(changed.filter(ImageFilter.MaxFilter(9)))
for samples in analytic:
 coords=samples.astype(int);assert np.all(coverage[coords[:,1],coords[:,0]])
report={'status':'Pass','native_numeric_cases':26,'all_accepted_fields_valid':True,'whole_artwork_unchanged_by_settings':True,'curves':curve_reports,'whole_undo_redo_and_native_project_png_reopen_exact':True,'sha256':hashes}
(out/'spiro-limits36-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
