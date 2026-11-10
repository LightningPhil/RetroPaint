"""Independent matrix/world-bound printer reports, scope/visibility and actual STL placement."""
from pathlib import Path
import copy,hashlib,itertools,json
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};metrics={}
def retain(name,mesh=False):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return read_binary(raw) if mesh else json.loads(raw)
base=retain('mouse-audit-printer183-fixed.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
assert canonical(retain('mouse-audit-printer183-fixed (1).retropaint'))==canonical(base)
local=np.vstack([np.array([[-10,-5,-5],[10,-5,-5],[-10,-5,25],[-10,5,-5],[10,5,-5],[-10,5,25]]),np.array(list(itertools.product([-2,2],repeat=3)))+[15,8,22]])
x,y,z=np.deg2rad([20,30,40]);rx=np.array([[1,0,0],[0,np.cos(x),-np.sin(x)],[0,np.sin(x),np.cos(x)]]);ry=np.array([[np.cos(y),0,np.sin(y)],[0,1,0],[-np.sin(y),0,np.cos(y)]]);rz=np.array([[np.cos(z),-np.sin(z),0],[np.sin(z),np.cos(z),0],[0,0,1]])
selected=(local*[1.5,.75,2])@(rz@ry@rx).T+[-13,8,-7];all_vertices=np.vstack([selected,np.array(list(itertools.product([-5,5],[-10,10],[-15,15])))+[100,50,30]])
ui=json.loads((out/'printer183-ui.json').read_text(encoding='utf-8'));assert len(ui['samples'])==9 and 'Oversize axes' not in ui['before']
for sample in ui['samples']:
 vertices=selected if sample['scope']=='selection' or sample['label']=='fits-hidden-reference' else all_vertices;size=vertices.max(axis=0)-vertices.min(axis=0);axes=[name for name,v,bed in zip('XYZ',size,sample['bed']) if v>bed+.001];report=sample['report'];volume,triangles=(6894,20) if len(vertices)==14 else (12894,32)
 assert report.startswith(' × '.join(f'{v:.2f}' for v in size)+' mm') and f'{volume/1000:.2f} cm³ · {triangles} triangles' in report
 if axes:assert 'Oversize axes: '+', '.join(axes) in report
 else:assert 'Fits the entered build volume' in report and 'Oversize axes' not in report
 assert ('Below Z = 0' not in report)==(sample['label']=='fits-all-on-bed')
for i,(label,vertices,volume) in enumerate([('selection',selected,6894),('all',all_vertices,12894),('all-on-bed',all_vertices+[0,0,-all_vertices[:,2].min()],12894)]):
 suffix=f' ({i})' if i else '';tri=retain('mouse-audit-printer183-fixed-3d-mm'+suffix+'.stl',True);stats=measure(tri);actual=np.unique(tri.reshape(-1,3),axis=0);assert len(actual)==len(vertices) and np.min(np.linalg.norm(actual[:,None]-vertices[None,:],axis=2),axis=1).max()<.00001
 assert abs(stats['signed_volume_mm3']-volume)<.003 and all(c['signed_volume_mm3']>0 and c['euler']==2 for c in stats['components']);metrics[label]=stats
report=dict(status='Pass',native_scope_and_axis_matrix=9,independent_world_vertices=True,all_oversize_axes_named=True,scope_and_visibility_change_report_and_actual_mesh=True,reported_volume_and_triangle_count_match_actual_mesh=True,bed_placement_only_translates_printed_mesh=True,whole_saved_source_and_paint_unchanged=True,meshes=metrics,excluded=ui['excluded'],unmapped_export=ui['unmappedExport'],hashes=hashes)
(out/'printer183-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes','excluded']},indent=2))
