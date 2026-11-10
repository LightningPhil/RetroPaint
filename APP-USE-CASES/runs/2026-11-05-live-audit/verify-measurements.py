"""Independent cube diagonal, point resets and known outward face-normal dot products."""
from pathlib import Path
import copy,hashlib,json,math,re
import numpy as np
from stl_oracle import measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};docs={}
for n in range(1,6):
 name=f'mouse-audit-measure189 ({n}).retropaint';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();docs[n]=json.loads(raw)
index=next(i for i,l in enumerate(docs[1]['layers']) if 'cad'in l);cube=docs[1]['layers'][index]['cad']['bodies'][0];mesh=cube['solid'];stats=measure(np.array(mesh['positions']).reshape(-1,3)[np.array(mesh['indices']).reshape(-1,3)]);assert stats['bounds_mm']==[[-10,-10,0],[10,10,20]] and stats['signed_volume_mm3']==8000
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
assert docs[1]==docs[2] and canonical(docs[3])==canonical(docs[1]);assert docs[4]['layers'][index]['cad']['bodies'][0]==cube and canonical(docs[5])==canonical(docs[4])
wedge=docs[4]['layers'][index]['cad']['bodies'][1];assert wedge['position']==[25,0,10] and wedge['scale']==[1,1,1] and wedge['rotation']==[0,0,0] and wedge['solid']['shape']=='wedge' and wedge['solid']['size']==[20,20,20]
ui=json.loads((out/'measure189-ui.json').read_text(encoding='utf-8'));numbers=lambda s:list(map(float,re.findall(r'[-+]?\d+(?:\.\d+)?',s)))
first=numbers(ui['diagonalFirst'].splitlines()[0]);d=numbers(ui['diagonal']);assert first==[-10,-10,0] and 'Vertex snapped' in ui['diagonalFirst'] and d[1:4]==[20,20,20] and abs(d[0]-math.sqrt(1200))<.0005
assert ui['thirdStartsNew'].startswith('Point:') and 'Δ' not in ui['thirdStartsNew'] and ui['clear']=='Pick a first point.' and ui['orbitBetweenPicks']==ui['oppositeFirst']
normals={'same-top-face':([0,0,1],[0,0,1]),'adjacent-top-front':([0,0,1],[0,-1,0]),'opposite-front-back':([0,-1,0],[0,1,0]),'cube-top-wedge-slope':([0,0,1],[1,0,1])};results={}
for sample in ui['measurements']:
 a=np.array(numbers(sample['first'].splitlines()[0]));values=numbers(sample['result']);distance=values[0];delta=np.array(values[1:4]);b=a+delta;reported=values[4];n,m=map(lambda v:np.array(v,dtype=float),normals[sample['label']]);expected=math.degrees(math.acos(np.clip(np.dot(n,m)/np.linalg.norm(n)/np.linalg.norm(m),-1,1)));assert abs(reported-expected)<.005 and abs(distance-np.linalg.norm(delta))<.0015
 label=sample['label']
 if label=='same-top-face':assert a[2]==b[2]==20
 elif label=='adjacent-top-front':assert a[2]==20 and abs(b[1]+10)<.001
 elif label=='opposite-front-back':assert a[1]==-10 and b[1]==10 and distance==20
 else:assert a[2]==20 and abs(b[0]+b[2]-35)<.002
 results[label]=dict(first_mm=a.tolist(),second_mm=b.tolist(),distance_mm=distance,normal_angle_degrees=reported)
report=dict(status='Pass',cube_edge_mm=20,opposite_corner_distance_mm=d[0],analytic_diagonal_mm=math.sqrt(1200),vertex_delta_mm=d[1:4],third_pick_starts_new=True,clear_resets=True,orbit_between_picks_does_not_pick=True,known_normal_angles=[0,45,90,180],face_normal_not_free_three_point_angle=True,source_geometry_and_paint_exact=True,diagonal_and_clear_cached_PNG_also_exact=True,measurements=results,hashes=hashes)
(out/'measure189-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['measurements','hashes']},indent=2))
