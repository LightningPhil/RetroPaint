"""Whole-face, recess, through-hole and explicit support recovery independent oracle."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-support204';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(18)];index=next(i for i,l in enumerate(docs[0]['layers']) if 'cad'in l)
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
def body(doc):return doc['layers'][index]['cad']['bodies'][0]
def recipe(doc):return body(doc)['solid']
for i in [2,4,6]:assert canonical(docs[i])==canonical(docs[0])
assert canonical(docs[3])==canonical(docs[5]) and canonical(docs[7])==canonical(docs[9]) and canonical(docs[8])==canonical(docs[10])==canonical(docs[11])==canonical(docs[13]) and canonical(docs[12])==canonical(docs[14])
assert canonical(docs[16])==canonical(docs[14]) and canonical(docs[15])==canonical(docs[17])
for doc in docs:
 expected=copy.deepcopy(docs[0]);expected['layers'][index]['cad']['bodies']=doc['layers'][index]['cad']['bodies'];assert canonical(expected)==canonical(doc)
cube=body(docs[0]);assert cube['solid']['shape']=='box' and cube['solid']['size']==[20,20,20] and cube['position']==[0,0,10]
for i in [1,3,7,8,12,15]:
 r=recipe(docs[i]);assert r['kind']=='boolean' and len(r['children'])==2 and r['operation']==('union' if i==1 else 'subtract');base,feature=r['children'];expected=copy.deepcopy(cube)
 if i>=8:expected['solid']['size'][2]=30;expected['solid']['feature']={'label':'Support cube'}
 assert base==expected
 s=feature['solid'];assert s['kind']=='extrude' and s['taper']==1 and s['twist']==0 and feature['position']==feature['rotation']==[0,0,0] and feature['scale']==[1,1,1]
 assert np.max(abs(np.array(s['plane']['origin'])-[0,0,25 if i in [12,15] else 20]))<1e-10 and s['plane']['normal']==[0,0,1] and s['plane']['u']==[1,0,0] and s['plane']['v']==[0,1,0]
 if i in [1,3]:assert s['points']==[[-5,-5],[5,-5],[5,5],[-5,5]] and s['height']==(10 if i==1 else -5) and not s['feature']['through']
 else:
  theta=np.arange(96)*2*math.pi/96;assert np.max(abs(np.array(s['points'])-np.column_stack([2*np.cos(theta),2*np.sin(theta)])))<1e-10
 if i not in [12,15]:
  a=s['feature']['attachment'];assert a['reference']==cube['id'] and np.max(abs(np.array(a['anchor'])-[.5,.5,1]))<1e-10 and a['normal']==[0,0,1]
 else:assert 'attachment'not in s['feature'] and not s['feature']['through']
assert recipe(docs[7])['children'][1]==recipe(docs[8])['children'][1]
assert recipe(docs[7])['children'][1]['solid']['height']==recipe(docs[12])['children'][1]['solid']['height']==-1 and recipe(docs[7])['children'][1]['solid']['feature']['through']
assert recipe(docs[15])['children'][1]['solid']['height']==-30
def ray(tri,x,y):
 a,b,c=tri[:,0],tri[:,1],tri[:,2];den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1]);valid=abs(den)>1e-9;a,b,c,den=a[valid],b[valid],c[valid],den[valid];u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/den;v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/den;hit=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7);return sorted(set(np.round((u*a[:,2]+v*b[:,2]+(1-u-v)*c[:,2])[hit],5).tolist()))
ui=json.loads((out/'support204-ui.json').read_text(encoding='utf-8'));area96=96/2*4*math.sin(2*math.pi/96);results=[];raws=[]
for s,volume,z0,z1,centre,top in zip(ui['meshes'],[9000,7500,8000-area96*20,12000-area96*30,12000-area96*30,12000-area96,12000-area96*30,12000-area96*30],[0,0,0,-5,-5,-5,-5,-5],[30,20,20,25,25,25,25,25],[[0,30],[0,15],[],[],[],[-5,24],[],[]],[20,20,20,25,25,25,25,25]):
 n=s['stlIndex'];raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws.append(raw);tri=read_binary(raw);stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==(2 if n in [0,1,5] else 0) and abs(stats['signed_volume_mm3']-volume)<.02
 assert np.max(abs(np.array(stats['bounds_mm'])-[[-10,-10,z0],[10,10,z1]]))<.001 and ray(tri,.31,.57)==centre and ray(tri,7.31,2.57)==[z0,top];results.append(dict(stage=s['stage'],mesh=stats,independent_volume_mm3=volume,centre_vertical_ray=centre,outside_vertical_ray=[z0,top]))
assert raws[3]==raws[4]
assert raws[6]==raws[7]
intended_fixed_recovery_volume=12000-area96*30
actual_fixed_recovery_volume=results[5]['mesh']['signed_volume_mm3']
assert actual_fixed_recovery_volume-intended_fixed_recovery_volume>300
results[5]['intended_recovery_volume_mm3']=intended_fixed_recovery_volume
results[5]['intended_through_hole_preserved']=False
results[5]['observed_unexpected_pocket_depth_mm']=1
assert ui['firstPick']['plane']==ui['secondPick']['plane']=='face' and ui['firstPick']['tap']==[808,358] and ui['secondPick']['tap']==[868,408] and ui['throughPreparation']=={'amount':'1','through':True}
assert ui['missingSupport']['editorOpen'] and ui['missingSupport']['centreX']=='100' and 'supporting flat face no longer exists'in ui['missingSupport']['error'] and 'fixed plane'in ui['missingSupport']['error'] and not ui['fixedPlanePreview']['error']
assert ui['planeChoices'][0]['label']=='Follow supporting face' and ui['reopenedFixedPlaneOptions'][0]['label']=='Keep current workplane'
curve_ui=json.loads((out/'support204-curve-ui.json').read_text(encoding='utf-8'));curve_docs=[json.loads(retain(prefix+'-curve'+(f' ({i})' if i else '')+'.retropaint')) for i in range(2)];assert canonical(curve_docs[0])==canonical(curve_docs[1]) and curve_ui['rejection']['plane']=='xy' and curve_ui['rejection']['faceOptionDisabled'] and 'Pick a flat face'in curve_ui['rejection']['status']
report=dict(status='Partial',cases={'SKETCH-004':'Pass','SKETCH-008':'Pass','SKETCH-009':'Pass','FEATURE-008':'Partial'},deferred_finding='SUPPORT-204: fixed-plane conversion clears Through all and restores stale1mm depth, closing the intended hole',sphere_surface_rejected_without_new_plane_or_source_change=True,two_triangle_halves_pick_same_whole_face_centre_and_normal=True,orbit_retains_exact_four_corner_face_sketch=True,top_boss_10mm_adds1000_and_far_endpoint30=True,recess_removes_exact500_and_floor15_with_outside_bounds_unchanged=True,recess_undo_redo_and_actual_reopen=True,through_checkbox_overrides1mm_depth_and_reaches_both_sides=True,source_height30_rebuilds_hole_across_minus5_to25=True,original_hole_sketch_and_attachment_preserved=True,missing_support_error_keeps_original_source_and_stl_byte_exact=True,fixed_plane_conversion_unexpectedly_closes_hole=True,intended_recovery_volume_mm3=intended_fixed_recovery_volume,actual_pocket_volume_mm3=actual_fixed_recovery_volume,explicit_depth30_manual_workaround_restores_hole=True,conversion_and_workaround_each_undo_redo_exact=True,all_original_paint_and_unrelated_source_exact=True,meshes=results,hashes=hashes)
(out/'support204-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
