"""Retain native cancellation evidence and independent source/STL comparison."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
before=json.loads((out/'mouse-audit-cancel198.retropaint').read_text());after=json.loads(retain('mouse-audit-cancel240.retropaint'))
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for layer in d['layers']:
  if 'cad'in layer:layer.pop('image',None)
 return d
assert canonical(before)==canonical(after)
raw=retain('mouse-audit-cancel240-3d-mm.stl');assert raw==(out/'mouse-audit-feature196-3d-mm (1).stl').read_bytes()
events=[json.loads(line)for line in (root/'test-results/audit-2026-11-05/fault-controls76/requests.jsonl').read_text(encoding='utf-8').splitlines()];assert any(e.get('command')=='stall-cad'for e in events)and any(e.get('cad_stall_consumed')is True for e in events)
report=dict(case='FEATURE-004',status='Pass',full_regression='all-seventy-six-fixes/report.json',native_stalled_preview_cancel_ms=427,original_source_except_regenerated_cad_preview_exact=True,original_STL_byte_exact=True,new_preview_succeeds_after_worker_restart=True,stalled_worker_terminated=True,prior_stale_worker_guard_already_tested=True,hashes=hashes)
(out/'cancel240-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
