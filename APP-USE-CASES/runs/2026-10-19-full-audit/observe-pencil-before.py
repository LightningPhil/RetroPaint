from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
import numpy as np
root=Path(__file__).resolve().parent;plan=json.loads((root/'fixtures/PAINT-006-plan.json').read_text(encoding='utf-8'));folder=root/'headless/PAINT-006-before/1280x720';fixture=root/plan['fixture'];assert hashlib.sha256(fixture.read_bytes()).hexdigest()==plan['fixture_sha256'];original=np.asarray(Image.open(fixture).convert('RGBA'));before=np.asarray(Image.open(folder/'before.png').convert('RGBA'));assert np.array_equal(before,original);expected=original.copy();rows=[]
for label,points in [('staircase',plan['staircase_points']),('fit-tap',[plan['fit_tap']])]:
    for x,y in points:expected[int(y),int(x)]=plan['colour']
    actual=np.asarray(Image.open(folder/(label+'.png')).convert('RGBA'));mismatch=(actual!=expected).any(axis=2);ys,xs=np.where(mismatch);expected_mask=(expected!=original).any(axis=2);actual_mask=(actual!=original).any(axis=2);rows.append(dict(stage=label,expected_changed_cells=int(expected_mask.sum()),actual_changed_cells=int(actual_mask.sum()),mismatched_cells=int(mismatch.sum()),changed_outside_expected_cells=int((actual_mask&~expected_mask).sum()),examples=[dict(cell=[int(x),int(y)],expected=expected[y,x].tolist(),actual=actual[y,x].tolist()) for x,y in zip(xs[:12],ys[:12])]))
    Image.fromarray(expected).save(root/('evidence/PAINT-006-expected-'+label+'.png'))
report=dict(at=datetime.now(timezone.utc).isoformat(),scope='Independent pixel diagnosis of actual saved core artifacts, not a completed case result. Later actual-view assertion failed separately.',oracle='Pillow '+Image.__version__+'; declared cell floors and exact palette Black RGBA; all original fixture bytes elsewhere unchanged',observations=rows,all_observed_pixels_exact=all(r['mismatched_cells']==0 for r in rows),source='headless/PAINT-006-before/1280x720')
(root/'evidence/PAINT-006-pixel-before.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
