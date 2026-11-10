"""Record complete live pair coverage, tooth bounds and the stable 36-fix build."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05'
report=json.loads((evidence/'all-thirty-six-fixes/report.json').read_bytes());assert report['status']=='Pass'
assert all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
pairs=json.loads((evidence/'mouse/spiro-pairs-verification.json').read_bytes());assert pairs['status']=='Pass' and len(pairs['combinations'])==30 and not pairs['missing_pairs_within_observed_levels'] and len(pairs['sha256'])==162
assert sum(c['native_reopened'] for c in pairs['combinations'])==6
assert json.loads((evidence/'mouse/spiro-limits36-verification.json').read_bytes())['status']=='Pass'
ledgerpath=folder/'execution.json';ledger=json.loads(ledgerpath.read_text(encoding='utf-8-sig'))
note='Completed live 30-combination gear×outer plan across all six gears, five named outer counts, four stators, Manual/Auto and Raster/Vector. Independent verification finds no missing pair among all five factors, checks every stored vector point analytically, raster/project/export agreement, full expected PNG curve support, whole per-case Undo/Redo and six native project/PNG reopens. 162 actual downloads retained. Together with all44 individual-hole drawings and valid/rejected/capture-loss gear-drop evidence, this completes PLAY-019 required options and branches. This is pairwise coverage, not full Cartesian coverage.'
limits='LIVE-036: accepted171/172inner teeth atouter180 were marked invalid byfixedHTMLmax170. Max now followsouter−8, initial88. Four-layout red/green and26actual native input checks cover min/max, decimals, negative/empty/huge inputs, shrinking a ring and oversized named gear. Constrained40/32 andmaximum180/172 actually draw; all34,381and167,665stored points independently fit configured curves, respectively. Whole Undo/Redo andnativeproject/PNGroundtrip exact; earlier artwork unchanged. PLAY-021 stator/ratio options, predictable paths and invalid combinations are complete.'
for case in ledger['cases']:
 if case['id'] not in ['PLAY-017','PLAY-018','PLAY-019','PLAY-020','PLAY-021','PLAY-022']:continue
 for text in [note,limits]:
  if text not in case['observations']:case['observations'].append(text)
 for path in ['test-results/audit-2026-11-05/mouse/spiro-pairs-verification.json','test-results/audit-2026-11-05/mouse/spiro-pair35-evidence.json','test-results/audit-2026-11-05/mouse/spiro-limits36-verification.json']:
  if path not in case['evidence']:case['evidence'].append(path)
 if case['id'] in ['PLAY-019','PLAY-021']:case['status']='Pass'
ledger['updated']=datetime.now(timezone.utc).isoformat();ledgerpath.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts=Counter(c['status'] for c in ledger['cases']);assert counts==Counter({'Pass':60,'Partial':286,'Blocked':3})
readme=folder/'README.md';text=readme.read_text(encoding='utf-8').replace('**58 Pass, 288 Partial, 0 Not run, 3 Blocked**','**60 Pass, 286 Partial, 0 Not run, 3 Blocked**').replace('after all thirty-five fixes passes **672 checks','after all thirty-six fixes passes **676 checks').replace('(`all-thirty-five-fixes-final/report.json`)','(`all-thirty-six-fixes/report.json`)')
if '## LIVE-036:' not in text:
 text+='\n## LIVE-036: inner-tooth bounds and completed pairwise matrix\n\n'+note+'\n\n'+limits+'\n\nFailed test actions and oracle diagnostics are retained. Pink105 first dragged the Cross stator fromsource360,320 rather than cranking; its original files remain and a new -v2 attempt uses450,320. A one-pixel PNG-mask gap lay1.30pxfromtheactual3pxpen centreline; the independent mask now unions round support at the unchanged3.5pxradius. Square/Cross corner and curve-self-intersection projections now try multiple analytic branches without loosening fit tolerance. Raster hover can change the offered hole: the verifier requires one unique offered-hole curve consistent with the actual pixels, rather than assuming hole2; reports label the inferred hole. A later Green screenshot classifier returned25components, so that measurement is retained as diagnostic and is not proof of a particular selected hole. The first post-fix numeric evidence helper retained an older array binding; the complete26-case native sequence was repeated with an explicit evidence argument, preserving the incomplete file.\n'
readme.write_text(text,encoding='utf-8')
envpath=evidence/'environment.json';env=json.loads(envpath.read_text(encoding='utf-8-sig'))
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=36;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-thirty-six-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==676
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':36,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()}
envpath.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(dict(counts));print(env['latest_regression'])
