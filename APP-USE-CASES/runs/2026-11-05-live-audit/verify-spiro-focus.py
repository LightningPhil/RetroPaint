"""Verify real held-mouse focus cancellation and rejected Photo-lab switch."""
import hashlib,io,json,math
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageDraw
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(suffix,ext='retropaint'):
 name='mouse-audit-spiro-focus36-'+suffix+'.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(suffix):return json.loads(actual(suffix))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
before=doc('before');after=doc('after');workflow=doc('workflow');assert doc('undone')==before and doc('redone')==after and doc('workflow-undone')==after and doc('workflow-redone')==workflow
assert before==json.loads((out/'mouse-audit-spiro-kit36-after.retropaint').read_bytes())
e=json.loads((out/'spiro-focus36-evidence.json').read_bytes());assert e['stateAfterFocus']==e['stateAfterRelease']=={'pressed':'false','text':'Wind the key'} and 0<e['raised']-e['running']<1000
attempt=e['workflowAttempt']['ui'];assert attempt['pressed']=='true' and attempt['wind']=='Stop drawing' and attempt['spiroVisible'] and attempt['photoExpanded']=='false' and attempt['status']=='Let the current effect finish first.'
native=[]
for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines():
 if 'native pointer' not in line:continue
 row=json.loads(line)['event'];at=datetime.fromisoformat(row['at'].replace('Z','+00:00')).timestamp()*1000
 if e['start']<=at<=e['raised']+7000:native.append((at,row['detail']))
down=next((at,p) for at,p in native if p['phase']=='pointerdown');up=next((at,p) for at,p in native if p['phase']=='pointerup');assert down[1]['target']==up[1]['target']=='view' and down[1]['pointerType']==up[1]['pointerType']=='mouse' and up[0]-down[0]>5900 and down[0]<e['running']<e['raised']<up[0]
previous=image((out/'mouse-audit-spiro-kit36-after.png').read_bytes());curves=[]
for suffix,old,current in [('after',before,after),('workflow',after,workflow)]:
 objects=current['layers'][0]['objects'];assert len(objects)==len(old['layers'][0]['objects'])+1 and objects[:-1]==old['layers'][0]['objects']
 expected=json.loads(json.dumps(old));expected['layers'][0]['objects']=objects;assert expected==current
 obj=objects[-1];assert obj['kind']=='path' and obj['name']=='Spiro' and obj['lineWidth']==3 and obj['stroke']['color']=='#1E88E5'
 points=np.array([[p['x']+obj['matrix'][4],p['y']+obj['matrix'][5]] for p in obj['paths'][0]['points']]);R=640/3;r=R*53/180;A=R-r;k=-A/r
 def curve(t,hole):
  d=r*(.18+.66*hole/7);phi=2.2*hole
  return np.column_stack((480+A*np.cos(t)+d*np.cos(k*t+phi),320+A*np.sin(t)+d*np.sin(k*t+phi)))
 distances=[np.linalg.norm(points[0]-curve(np.array([0]),h)[0]) for h in range(8)];hole=int(np.argmin(distances));assert distances[hole]<1e-6
 theta=np.unwrap(np.arctan2(points[:,1]-320,points[:,0]-480));d=r*(.18+.66*hole/7);phi=2.2*hole
 for _ in range(16):
  error=curve(theta,hole)-points;velocity=np.column_stack((-A*np.sin(theta)-d*k*np.sin(k*theta+phi),A*np.cos(theta)+d*k*np.cos(k*theta+phi)));theta-=np.sum(error*velocity,axis=1)/np.sum(velocity*velocity,axis=1)
 error=np.linalg.norm(curve(theta,hole)-points,axis=1);assert error.max()<1e-5 and abs(theta[0])<1e-7 and 0<theta[-1]<2*math.pi*53
 png=image(actual(suffix,'png'));allowed=Image.new('L',png.size);draw=ImageDraw.Draw(allowed);pts=[tuple(p) for p in points];draw.line(pts,fill=255,width=7)
 for x,y in pts[::5]+[pts[-1]]:draw.ellipse((x-3.5,y-3.5,x+3.5,y+3.5),fill=255)
 changed=ImageChops.difference(previous,png).convert('RGB').convert('L').point(lambda v:255 if v else 0);assert changed.getbbox() and ImageChops.subtract(changed,allowed).getbbox() is None
 curves.append({'action':suffix,'hole_zero_based':hole,'points':len(points),'theta_end':float(theta[-1]),'full_curve_theta':2*math.pi*53,'maximum_curve_error_source_px':float(error.max())});previous=png
assert doc('reopened')==workflow and image(actual('reopened','png')).tobytes()==previous.tobytes()
report={'status':'Pass','real_six_second_mouse_hold_interrupted_before_release':True,'stopped_before_natural_completion':True,'no_late_complete_curve_after_release':True,'photo_workflow_rejected_with_visible_stop_and_explanation':True,'whole_undo_redo_exact':True,'curves':curves,'native_project_and_png_roundtrip_exact':True,'recovery_note':'Earlier owned-dialog attempts targeted a different foreground audit tab after focus loss. Escape dismissed the leftover dialog; activating the new audit tab and reopening natively succeeded. Initial immediate AX observation preceded the completed file load. Extension file-URL access remains disabled; no permission was changed.','sha256':hashes}
(out/'spiro-focus36-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
