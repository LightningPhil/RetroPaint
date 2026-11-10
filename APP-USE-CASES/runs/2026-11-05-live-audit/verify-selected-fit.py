"""Independent saved-camera framing of selected, empty and hidden scopes in both projections."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from stl_oracle import read_binary
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};results={}
def retain(n):
 name='mouse-audit-fit188'+(f' ({n})' if n else '')+'.retropaint';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
base=retain(0);index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');d['layers'][index]['cad'].pop('view');return d
moving=np.unique(read_binary((out/'mouse-audit-printer183-fixed-3d-mm.stl').read_bytes()).reshape(-1,3),axis=0);all_vertices=np.unique(read_binary((out/'mouse-audit-printer183-fixed-3d-mm (1).stl').read_bytes()).reshape(-1,3),axis=0);small=np.array(sorted(set(map(tuple,all_vertices))-set(map(tuple,moving))));assert len(small)==8
def project(points,v):
 direction=np.array(v['position'])-v['target'];distance=np.linalg.norm(direction);direction/=distance;right=np.cross(v['up'],direction);right/=np.linalg.norm(right);up=np.cross(direction,right);relative=points-np.array(v['target']);xy=np.column_stack([relative@right/(4/3),relative@up])*2/v['span']
 if v['projection']=='perspective':xy*=distance/(distance-relative@direction)[:,None]
 return xy
ui=json.loads((out/'fit188-ui.json').read_text(encoding='utf-8'));assert len(ui['samples'])==7
for s in ui['samples']:
 d=retain(s['index']);expected=copy.deepcopy(base);label=s['label'];hidden=label.startswith('hidden');selected=label.startswith('small');expected['layers'][index]['cad']['bodies'][1]['visible']=not hidden;assert canonical(d)==canonical(expected);v=d['layers'][index]['cad']['view'];assert v['projection']==s['projection'];points=small if selected else moving if hidden else all_vertices;assert np.max(np.abs(project(points,v)))<1
 if selected:assert np.allclose(v['target'],[100,50,30]) and np.max(np.abs(project(moving,v)))>1
 elif hidden:assert not np.allclose(v['target'],[100,50,30])
 results[label]=dict(projection=v['projection'],target_mm=v['target'],span_mm=v['span'],all_intended_vertices_inside=True,source_index=s['index'])
for projection in ['perspective','orthographic']:assert results['small-'+projection]['span_mm']<results['hidden-'+projection]['span_mm']<results['empty-'+projection]['span_mm']
report=dict(status='Pass',both_projections_selected_empty_hidden_scopes=True,small_selection_excludes_distant_large_piece_from_fit=True,hidden_selection_falls_back_to_visible_model=True,all_intended_world_vertices_inside_frame=True,only_intentional_visibility_and_camera_change=True,original_model_and_paint_restored=True,results=results,immediate_ARIA_correction=ui['excludedNote'],hashes=hashes)
(out/'fit188-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['hashes','results']},indent=2))
