"""Measure live rig screenshots independently of the document renderer."""
import hashlib,io,json,math
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';e=json.loads((out/'spiro-kit36-evidence.json').read_bytes());hashes={}
for ext in ['retropaint','png']:
 names=['mouse-audit-spiro-kit36-'+stage+'.'+ext for stage in ['before','after']]
 data=[(downloads/name).read_bytes() for name in names]
 for name,content in zip(names,data):(out/name).write_bytes(content);hashes[name]=hashlib.sha256(content).hexdigest()
 if ext=='retropaint':assert json.loads(data[0])==json.loads(data[1])
 else:assert Image.open(io.BytesIO(data[0])).tobytes()==Image.open(io.BytesIO(data[1])).tobytes()
def native(action):
 events=[]
 for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines():
  if 'native pointer' not in line:continue
  row=json.loads(line)['event'];at=datetime.fromisoformat(row['at'].replace('Z','+00:00')).timestamp()*1000
  if action['start']<=at<=action['end']:events.append(row['detail'])
 down=next(p for p in events if p['phase']=='pointerdown');up=next(p for p in events if p['phase']=='pointerup');assert down['target']==up['target']=='view' and down['pointerType']==up['pointerType']=='mouse'
 def source(p):return np.array([(p['clientX']-p['rect']['x'])/p['rect']['width']*960,(p['clientY']-p['rect']['y'])/p['rect']['height']*640])
 return source(down),source(up)
down,up=native(e['move']);centre=np.array([480,320])+up-down
down,up=native(e['resize']);radius=float(np.linalg.norm(up-centre))
assert abs(float(e['stages'][2]['radius'])-radius)<1e-8 and e['stages'][3]['radius']=='120.5'
expected={'initial':([480,320],160),'moved':(centre,160),'resized':(centre,radius),'exact':(centre,120.5),'reset':([480,320],640/3)}
measurements=[];paper=e['paper']
for stage,(centre_expected,radius_expected) in expected.items():
 path=out/('spiro-kit36-'+stage+'.jpg');im=Image.open(path);rgb=np.array(im.convert('RGB'));h,w=rgb.shape[:2]
 yy,xx=np.mgrid[0:h,0:w];sx=(xx+.5-paper['x'])/paper['width']*960;sy=(yy+.5-paper['y'])/paper['height']*640
 colour=rgb.astype(float);rig_distance=np.sum((colour-np.array([41,150,186]))**2,axis=2);ink_distance=np.sum((colour-np.array([30,136,229]))**2,axis=2)
 mask=(sx>=0)&(sx<960)&(sy>=0)&(sy<640)&(rig_distance<15**2)&(rig_distance<ink_distance)
 x=sx[mask];y=sy[mask];assert len(x)>1000
 for iteration in range(4):
  a,b,c=np.linalg.lstsq(np.column_stack((x,y,np.ones_like(x))),x*x+y*y,rcond=None)[0];cx=a/2;cy=b/2;r=math.sqrt(c+cx*cx+cy*cy)
  # JPEG colour bleed can classify isolated artwork edge pixels as rig.
  # Retain the fitted ring's 16 CSS-pixel stroke, allowing its antialias edge.
  radial=np.hypot(x-cx,y-cy);keep=abs(radial-np.median(radial))<15;x=x[keep];y=y[keep]
 assert math.hypot(cx-centre_expected[0],cy-centre_expected[1])<1.5 and abs(r-radius_expected)<1.5,(stage,cx,cy,r,centre_expected,radius_expected)
 measurements.append({'stage':stage,'measured_source_centre':[cx,cy],'measured_source_radius':r,'expected_source_radius':radius_expected,'classified_rig_pixels':len(x),'actual_image_format':im.format})
assert e['reset']['enabled'] and e['reset']['radius']['valid'] and float(e['reset']['radius']['value'])==640/3
report={'status':'Pass','circle_screen_measurements':measurements,'numeric_handle_radius_matches_actual_mouse_endpoint':True,'whole_project_and_png_artwork_exact':True,'minimum_and_maximum_reset_accessible':True,'sha256':hashes}
(out/'spiro-kit36-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
