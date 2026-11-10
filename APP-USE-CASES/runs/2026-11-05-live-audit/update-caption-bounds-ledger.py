"""Record LIVE-040 without closing incomplete caption/font acceptance cases."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05';report=json.loads((evidence/'all-forty-fixes/report.json').read_bytes());assert report['status']=='Pass' and all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files']);assert json.loads((evidence/'mouse/caption-bounds40-verification.json').read_bytes())['status']=='Pass'
note='LIVE-040: native caption Size1/BoxWidth1 remained invalid after blur while Place silently used minimumfont6 and bitmap20×40. Text controls now bound preview values consistently, preserve in-progress text/caret, normalize on blur or explicit placement, restore defaults for blank/non-numeric input, retain fractional font sizes (stepany), and round box width to whole pixels. Twenty-one native size/width edits cover below-minimum,zero,negative,minimum,maximum,over-limit,blank,text,36.5font and200.4/200.5widths; all committed fields valid and exact. Minimum placed pixels match the pre-fix accepted bitmap exactly; whole Undo/Redo and native project/PNG reopen exact. Four-layout regression fails before and passes after; full692checks, TypeScript/build and diff check pass. Caption workflow/font/wrapping variants remain Partial until separately verified.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for case in ledger['cases']:
 if case['id'] not in ('EDIT-021','EDIT-022','EDIT-023'):continue
 if note not in case['observations']:case['observations'].append(note)
 for name in ('caption-bounds40-verification.json','caption-bounds40-evidence.json','caption-bounds39-before-fix-verification.json','caption-bounds39-before-fix-evidence.json'):
  path='test-results/audit-2026-11-05/mouse/'+name
  if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('after all thirty-nine fixes passes **688 checks','after all forty fixes passes **692 checks').replace('(`all-thirty-nine-fixes/report.json`)','(`all-forty-fixes/report.json`)')
if '## LIVE-040:' not in text:text+='\n## LIVE-040: caption numeric controls and accepted bounds\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
if not any(f['path']=='src/text-tool.ts' for f in env['dirty_source']):env['dirty_source'].append({'path':'src/text-tool.ts'})
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=40;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-forty-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==692
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':40,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()};ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(env['latest_regression'])
