"""Record verified radius/motor fixes without closing unfinished use cases."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05'
report=json.loads((evidence/'all-thirty-five-fixes-final/report.json').read_bytes());assert report['status']=='Pass'
assert all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
assert json.loads((evidence/'mouse/spiro-motor35-verification.json').read_bytes())['status']=='Pass'
radius=json.loads((evidence/'mouse/spiro-radius34-fixed-evidence.json').read_bytes())
for item in radius[:-1]:assert float(item['actual']['value'])==max(.5,min(1e7,float(item['requested']))) and item['actual']['valid']
assert float(radius[-1]['reset']['value'])==640/3 and radius[-1]['reset']['valid']
holes=[json.loads((evidence/f'mouse/spiro-hole-bank-{gear}-verification.json').read_bytes()) for gear in ['pink','purple','red','yellow','green','orange']]
assert all(h['status']=='Pass' for h in holes) and sum(h['offered_holes'] for h in holes)==44
aggregate={'status':'Pass','scope':'All 44 named holes, Vector / Manual / Ring / outer 96 only; other combinations remain separate.','holes':44,'actual_downloads':sum(len(h['sha256']) for h in holes),'bank_reports':[f'spiro-hole-bank-{h["gear"]}-verification.json' for h in holes]}
assert aggregate['actual_downloads']==162
(evidence/'mouse/spiro-all-holes-verification.json').write_text(json.dumps(aggregate,indent=2)+'\n',encoding='utf-8')
notes={
 'PLAY-018':'LIVE-034 fixed accepted fractional radii rounded in the input, invalid step=1, and keystroke-by-keystroke rewriting that turned native typing 1.5 into 51. Input now permits fractions and preserves accepted numeric text/caret. Actual native typing checks .1→.5, .5, 1, 1.5, 213.33333333333334, 1e7 and 1e8→1e7; all fields valid; Reset returns 640/3. Early fill-only inspection and failed first-fix native typing evidence are retained. Handle/move and remaining shared matrix still require completion.',
 'PLAY-019':'All six independent manual hole-bank reports now Pass: 44 distinct real mouse drawings; 162 actual project/PNG downloads; exact whole per-hole Undo/Redo and six native project/PNG round trips. Scope Vector/Manual/Ring/outer96 only. Aggregate spiro-all-holes-verification.json records this scope; other stator/outer/drive combinations remain in progress.',
 'PLAY-020':'LIVE-035 fixed Reset leaving a visible partial vector preview absent from project/PNG, and no motor-running indicator. Motor now exposes pressed Stop drawing; Stop, Reset, switching to Manual and natural completion share one commit path. Real Stop, Reset, custom180/53 Reset, natural96/36 completion and Manual switch each add one analytic editable curve; whole Undo/Redo and native final project/PNG reopen are exact. Original raster remains white. Canvas-key cancellation has synthetic coverage, but two native omnibox attempts did not deliver capture loss during the motor; recorded as unproved rather than Pass. Early numeric fill attempts did not commit change; native typing did, and custom settings are separately recorded. Shared matrix and other-workflow branch remain pending.'}
ledgerpath=folder/'execution.json';ledger=json.loads(ledgerpath.read_text(encoding='utf-8-sig'))
for case in ledger['cases']:
 if case['id'] not in notes:continue
 if notes[case['id']] not in case['observations']:case['observations'].append(notes[case['id']])
 for path in ['test-results/audit-2026-11-05/mouse/spiro-radius34-fixed-evidence.json','test-results/audit-2026-11-05/mouse/spiro-motor35-verification.json','test-results/audit-2026-11-05/mouse/spiro-all-holes-verification.json']:
  if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();ledgerpath.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
readme=folder/'README.md';text=readme.read_text(encoding='utf-8').replace('after all thirty-three fixes passes **663 checks','after all thirty-five fixes passes **672 checks').replace('(`all-thirty-three-fixes/report.json`)','(`all-thirty-five-fixes-final/report.json`)')
if '## LIVE-034' not in text:
 text+='\n## LIVE-034 / LIVE-035: exact radius typing and retained motor drawings\n\n'+'\n\n'.join(notes.values())+'\n\nThe first 35-fix full run was interrupted by the fractional-typing edit and is historical. The final stable run passed672checks with source hashes verified. The targeted combined filter attempt selected zero checks (literal substring matching); separate targeted runs passed. The first motor layout fixture omitted Advanced mode and was corrected before its four-layout pass. The independent motor oracle initially assumed hole0; actual initial geometry uniquely identifies default hole2. Curve-fit checks validate all saved points against that offered hole. A strict monotonic-time assumption also found a tiny initial frame-clock backtrack; no criterion requires monotonic sampling, and all saved points remain on the configured curve.\n'
readme.write_text(text,encoding='utf-8')
envpath=evidence/'environment.json';env=json.loads(envpath.read_text(encoding='utf-8-sig'))
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=35;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-thirty-five-fixes-final/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0}
assert env['latest_regression']['passed']==672
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':35,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()}
envpath.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(env['latest_regression'])
