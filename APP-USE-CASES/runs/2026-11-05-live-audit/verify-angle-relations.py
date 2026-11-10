"""Independent directed-vector relations, persistence and actual solid geometry."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-angles202';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
ui=json.loads((out/'angles202-ui.json').read_text(encoding='utf-8'));docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(11)];index=next(i for i,l in enumerate(docs[0]['layers']) if 'cad'in l)
def recipe(doc):return doc['layers'][index]['cad']['bodies'][0]['solid']
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
def stripped(doc):
 d=canonical(doc);r=recipe(d);r.pop('points');r['feature'].pop('constraints',None);r['feature'].pop('sketchName',None);return d
expected=[('angle',-10),('angle',-20),('parallel',None),('perpendicular',None),('angle-between',120),('angle-between',110)];results=[]
for i,(s,(kind,value)) in enumerate(zip(ui['meshes'],expected),1):
 r=recipe(docs[i]);p=np.array(r['points']);v=np.roll(p,-1,axis=0)-p;rules=r['feature']['constraints'];assert rules[0]['kind']==kind and stripped(docs[i])==stripped(docs[0]) and not np.allclose(p,recipe(docs[0])['points'])
 if value is not None:assert rules[0]['value']==value
 for c in rules:
  a=v[c['edge']];angle=math.degrees(math.atan2(a[1],a[0]))
  if c['kind']=='angle':assert abs((angle-c['value']+180)%360-180)<.001
  else:
   b=v[c['other']];dot=np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b))
   if c['kind']=='parallel':assert abs(abs(dot)-1)<1e-8
   elif c['kind']=='perpendicular':assert abs(dot)<1e-8
   else:assert abs(math.degrees(math.acos(np.clip(dot,-1,1)))-c['value'])<.001
 if kind=='parallel':assert rules[0]['edge']==0 and rules[0]['other']==2 and rules[1]['kind']=='angle' and rules[1]['value']==20
 if kind in ['perpendicular','angle-between']:assert rules[0]['edge']==0 and rules[0]['other']==1
 n=s['stlIndex'];tri=read_binary(retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl'));stats=measure(tri);wanted=np.array([[x,y,z] for z in [0,10] for x,y in p]);actual=np.unique(tri.reshape(-1,3),axis=0)
 assert len(actual)==8 and np.min(np.linalg.norm(actual[:,None]-wanted[None,:],axis=2),axis=1).max()<.00001 and len(stats['components'])==1 and stats['components'][0]['euler']==2
 area=abs(np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]))/2;assert abs(stats['signed_volume_mm3']-area*10)<.02;results.append(dict(stage=s['stage'],mesh=stats,independent_area_mm2=float(area)))
assert recipe(docs[1])['feature']['constraints'][0]['id']==recipe(docs[2])['feature']['constraints'][0]['id'] and recipe(docs[5])['feature']['constraints'][0]['id']==recipe(docs[6])['feature']['constraints'][0]['id']
for reopened,target,source in zip(ui['reopened'],[7,8,9,10],[2,3,4,6]):
 assert canonical(docs[target])==canonical(docs[source]);rules=recipe(docs[source])['feature']['constraints'];assert [x['id'] for x in reopened['definitions']]==[r['id'] for r in rules];points=np.array([[float(x),-float(y)] for x,y in (pair.split(',') for pair in reopened['plot'].split())]);assert np.max(abs(points-np.array(recipe(docs[source])['points'])))<1e-8
assert ui['sameLine']['error']=='Choose two different sketch lines.' and ui['sameLine']['plotUnchanged'] and [x['value'] for x in ui['lineOptions']]==['0','1','2','3'] and ui['lastLineDownValue']=='3'
assert len(ui['invalidAngles'])==2 and all(x['error'] and x['plotUnchanged'] for x in ui['invalidAngles']) and ui['angleXLabelBefore']=='-10' and ui['betweenLabelBefore']=='120'
report=dict(status='Pass',signed_X_angles_minus10_and_minus20=True,opposite_lines_stay_parallel_under_driving20degree_angle=True,adjacent_lines_perpendicular=True,directed_angle_between120_then110_uses_zero_to180_convention=True,same_line_pair_rejected_without_movement=True,native_line_selector_cannot_exceed_four_valid_indices=True,invalid_minus1_and181_keep_last_outline=True,same_constraint_ids_retained_on_value_edits=True,all_four_relation_types_actual_reopen_cancel_source_exact=True,all_six_actual_meshes_closed_and_match_independent_vertices_area=True,unrelated_source_and_original_paint_exact=True,range_message_before='Generic millimetre/workspace feedback on angular bounds; separate wording fix pending',meshes=results,hashes=hashes)
(out/'angles202-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
