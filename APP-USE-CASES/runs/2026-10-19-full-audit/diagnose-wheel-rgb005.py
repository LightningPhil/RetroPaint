from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,base64,io,numpy as np
root=Path(__file__).resolve().parent;plan=json.loads((root/'fixtures/INK-005-plan.json').read_text(encoding='utf-8'));records=[];rgba=lambda p:np.asarray(Image.open(p).convert('RGBA'))
for row in plan['rows']:
    folder=root/'headless/INK-005-wheel-rgb'/row['id'];count=len(plan['operation_groups'][row['group']]);public=rgba(folder/f's{count-1}-redone-public.png');doc=json.loads((folder/'all-colours.retropaint').read_text(encoding='utf-8'));source=rgba(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1])));saved=rgba(folder/'all-colours.png');pairs=[]
    for name,a,b in [('public-vs-source',public,source),('public-vs-PNG',public,saved),('source-vs-PNG',source,saved)]:
        mask=np.any(a!=b,axis=2);ys,xs=np.where(mask);examples=[dict(position=[int(x),int(y)],before=a[y,x].tolist(),after=b[y,x].tolist()) for x,y in zip(xs[:8],ys[:8])];pairs.append(dict(name=name,changed_pixels=int(mask.sum()),maximum_error=int(np.abs(a.astype(int)-b.astype(int)).max()),changed_bounds=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if mask.any() else None,examples=examples))
    records.append(dict(id=row['id'],pairs=pairs))
report=dict(at=datetime.now(timezone.utc).isoformat(),records=records);(root/'evidence/INK-005-final-frame-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
