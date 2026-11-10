"""Reuse preserved public-UI-produced pixels/objects/live/photo fixture."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3];old=root/'APP-USE-CASES/runs/2026-10-19-full-audit/headless/LAYER-007-fixture/fresh/fixture.retropaint'
d=json.loads(old.read_text(encoding='utf-8'))
for layer in d['layers']:
    if isinstance(layer.get('paper'),bool):layer['paper']='#ffffff' if layer['paper'] else None
d['active']=d['layers'][2]['id']
out=root/'test-results/audit-2026-11-05/fixtures/rich-layer.retropaint';out.write_text(json.dumps(d),encoding='utf-8')
report=dict(source=str(old.relative_to(root)),source_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),source_verification='APP-USE-CASES/runs/2026-10-19-full-audit/evidence/LAYER-007-independent-verification.json',changes='Only legacy boolean Paper metadata converted to current colour/null; active Character')
out.with_suffix('.provenance.json').write_text(json.dumps(report,indent=2)+'\n')
print([(l['name'],list(l.get('live',{})),len(l.get('objects',[])),bool(l.get('photo'))) for l in d['layers']])
