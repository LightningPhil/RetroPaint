"""Independent label hit identity, unchanged constraint definitions and rebuilt50mm mesh."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-labels200';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
ui=json.loads((out/'labels200-ui.json').read_text(encoding='utf-8'));docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(5)];index=next(i for i,l in enumerate(docs[0]['layers']) if 'cad'in l)
def recipe(doc):return doc['layers'][index]['cad']['bodies'][0]['solid']
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
assert ui['beforeClick']['requested']!=ui['beforeClick']['selected'] and ui['beforeClick']['value']=='0'
assert 'index-DnD9faHw.js'in ui['build'] and len(ui['hits'])==4
ids=[x['id'] for x in ui['after']]
for layout in ui['hits']:
 assert [x['requested'] for x in layout['hits']]==ids and all(x['requested']==x['selected'] for x in layout['hits'])
 for i,first in enumerate(layout['rects']):
  for second in layout['rects'][i+1:]:
   a,b=first['rect'],second['rect'];assert a['right']<=b['left'] or b['right']<=a['left'] or a['bottom']<=b['top'] or b['bottom']<=a['top']
assert ui['editThroughLabel']=={'selected':ids[0],'before':'45'} and ui['updatedLabels'][0]=='Line 1 · 50 mm' and ui['reopenedSelection']=={'id':ids[0],'value':'50'} and ui['viewportReset']==[1757,853]
base=recipe(docs[0]);r=recipe(docs[1]);expected=copy.deepcopy(docs[0]);recipe(expected)['points']=r['points'];recipe(expected)['feature']['constraints'][0]['value']=50
assert canonical(expected)==canonical(docs[1])==canonical(docs[3])==canonical(docs[4]) and canonical(docs[2])==canonical(docs[0]);assert r['feature']['constraints'][0]['id']==ids[0] and len(r['feature']['constraints'])==5
p=np.array(r['points']);e=np.roll(p,-1,axis=0)-p;assert abs(np.linalg.norm(e[0])-50)<.001 and abs(e[0,1])<.001 and abs(math.degrees(math.atan2(e[1,1],e[1,0]))-60)<.001
raw=retain(prefix+'-3d-mm.stl');assert raw==retain(prefix+'-3d-mm (1).stl');tri=read_binary(raw);stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==2
wanted=np.array([[x,y,z] for z in [0,10] for x,y in p]);actual=np.unique(tri.reshape(-1,3),axis=0);assert len(actual)==8 and np.min(np.linalg.norm(actual[:,None]-wanted[None,:],axis=2),axis=1).max()<.00001
area=abs(np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1]))/2;assert abs(stats['signed_volume_mm3']-area*10)<.02
report=dict(status='Pass',confirmed_before45mm_centre_click_selected_other0degree_rule=True,fixed_every_label_hits_own_definition_across_four_native_layouts=True,measured_text_rectangles_separate=True,label45_to50_updates_only_intended_constraint=True,all_other_ids_and_relations_retained=True,rebuilt_mesh_has50mm_line_and60degree_neighbour=True,mesh_matches_independent_outline_area=True,single_undo_redo_and_actual_reopen_exact=True,both_actual_stls_byte_exact=True,original_paint_and_unrelated_source_exact=True,default_viewport_restored=True,mesh=stats,independent_area_mm2=float(area),hashes=hashes)
(out/'labels200-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['mesh','hashes']},indent=2))
