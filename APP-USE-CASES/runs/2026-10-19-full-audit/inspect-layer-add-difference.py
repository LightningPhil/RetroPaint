from pathlib import Path
from PIL import Image
import json,base64,io,hashlib
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/LAYER-001-complete/1280x720';read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'));differences=[]
def walk(a,b,path):
    if isinstance(a,dict) and isinstance(b,dict):
        for key in a.keys()|b.keys():
            if key not in a or key not in b:differences.append(dict(path=path+'.'+key,before_present=key in a,after_present=key in b,before=repr(a.get(key)),after=repr(b.get(key))))
            else:walk(a[key],b[key],path+'.'+key)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):differences.append(dict(path=path,length_before=len(a),length_after=len(b)))
        for i,(x,y) in enumerate(zip(a,b)):walk(x,y,path+f'[{i}]')
    elif a!=b:
        row=dict(path=path)
        if isinstance(a,str) and a.startswith('data:image/'):
            decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'))
            aa,bb=decode(a),decode(b);row.update(encoded_sha_before=hashlib.sha256(a.encode()).hexdigest(),encoded_sha_after=hashlib.sha256(b.encode()).hexdigest(),decoded_rgba_equal=bool(np.array_equal(aa,bb)),maximum_difference=int(np.abs(aa.astype(int)-bb.astype(int)).max()))
        else:row.update(before=repr(a),after=repr(b))
        differences.append(row)
walk(read('picked-caption'),read('fresh/reopened'),'project')
(root/'evidence/LAYER-001-reopen-difference.json').write_text(json.dumps(differences,indent=2)+'\n',encoding='utf-8');print(json.dumps(differences,indent=2))
