from pathlib import Path
from itertools import combinations,product
from datetime import datetime,timezone
import json
root=Path(__file__).resolve().parent;file=root/'fixtures/CADMIX-pairwise-plan.json';assert not file.exists(),'Retain the recorded pre-execution plan'
viewports=[(1280,720),(320,568),(390,844),(844,390)];triples=[[(0,0,0),(1,1,1)],[(0,0,1),(1,1,0)],[(0,1,0),(1,0,1)],[(0,1,1),(1,0,0)]];rows=[]
for viewport,values in zip(viewports,triples):
    for projection,photo,crop in values:
        projection=['perspective','orthographic'][projection];rows.append(dict(id='v'+str(len(rows)+1),viewport=list(viewport),projection=projection,photo=bool(photo),crop=bool(crop),fixture=projection+('-photo' if photo else '-plain')+('-crop' if crop else '-full')))
levels=dict(viewport=[list(v) for v in viewports],projection=['perspective','orthographic'],photo=[False,True],crop=[False,True]);coverage=[]
key=lambda value:json.dumps(value,sort_keys=True)
for a,b in combinations(levels,2):
    required={(key(x),key(y)) for x,y in product(levels[a],levels[b])};actual={(key(row[a]),key(row[b])) for row in rows};assert actual==required;coverage.append(dict(factors=[a,b],required_pairs=len(required),executed_plan_pairs=len(actual)))
assert len({(r['projection'],r['photo'],r['crop']) for r in rows})==8
report=dict(at=datetime.now(timezone.utc).isoformat(),cases=['LAYER-013','LAYER-014'],status='Plan recorded before execution; not a test result',levels=levels,rows=rows,pairwise_proof=coverage,scope='Every projection/photo/crop triple once; every screen size twice with both values of each other factor. Each case executes all8 rows. Every guide hide/show/history and hand-off branch runs per row. This reduces32 lower-risk layout combinations while retaining exhaustive named states and pairwise interactions.',fixture_preparation='All8 CADMIX variants are actual UI-created copies of the immutable original artwork. Set/pin known isometric view, adjust only Backdrop when photo=true, crop to source100,80,760,480 when crop=true; retain every original body recipe and other source pixels. Actual fresh file reopen for each fixture.')
file.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Recorded8 rows per case; all6 factor-pair families covered.')
