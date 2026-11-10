"""Preserve the pending-Cancel limitation and independently prove timeout/retry recovery."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-cancel198';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(3)];index=next(i for i,l in enumerate(docs[0]['layers']) if l['name']=='Trace plate')
def canonical(doc):
 d=copy.deepcopy(doc);d.pop('active',None);d['layers'][index].pop('image',None);return d
assert all(canonical(d)==canonical(docs[0]) for d in docs)
prior=(out/'mouse-audit-feature196-3d-mm (1).stl').read_bytes()
assert retain(prefix+'-3d-mm.stl')==retain(prefix+'-3d-mm (1).stl')==prior
ui=json.loads((out/'cancel198-ui.json').read_text(encoding='utf-8'));assert ui['pending']['busy']=='true' and not ui['pending']['cancel']['disabled'] and ui['afterCancelClick']['busy']=='true' and ui['afterCancelClick']['editorOpen'] and ui['afterCancelClick']['depth']=='8'
assert ui['afterTimeout']['busy'] is None and ui['afterTimeout']['editorOpen'] and ui['afterTimeout']['depth']=='8' and 'took too long'in ui['afterTimeout']['status'] and 'Preview of the rebuilt solid'in ui['retry']['status']
events=[json.loads(line) for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines()];last=max(i for i,e in enumerate(events) if e.get('command')=='stall-cad');relevant=[e for e in events[last:] if 'command'in e or e.get('cad_stall_consumed') is True]
assert len(relevant)==2
report=dict(status='Partial',deferred_finding='CANCEL-198: visible Cancel cannot interrupt a pending feature rebuild; user must await completion or45s timeout',native_cancel_click_left_busy_and_editor_open=True,timeout_kept_draft_and_recovered=True,post_timeout_cancel_source_exact=True,restarted_engine_preview_retry_succeeds=True,retry_cancel_source_exact=True,both_restored_stls_byte_exact_known7mm_finished_plate=True,unrelated_model_photo_annotation_stack_exact=True,late_reply_after_successful_pending_cancellation_not_certified=True,fault_events=relevant,hashes=hashes)
(out/'cancel198-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['hashes','fault_events']},indent=2))
