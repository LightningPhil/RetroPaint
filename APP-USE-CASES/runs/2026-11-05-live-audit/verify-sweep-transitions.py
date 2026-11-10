"""Independent round/miter/smooth transport checks, retaining a tight-bend failure."""
from collections import Counter
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-sweep217';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(11)]
def body(d):return next(l['cad']['bodies'][0]for l in d['layers']if'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
assert canonical(docs[1])==canonical(docs[6]) and canonical(docs[2])==canonical(docs[7]) and canonical(docs[3])==canonical(docs[5])==canonical(docs[8])==canonical(docs[10]) and canonical(docs[4])==canonical(docs[9])
for d in docs:
 expected=copy.deepcopy(docs[0]);next(l for l in expected['layers']if'cad'in l)['cad']['bodies']=[body(d)];assert canonical(expected)==canonical(d)
for n,smooth,mode,roll,w,h,scale in [(1,False,'round',0,8,4,1),(2,False,'right',30,8,4,1),(3,True,'round',30,4,2,1),(4,True,'round',30,4,2,.1)]:
 s=body(docs[n])['solid'];assert s['kind']=='sweep' and s['path']['smooth']==smooth and s['transition']==mode and s['roll']==roll and s['path']['points']==[[0,0,0],[0,0,20*scale],[20*scale,0,20*scale]]
 pts=np.array(s['profile']['points']);assert np.max(abs(pts-[[-w/2,-h/2],[w/2,-h/2],[w/2,h/2],[-w/2,h/2]]))<1e-10
# Independently integrate interpolating cubic-Hermite centreline arc length.
p=np.array([[0,0,0],[0,0,20],[20,0,20]],dtype=float);x,weights=np.polynomial.legendre.leggauss(96);t=(x+1)/2;arc=0
for i in range(2):
 a,b=p[i],p[i+1];m0=(b-p[max(0,i-1)])/2;m1=(p[min(2,i+2)]-a)/2;der=(6*t*t-6*t)[:,None]*a+(3*t*t-4*t+1)[:,None]*m0+(-6*t*t+6*t)[:,None]*b+(3*t*t-2*t)[:,None]*m1;arc+=float(np.dot(weights,np.linalg.norm(der,axis=1))/2)
def cap_checks(tri,w,h,roll):
 a=math.radians(roll);rz=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]]);ry=np.array([[0,0,1],[0,1,0],[-1,0,0]]);corners=np.array([[-w/2,-h/2,0],[w/2,-h/2,0],[w/2,h/2,0],[-w/2,h/2,0]])@rz.T;result=[]
 for centre,normal,expected in [(np.zeros(3),np.array([0,0,-1]),corners),(np.array([20,0,20]),np.array([1,0,0]),corners@ry.T+[20,0,20])]:
  selected=tri[np.max(abs((tri-centre)@normal),axis=1)<.001];vertices=np.unique(np.round(selected.reshape(-1,3),6),axis=0);assert len(vertices)==4 and max(min(np.linalg.norm(v-p)for v in vertices)for p in expected)<.003
  normals=np.cross(selected[:,1]-selected[:,0],selected[:,2]-selected[:,0]);area=np.linalg.norm(normals,axis=1).sum()/2;assert abs(area-w*h)<.005 and np.all(normals@normal>0);result.append(dict(area_mm2=float(area),rotated_transported_corners_verified=True))
 return result
raws=[];results=[];bad=None
for n in range(7):
 raw=retain(prefix+'-3d-mm'+(f' ({n})'if n else '')+'.stl');raws.append(raw);tri=read_binary(raw)
 if n in [3,5]:
  edges=Counter();orientation=Counter()
  for face in tri:
   for a,b in zip(face,np.roll(face,-1,axis=0)):
    aa,bb=tuple(a),tuple(b);key=tuple(sorted((aa,bb)));edges[key]+=1;orientation[key]+=1 if aa<bb else -1
  counts=Counter(edges.values());assert counts==Counter({2:119838,4:882,6:1}) and not any(orientation.values())
  zero=int((np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)==0).sum());assert zero>0
  bad=dict(triangles=len(tri),edge_incidence_counts={str(k):v for k,v in counts.items()},nonmanifold_edges=sum(v for k,v in counts.items()if k!=2),zero_area_triangles=zero,signed_volume_mm3=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6),closed_manifold=False)
  results.append(dict(index=n,mesh=bad));continue
 stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==2
 w,h,roll,volume,budget=(8,4,0,1280-64+16*math.pi,.03)if n==0 else (8,4,30,1280,.03)if n==1 else (4,2,30,8*arc,.1)
 assert abs(stats['signed_volume_mm3']-volume)<budget
 if n==0:
  z=ray_y(tri[:,:,[0,2,1]],-2,.123);xx=ray_y(tri[:,:,[1,0,2]],.123,22);assert len(z)==len(xx)==2 and np.max(abs(np.array(z)-[0,20+math.sqrt(12)]))<.01 and np.max(abs(np.array(xx)-[-math.sqrt(12),20]))<.01
 results.append(dict(index=n,mesh=stats,analytic_volume_mm3=volume,volume_tolerance_mm3=budget,end_caps=cap_checks(tri,w,h,roll)))
assert raws[2]==raws[4]==raws[6] and raws[3]==raws[5]
ui=json.loads((out/'sweep217-ui.json').read_text(encoding='utf-8'));states={s['stage']:s for s in ui['states']};assert 'Cannot sweep'not in states['tight-smooth-bend']['text']
for label,path,mode,roll in [('straight-round','polyline','round','0'),('miter-roll30','polyline','right','30'),('smooth-roll30','smooth','round','30'),('tight-accepted','smooth','round','30')]:
 settings=states['reopened-'+label]['settings'];assert settings['cadFeatureFormPathMode']==path and settings['cadFeatureFormCorners']==mode and settings['cadFeatureFormRoll']==roll
report=dict(status='Partial',case='FEATURE-027',deferred_finding='SWEEP217 tight smooth bend accepted and saved with883 nonmanifold STL edges; native Print reports closed',round_transition_real_radius4_and_analytic_volume_verified=True,miter_roll30_cap_transport_no_extra_twist_and_volume1280_verified=True,smooth_curve_arc_length_mm=arc,smooth_roll30_small_section_caps_and_volume_verified=True,all_four_actual_saved_variants_reopened=True,tight_bend_safely_rejected=False,tight_nonmanifold_stl_reproduced_byte_exact_after_actual_reopen=True,one_undo_restores_valid_smooth_source_and_stl_byte_exact=True,final_valid_smooth_reopen_cancel_source_and_stl_exact=True,invalid_mesh=bad,meshes=results,hashes=hashes)
(out/'sweep217-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k not in ['meshes','hashes']},indent=2))
