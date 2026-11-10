"""Modern disposable move-capacity fixture, derived from native Boolean layer scene."""
from pathlib import Path
import copy,hashlib,json,uuid
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures';source=Path.home()/'Downloads/mouse-audit-solid163-boolean165-baseline.retropaint';raw=source.read_bytes();d=json.loads(raw);target=next(l for l in d['layers'] if l['name']=='Far cubes');prototype=next(l for l in d['layers'] if l['name']=='Boolean pair')['cad']['bodies'][0];assert len(target['cad']['bodies'])==2
for i in range(125):
    b=copy.deepcopy(prototype);b.update(id=str(uuid.uuid5(uuid.NAMESPACE_URL,f'retropaint-live-audit-move166-capacity/{i}')),name=f'Capacity {i:03d}',position=[50+(i%25)*.5,50+(i//25)*.5,.1],scale=[.01,.01,.01]);target['cad']['bodies'].append(b)
assert len(target['cad']['bodies'])==127;output=folder/'cad-move166-destination127.retropaint';output.write_text(json.dumps(d,separators=(',',':'))+'\n',encoding='utf-8');(folder/'cad-move166-capacity-provenance.json').write_text(json.dumps(dict(source=str(source),source_sha256=hashlib.sha256(raw).hexdigest(),fixture_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),description=__doc__,added_bodies=125,total_destination=127,moving_bodies=2,expected='129 exceeds128 per-layer limit; fail atomically with source ownership intact.'),indent=2)+'\n')
