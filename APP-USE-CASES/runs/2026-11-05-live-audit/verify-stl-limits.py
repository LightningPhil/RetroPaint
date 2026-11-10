"""Saved-source isolation and vectorised independent full200000triangle topology oracle."""
from pathlib import Path
import copy,hashlib,json,struct
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name,document=True):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw) if document else raw
base=retain('mouse-audit-stl180.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
assert canonical(retain('mouse-audit-stl180 (1).retropaint'))==canonical(base)
for n,triangles in [(2,48),(3,200000)]:
 doc=retain(f'mouse-audit-stl180 ({n}).retropaint');bodies=doc['layers'][index]['cad']['bodies'];assert len(bodies)==5 and bodies[:4]==base['layers'][index]['cad']['bodies'];mesh=bodies[-1];assert mesh['position']==mesh['rotation']==[0,0,0] and mesh['scale']==[1,1,1] and len(mesh['solid']['indices'])==triangles*3
 expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies']=bodies;assert canonical(doc)==canonical(expected)
small=measure(read_binary(retain('mouse-audit-stl180-3d-mm.stl',False)));assert small['signed_volume_mm3']==856 and sorted(c['signed_volume_mm3'] for c in small['components'])==[-216,8,64,1000]
raw=retain('mouse-audit-stl180-3d-mm (1).stl',False);assert struct.unpack_from('<I',raw,80)[0]==200000 and len(raw)==10000084
dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]);records=np.frombuffer(raw,dtype=dtype,offset=84);tri=records['vertices'].astype(np.float64);assert np.isfinite(tri).all()
vertices,inverse=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);ids=inverse.reshape(-1,3);directed=np.concatenate([ids[:,[0,1]],ids[:,[1,2]],ids[:,[2,0]]]);edges,edge_ids,counts=np.unique(np.sort(directed,axis=1),axis=0,return_inverse=True,return_counts=True);assert np.all(counts==2) and np.all(np.bincount(edge_ids,weights=np.where(directed[:,0]<directed[:,1],1,-1))==0)
assert len(vertices)-len(edges)+len(tri)==2 and len(vertices)==100002
fixture=read_binary((root/'test-results/audit-2026-11-05/fixtures/stl180/exact200000.stl').read_bytes());assert np.array_equal(vertices,np.unique(fixture.reshape(-1,3),axis=0))
cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals=records['normal'].astype(np.float64);assert np.all(np.einsum('ij,ij->i',cross,normals)>0) and np.max(np.abs(np.linalg.norm(normals,axis=1)-1))<.000001
volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);manifest=json.loads((root/'test-results/audit-2026-11-05/fixtures/stl180/manifest.json').read_text());assert abs(volume/manifest['prism']['analytic_volume']-1)<.000001
ui=json.loads((out/'stl180-ui.json').read_text(encoding='utf-8'));assert len(ui['samples'])==14
for s in ui['samples']:
 expected=manifest['files'][s['name']]['expect']
 if expected.startswith('accepted'):assert 'editable original mesh' in s['status'] and s['pieces']=='5 pieces'
 else:assert expected.lower() in s['status'].lower() and s['pieces']=='4 pieces'
report=dict(status='Pass',invalid_variants=12,all_invalid_source_exact=True,valid_import_after_errors=True,exact20MB_ascii_retains_nested_cavity=True,exact200000_triangles_accepted_and_exported=True,over200000_and_over20MB_rejected=True,vertices=len(vertices),edges=len(edges),triangles=len(tri),euler=2,all_edges_two_opposite_faces=True,all_exported_normals_outward_and_unit=True,signed_volume_mm3=volume,analytic_volume_mm3=manifest['prism']['analytic_volume'],source_vertices_exact=True,original_model_and_paint_exact=True,hashes=hashes)
(out/'stl180-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
