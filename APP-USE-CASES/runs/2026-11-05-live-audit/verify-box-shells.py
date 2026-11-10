"""Independent exact20mm box/3mm shell cavity and multiple-opening oracle."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-shell210';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(9)]
def body(d):return next(l['cad']['bodies'][0] for l in d['layers'] if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
assert canonical(docs[1])==canonical(docs[6]) and canonical(docs[2])==canonical(docs[4])==canonical(docs[7]) and canonical(docs[3])==canonical(docs[5])==canonical(docs[8])
for d in docs:
 expected=copy.deepcopy(docs[0]);next(l for l in expected['layers'] if 'cad'in l)['cad']['bodies']=[body(d)];assert canonical(expected)==canonical(d)
for i,count in [(1,1),(2,0),(3,2)]:
 s=body(docs[i])['solid'];assert s['kind']=='shell' and s['thickness']==3 and len(s['faces'])==count
 source=copy.deepcopy(body(docs[0]));source['position']=[0,0,0];assert s['source']==source
 normals=sorted(f['normal'] for f in s['faces']);assert normals==([[0,0,1]] if i==1 else [] if i==2 else [[0,-1,0],[0,0,1]])
results=[]
for n,volume in [(0,4668),(1,5256),(2,3954)]:
 tri=read_binary(retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl'));stats=measure(tri);assert abs(stats['signed_volume_mm3']-volume)<.02
 assert np.max(abs(np.array(stats['bounds_mm'])-[[-10,-10,0],[10,10,20]]))<.001
 assert len(stats['components'])==(2 if n==1 else 1) and all(c['euler']==2 for c in stats['components'])
 if n==1:assert sorted(round(c['signed_volume_mm3'],3) for c in stats['components'])==[-2744,8000]
 vertical=ray_y(tri[:,:,[0,2,1]],.31,.57);assert vertical==([0,3,17,20] if n==1 else [0,3])
 side=ray_y(tri[:,:,[0,2,1]],8,.57);assert side==[0,20]
 horizontal=ray_y(tri,.31,10);assert horizontal==([7,10] if n==2 else [-10,-7,7,10])
 assert ray_y(tri,.31,1)==[-10,10]
 results.append(dict(index=n,mesh=stats,analytic_volume_mm3=volume,centre_vertical_ray=vertical,side_vertical_ray=side,mid_height_y_ray=horizontal,floor_y_ray=[-10,10]))
ui=json.loads((out/'shell210-ui.json').read_text(encoding='utf-8'));assert '2 faces left open' in next(s for s in ui['states'] if s['stage']=='two-adjacent-openings')['text']
report=dict(status='Pass',cases=['FEATURE-016','FEATURE-017'],exact_cube20_wall3_floor3_top_open_volume4668=True,sealed_cavity_volume5256_with_negative2744_inner_component=True,two_adjacent_openings_volume3954_and_real_cavity=True,all_outer_bounds_preserved_and_closed_oriented=True,independent_rays_distinguish_openings_and_internal_voids=True,two_openings_undo_redo_source_exact=True,all_three_actual_projects_reopened_and_cancel_exact=True,paint_and_unrelated_source_exact=True,meshes=results,hashes=hashes)
(out/'shell210-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
