"""Real imported shell, rejected detailed precision, supported detailed Boolean and source recovery."""
from pathlib import Path
import copy,hashlib,json,struct
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name,document=True):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw) if document else raw
def canonical(d):
 d=copy.deepcopy(d);d.pop('active')
 for l in d['layers']:
  if 'cad'in l:l.pop('image')
 return d
complex_original=retain('mouse-audit-stl180 (3).retropaint');assert canonical(retain('mouse-audit-stl180 (4).retropaint'))==canonical(complex_original)
before=retain('mouse-audit-precision181.retropaint');index=next(i for i,l in enumerate(before['layers']) if 'cad'in l);after=retain('mouse-audit-precision181 (1).retropaint');bodies=before['layers'][index]['cad']['bodies'];cut=after['layers'][index]['cad']['bodies'][0];assert cut['solid']==dict(kind='boolean',operation='subtract',children=bodies)
expected=copy.deepcopy(before);expected['layers'][index]['cad']['bodies']=[cut];assert canonical(after)==canonical(expected)
assert canonical(retain('mouse-audit-precision181 (2).retropaint'))==canonical(before)
moved=retain('mouse-audit-precision181 (3).retropaint');expected=copy.deepcopy(before);expected['layers'][index]['cad']['bodies'][0]['position']=[12,-5,10];assert canonical(moved)==canonical(expected)
assert canonical(retain('mouse-audit-precision181 (4).retropaint'))==canonical(before)
raw=retain('mouse-audit-precision181-3d-mm.stl',False);count=struct.unpack_from('<I',raw,80)[0];assert count==200016 and len(raw)==84+50*count
records=np.frombuffer(raw,dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]),offset=84);tri=records['vertices'].astype(np.float64);vertices,inverse=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);ids=inverse.reshape(-1,3);directed=np.concatenate([ids[:,[0,1]],ids[:,[1,2]],ids[:,[2,0]]]);edges,edge_ids,counts=np.unique(np.sort(directed,axis=1),axis=0,return_inverse=True,return_counts=True);assert np.all(counts==2) and np.all(np.bincount(edge_ids,weights=np.where(directed[:,0]<directed[:,1],1,-1))==0);assert len(vertices)-len(edges)+count==0
volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);prism=json.loads((out/'stl180-verification.json').read_text())['signed_volume_mm3'];assert abs(volume-(prism-12000))<.1
assert np.array_equal(tri.min(axis=(0,1)),[-1000,-1000,0]) and np.array_equal(tri.max(axis=(0,1)),[1000,1000,10])
assert np.all(np.einsum('ij,ij->i',np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),records['normal'])>0)
simple=retain('mouse-audit-precision182 (1).retropaint');shell_doc=retain('mouse-audit-precision182 (2).retropaint');original=simple['layers'][index]['cad']['bodies'][0];shell=shell_doc['layers'][index]['cad']['bodies'][0];assert shell['solid']['kind']=='shell' and shell['solid']['thickness']==2 and shell['solid']['faces']==[] and shell['solid']['source']==original
expected=copy.deepcopy(simple);expected['layers'][index]['cad']['bodies'][0]=shell;assert canonical(expected)==canonical(shell_doc);assert canonical(retain('mouse-audit-precision182 (3).retropaint'))==canonical(simple)
stats=measure(read_binary(retain('mouse-audit-precision182-3d-mm.stl',False)));assert stats['signed_volume_mm3']==3904 and sorted(c['signed_volume_mm3'] for c in stats['components'])==[-4096,8000];assert stats['bounds_mm']==[[-10,-10,0],[10,10,20]]
ui=json.loads((out/'precision181-ui.json').read_text(encoding='utf-8'));assert all('too detailed' in ui[k] and 'Subtract' in ui[k] for k in ['edge','shell'])
report=dict(status='Pass',simple_import_real_shell=dict(thickness_mm=2,outer_volume=8000,inner_cavity_volume=4096,material_volume=3904,original_mesh_recipe_retained=True),complex_precision_rejection_source_exact=True,detailed200000_triangle_boolean_cut=dict(output_triangles=count,closed_edges=True,euler=0,through_hole_volume_mm3=12000,material_volume_mm3=volume),move_and_undo_source_exact=True,cut_and_shell_one_step_undo_exact=True,other_model_and_paint_exact=True,excluded='Earlier stl180 move attempt did not commit: saved (5) matches original and Undo (6) removed import. Excluded; precision181 actual move/Undo independently verified instead. Long detailed Boolean eventually completed; no timeout or defect inferred.',hashes=hashes)
(out/'precision181-182-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
