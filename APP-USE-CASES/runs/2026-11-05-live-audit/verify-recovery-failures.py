"""Native missing/corrupt recovery results preserve full MIX and stored drafts."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(stage):
 name='mouse-audit-recovery-failure-'+stage+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
original=doc('before');assert doc('missing-before-fix')==original
assert doc('fixed-before')==doc('final-before')==original
for stage in ['missing','json','png','missing-phone','json-landscape','retry-undone','inplace-undone','final-current']:assert doc(stage)==original,stage
restored=doc('retry-restored');assert doc('inplace-restored')==doc('inplace-redone')==restored
expected=json.loads((Path.home()/'Downloads/mouse-audit-label-r2-browser-key-undone.retropaint').read_bytes());assert restored==expected
assert len(original['layers'])==5 and len(restored['layers'])==3
assert sum(len(l.get('objects',[])) for l in restored['layers'])==4
for o in restored['layers'][-1]['objects']:assert o['kind']=='text' and o.get('callout')
evidence=json.loads((out/'recovery-failure-evidence.json').read_bytes());assert len(evidence)==5
for e in evidence:
 assert e['dialogOpen'] and e['role']=='alert' and not e['focusedDisabled'] and e['focusedText']==e['chosen']
 assert 'mouse-audit-label' in e['chosen'] and len(e['error'])>20
 r,d=e['errorRect'],e['dialogRect'];w,h=e['viewport']
 assert r['x']>=d['x'] and r['x']+r['width']<=d['x']+d['width']+.1
 assert r['y']>=d['y'] and r['y']+r['height']<=d['y']+d['height']+.1
 assert d['x']>=0 and d['y']>=0 and d['x']+d['width']<=w+.1 and d['y']+d['height']<=h+.1
assert {tuple(e['viewport']) for e in evidence}>={(320,568),(844,390)}
retry=json.loads((out/'recovery-inplace-retry-evidence.json').read_bytes());assert retry['successful'] and not retry['before']['disabled']
assert retry['before']['focusText']==retry['chosen'] and 'no longer available' in retry['before']['error']
events=[json.loads(line).get('event',{}) for line in (out.parent/'fault-controls/requests.jsonl').read_text().splitlines()]
faults=[e for e in events if e.get('type')=='draft read fault']
assert {e['detail']['fault'] for e in faults}>={'missing','json','image'}
(out/'recovery-standard-api-fault-evidence.json').write_text(json.dumps(faults,indent=2)+'\n')
report={'all_missing_json_png_failures_preserve_exact_five_layer_MIX':True,'local_alert_visible_with_focused_enabled_retry_on_desktop_phone_landscape':True,'in_place_keyboard_retry_success_and_exact_undo_redo':True,'original_stored_four_label_draft_still_exact_after_faults':True,'fault_scope':'One standard IndexedDB request result is degraded; original stored bytes remain untouched.','sha256':hashes}
(out/'recovery-failures-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
