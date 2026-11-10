"""Independent transported end caps, sweep volume, path projections and point limits."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def docs(prefix,count):return [json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(count)]
def bodies(d):return next(l['cad']['bodies'] for l in d['layers'] if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
a=docs('mouse-audit-sweep215',7);b=docs('mouse-audit-sweep216',7)
assert canonical(a[0])==canonical(a[2])
assert all(canonical(a[1])==canonical(a[i]) for i in [3,4,5,6])
assert canonical(b[0])==canonical(b[1])==canonical(b[3]) and all(canonical(b[2])==canonical(b[i]) for i in [4,5,6])
assert bodies(a[1])==bodies(b[0])
before=copy.deepcopy(bodies(b[0])[0]);before['solid']['path']['points'][-1]=[22,4,24];before['solid']['feature']={'label':'Sweep'};assert before==bodies(b[2])[0]
for group in [a,b]:
 for d in group:
  expected=copy.deepcopy(group[0]);next(l for l in expected['layers'] if 'cad'in l)['cad']['bodies']=bodies(d);assert canonical(expected)==canonical(d)
for d,end in [(a[1],[20,0,20]),(b[2],[22,4,24])]:
 s=bodies(d)[0]['solid'];assert s['kind']=='sweep' and not s['path']['smooth'] and s['transition']=='right' and s['roll']==0 and s['path']['points']==[[0,0,0],[0,0,20],end] and np.max(abs(np.array(s['profile']['points'])-[[-4,-2],[4,-2],[4,2],[-4,2]]))<1e-10
def caps(tri,end):
 end=np.array(end,dtype=float);normal=end-[0,0,20];normal/=np.linalg.norm(normal);axis=np.cross([0,0,1],normal);sin=np.linalg.norm(axis);axis/=sin;cos=normal[2];kx,ky,kz=axis;cross=np.array([[0,-kz,ky],[kz,0,-kx],[-ky,kx,0]]);rotation=np.eye(3)+sin*cross+(1-cos)*cross@cross
 result=[]
 for centre,norm,expected in [(np.zeros(3),np.array([0,0,-1]),np.array([[-4,-2,0],[4,-2,0],[4,2,0],[-4,2,0]])),(end,normal,np.array([[-4,-2,0],[4,-2,0],[4,2,0],[-4,2,0]])@rotation.T+end)]:
  selected=tri[np.max(abs((tri-centre)@norm),axis=1)<.001];vertices=np.unique(np.round(selected.reshape(-1,3),6),axis=0);assert len(vertices)==4
  assert max(min(np.linalg.norm(v-p)for v in vertices)for p in expected)<.001
  normals=np.cross(selected[:,1]-selected[:,0],selected[:,2]-selected[:,0]);area=np.linalg.norm(normals,axis=1).sum()/2;assert abs(area-32)<.003 and np.all(normals@norm>0);result.append(dict(centre=centre.tolist(),outward_normal=norm.tolist(),area_mm2=float(area),transported_corners_verified=True))
 return result
results=[]
for prefix,end in [('mouse-audit-sweep215',[20,0,20]),('mouse-audit-sweep216',[22,4,24])]:
 raws=[]
 for n in range(2):
  raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws.append(raw);tri=read_binary(raw);stats=measure(tri);volume=32*(20+np.linalg.norm(np.array(end)-[0,0,20]));assert len(stats['components'])==1 and stats['components'][0]['euler']==2 and abs(stats['signed_volume_mm3']-volume)<.03
  if prefix.endswith('215'):
   assert np.max(abs(np.array(stats['bounds_mm'])-[[-4,-2,0],[20,2,24]]))<.001 and ray_y(tri,0,5)==[-2,2] and ray_y(tri[:,:,[0,2,1]],10,.123)==[16,24] and ray_y(tri[:,:,[1,0,2]],.123,10)==[-4,4] and ray_y(tri[:,:,[1,0,2]],.123,20)==[-4,20]
  results.append(dict(specimen=prefix,index=n,mesh=stats,analytic_volume_mm3=float(volume),end_caps=caps(tri,end)))
 assert raws[0]==raws[1]
old=json.loads((out/'sweep215-ui.json').read_text(encoding='utf-8'));new=json.loads((out/'sweep216-ui.json').read_text(encoding='utf-8'));os={s['stage']:s for s in old['states']};ns={s['stage']:s for s in new['states']}
assert '0.01 mm apart' in os['duplicate-consecutive-path-rejected']['text'] and 'Use an open path' in os['closed-path-rejected']['text']
assert os['before-fix-max64-enabled']==dict(stage='before-fix-max64-enabled',count=64,addEnabled=True) and os['before-fix-min2-enabled']['removeEnabled'] and os['before-fix-add65-no-op']['count']==64 and os['before-fix-remove1-no-op']['count']==2
for stage,count,enabled in [('fixed-max64',64,'addEnabled'),('fixed-min2',2,'removeEnabled'),('fixed-builder-sweep64',64,'addEnabled'),('fixed-builder-sweep2',2,'removeEnabled'),('fixed-builder-profile256',256,'addEnabled'),('fixed-builder-profile3',3,'removeEnabled')]: assert ns[stage]['count']==count and not ns[stage][enabled]
drags=[s for s in new['states'] if s['stage']=='native-projected-drag'];previous=[20,0,20]
for drag,preserved in zip(drags,[1,2,0]):
 values=list(map(float,drag['values']));assert values[preserved]==previous[preserved] and all(values[i]!=previous[i]for i in range(3)if i!=preserved);previous=values
for s in [s for s in new['states'] if s['stage']=='numeric-values-match-plot']:
 expected={'xz':[[0,0],[0,-20],[22,-24]],'xy':[[0,0],[0,0],[22,-4]],'yz':[[0,0],[0,-20],[4,-24]]}[s['projection']];assert np.max(abs(np.array(s['points'],dtype=float)-expected))<1e-10
assert os['actual-original-sweep-reopened']['coordinates']=='0,0,0; 0,0,20; 20,0,20' and ns['actual-exact-path-reopened']['coordinates']=='0,0,0; 0,0,20; 22,4,24'
report=dict(status='Pass',cases=['FEATURE-025','FEATURE-026'],fix='LIVE-071 point add/remove controls disabled at supported boundaries',native_front_top_side_drag_each_changes_only_intended_coordinate_pair=True,exact_numbers_and_three_svg_projections_agree=True,sweep2_to64_and_profile3_to256_buttons_native_verified=True,closed_or_duplicate_paths_reject_and_correct_safely=True,independent_area32_times_pathlength_volumes_and_transported_caps_verified=True,straight_elbow_complete_legs_and_miter_sections_verified=True,closed_oriented_euler2=True,creation_and_path_edit_each_one_undo_redo_exact=True,actual_both_projects_reopened_and_cancel_exact=True,each_reopened_or_canceled_stl_byte_exact=True,builder_limit_probes_preserve_saved_sweep=True,meshes=results,hashes=hashes)
(out/'sweep215-216-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
