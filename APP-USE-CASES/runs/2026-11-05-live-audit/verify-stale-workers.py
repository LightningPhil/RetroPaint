"""Correlate native controlled worker failures with unchanged downloaded document."""
import hashlib,json
from datetime import datetime
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
assert json.loads(retain('mouse-audit-code-after-stale-workers.retropaint'))==json.loads(retain('mouse-audit-code-boolean-reopened.retropaint'))
log=json.loads(retain('mouse-audit-fault-log (3).json'))
late=[e for e in log if e['type']=='late delivery']
for kind in ['cad','openscad']:
 assert any(e['detail'].startswith(kind+' obsolete message handler invoked') for e in late)
 assert any(e['detail']==kind+' obsolete error handler invoked' for e in late)
assert any('current CAD request 26' in e['detail'] for e in late)
records=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines()]
records=[r for r in records if r['at']>=log[0]['at'] and r['at']<=log[-1]['at']]
starts=[datetime.fromisoformat(r['at']) for r in records if r.get('cad_stall_consumed')]
ends=[datetime.fromisoformat(e['at'].replace('Z','+00:00')) for e in log if e['type']=='retired worker' and e['detail']=='cad']
assert len(starts)==len(ends)==2
durations=[(end-start).total_seconds() for start,end in zip(starts,ends)]
assert all(44.9<d<46 for d in durations),durations
observations=json.loads((out/'code-import-limit-dom-evidence.json').read_bytes())
active=next(e for e in observations if e['label']=='old-openscad-errors-ignored-while-new-job-running')
assert 'fib(44)' in active['source'] and active['status'].startswith('Rendering') and active['addDisabled']
retry=next(e for e in observations if e['label']=='adversarial-old-response-retry-ready')
assert retry['source']=='cube([11,7,3]);' and retry['status'].startswith('Preview ready') and not retry['addDisabled']
report=next(e for e in observations if e['label']=='stale-worker-successful-check-print')['report']
assert '10.00 × 60.00 × 6.00 mm' in report and '2.59 cm³' in report and 'Closed solid' in report
result={'two_real_foreground_timeout_seconds':durations,'old_worker_current_request_id_and_error_events_delivered':True,
 'old_openscad_errors_leave_active_replacement_source_and_render_unchanged':True,
 'successful_retry_after_restart':True,'whole_downloaded_document_exact':True,'final_print_report':report,
 'late_events':late,'sha256':hashes}
(out/'stale-workers-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['sha256','late_events']},indent=2))
