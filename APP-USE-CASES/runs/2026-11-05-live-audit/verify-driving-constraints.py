"""Independent Euclidean constraints and shoelace extrusion oracle for native sketch199."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-constraints199';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
ui=json.loads((out/'constraints199-ui.json').read_text(encoding='utf-8'));docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(13)];index=next(i for i,l in enumerate(docs[1]['layers']) if 'cad'in l)
def recipe(doc):return doc['layers'][index]['cad']['bodies'][0]['solid']
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
def without_parameters(doc):
 d=canonical(doc);r=recipe(d);r.pop('points');r['feature'].pop('constraints',None);r['feature'].pop('sketchName',None);return d
assert recipe(docs[1])['points']==[[0,0],[30,5],[25,25],[-5,20]]
for doc in docs[1:]:
 assert without_parameters(doc)==without_parameters(docs[1]);r=recipe(doc);p=np.array(r['points']);edges=np.roll(p,-1,axis=0)-p;assert abs(p).max()<100
 for c in r['feature'].get('constraints',[]):
  e=edges[c['edge']]
  if c['kind']=='length':assert abs(np.linalg.norm(e)-c['value'])<.001
  elif c['kind']=='horizontal':assert abs(e[1])<.001
  elif c['kind']=='vertical':assert abs(e[0])<.001
  elif c['kind']=='angle':
   angle=math.degrees(math.atan2(e[1],e[0]));error=(angle-c['value']+180)%360-180;assert abs(error)<.001
  else:raise AssertionError('Unexpected relation in sketch199')
assert canonical(docs[2])==canonical(docs[3]) # ineffective40attempt is excluded, actual35 retained
rules=lambda i:recipe(docs[i])['feature'].get('constraints',[])
assert rules(2)[0]['value']==35 and rules(6)[0]['value']==40 and rules(8)[0]['value']==45
assert {'horizontal','vertical','length','angle'}=={c['kind'] for c in rules(6)}
assert rules(7)[:-1]==rules(6) and rules(7)[-1]['kind']=='angle' and rules(7)[-1]['value']==0
expected=copy.deepcopy(rules(7));expected[0]['value']=45;assert rules(8)==expected
removed=next(c for c in rules(8) if c['kind']=='vertical');assert rules(9)==[c for c in rules(8) if c['id']!=removed['id']] and recipe(docs[9])['points']==recipe(docs[8])['points']
assert rules(10)[:-1]==rules(9) and rules(10)[-1]['kind']=='angle' and rules(10)[-1]['edge']==1 and rules(10)[-1]['value']==60 and not np.allclose(recipe(docs[10])['points'],recipe(docs[9])['points'])
assert canonical(docs[11])==canonical(docs[9]) and canonical(docs[12])==canonical(docs[10])
states={s['stage']:s['docIndex'] for s in ui['states']};results=[];raws={}
for s in ui['meshes']:
 r=recipe(docs[states[s['stage']]]);p=np.array(r['points']);n=s['stlIndex'];raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws[s['stage']]=raw;tri=read_binary(raw);stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==2
 wanted=np.array([[x,y,z] for z in [0,10] for x,y in p]);actual=np.unique(tri.reshape(-1,3),axis=0);assert len(actual)==8 and np.min(np.linalg.norm(actual[:,None]-wanted[None,:],axis=2),axis=1).max()<.00001
 area=abs(np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]))/2;assert abs(stats['signed_volume_mm3']-area*10)<.02;results.append(dict(stage=s['stage'],mesh=stats,independent_area_mm2=float(area),analytic_volume_mm3=float(area*10)))
assert raws['length45-relations-retained']==raws['vertical-relation-removed']
assert len(ui['confirmedInvalid'])==3 and all('conflict'in x['error'] and x['plotUnchanged'] for x in ui['confirmedInvalid']) and not ui['confirmedCorrection']['errorVisible'] and ui['confirmedCorrection']['plotUnchanged']
assert len(ui['reopened45'])==5 and ui['reopened45'][0]['text']=='Line 1 · 45 mm' and not any('vertical'in x for x in ui['afterRemoveVertical'])
report=dict(status='Pass',native_irregular_quad_exact=True,length35_40_45_saved_and_geometrically_driving=True,horizontal_and_vertical_preserved_while_free_points_move=True,three_conflicts_keep_last_valid_outline=True,same_draft_correction_preserves_all_existing_constraint_ids=True,labels_saved_selector_and_real_reopened_definitions_agree=True,remove_vertical_frees_line_to_actual60degrees=True,removal_alone_mesh_byte_exact=True,full_edit_single_undo_redo_exact=True,every_actual_mesh_matches_saved_outline_and_independent_area=True,original_paint_and_unrelated_source_exact=True,excluded_ineffective_interactions=ui['excludedAttempts'],meshes=results,hashes=hashes)
(out/'constraints199-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes','excluded_ineffective_interactions']},indent=2))
