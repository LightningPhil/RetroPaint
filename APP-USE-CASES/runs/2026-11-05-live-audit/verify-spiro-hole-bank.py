"""Independent hypotrochoid, history, rendered support and native round trip."""
import base64,hashlib,io,json,math,sys
from datetime import datetime
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
gear=sys.argv[1];bank=next(b for b in json.loads((out/'spiro-holes33-evidence.json').read_bytes())['banks'] if b['gear']==gear)
pointer=[]
for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines():
 if 'native pointer' not in line:continue
 row=json.loads(line)['event'];pointer.append((datetime.fromisoformat(row['at'].replace('Z','+00:00')).timestamp()*1000,row['detail']))
def actual(stem,ext='retropaint'):
 name=stem+'.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(actual(stem))
prefix='mouse-audit-spiro-holes33-'+gear;before=doc(prefix+'-before');previous=before;curves=[];assert bank.get('reopened') and len(bank['placements'])==bank['expectedHoles']
for i,event in enumerate(bank['placements']):
 assert event['hole']==i
 after=doc(prefix+'-'+str(i+1));assert doc(prefix+'-'+str(i+1)+'-undone')==previous and doc(prefix+'-'+str(i+1)+'-redone')==after
 objects=after['layers'][0]['objects'];assert len(objects)==i+1 and objects[:-1]==previous['layers'][0].get('objects',[])
 expected=json.loads(json.dumps(before));expected['layers'][0]['objects']=objects;assert expected==after
 obj=objects[-1];assert obj['kind']=='path' and obj['name']=='Spiro' and obj['opacity']==1 and obj['lineWidth']==3 and obj['fill'] is None and obj['stroke']['color']=='#1E88E5' and len(obj['paths'])==1 and not obj['paths'][0]['closed']
 assert obj['matrix'][:4]==[1,0,0,1]
 points=np.array([[p['x']+obj['matrix'][4],p['y']+obj['matrix'][5]] for p in obj['paths'][0]['points']]);assert len(points)>100
 R=bank['controls']['radius'];r=R*bank['teeth']/96;A=R-r;k=-A/r;phi=i*2.2;d=r*(.18+.66*i/(bank['expectedHoles']-1))
 # An ordinary rolling circle: orbit radius R-r, opposite gear rotation,
 # fixed radial hole offset. No application renderer/geometry module is used.
 native=[p for at,p in pointer if event['start']<=at<=event['end']]
 downs=[p for p in native if p['phase']=='pointerdown'];ups=[p for p in native if p['phase']=='pointerup'];moves=[p for p in native if p['phase']=='pointermove' and p['buttons']==1]
 assert len(downs)==len(ups)==1 and moves and all(p['pointerType']=='mouse' and p['target']=='view' for p in downs+ups+moves)
 def angle(p):
  box=p['rect'];return math.atan2((p['clientY']-box['y'])/box['height']*640-320,(p['clientX']-box['x'])/box['width']*960-480)
 # Use delivered coordinates, not the proposed host-double coordinates:
 # browser input quantizes clientX/clientY to float32 before event dispatch.
 angles=[angle(p) for p in downs+moves];deltas=[math.atan2(math.sin(b-a),math.cos(b-a)) for a,b in zip(angles,angles[1:])]
 assert all(abs(d)<.75 for d in deltas)
 end=sum(deltas)*2.5;theta=np.linspace(0,end,len(points))
 def position(t):return np.column_stack((480+A*np.cos(t)+d*np.cos(k*t+phi),320+A*np.sin(t)+d*np.sin(k*t+phi)))
 assert np.linalg.norm(points[0]-position(np.array([0]))[0])<1e-7,(gear,i,'Wrong offered hole')
 assert np.linalg.norm(points[-1]-position(np.array([end]))[0])<1e-5,(gear,i,'Wrong gesture endpoint')
 for iteration in range(15):
  error=position(theta)-points
  velocity=np.column_stack((-A*np.sin(theta)-d*k*np.sin(k*theta+phi),A*np.cos(theta)+d*k*np.cos(k*theta+phi)))
  acceleration=np.column_stack((-A*np.cos(theta)-d*k*k*np.cos(k*theta+phi),-A*np.sin(theta)-d*k*k*np.sin(k*theta+phi)))
  theta-=np.sum(error*velocity,axis=1)/(np.sum(velocity*velocity,axis=1)+np.sum(error*acceleration,axis=1))
 error=np.linalg.norm(position(theta)-points,axis=1);assert error.max()<1e-6 and np.diff(theta).max()<1e-7,(gear,i,float(error.max()))
 curves.append({'hole':i,'points':len(points),'maximum_curve_error_source_px':float(error.max())});previous=after
assert previous==doc(prefix)==doc(prefix+'-reopened')
png=Image.open(io.BytesIO(actual(prefix,'png'))).convert('RGBA');reopened=Image.open(io.BytesIO(actual(prefix+'-reopened','png'))).convert('RGBA');assert png.size==(960,640) and png.tobytes()==reopened.tobytes()
source=Image.open(io.BytesIO(base64.b64decode(previous['layers'][0]['image'].split(',',1)[1]))).convert('RGBA');assert source.getextrema()==((255,255),)*4
allowed=Image.new('L',(960,640));draw=ImageDraw.Draw(allowed)
for obj in previous['layers'][0]['objects']:
 points=[(p['x']+obj['matrix'][4],p['y']+obj['matrix'][5]) for p in obj['paths'][0]['points']];draw.line(points,fill=255,width=7)
 # Pillow's line endpoints are flat; the actual supported pen has round caps.
 for x,y in [points[0],points[-1]]:draw.ellipse((x-3.5,y-3.5,x+3.5,y+3.5),fill=255)
rgb=png.convert('RGB');changed=ImageChops.difference(rgb,Image.new('RGB',rgb.size,'white')).convert('L').point(lambda v:255 if v else 0)
assert ImageChops.subtract(changed,allowed).getbbox() is None,'Export includes pixels outside the independently checked curves'
assert sum(p==(30,136,229,255) for p in png.get_flattened_data())>100
report={'status':'Pass','gear':gear,'offered_holes':len(curves),'each_hole_independent_analytic_curve':curves,'whole_per_hole_undo_redo_and_native_reopen_exact':True,'original_raster_remains_opaque_white':True,'export_only_contains_supported_blue_curves':True,'actual_png_reopen_pixel_exact':True,'sha256':hashes}
(out/f'spiro-hole-bank-{gear}-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','each_hole_independent_analytic_curve']},indent=2))
