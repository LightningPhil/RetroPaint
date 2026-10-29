from pathlib import Path
from datetime import datetime,timezone
from itertools import combinations,product
import json
root=Path(__file__).resolve().parent;file=root/'fixtures/PAINT-001-plan.json';assert not file.exists(),'Retain the pre-execution plan';rows=[];viewports=[[1280,720],[320,568],[390,844],[844,390]]
for layout,viewport in enumerate(viewports):
    for size_index,size in enumerate([1,22,96]):rows.append(dict(id='p'+str(len(rows)+1),viewport=viewport,size=size,strength=.15 if (layout+size_index)%2==0 else 1))
    if not any(r['viewport']==viewport and r['size']==22 and r['strength']==1 for r in rows):rows.append(dict(id='p'+str(len(rows)+1),viewport=viewport,size=22,strength=1))
levels=dict(viewport=viewports,size=[1,22,96],strength=[.15,1]);proof=[];key=lambda v:json.dumps(v)
for a,b in combinations(levels,2):
    expected={(key(x),key(y)) for x,y in product(levels[a],levels[b])};actual={(key(r[a]),key(r[b])) for r in rows};assert actual==expected;proof.append(dict(factors=[a,b],pairs=len(actual)))
assert len(rows)==14 and sum(r['size']==22 and r['strength']==1 for r in rows)==4
report=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-001',status='Plan recorded before execution, not a test result',rows=rows,pairwise_proof=proof,main_flow='Marker22/full Strength at every viewport. Every row additionally runs slow curve, tap, fast curve, three Undo and three Redo, actual fresh saved file input.',stroke_geometry=dict(slow='Quadratic from150,280 through400,160 to650,280;41 native points,15ms delay between points',fast='Same quadratic shifted160px up;41 native points, no inserted delay',tap=[800,200]),oracles='Independent connectivity, centreline coverage and distance-to-segment bounds; round tap/caps; known red alpha contribution; actual cursor-overlay geometry at22px; exact gesture history/source data/fresh file. Mouse input only, no physical pen claim. AA geometry allowance2 paper pixels; full core colour/alpha blend tolerance2/255. Cursor outer stroke accounts for3 CSS-pixel outline, independently scaled from public canvas rectangle.')
file.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Recorded14 Marker rows; all size/Strength/layout factor pairs and four exact main flows.')
