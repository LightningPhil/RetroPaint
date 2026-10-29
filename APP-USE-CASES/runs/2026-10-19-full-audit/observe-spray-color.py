from pathlib import Path
from PIL import Image
import numpy as np
import json,sys
root=Path(__file__).resolve().parent;kind=sys.argv[1] if len(sys.argv)>1 else 'mist';case={'mist':'PAINT-010','splatter':'PAINT-011','confetti':'PAINT-012'}[kind];base=root/('headless/SPRAY-foreground/mist' if kind=='mist' else 'headless/SPRAY-supported/'+kind);ui=json.loads((base/(case+'-ui.json')).read_text(encoding='utf-8'));out=[];ink=np.array([229,57,53])
for row in ui['rows']:
    previous=np.asarray(Image.open(base/row['id']/'before.png')).astype(float)
    for label in row['labels']:
        pixels=np.asarray(Image.open(base/row['id']/(label+'.png'))).astype(float);mask=np.any(pixels!=previous,axis=2);ys,xs=np.where(mask);a=previous[mask,:3];b=pixels[mask,:3];v=ink-a;den=np.sum(v*v,axis=1);t=np.divide(np.sum((b-a)*v,axis=1),den,out=np.zeros(len(a)),where=den!=0);error=np.max(np.abs(b-(a+t[:,None]*v)),axis=1);i=np.argmax(error);outside=np.maximum(np.minimum(a,ink)-b,b-np.maximum(a,ink));oi,oc=np.unravel_index(np.argmax(outside),outside.shape);out.append(dict(row=row['id'],label=label,maximum=float(error[i]),prior=a[i].tolist(),pixel=b[i].tolist(),source=[int(xs[i]),int(ys[i])],maximum_endpoint_overshoot=float(outside[oi,oc]),overshoot_prior=a[oi].tolist(),overshoot_actual=b[oi].tolist(),overshoot_source=[int(xs[oi]),int(ys[oi])],saturating_pixels=int((b==ink).all(axis=1).sum())));previous=pixels
(root/('evidence/SPRAY-'+kind+'-color-observations.json')).write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out[:12]))
