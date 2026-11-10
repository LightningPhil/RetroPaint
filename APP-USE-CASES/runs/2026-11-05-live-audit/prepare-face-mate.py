"""Declared modern mating fixture derived from a native primitive cube recipe."""
from pathlib import Path
import copy,json,uuid,hashlib
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';source=Path.home()/'Downloads/mouse-audit-alignment176-normal.retropaint';raw=source.read_bytes();doc=json.loads(raw);layer=next(l for l in doc['layers'] if 'cad'in l);cube=layer['cad']['bodies'][1];bodies=[]
for name,position,scale,shape,locked in [('Moving cube',[30,0,50],[1,1,1],'box',False),('Target base',[-30,0,10],[2,1.5,1],'box',False),('Curved sphere',[0,45,10],[1,1,1],'sphere',False),('Locked cube',[45,45,10],[1,1,1],'box',True)]:
 b=copy.deepcopy(cube);b.update(id=uuid.uuid4().hex,name=name,position=position,scale=scale,locked=locked);b['solid']['shape']=shape;bodies.append(b)
layer['cad']['bodies']=bodies;path=out/'mate179-modern.retropaint';path.write_text(json.dumps(doc,separators=(',',':')),encoding='utf-8');(out/'mate179-modern.json').write_text(json.dumps(dict(provenance=__doc__,source_sha256=hashlib.sha256(raw).hexdigest(),fixture_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bodies=[dict(name=b['name'],id=b['id']) for b in bodies]),indent=2)+'\n')
