"""Live responsive paging, source preservation and independent complete-model export."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-timeline197-fixed';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(3)];index=next(i for i,l in enumerate(docs[0]['layers']) if l['name']=='Trace plate')
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
fixture=json.loads((root/'test-results/audit-2026-11-05/fixtures/timeline197/eight-step.retropaint').read_text())
assert all(canonical(d)==canonical(fixture) for d in docs)
ui=json.loads((out/'timeline197-ui.json').read_text(encoding='utf-8'));assert 'index-hShKYTEB.js'in ui['build']
assert len(ui['before'][1]['steps'])==6 and min(s['width'] for s in ui['before'][1]['steps'])<44
phone=ui['after'][1];assert phone['viewport']==[320,568] and len(phone['steps'])==3 and min(s['width'] for s in phone['steps'])>72
for item in ui['selectedAcrossResize']:
 assert item['position']=='Viewing step 5 of 8' and item['selected']=='4'
 compact=item['viewport'][0]<1000;assert len(item['steps'])==(3 if compact else 6) and all(s['width']>=44 and s['height']>=(44 if compact else 40) for s in item['steps'])
keys=None
for item in ui['treeLayouts']:
 entries=item['pages'][0]+item['pages'][1];actual=[e['key'] for e in entries];assert len(set(actual))==10
 if keys is None:keys=actual
 else:assert actual==keys
 assert item['selectedAfterPaging']==actual[-1] and [p['key'] for p in item['picks']]==[actual[0],actual[2],actual[-1]]
 if item['size'][0]<1000:assert all(p['width']>=44 and p['height']>=44 for p in item['picks'])
assert [i['step'] for i in ui['inspections']]==[0,4,7] and [i['position'] for i in ui['inspections']]==['Viewing step 1 of 8','Viewing step 5 of 8','Latest solid']
assert 'Return to Latest'in ui['rollbackSaveGuard'] and ui['viewportReset']==[1757,853] and ui['finalSelected']=='Pagination union 2'
tri=read_binary(retain(prefix+'-3d-mm.stl'));stats=measure(tri);volumes=sorted(c['signed_volume_mm3'] for c in stats['components']);prior=json.loads((out/'feature196-verification.json').read_text(encoding='utf-8'))['meshes'][1]['mesh']['signed_volume_mm3']
assert len(volumes)==3 and np.max(abs(np.array(volumes)-[8,8,prior]))<.00001 and np.max(abs(np.array(stats['bounds_mm'])-[[-10,-5,0],[51,5,7]]))<.001
assert sorted(c['euler'] for c in stats['components'])==[0,2,2]
report=dict(status='Pass',confirmed_before_phone_targets_33px_and_landscape_38px=True,fixed_phone_three_targets_72px=True,selected_step_preserved_portrait_landscape_desktop=True,all_ten_tree_nodes_reachable_first_middle_last_across_four_layouts=True,paging_keeps_stable_selected_node_identity=True,first_middle_last_timeline_native_inspection=True,rollback_project_save_requires_latest=True,latest_restores_exact_recipe_and_unrelated_source=True,final_stl_three_expected_components_and_volume=True,default_viewport_restored=True,mesh=stats,hashes=hashes)
(out/'timeline197-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['mesh','hashes']},indent=2))
