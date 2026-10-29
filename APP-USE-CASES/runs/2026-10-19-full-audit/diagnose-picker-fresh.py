from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,numpy as np
root=Path(__file__).resolve().parent;records=[]
def differences(a,b,path='$'):
    if type(a)!=type(b):return [dict(path=path,before_type=type(a).__name__,after_type=type(b).__name__)]
    if isinstance(a,dict):
        out=[]
        for k in a.keys()|b.keys():
            if k not in a or k not in b:out.append(dict(path=path+'.'+k,before_present=k in a,after_present=k in b,before=a.get(k),after=b.get(k)))
            else:out+=differences(a[k],b[k],path+'.'+k)
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(path=path,before_length=len(a),after_length=len(b))]
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in differences(x,y,path+f'[{i}]')]
    if a!=b:
        if isinstance(a,str) and len(a)>200:return [dict(path=path,before_sha256=hashlib.sha256(a.encode()).hexdigest(),after_sha256=hashlib.sha256(b.encode()).hexdigest())]
        return [dict(path=path,before=a,after=b)]
    return []
for i in range(1,5):
    folder=root/f'headless/INK-002-picker/v{i}';a=json.loads((folder/'hidden-character-marked.retropaint').read_text(encoding='utf-8'));b=json.loads((folder/'fresh/reopened.retropaint').read_text(encoding='utf-8'));x=np.asarray(Image.open(folder/'hidden-character-marked.png').convert('RGBA'));y=np.asarray(Image.open(folder/'fresh/reopened.png').convert('RGBA'));mask=np.any(x!=y,axis=2);ys,xs=np.where(mask);records.append(dict(row=f'v{i}',source_differences=differences(a,b),changed_pixels=int(mask.sum()),max_channel_error=int(np.abs(x.astype(int)-y.astype(int)).max()),first_changed=dict(position=[int(xs[0]),int(ys[0])],before=x[ys[0],xs[0]].tolist(),after=y[ys[0],xs[0]].tolist()) if mask.any() else None))
report=dict(at=datetime.now(timezone.utc).isoformat(),records=records);(root/'evidence/INK-002-fresh-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
