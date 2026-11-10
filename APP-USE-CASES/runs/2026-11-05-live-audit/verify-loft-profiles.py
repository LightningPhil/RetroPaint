"""Independent ordered, ruled and smooth loft surfaces and editable-profile oracle."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-loft213';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(16)]
def bodies(d):return next(l['cad']['bodies'] for l in d['layers'] if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
assert canonical(docs[0])==canonical(docs[2]) and canonical(docs[1])==canonical(docs[3])==canonical(docs[4])==canonical(docs[13])
assert canonical(docs[5])==canonical(docs[7])==canonical(docs[8])==canonical(docs[14]) and canonical(docs[9])==canonical(docs[11]) and canonical(docs[10])==canonical(docs[12])==canonical(docs[15])
# A label is added explicitly by the history editor; no geometric field changes on style switch.
before=copy.deepcopy(bodies(docs[1])[0]);before['solid']['ruled']=False;before['solid']['feature']={'label':'Loft'};assert before==bodies(docs[5])[0]
assert canonical(docs[6])==canonical(docs[1])
ui=json.loads((out/'loft213-ui.json').read_text(encoding='utf-8'));plans=ui['profileEdits'];base=bodies(docs[1])[0]['solid']['profiles'];edited=bodies(docs[9])[0]['solid']['profiles']
for i,(w,z) in enumerate([(20,0),(10,20),(30,40)]):
 p=base[i];assert p['shape']=='rectangle' and p['rotation']==0 and p['plane']['origin']==[0,0,z] and np.max(abs(np.array(p['points'])-[[-w/2,-w/2],[w/2,-w/2],[w/2,w/2],[-w/2,w/2]]))<1e-10
for p,plan in zip(edited,plans):
 assert p['name']==base[plan['index']]['name'] and p['rotation']==plan['turn'] and p['plane']['origin']==plan['origin'];pts=np.array(p['points']);assert np.max(abs(pts.max(0)-pts.min(0)-[plan['width'],plan['height']]))<1e-10 and np.max(abs((pts.max(0)+pts.min(0))/2-plan['center']))<1e-10
assert bodies(docs[10])[0]['solid']['profiles']==edited[::-1]
for d in docs:
 expected=copy.deepcopy(docs[0]);next(l for l in expected['layers'] if 'cad'in l)['cad']['bodies']=bodies(d);assert canonical(expected)==canonical(d)
raws=[];triangles=[];results=[]
for n in range(5):
 raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws.append(raw);tri=read_binary(raw);triangles.append(tri);stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==2;results.append(dict(index=n,mesh=stats))
assert raws[3]==raws[4]
assert abs(results[0]['mesh']['signed_volume_mm3']-40000/3)<.02
ruled,smooth=triangles[:2]
for z in [.001,10,19,19.5,20,20.5,21,30,39.999]:
 width=20-z/2 if z<=20 else 10+(z-20);actual=ray_y(ruled,.123,z);assert len(actual)==2 and np.max(abs(np.array(actual)-[-width/2,width/2]))<.001
for z,radius in [(.001,10),(20,5),(39.999,15)]:
 actual=ray_y(smooth,.123,z);assert len(actual)==2 and np.max(abs(np.array(actual)-[-radius,radius]))<.01
def width(tri,z):
 hits=ray_y(tri,.123,z);assert len(hits)==2;return hits[1]-hits[0]
slopes={}
for label,tri in [('ruled',ruled),('smooth',smooth)]:
 left=(width(tri,20)-width(tri,19.5))/.5;right=(width(tri,20.5)-width(tri,20))/.5;slopes[label]=dict(left=left,right=right,jump=abs(right-left))
assert slopes['smooth']['jump']<.1 and abs(slopes['ruled']['jump']-1.5)<.001 and abs(width(smooth,10)-width(ruled,10))>1
# All edited profiles share30degree axes; independently undo that rotation.
angle=math.pi/6;rotation=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]);centres=[np.array(p['origin'][:2])@rotation+np.array(p['center']) for p in plans]
volume=0
for a,b in zip(plans,plans[1:]):
 dw,dh=b['width']-a['width'],b['height']-a['height'];volume+=(b['origin'][2]-a['origin'][2])*(a['width']*a['height']+(a['width']*dh+a['height']*dw)/2+dw*dh/3)
for n in [2,3,4]:
 tri=triangles[n].copy();tri[:,:,:2]=tri[:,:,:2]@rotation;assert abs(results[n]['mesh']['signed_volume_mm3']-volume)<.03;rays=[]
 for z in [-4.99,5,14.99,15,25,34.99]:
  k=0 if z<=15 else 1;t=(z-plans[k]['origin'][2])/20;c=centres[k]*(1-t)+centres[k+1]*t;w=plans[k]['width']*(1-t)+plans[k+1]['width']*t;h=plans[k]['height']*(1-t)+plans[k+1]['height']*t
  yy=ray_y(tri,float(c[0]),z);xx=ray_y(tri[:,:,[1,0,2]],float(c[1]),z);assert len(yy)==len(xx)==2 and np.max(abs(np.array(yy)-(c[1]+np.array([-h/2,h/2]))))<.003 and np.max(abs(np.array(xx)-(c[0]+np.array([-w/2,w/2]))))<.003;rays.append(dict(z=z,x=xx,y=yy))
 results[n]['unrotated_sections']=rays;results[n]['analytic_volume_mm3']=volume
states={s['stage']:s for s in ui['states']};assert states['max16']['count']==16 and not states['max16']['addEnabled'] and states['min2']['count']==2 and not states['min2']['removeEnabled']
assert 'Cannot loft' in states['all-three-planes-collapsed-rejected']['text'] and states['deliberate-reverse-profile-order']['options']==['1. Top30','2. Waist10','3. Base20']
assert states['reopened-ruled']['settings']=='ruled' and states['reopened-smooth']['settings']=='smooth'
for rec,plan in zip(states['reopened-reversed-edited']['profiles'],plans[::-1]):
 values=dict(rec['outline']+rec['placement']);assert float(values['cadFeatureFormWidth'])==plan['width'] and float(values['cadFeatureFormHeight'])==plan['height'] and [float(values['cadFeatureFormCenter'+a])for a in ['X','Y']]==plan['center'] and [float(values['cadFeatureFormOrigin'+str(a)])for a in range(3)]==plan['origin'] and float(values['cadFeatureFormRotation'])==30
report=dict(status='Pass',cases=['FEATURE-021','FEATURE-022'],style_geometry_checks_pass_for_FEATURE023_pending_constraint_preservation=True,ruled_volume_exact40000over3=True,smooth_interpolates_all_profiles_with_continuous_waist_slope=True,slopes=slopes,independent_profile_size_centre_origin_turns_and_actual_mesh_sections_verified=True,deliberate_reverse_order_preserves_physical_shape=True,profile_limits2_to16_enforced=True,collapsed_stack_rejected_cancel_exact=True,creation_and_reorder_one_undo_redo_exact=True,actual_ruled_smooth_reversed_projects_reopened_and_cancel_exact=True,all_reopened_profile_values_match=True,reopened_final_stl_byte_exact=True,meshes=results,hashes=hashes)
(out/'loft213-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
