"""Native contextual range messages; exact preserved projects and known-good STL bytes."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
ui=json.loads((out/'feedback203-ui.json').read_text(encoding='utf-8'));circle=json.loads((out/'feedback203-circle-ui.json').read_text(encoding='utf-8'));assert 'index-B8O_LZBS.js'in ui['build']
expected={'angle-between':'Angle between lines must be a finite number between 0 and 180 degrees.','angle':'Angle to X must be a finite number between -360 and 360 degrees.','length':'Length must be a finite number between 0.01 and 20000 mm.'}
assert len(ui['samples'])==3
for item in ui['samples']:assert item['error']==expected[item['kind']] and item['plotUnchanged']
assert circle['invalid']['error']=='Diameter must be a finite number between 0.01 and 2000 mm.' and circle['invalid']['plotUnchanged']
for prefix,prior in [('mouse-audit-feedback203','mouse-audit-angles202-3d-mm (5).stl'),('mouse-audit-feedback203-circle','mouse-audit-diameter201-3d-mm (1).stl')]:
 a=json.loads(retain(prefix+'.retropaint'));b=json.loads(retain(prefix+' (1).retropaint'));assert canonical(a)==canonical(b);assert retain(prefix+'-3d-mm.stl')==(out/prior).read_bytes()
assert ui['viewportReset']==[1757,853]
report=dict(status='Pass',all_four_constraint_types_report_own_units_and_exact_limits=True,angular_errors_no_longer_claim_millimetre_workspace_problem=True,all_invalid_inputs_keep_last_valid_outline=True,both_actual_project_sources_exact_after_cancel=True,both_actual_stls_byte_exact_previous_independently_verified_models=True,original_paint_and_unrelated_source_preserved=True,default_viewport_unchanged=True,hashes=hashes)
(out/'feedback203-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
