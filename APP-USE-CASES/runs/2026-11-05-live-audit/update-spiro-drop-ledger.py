"""Record verified fixes without closing outstanding Spiro matrix variants."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05'
assert json.loads((evidence/'mouse/spiro-drop-verification.json').read_bytes())['status']=='Pass'
report=json.loads((evidence/'all-thirty-two-fixes/report.json').read_bytes());assert report['status']=='Pass'
assert all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
ledgerpath=folder/'execution.json';ledger=json.loads(ledgerpath.read_text(encoding='utf-8-sig'));cases={c['id']:c for c in ledger['cases']}
notes={
 'PLAY-017':'Native fresh960x640White/Blueink: sixgear taps, invalid/valid geardrops, interrupted gearcapture andkeyboardselection preserve wholeproject andblankPNGexact throughnative precondition reopening. Opening/closingkit andreturningBrushes producesnoart. Additional offered-hole/drive variants remain under the shared Spiro matrix; case stays Partial.',
 'PLAY-019':'LIVE-030 actual off-paperOrangegear drop wrongly replacedRed. Firstposguardfix stillfailed becausepointercapture producesaClickafterdrop. Completefix ignorespointer-originClick becausepointerupalreadyhandlesit, retainingkeyboard/ATClick. Liveoff-paper andon-paper/outsideRingdrops retainRed; validcentredrop selectsOrange; all6taps work; capturelossduring6sheldpress clearsghostandretainsOrange before/afterrelease. Four-layout regression alsoincludes thecapturedClicksequence. Alloffered-hole/pathvariants stillpending.',
 'ACCESS-006':'LIVE-031 sixSpirogearbuttons exposedselectedclassbutnoaria-pressed. Allsixnowannouncecorrecttrue/false states, verifiedagainstactualpickedhighlightfor6nativetaps. Actualscreen-readerhardware remainsunavailable; case remainsPartial.',
 'ACCESS-007':'LIVE-032 nativeSpaceonfocusedOrangegear leftPinkselected becausepaperpan swallowedthebuttonkey; Enterworked. Spacepan nowexcludesbuttons/links/summary/tabsandtyping. NativeSpace selectsOrange,EnterselectsRed; focusedcanvasSpace+nativeWindowsdrag stillmovespaper-45.4545/+45.4545CSS during6skeyholdwithoutchangingwholeprojectorPNG. Four-layout red/green checks preservebuttondefaultactivation andcanvaspan.'
}
for key,note in notes.items():
 case=cases[key]
 if note not in case['observations']:case['observations'].append(note)
 for path in ['test-results/audit-2026-11-05/mouse/spiro-drop-verification.json','APP-USE-CASES/runs/2026-11-05-live-audit/verify-spiro-drop.py']:
  if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();ledgerpath.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
readme=folder/'README.md';text=readme.read_text(encoding='utf-8').replace('after all twenty-nine fixes passes **654 checks','after all thirty-two fixes passes **662 checks').replace('(`all-twenty-nine-fixes-final/report.json`)','(`all-thirty-two-fixes/report.json`)')
if '## LIVE-030' not in text:
 text+='\n## LIVE-030 to LIVE-032: Spiro drop safety and keyboard selection\n\n'+'\n\n'.join(notes.values())+'\n\nThe incomplete position-only fix and its successful but insufficient synthetic\ncheck are retained. Native input exposed the extra captured Click; the regression\nnow includes that event. The first successful event helper captured an old REPL\nobject after reassignment, so its JSON lacked the three successful drag records;\nthat diagnostic is retained and the three actual drags were repeated, saving to\n`spiro-drop-fixed32.json` explicitly. `verify-spiro-drop.py` passes.\n\nThe earlier31-fix full run reloaded during later edits and is historical only.\nThe stable32-fix full run hashes the final sources and passes662checks with zero\nfailures/pageerrors. TypeScript/build pass. Spiro acceptance cases remainPartial\nuntil the required hole/drawing variants are verified.\n'
readme.write_text(text,encoding='utf-8')
envpath=evidence/'environment.json';env=json.loads(envpath.read_text(encoding='utf-8-sig'));entries={x['path']:x for x in env['dirty_source']};entries.setdefault('src/paper-view.ts',{'path':'src/paper-view.ts'})
for f in entries.values():f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['dirty_source']=list(entries.values());env['recorded']=ledger['updated'];env['fix_count']=32;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-thirty-two-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0}
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':32,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()}
envpath.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(dict(Counter(c['status'] for c in ledger['cases'])));print(env['latest_regression'])
