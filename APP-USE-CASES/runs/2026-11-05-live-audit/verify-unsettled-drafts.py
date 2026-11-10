"""Native refresh must resume settled snapshots, excluding text/photo drafts."""
import hashlib,json
from datetime import datetime
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(name):
 data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
evidence=json.loads((out/'unsettled-draft-evidence.json').read_bytes())
text_before=doc('mouse-audit-unsettled-text-r2-before.retropaint');text_after=doc('mouse-audit-unsettled-text-r2-recovered.retropaint')
assert text_before==text_after and len(text_after['layers'])==5
assert next(l for l in text_after['layers'] if l['id']==104)['name']=='Checkpoint Caption'
e=evidence['textR2'];assert e['initial']['status']==e['afterWait']['status']=='Draft pending'
assert e['afterWait']['elapsed']>=3000 and e['initial']['text']==e['afterWait']['text'] and len(e['initial']['text'])>20
assert 'Uncheckpointed text layer' in e['initial']['layerHint'] and 'Checkpoint Caption' in e['recovered']['layerHint'] and not e['recovered']['text']
photo_before=doc('mouse-audit-unsettled-photo-before.retropaint');photo_after=doc('mouse-audit-unsettled-photo-recovered.retropaint')
assert photo_before==photo_after and len(photo_after['layers'])==5
character=next(l for l in photo_after['layers'] if l['id']==103)
assert character['name']=='Checkpoint Character' and character['photo']['settings']['brightness']==12
e=evidence['photo'];assert e['initial']['status']==e['afterWait']['status']=='Draft pending'
assert e['afterWait']['elapsed']>=3000 and e['initial']['photoOpen'] and e['afterWait']['photoOpen']
assert e['initial']['brightness']==e['afterWait']['brightness']=='35' and e['initial']['layerName']=='Uncheckpointed photo layer'
assert not e['recovered']['photoOpen'] and e['recovered']['layerName']=='Checkpoint Character'
gesture_before=doc('mouse-audit-unsettled-gesture-r2-before.retropaint');gesture_after=doc('mouse-audit-unsettled-gesture-r2-recovered.retropaint');assert gesture_before==gesture_after
held=json.loads((out/'held-gesture-refresh-evidence.json').read_bytes());assert held['during']['inputCompleted'] is None
assert held['during']['status']=='Draft pending' and held['during']['elapsed']>=3000
assert '"phase":"pointerdown"' in held['during']['trace'].strip().split('\n')[-1]
assert held['reloadRequested']<held['reloadCompleted']<held['inputCompleted'] and held['inputResult']=='completed'
assert held['inputCompleted']-held['started']>=held['requestedDuration']
rows=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text().splitlines()]
assert any(row.get('method')=='GET' and row.get('path','').startswith('/?') and held['reloadRequested']<=datetime.fromisoformat(row['at']).timestamp()*1000<=held['reloadCompleted'] for row in rows)
report={'unfinished_text_photo_and_actual_held_mouse_gesture_postpone_pending_autosave':True,'refresh_resume_restores_whole_settled_five_layer_documents_exact':True,'uncommitted_text_and_brightness35_not_applied':True,'settled_photo_brightness12_and_originals_retained':True,'text_elapsed_ms':evidence['textR2']['afterWait']['elapsed'],'photo_elapsed_ms':evidence['photo']['afterWait']['elapsed'],'mouse_held_at_refresh_ms':held['during']['elapsed'],'reload_finishes_before_native_mouse_release':True,'sha256':hashes}
(out/'unsettled-drafts-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
