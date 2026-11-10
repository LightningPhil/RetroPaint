"""Independent geometry, support, history and coverage for real UI Spiro pairs."""
import base64,hashlib,io,itertools,json,math,sys
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageDraw,ImageFilter

root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads'
evidence=json.loads((out/'spiro-pair35-evidence.json').read_bytes());cases=evidence['cases'];hashes={};results=[]
if len(sys.argv)>1:cases=[c for c in cases if c['gear'] in sys.argv[1:]]
else:assert len(cases)==30
gear_values={'pink':(24,5),'purple':(30,6),'red':(36,7),'yellow':(42,8),'green':(48,8),'orange':(54,10)}
pointer=[]
for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines():
 if 'native pointer' in line:
  row=json.loads(line)['event'];pointer.append((datetime.fromisoformat(row['at'].replace('Z','+00:00')).timestamp()*1000,row['detail']))
def actual(stem,ext='retropaint'):
 name=stem+'.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(actual(stem))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
for case in cases:
 prefix=case['prefix'];before=doc(prefix+'-before');after=doc(prefix)
 assert doc(prefix+'-undone')==before and doc(prefix+'-redone')==after,(prefix,'history')
 assert before['width']==after['width']==960 and before['height']==after['height']==640
 inner,holes=gear_values[case['gear']];R=640/3;outer=case['outer'];r=R*inner/outer;A=R-r;k=-A/r
 assert float(case['controls']['radius'])==R and int(case['controls']['outer'])==outer and int(case['controls']['inner'])==inner and case['controls']['gear']==case['gear']
 if case['drive']=='auto':end=2*math.pi*inner/math.gcd(outer,inner)
 else:
  native=[p for at,p in pointer if case['start']<=at<=case['end']]
  downs=[p for p in native if p['phase']=='pointerdown'];ups=[p for p in native if p['phase']=='pointerup'];moves=[p for p in native if p['phase']=='pointermove' and p['buttons']==1]
  assert len(downs)==len(ups)==1 and moves and all(p['target']=='view' and p['pointerType']=='mouse' for p in downs+ups+moves)
  def angle(p):
   box=p['rect'];return math.atan2((p['clientY']-box['y'])/box['height']*640-320,(p['clientX']-box['x'])/box['width']*960-480)
  angles=[angle(p) for p in downs+moves];delta=[math.atan2(math.sin(b-a),math.cos(b-a)) for a,b in zip(angles,angles[1:])];assert all(abs(d)<.75 for d in delta);end=sum(delta)*2.5
 shape=case['shape'];selected_hole=2
 def curve(t,hole=None):
  if hole is None:hole=selected_hole
  c=np.cos(t);s=np.sin(t);scale=np.ones_like(t)
  if shape=='square':scale=.92/np.maximum(abs(c),abs(s))
  if shape=='cross':scale=.4+.9*abs(np.sin(2*t))
  x=A*c*scale*(1.28 if shape=='oval' else 1);y=A*s*scale*(.72 if shape=='oval' else 1)
  d=r*(.18+.66*hole/(holes-1));phi=2.2*hole
  return np.column_stack((480+x+d*np.cos(k*t+phi),320+y+d*np.sin(k*t+phi)))
 png=image(actual(prefix,'png'));assert png.size==(960,640)
 original=image(base64.b64decode(before['layers'][0]['image'].split(',',1)[1]));assert original.getextrema()==((255,255),)*4
 if case['mode']=='vector':
  objects=after['layers'][0]['objects'];assert len(objects)==1
  expected=json.loads(json.dumps(before));expected['layers'][0]['objects']=objects;assert expected==after
  obj=objects[0];assert obj['kind']=='path' and obj['name']=='Spiro' and obj['lineWidth']==3 and obj['stroke']['color']=='#1E88E5' and obj['fill'] is None and not obj['paths'][0]['closed']
  points=np.array([[p['x']+obj['matrix'][4],p['y']+obj['matrix'][5]] for p in obj['paths'][0]['points']])
  distances=[float(np.linalg.norm(points[0]-curve(np.array([0]),h)[0])) for h in range(holes)]
  selected_hole=int(np.argmin(distances));assert distances[selected_hole]<1e-6
  assert np.linalg.norm(points[0]-curve(np.array([0]))[0])<1e-6 and np.linalg.norm(points[-1]-curve(np.array([end]))[0])<1e-5,(prefix,'endpoint')
  seed=np.linspace(0,end,len(points));error=np.full(len(points),np.inf)
  # Square/Cross corners can give the one-dimensional projection a local
  # minimum on the other side of a corner. Try both sides, keeping exact fits.
  for shift in [0,-.002,.002,-.01,.01,-.05,.05]:
   unresolved=error>=1e-5
   if not unresolved.any():break
   theta=seed[unresolved]+shift;target=points[unresolved]
   for _ in range(32):
    residual=curve(theta)-target;velocity=(curve(theta+1e-6)-curve(theta-1e-6))/2e-6
    theta-=np.clip(np.sum(residual*velocity,axis=1)/np.maximum(1e-12,np.sum(velocity*velocity,axis=1)),-.05,.05)
   error[unresolved]=np.minimum(error[unresolved],np.linalg.norm(curve(theta)-target,axis=1))
  assert error.max()<1e-5,(prefix,float(error.max()))
  geometric={'stored_points':len(points),'maximum_curve_error_source_px':float(error.max())}
 else:
  assert not after['layers'][0].get('objects')
  expected=json.loads(json.dumps(before));expected['layers'][0]['image']=after['layers'][0]['image'];assert expected==after
  source=image(base64.b64decode(after['layers'][0]['image'].split(',',1)[1]));assert source.tobytes()==png.tobytes()
  geometric={'raster_export_exact':True}
  # Hover can choose a different offered hole before a manual crank. Identify
  # the unique compatible offered hole from the actual raster, rather than
  # assuming the kit's default. Every individual hole has a separate live test.
  changed_probe=ImageChops.difference(png.convert('RGB'),Image.new('RGB',png.size,'white')).convert('L').point(lambda v:255 if v else 0)
  covered_probe=np.array(changed_probe.filter(ImageFilter.MaxFilter(9)));candidates=[]
  for h in range(holes):
   sample=curve(np.linspace(0,end,max(2000,math.ceil(abs(end)*max(A,r*abs(k))*5))),h)
   visible=sample[(sample[:,0]>=0)&(sample[:,0]<960)&(sample[:,1]>=0)&(sample[:,1]<640)].astype(int)
   if np.all(covered_probe[visible[:,1],visible[:,0]]):candidates.append(h)
  assert len(candidates)==1,(prefix,'ambiguous offered hole',candidates)
  selected_hole=candidates[0]
 # Independent densely sampled hypotrochoid swept over the selected stator.
 # The support tolerance covers the 3px pen and decoder antialiasing only.
 samples=curve(np.linspace(0,end,max(2000,math.ceil(abs(end)*max(A,r*abs(k))*25))))
 allowed=Image.new('L',png.size);draw=ImageDraw.Draw(allowed);pts=[tuple(p) for p in samples];draw.line(pts,fill=255,width=7)
 # Pillow's integer line rasterizer can leave joint gaps even for densely
 # sampled float segments. Union round support at samples at the same radius.
 for x,y in pts[::5]+[pts[-1]]:draw.ellipse((x-3.5,y-3.5,x+3.5,y+3.5),fill=255)
 changed=ImageChops.difference(png.convert('RGB'),Image.new('RGB',png.size,'white')).convert('L').point(lambda v:255 if v else 0)
 outside=ImageChops.subtract(changed,allowed)
 if outside.getbbox():
  outside.save(out/(prefix+'-outside-oracle.png'));allowed.save(out/(prefix+'-allowed-oracle.png'))
  yy,xx=np.nonzero(np.array(outside));nearest=[float(np.linalg.norm(samples-np.array([x+.5,y+.5]),axis=1).min()) for x,y in zip(xx,yy)]
  raise AssertionError((prefix,'unexpected pixels',outside.getbbox(),len(xx),min(nearest),max(nearest)))
 assert changed.getbbox()
 coverage=np.array(changed.filter(ImageFilter.MaxFilter(9)))
 visible=samples[(samples[:,0]>=0)&(samples[:,0]<960)&(samples[:,1]>=0)&(samples[:,1]<640)].astype(int)
 assert np.all(coverage[visible[:,1],visible[:,0]]),(prefix,'missing curve')
 assert sum(p==(30,136,229,255) for p in png.get_flattened_data())>20
 if case.get('nativeReopened'):
  assert doc(prefix+'-reopened')==after and image(actual(prefix+'-reopened','png')).tobytes()==png.tobytes()
 results.append({key:case[key] for key in ['gear','outer','shape','drive','mode']}|geometric|{'offered_hole_zero_based':selected_hole,'whole_undo_redo_exact':True,'native_reopened':bool(case.get('nativeReopened'))})
levels={key:sorted({c[key] for c in cases}) for key in ['gear','outer','shape','drive','mode']};missing={}
for a,b in itertools.combinations(levels,2):
 absent=[list(pair) for pair in itertools.product(levels[a],levels[b]) if not any(c[a]==pair[0] and c[b]==pair[1] for c in cases)]
 if absent:missing[a+'/'+b]=absent
if len(sys.argv)==1:assert not missing,missing
report={'status':'Pass','scope':'Recorded combinations only; no full Cartesian claim.','combinations':results,'missing_pairs_within_observed_levels':missing,'sha256':hashes}
name='spiro-pairs-verification'+('-'+'-'.join(sys.argv[1:]) if len(sys.argv)>1 else '')+'.json'
(out/name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':'Pass','cases':len(results),'missing_pairs':missing,'downloads':len(hashes)},indent=2))
