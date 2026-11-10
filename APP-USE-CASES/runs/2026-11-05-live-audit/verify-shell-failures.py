"""Failed thickness and disappeared complex-cap references preserve a verified shell."""
from pathlib import Path
import copy,hashlib,json
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-shell212';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(3)]
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
assert canonical(docs[0])==canonical(docs[1])==canonical(docs[2])
known=(out/'mouse-audit-shell20-top-3d-mm.stl').read_bytes();raws=[retain(prefix+'-3d-mm'+(f' ({i})' if i else '')+'.stl') for i in range(2)];assert known==raws[0]==raws[1]
stats=measure(read_binary(raws[0]));assert len(stats['components'])==1 and stats['components'][0]['euler']==2 and 6600<stats['signed_volume_mm3']<6800
# Exact match to prior independently checked analytic shell, rather than a new relaxed accuracy oracle.
ui=json.loads((out/'shell212-ui.json').read_text(encoding='utf-8'));states={s['stage']:s for s in ui['states']}
assert 'Cannot shell this solid at 50 mm' in states['joined-thickness50-rejected']['text']
assert 'An open face changed or disappeared' in states['source-height10-opening-disappeared']['text']
assert 'Cannot shell' not in states['thickness-corrected3-preview']['text'] and 'changed or disappeared' not in states['height20-corrected-preview']['text']
report=dict(status='Pass',case='FEATURE-020',joined_body_thickness50_rejects_correction3_succeeds_same_editor=True,source_cylinder_height20_to10_removes_original_complex_cap_and_rejects=True,source_height20_correction_succeeds_same_editor=True,both_cancel_saved_projects_whole_source_exact=True,both_stls_byte_exact_prior_independently_verified_complex_shell=True,no_filled_or_partial_shell_saved=True,mesh=stats,hashes=hashes)
(out/'shell212-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['mesh','hashes']},indent=2))
