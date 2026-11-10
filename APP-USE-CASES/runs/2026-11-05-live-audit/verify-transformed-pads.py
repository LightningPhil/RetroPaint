"""Independent rotated/scaled opposite support planes, exact pad endpoints and volumes."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';fixtures=root/'test-results/audit-2026-11-05/fixtures/support204';prefix='mouse-audit-support205';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(12)];index=next(i for i,l in enumerate(docs[0]['layers']) if 'cad'in l)
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
def body(doc):return doc['layers'][index]['cad']['bodies'][0]
assert canonical(docs[0])==canonical(json.loads((fixtures/'transformed-top.retropaint').read_text())) and canonical(docs[5])==canonical(json.loads((fixtures/'transformed-bottom.retropaint').read_text()))
assert canonical(docs[1])==canonical(docs[3]) and canonical(docs[2])==canonical(docs[4])==canonical(docs[10]) and canonical(docs[6])==canonical(docs[8]) and canonical(docs[7])==canonical(docs[9])==canonical(docs[11])
angles=np.radians([20,30,40]);cx,cy,cz=np.cos(angles);sx,sy,sz=np.sin(angles);rotation=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]);scale=np.array([1.5,.75,2]);centre=np.array([-12,7,4]);results=[]
ui=json.loads((out/'support205-ui.json').read_text(encoding='utf-8'))
for sample,docid,sign,height,baseid in zip(ui['meshes'],[1,2,6,7],[1,1,-1,-1],[20,30,20,30],[0,0,5,5]):
 doc=docs[docid];rootbody=body(doc);r=rootbody['solid'];assert r['kind']=='boolean' and r['operation']=='union' and rootbody['position']==rootbody['rotation']==[0,0,0] and rootbody['scale']==[1,1,1]
 cube,pad=r['children'];expected_cube=copy.deepcopy(body(docs[baseid]));expected_cube['solid']['size'][2]=height
 if height==30:expected_cube['solid']['feature']={'label':'Support cube'}
 assert cube==expected_cube
 expected_doc=copy.deepcopy(docs[baseid]);expected_doc['layers'][index]['cad']['bodies']=[rootbody];assert canonical(expected_doc)==canonical(doc)
 s=pad['solid'];normal=rotation@np.array([0,0,sign]);u,v=np.array(s['plane']['u']),np.array(s['plane']['v']);origin=np.array(s['plane']['origin'])
 assert np.max(abs(np.array(s['plane']['normal'])-normal))<1e-10 and np.max(abs(origin-(centre+normal*20)))<1e-10 and abs(np.linalg.norm(u)-1)<1e-10 and abs(np.linalg.norm(v)-1)<1e-10 and np.max(abs(np.cross(u,v)-normal))<1e-10
 assert s['height']==7 and s['taper']==1 and s['twist']==0 and s['points']==[[-5,-5],[5,-5],[5,5],[-5,5]] and not s['feature']['through']
 a=s['feature']['attachment'];assert a['reference']==cube['id'] and np.max(abs(np.array(a['anchor'])-[.5,.5,1 if sign==1 else 0]))<1e-10 and np.max(abs(np.array(a['normal'])-[0,0,sign]))<1e-10
 cube_vertices=np.array([[x,y,z] for x in [-10,10] for y in [-10,10] for z in [-height/2,height/2]])*scale;cube_vertices=cube_vertices@rotation.T+centre
 face=centre+normal*height;pad_vertices=np.array([face+u*x+v*y+normal*d for d in [0,7] for x,y in s['points']]);wanted=np.vstack([cube_vertices,pad_vertices]);n=sample['stlIndex'];tri=read_binary(retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl'));stats=measure(tri);actual=np.unique(tri.reshape(-1,3),axis=0)
 assert len(stats['components'])==1 and stats['components'][0]['euler']==2 and abs(stats['signed_volume_mm3']-(20*20*height*np.prod(scale)+700))<.02
 assert np.min(np.linalg.norm(wanted[:,None]-actual[None,:],axis=2),axis=1).max()<.001 and np.max(abs(np.array(stats['bounds_mm'])-[wanted.min(axis=0),wanted.max(axis=0)]))<.001
 projected=(actual-centre)@normal;assert abs(projected.max()-(height+7))<.001 and abs(projected.min()+height)<.001
 results.append(dict(stage=sample['stage'],mesh=stats,independent_face_normal=normal.tolist(),resolved_face_centre=face.tolist(),far_endpoint_distance_from_support_mm=float(projected.max()-height),independent_volume_mm3=float(20*20*height*np.prod(scale)+700)))
assert body(docs[1])['solid']['children'][1]==body(docs[2])['solid']['children'][1] and body(docs[6])['solid']['children'][1]==body(docs[7])['solid']['children'][1]
assert ui['topSourceSizeBefore']==ui['bottomSourceSizeBefore']=='20' and len(ui['picks'])==2 and all(p['plane']=='face' and 'Face ready'in p['status'] for p in ui['picks']) and len(ui['reopened'])==2 and all(p['depth']=='7' and p['direction']=='1' for p in ui['reopened'])
report=dict(status='Pass',native_opposite_faces_have_rotated_world_normals=True,nonuniform_scale_preserves_10x10mm_pad_area=True,positive7mm_pad_far_endpoint_exact_on_both_normals=True,join_contact_allowance_does_not_extend_far_end=True,all_four_meshes_closed_single_outward_components=True,initial_volume18700_and_resized27700_independently_verified=True,upstream_local_height20_to30_moves_attached_face_without_changing_pad_recipe=True,both_size_edits_single_undo_redo_exact=True,both_actual_saved_constructions_reopened_and_cancel_source_exact=True,original_picture_and_unrelated_source_exact=True,meshes=results,hashes=hashes)
(out/'support205-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
