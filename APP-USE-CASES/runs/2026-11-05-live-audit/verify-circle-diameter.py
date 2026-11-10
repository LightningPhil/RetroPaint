"""Ellipse-to-circle driver, exact96gon section, invalid diameters and stale-control guard."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-diameter201';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
ui=json.loads((out/'diameter201-ui.json').read_text(encoding='utf-8'));docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(5)];index=next(i for i,l in enumerate(docs[0]['layers']) if 'cad'in l)
def recipe(doc):return doc['layers'][index]['cad']['bodies'][0]['solid']
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
def plot(text):return np.array([[float(x),-float(y)] for x,y in [pair.split(',') for pair in text.split()]])
theta=np.arange(96)*2*math.pi/96;ellipse=np.column_stack([30+10*np.cos(theta),10+5*np.sin(theta)]);assert np.max(abs(plot(ui['ellipse'])-ellipse))<1e-10
results=[];raws=[];id0=recipe(docs[1])['feature']['constraints'][0]['id']
for mesh,docid,diameter in zip(ui['meshes'],[1,2,4],[24,30,30]):
 doc=docs[docid];r=recipe(doc);wanted2=np.column_stack([30+diameter/2*np.cos(theta),10+diameter/2*np.sin(theta)]);assert np.max(abs(np.array(r['points'])-wanted2))<1e-10 and r['height']==10 and r['taper']==1 and r['twist']==0 and r['feature']['sketch']=='circle'
 assert r['feature']['constraints']==[{'id':id0,'kind':'diameter','value':diameter}]
 expected=copy.deepcopy(docs[0]);expected['layers'][index]['cad']['bodies']=doc['layers'][index]['cad']['bodies'];assert canonical(expected)==canonical(doc)
 n=mesh['stlIndex'];raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws.append(raw);tri=read_binary(raw);stats=measure(tri);actual=np.unique(tri.reshape(-1,3),axis=0);wanted=np.array([[x,y,z] for z in [0,10] for x,y in wanted2]);assert len(actual)==192 and np.min(np.linalg.norm(actual[:,None]-wanted[None,:],axis=2),axis=1).max()<.00001
 polygon_area=96/2*(diameter/2)**2*math.sin(2*math.pi/96);continuous=math.pi*(diameter/2)**2*10
 assert len(stats['components'])==1 and stats['components'][0]['euler']==2 and abs(stats['signed_volume_mm3']-polygon_area*10)<.02 and abs(stats['signed_volume_mm3']-continuous)/continuous<.00072
 assert np.max(abs(np.array(stats['bounds_mm'])-[[30-diameter/2,10-diameter/2,0],[30+diameter/2,10+diameter/2,10]]))<.001
 results.append(dict(stage=mesh['stage'],mesh=stats,exact_polygon_volume_mm3=polygon_area*10,continuous_volume_mm3=continuous))
assert raws[1]==raws[2] and canonical(docs[1])==canonical(docs[3]) and canonical(docs[2])==canonical(docs[4])
expected=copy.deepcopy(docs[1]);recipe(expected)['points']=recipe(docs[2])['points'];recipe(expected)['feature']['constraints'][0]['value']=30;recipe(expected)['feature']['sketchName']='circle sketch';assert canonical(expected)==canonical(docs[2])
assert ui['circleKinds']==ui['historyCircleKinds']==['diameter'] and 'diameter'not in ui['polygonKindsAfterCircle'] and len(ui['polygonKindsAfterCircle'])==7
assert ui['invalid'][0]['error'] and ui['invalid'][0]['ellipseUnchanged'] and ui['invalid'][0]['pieces']=='0 pieces' and 'conflict'in ui['invalid'][1]['error'] and ui['invalid'][1]['roundUnchanged']
assert ui['editedViaLabel']=={'id':id0,'before':'24'} and ui['saved30']==['Ø 30 mm'];fields={x['id']:x['value'] for x in ui['reopenedGeometry']};assert [fields['cadFeatureSketch'+k] for k in ['X','Y','Width','Height']]==['30','10','30','30']
guard=[json.loads(retain(prefix+'-polygon-guard'+(f' ({i})' if i else '')+'.retropaint')) for i in range(2)];assert canonical(guard[0])==canonical(guard[1])
report=dict(status='Pass',native20x10ellipse_centre30_10=True,diameter24_then30_drives_round96point_section=True,exact_physical_diameters_and_centres=True,all_three_meshes_closed_and_exact_polygon_volume=True,continuous_circle_error_within_predeclared_point072percent_budget=True,zero_and_conflicting_diameters_keep_last_outline=True,single_constraint_id_persists_through_label_edit=True,one_undo_redo_and_reopen_fields_exact=True,polygon_after_circle_has_no_diameter_control_and_source_unchanged=True,original_paint_and_unrelated_source_exact=True,meshes=results,hashes=hashes)
(out/'diameter201-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
