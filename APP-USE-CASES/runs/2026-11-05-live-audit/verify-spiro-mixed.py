"""Verify the exact mixed VECTOR fixture and live Spiro transforms."""
import hashlib,io,json,math
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageDraw
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(suffix,ext='retropaint'):
 name='mouse-audit-spiro-mixed36-'+suffix+'.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(suffix):return json.loads(actual(suffix))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
before=doc('before');fixture=json.loads((out/'mouse-audit-vector-mixed-baseline.retropaint').read_bytes())
# Current serialization omits the optional false wet flag on the two old brush
# pieces. Require that exact known default normalization and no other change.
for i in [7,8]:assert fixture['layers'][0]['objects'][i].pop('wet') is False
assert before==fixture
original=before['layers'][0]['objects'];assert len(original)==9 and {o['kind'] for o in original}=={'path','text','stamp','raster'}
assert sum(o['kind']=='raster' for o in original)==3 and next(o for o in original if o['name']=='Transparent PNG')['matrix'][4]<0
created=doc('created');resized=doc('resized');moved=doc('moved');raster=doc('raster');reopened=doc('reopened')
assert doc('resize-undone')==created and doc('resize-redone')==resized and doc('move-undone')==resized and doc('move-redone')==moved
for d in [created,resized,moved,raster,reopened]:assert len(d['layers'][0]['objects'])==10 and d['layers'][0]['objects'][:9]==original
new=created['layers'][0]['objects'][-1];assert new['kind']=='path' and new['name']=='Spiro' and new['lineWidth']==3 and new['stroke']['color']=='#1E88E5' and new['fill'] is None
expected=json.loads(json.dumps(before));expected['layers'][0]['objects'].append(new);assert expected==created
for d in [resized,moved]:
 obj=d['layers'][0]['objects'][-1];expected=json.loads(json.dumps(created));expected['layers'][0]['objects'][-1]['matrix']=obj['matrix'];assert expected==d
expected=json.loads(json.dumps(moved));expected['drawingMode']='raster';assert expected==raster==reopened
e=json.loads((out/'spiro-mixed36-evidence.json').read_bytes());assert e['selected']['value']==e['reopenedSelected']['value']==new['id'] and len(e['reopenedSelected']['choices'])==11
pointer=[]
for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines():
 if 'native pointer' in line:
  row=json.loads(line)['event'];at=datetime.fromisoformat(row['at'].replace('Z','+00:00')).timestamp()*1000
  if e['resize']['start']<=at<=e['resize']['end']:pointer.append(row['detail'])
down=next(p for p in pointer if p['phase']=='pointerdown');up=next(p for p in pointer if p['phase']=='pointerup');assert down['target']==up['target']=='view' and down['pointerType']==up['pointerType']=='mouse'
dx=(up['clientX']-down['clientX'])/down['rect']['width']*960;dy=(up['clientY']-down['clientY'])/down['rect']['height']*640
m=resized['layers'][0]['objects'][-1]['matrix'];assert abs(m[0]-(1+dx/new['width']))<1e-8 and abs(m[3]-(1+dy/new['height']))<1e-8 and m[1:3]==[0,0] and max(abs(a-b) for a,b in zip(m[4:],new['matrix'][4:]))<1e-10
assert max(abs(a-b) for a,b in zip(moved['layers'][0]['objects'][-1]['matrix'],m[:4]+[420,260]))<1e-10
points=np.array([[p['x']+new['matrix'][4],p['y']+new['matrix'][5]] for p in new['paths'][0]['points']]);R=120;r=45;A=75;k=-A/r;d=.4*r;phi=4.4
def curve(t):return np.column_stack((480+A*np.cos(t)+d*np.cos(k*t+phi),320+A*np.sin(t)+d*np.sin(k*t+phi)))
theta=np.unwrap(np.arctan2(points[:,1]-320,points[:,0]-480))
for _ in range(12):
 error=curve(theta)-points;velocity=np.column_stack((-A*np.sin(theta)-d*k*np.sin(k*theta+phi),A*np.cos(theta)+d*k*np.cos(k*theta+phi)));theta-=np.sum(error*velocity,axis=1)/np.sum(velocity*velocity,axis=1)
error=np.linalg.norm(curve(theta)-points,axis=1);assert error.max()<1e-6 and abs(theta[0])<1e-7 and abs(theta[-1]-6*math.pi)<1e-6
base=image(actual('before','png'));assert base.tobytes()==image((out/'mouse-audit-vector-mixed-baseline.png').read_bytes()).tobytes()
previous=base;previous_doc=before
for suffix,d in [('created',created),('resized',resized),('moved',moved)]:
 png=image(actual(suffix,'png'));allowed=Image.new('L',png.size);draw=ImageDraw.Draw(allowed)
 for document in [previous_doc,d]:
  if len(document['layers'][0]['objects'])<10:continue
  obj=document['layers'][0]['objects'][-1];a,b,c,dd,tx,ty=obj['matrix'];pts=[(a*p['x']+c*p['y']+tx,b*p['x']+dd*p['y']+ty) for p in obj['paths'][0]['points']]
  draw.line(pts,fill=255,width=9)
  for x,y in pts[::5]+[pts[-1]]:draw.ellipse((x-4.5,y-4.5,x+4.5,y+4.5),fill=255)
 changed=ImageChops.difference(previous,png).convert('RGB').convert('L').point(lambda v:255 if v else 0)
 assert changed.getbbox() and ImageChops.subtract(changed,allowed).getbbox() is None,(suffix,'neighbour pixels changed')
 previous=png;previous_doc=d
assert previous.tobytes()==image(actual('raster','png')).tobytes()==image(actual('reopened','png')).tobytes()
report={'status':'Pass','original_nine_objects_and_raster_exact':True,'new_spiro_all_points_analytic_error_source_px':float(error.max()),'native_gold_handle_delta_source_px':[dx,dy],'resize_and_move_only_change_selected_matrix':True,'whole_undo_redo_exact':True,'raster_switch_keeps_ten_objects':True,'native_project_and_png_roundtrip_exact':True,'reopened_new_piece_selected_individually':True,'sha256':hashes}
(out/'spiro-mixed36-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
