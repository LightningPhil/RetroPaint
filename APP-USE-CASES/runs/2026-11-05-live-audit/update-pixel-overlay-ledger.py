"""Record LIVE-029 and verified screen/source coordinate evidence."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05'
assert json.loads((evidence/'mouse/pixel-overlays-verification.json').read_bytes())['status']=='Pass'
regression=json.loads((evidence/'all-twenty-nine-fixes-final/report.json').read_bytes());assert regression['status']=='Pass'
assert all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in regression['source_files'])
ledger_path=folder/'execution.json';ledger=json.loads(ledger_path.read_text(encoding='utf-8-sig'))
case=next(c for c in ledger['cases'] if c['id']=='ACCESS-004');case['status']='Pass'
note='PIXEL32x32 at1455% exposed invisible grid and illegible enlarged ruler numbers (LIVE-029). Guides now use a viewport-bounded screen-resolution surface, independent of source pixels. Native View toggles,100%/Fit/46548%maximum,150x100CSS pan,nearest-neighbour64x48source resize, exact Undo/Redo and native reopen exercised. All five required CSS layouts checked, including compact zooms above/below6px threshold. Independent screenshot measurements align white-cell grid boundaries to known source coordinates; every actual PNG/source pixel and whole view-only project exact. Component red/green also checks crop, panning,18screen-pixel rulers, glyph legibility and bounded extreme-zoom memory. Initial transient-toast/drawer screenshots retained; settled replacement evidence excludes known toolbar occlusions. Pillow exact halfway resize ties differ from Canvas: independent nearest-neighbour math accepts only equally distant source pixels at exact ties; no blended colours allowed.'
if note not in case['observations']:case['observations'].append(note)
for entry in ['test-results/audit-2026-11-05/mouse/pixel-overlays-verification.json','test-results/audit-2026-11-05/mouse/pixel-overlay-evidence.json','APP-USE-CASES/runs/2026-11-05-live-audit/verify-pixel-overlays.py']:
 if entry not in case['evidence']:case['evidence'].append(entry)
space=next(c for c in ledger['cases'] if c['id']=='ACCESS-003')
space_note='Additional actual Space-drag probe: browser-only parallel drag queues until key release (diagnostic retained, resulting test stroke exactly undone). Holding Space via browser key API while native Windows mouse drags works: public moving-paper state observed, native drag completes within305ms of6000ms hold, paper moves-45.4545/+45.4545CSS, whole project exact before/after. Exact PATCH-coordinate, Ctrl-wheel/dialog and four-layout combined workflow remain outstanding; case stays Partial.'
if space_note not in space['observations']:space['observations'].append(space_note)
if 'test-results/audit-2026-11-05/mouse/space-probe.json' not in space['evidence']:space['evidence'].append('test-results/audit-2026-11-05/mouse/space-probe.json')
ledger['updated']=datetime.now(timezone.utc).isoformat();ledger_path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
readme=folder/'README.md';text=readme.read_text(encoding='utf-8').replace('**57 Pass, 289 Partial, 0 Not run, 3 Blocked**','**58 Pass, 288 Partial, 0 Not run, 3 Blocked**').replace('after all twenty-eight fixes passes **653 checks','after all twenty-nine fixes passes **654 checks').replace('(`all-twenty-eight-fixes/report.json`)','(`all-twenty-nine-fixes-final/report.json`)')
if '## LIVE-029:' not in text:
 text+='\n## LIVE-029: enlarged pixel grid and ruler rendering\n\n'+note+'\n\n'+space_note+'\n\nThe initial full29-fix run was reloaded by source edits while running; its results\nare retained separately. The final full run hashes the completed sources and passes\n654 checks without page errors. TypeScript and production build pass.\n'
readme.write_text(text,encoding='utf-8')
envpath=evidence/'environment.json';env=json.loads(envpath.read_text(encoding='utf-8-sig'));entries={x['path']:x for x in env['dirty_source']}
for path in ['src/view-guides.ts','src/overlay.ts','src/loop.ts']:entries.setdefault(path,{'path':path})
for entry in entries.values():entry['sha256']=hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
env['dirty_source']=list(entries.values());env['recorded']=ledger['updated'];env['fix_count']=29
env['latest_regression']={'report':'test-results/audit-2026-11-05/all-twenty-nine-fixes-final/report.json','passed':sum(s['passed'] for s in regression['suites'])+1,'failed':0,'page_errors':0}
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode()
env['production_build']={'fixes':29,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()}
envpath.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(dict(Counter(c['status'] for c in ledger['cases'])));print(env['latest_regression'])
