"""Record LIVE-038 and the independently verified clipboard/place/cancel cases."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05';report=json.loads((evidence/'all-thirty-eight-fixes/report.json').read_bytes())
assert report['status']=='Pass' and all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
for name in ['edit-clipboard38-verification.json','edit-place-cancel38-verification.json']:assert json.loads((evidence/'mouse'/name).read_bytes())['status']=='Pass'
notes={
 'EDIT-005':'LIVE-038: actual native raster Copy/Move/Paste retains Red source; Cut removes only the selected Green; pasted Green moves to the expected destination; separate Undo/Redo steps for Cut and Paste restore whole projects exactly. Native project and PNG reopen exact. API-denial controls reject actual navigator.clipboard.write/read without changing browser permissions: OS Blue sentinel remains unchanged, local Red pastes exactly. Before-fix stale Copied notice retained. Paste now explains that the system clipboard is unavailable and the session copy was used. Four-layout regression fails on the old notice and passes after the fix; normal image paste and external-text rejection remain covered. Original overly broad pending lasso note does not apply to this case’s copy/cut/fallback criteria.',
 'EDIT-006':'Native labelled RGBA PATCH: lift/move Red by150,100 and freely resize110×90 to220×270, then Place. Blue is lifted/moved150,300 and resized220×180 before switching to Brushes. Both settlement paths hide handles and commit once; source removal, transformed destination, all neighbouring pixels and labels independently exact. One Undo/Redo per settlement restores complete before/after projects exactly. Native project/PNG reopen exact. Initial oracle incorrectly assumed nearest-neighbour while Smooth was active; retained observations show1760 edge differences. Correct bilinear interpolation leaves four straight-RGBA compositing rounding differences; an elementary eight-bit premultiplied source-over calculation matches every RGBA pixel exactly, without any tolerance.',
 'EDIT-007':'Native labelled RGBA PATCH in ordinary object-free Raster mode: lift/move Red then Escape; separately lift/move Green and resize110×90 to165×135 then Cancel. Both remove floating handles and restore the complete before project and PNG bytes pixel-for-pixel. Ordinary Raster cancellation tested separately from editable-object Escape behavior.'}
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for case in ledger['cases']:
 if case['id'] not in notes:continue
 case['status']='Pass';note=notes[case['id']]
 if note not in case['observations']:case['observations'].append(note)
 names=['edit-clipboard38-verification.json','edit-clipboard38-evidence.json','edit-clipboard38-normal-evidence.json'] if case['id']=='EDIT-005' else ['edit-place-cancel38-verification.json','edit-place38-evidence.json','edit-cancel38-evidence.json']
 for name in names:
  path='test-results/audit-2026-11-05/mouse/'+name
  if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts==Counter({'Pass':69,'Partial':277,'Blocked':3})
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**66 Pass, 280 Partial, 0 Not run, 3 Blocked**','**69 Pass, 277 Partial, 0 Not run, 3 Blocked**').replace('after all thirty-seven fixes passes **680 checks','after all thirty-eight fixes passes **684 checks').replace('(`all-thirty-seven-fixes/report.json`)','(`all-thirty-eight-fixes/report.json`)')
if '## LIVE-038:' not in text:text+='\n## LIVE-038: clipboard fallback feedback; raster settlement\n\n'+'\n\n'.join(notes.values())+'\n\nThe first new regression accidentally read selectionBounds.w; its diagnostic report is retained. The corrected width fixture fails on the old missing message in all four layouts and passes after the product fix. No clipboard permission was changed. Pointer audit observation now also records actual event modifier flags for forthcoming Shift checks.\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=38;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-thirty-eight-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==684
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':38,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()}
ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(dict(counts));print(env['latest_regression'])
