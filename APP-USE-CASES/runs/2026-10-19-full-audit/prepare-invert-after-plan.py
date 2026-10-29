from pathlib import Path
from datetime import datetime,timezone
from itertools import combinations,product
import json
root=Path(__file__).resolve().parent;read=lambda p:json.loads((root/p).read_text(encoding='utf-8'));target=root/'fixtures/PAINT-017-after-plan.json';assert not target.exists();before=read('fixtures/PAINT-017-plan.json');rows=[];viewports=[[1280,720],[320,568],[390,844],[844,390]]
for row in before['before_rows']:rows.append(dict(**row,kind='core',gestures=[dict(label='first',points=row['points']),dict(label='second',points=row['points'])]))
boundary=[]
for index,item in enumerate(read('fixtures/PAINT-001-plan.json')['rows']):
    row=dict(id='b'+str(index+1),viewport=item['viewport'],size=item['size'],strength=item['strength'],kind='boundary',gestures=[dict(label='dense',points=[[120+4*n,140] for n in range(91)]),dict(label='sparse',points=[[120+12*n,140] for n in range(31)]),dict(label='green',points=[[150,340]])]);rows.append(row);boundary.append(row)
proof=[];factors=dict(viewport=[tuple(v) for v in viewports],size=[1,22,96],strength=[.15,1])
for a,b in combinations(factors,2):
    pairs={(tuple(r[a]) if a=='viewport' else r[a],tuple(r[b]) if b=='viewport' else r[b]) for r in boundary};expected=set(product(factors[a],factors[b]));assert expected<=pairs;proof.append(dict(factors=[a,b],pairs=len(pairs)))
for strength in [1,.15]:
    for index,viewport in enumerate(viewports):
        gestures=[dict(label=f'p{p+1}-{phase}',points=[point]) for phase in ['first','second'] for p,point in enumerate([[150,140],[450,140],[150,340],[450,340]])];rows.append(dict(id=('main-full-v' if strength==1 else 'main-weak-v')+str(index+1),viewport=viewport,size=22,strength=strength,kind='patches',gestures=gestures))
assert len(rows)==38 and sum(6*len(r['gestures'])+4 for r in rows)==980
data=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-017',status='Pre-execution expanded repair plan, not a result',fixture=before['fixture'],fixture_sha256=before['fixture_sha256'],rows=rows,boundary_pairwise_proof=proof,expected_actual_downloads=980,oracle='Known PATCH original RGBA independently decoded. Fully covered pixels (path distance below R-1, R=max20,1.3*Size) get exactly one Cnew=C+Strength*(255-2*C) contribution per gesture, within1/255 opaque or2/255 native half-alpha rounding. All alpha unchanged. Pixels beyond R+1 remain exact; the one-pixel boundary band is checked by a common RGB inversion mask coefficient in0..Strength within2/255, not falsely treated as a fully covered cell. Dense/sparse native paths must both cover the same interior, with no overlap toggling. Two full inversions restore original fully covered RGBA exactly. Main Red/Blue/Green/half-alpha Red each gets two independent taps at both Strength endpoints in every layout. Every non-image source field, complete gesture Undo/Redo, actual settled public canvas/PNG and fresh project source/RGBA is exact. All actual downloads hashed; no app rendering/filter/serializer computes expected results.',scope='The same16 failing-before core rows, additional14 size1/22/96/Strength15/100% pairwise layout rows, plus8 complete four-patch main rows. No original source point, core tolerance or branch reduced; extra half-alpha/edge/size/history/fresh verification is mandatory for Pass.')
target.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');print('Prepared38 workflows/980 real-download expanded Invert plan; all boundary factor pairs proved.')
