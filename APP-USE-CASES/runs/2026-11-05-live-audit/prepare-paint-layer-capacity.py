"""Declared modern16layer fixture: native mixed4layer scene plus12 copies of native blank normal sheet."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures';downloads=Path.home()/'Downloads';base_raw=(downloads/'mouse-audit-paintlayers190-baseline.retropaint').read_bytes();blank_raw=(downloads/'mouse-audit-paintlayers190-above-blank.retropaint').read_bytes();base=json.loads(base_raw);above=json.loads(blank_raw);ids={l['id'] for l in base['layers']};blank=next(l for l in above['layers'] if l['id'] not in ids);assert 'cad' not in blank and blank['paper'] is None
for i in range(12):
 layer=copy.deepcopy(blank);layer.update(id=max(ids)+i+1,name=f'Capacity blank {i+1}');base['layers'].append(layer)
path=out/'paintlayers190-capacity16-modern.retropaint';path.write_text(json.dumps(base,separators=(',',':')),encoding='utf-8');(out/'paintlayers190-capacity16-modern.json').write_text(json.dumps(dict(provenance=__doc__,base_sha256=hashlib.sha256(base_raw).hexdigest(),blank_producer_sha256=hashlib.sha256(blank_raw).hexdigest(),fixture_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),layers=len(base['layers'])),indent=2)+'\n')
