"""One malformed recipe field per copy of the genuine saved cropped project."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];source=Path.home()/'Downloads/mouse-audit-photo105-cropped-warm.retropaint';base=json.loads(source.read_text(encoding='utf-8'));out=root/'test-results/audit-2026-11-05/fixtures/photo105-invalid';out.mkdir(exist_ok=True);rows=[]
for name,path,value in [('exposure-type',['settings','exposure'],'bright'),('look-unknown',['look'],'unknown-look'),('curve-order',['settings','curves','rgb'],[dict(x=0,y=0),dict(x=.8,y=.8),dict(x=.2,y=.2),dict(x=1,y=1)])]:
    d=copy.deepcopy(base);p=d['layers'][0]['photo']
    for key in path[:-1]:p=p[key]
    p[path[-1]]=value;target=out/(name+'.retropaint');target.write_text(json.dumps(d),encoding='utf-8');rows.append(dict(file=target.name,mutation=path,value=value,sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
(out/'manifest.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),copies=rows),indent=2)+'\n');print('Prepared three one-field malformed photo recipes')
