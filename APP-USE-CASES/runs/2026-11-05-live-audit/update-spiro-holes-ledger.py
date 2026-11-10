"""Record the stable hole-count fix while its live matrix continues."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05'
report=json.loads((evidence/'all-thirty-three-fixes/report.json').read_bytes());assert report['status']=='Pass'
assert all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
assert json.loads((evidence/'mouse/spiro-orange-holes-before-measurement.json').read_bytes())['observed_holes']==8
ledgerpath=folder/'execution.json';ledger=json.loads(ledgerpath.read_text(encoding='utf-8-sig'))
note='LIVE-033 namedgearholes were overwritten bycustom-teethformula: purple5ratherthan6,red5ratherthan7,yellow6ratherthan8,green7ratherthan8,orange8ratherthan10. Fixedexactpresetcounts while retainingcustomteethderivedholes. IndependentnativebeforeOrange screenshotcounts8; geometryregressionchecksall44offeredholepenpositions aredistinct. Liveindividual-holematrixusesactualscreenshot-measuredpositions,eachmanualgesturewholeUndo/Redo,sixseparatebankprojectsandnativePNG/projectreopens. Progressandper-bankanalyticverifiersareexplicitlyrecorded; remainingstator/outer/drive/mixed-vectorvariants keepSpirocasesPartial.'
for case in ledger['cases']:
 if case['id']!='PLAY-019':continue
 if note not in case['observations']:case['observations'].append(note)
 for path in ['test-results/audit-2026-11-05/mouse/spiro-holes33-evidence.json','APP-USE-CASES/runs/2026-11-05-live-audit/measure-spiro-holes.py','APP-USE-CASES/runs/2026-11-05-live-audit/verify-spiro-hole-bank.py']:
  if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();ledgerpath.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
readme=folder/'README.md';text=readme.read_text(encoding='utf-8').replace('after all thirty-two fixes passes **662 checks','after all thirty-three fixes passes **663 checks').replace('(`all-thirty-two-fixes/report.json`)','(`all-thirty-three-fixes/report.json`)')
if '## LIVE-033:' not in text:
 text+='\n## LIVE-033: named gears lose offered drawing holes\n\n'+note+'\n\nThe browser screenshot API returns JPEG bytes, even where older evidence files\nuse a.png suffix. Independent image readers detect the format. The new hole\nlocator uses measured luminance above the gear interior to handle chroma\nsubsampling; the original exact-white classifier attempt is retained in tool\nhistory. Native old-orange measurement finds8holes. Each completed bank must\npass its independent curve, history, original-raster, PNG-support and native\nround-trip checks.\n\nThe curve verifier uses delivered pointer coordinates, which Chrome quantizes\nto float32, rather than host-double proposals. Its initial tiny endpoint\nmismatch is retained. The independent PNG support mask includes round caps;\nPillow line endpoints alone are flat. No actual failed artwork was discarded.\n'
readme.write_text(text,encoding='utf-8')
envpath=evidence/'environment.json';env=json.loads(envpath.read_text(encoding='utf-8-sig'));entries={f['path']:f for f in env['dirty_source']};entries.setdefault('src/spiro.ts',{'path':'src/spiro.ts'})
for f in entries.values():f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['dirty_source']=list(entries.values());env['recorded']=ledger['updated'];env['fix_count']=33;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-thirty-three-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0}
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':33,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()}
envpath.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(env['latest_regression'])
