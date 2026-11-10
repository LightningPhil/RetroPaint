"""Independent exact workplane bases, positive/negative pulls and centred editable96gon circle."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};results={}
def retain(name,mesh=False):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return read_binary(raw) if mesh else json.loads(raw)
prefix='mouse-audit-sketch191';base=retain(prefix+'.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l);assert not base['layers'][index]['cad']['bodies']
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
planes={'xy':([1,0,0],[0,1,0],[0,0,1]),'xz':([1,0,0],[0,0,1],[0,-1,0]),'yz':([0,1,0],[0,0,1],[1,0,0])};ui=json.loads((out/'sketch191-ui.json').read_text(encoding='utf-8'));ids=[];circle_doc=None
for s in ui['samples']:
 doc=retain(prefix+f" ({s['docIndex']}).retropaint");bodies=doc['layers'][index]['cad']['bodies'];assert len(bodies)==1;body=bodies[0];ids.append(body['id']);recipe=body['solid'];u,v,normal=map(np.array,planes[s['plane']]);assert body['position']==body['rotation']==[0,0,0] and body['scale']==[1,1,1] and recipe['plane']==dict(origin=[0,0,0],u=u.tolist(),v=v.tolist(),normal=normal.tolist())
 assert recipe['height']==s['depth'] and recipe['taper']==1 and recipe['twist']==0 and recipe['feature']['sketch']==s['shape']
 if s['shape']=='rectangle':
  points=np.array([[-5,-5],[5,-5],[5,5],[-5,5]]);assert np.array_equal(recipe['points'],points);area=100
 else:
  n=96;theta=np.arange(n)*2*math.pi/n;points=np.column_stack([30+10*np.cos(theta),10+10*np.sin(theta)]);assert np.max(np.abs(np.array(recipe['points'])-points))<1e-10;area=n/2*100*math.sin(2*math.pi/n);circle_doc=doc
 wanted=np.vstack([points[:,0,None]*u+points[:,1,None]*v+h*normal for h in [0,s['depth']]])
 suffix=f" ({s['stlIndex']})" if s['stlIndex'] else '';tri=retain(prefix+'-3d-mm'+suffix+'.stl',True);actual=np.unique(tri.reshape(-1,3),axis=0);assert len(actual)==len(wanted) and np.min(np.linalg.norm(actual[:,None]-wanted[None,:],axis=2),axis=1).max()<.000003;stats=measure(tri);expected_volume=area*abs(s['depth']);assert abs(stats['signed_volume_mm3']-expected_volume)<.003 and len(stats['components'])==1 and stats['components'][0]['euler']==2
 expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies']=bodies;assert canonical(doc)==canonical(expected) and s['afterOneUndo']=='0 pieces';results[s['stage']]=dict(mesh=stats,independent_volume_mm3=expected_volume)
assert len(set(ids))==5 and canonical(retain(prefix+f" ({ui['emptyDocIndex']}).retropaint"))==canonical(base) and canonical(retain(prefix+f" ({ui['reopenedDocIndex']}).retropaint"))==canonical(circle_doc)
fields={f['id']:f['value'] for f in ui['reopenedCircleFields']};assert fields['cadFeatureSketchX']=='30' and fields['cadFeatureSketchY']=='10' and fields['cadFeatureSketchWidth']==fields['cadFeatureSketchHeight']=='20';assert 'Draw a sketch first' in ui['planeChange']['status'] and ui['planeChange']['pieces']=='0 pieces' and all(s['pieces']=='0 pieces' for s in ui['invalid']) and any('0.05' in s['status'] for s in ui['invalid']) and any('must be between' in s['status'] for s in ui['invalid'])
report=dict(status='Pass',all3_fixed_planes_match_cartesian_basis=True,exact_10x10_positive30_volume_mm3=3000,negative10_below_zero_closed_outward_volume_mm3=1000,unchanged_plane_while_partial_rejected_without_mixed_points=True,zero_and_empty_depth_rejected_then_same_sketch_succeeds=True,circle_centre_mm=[30,10],diameter_mm=20,reopened_editable_circle_parameters_exact=True,each_creation_single_undo=True,empty_source_restored_and_original_paint_exact=True,meshes=results,hashes=hashes)
(out/'sketch191-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
