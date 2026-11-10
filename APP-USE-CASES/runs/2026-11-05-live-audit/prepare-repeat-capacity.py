"""Declared modern capacity fixture: native two-piece scene plus125 tiny independent cubes."""
from pathlib import Path
import copy,json,uuid,hashlib
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';source=Path.home()/'Downloads/mouse-audit-alignment176-normal.retropaint';raw=source.read_bytes();doc=json.loads(raw);layer=next(l for l in doc['layers'] if 'cad'in l);reference=layer['cad']['bodies'][1]
for i in range(125):
 b=copy.deepcopy(reference);b.update(id=uuid.uuid4().hex,name=f'Capacity filler {i+1}',position=[1000+2*(i%25),1000+2*(i//25),1],scale=[.05,.05,.05]);layer['cad']['bodies'].append(b)
path=out/'repeat177-capacity127.retropaint';path.write_text(json.dumps(doc,separators=(',',':')),encoding='utf-8');(out/'repeat177-capacity127.json').write_text(json.dumps(dict(provenance=__doc__,source_sha256=hashlib.sha256(raw).hexdigest(),fixture_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),pieces=len(layer['cad']['bodies'])),indent=2)+'\n')
