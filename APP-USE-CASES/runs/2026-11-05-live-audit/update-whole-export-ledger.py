"""Close whole-image transforms after live correction of export round-trip drift."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05';report=json.loads((evidence/'all-forty-three-fixes-pass2/report.json').read_bytes());assert report['status']=='Pass' and all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
for name in ['edit-whole42-verification.json','export-canonical43-verification.json']:assert json.loads((evidence/'mouse'/name).read_bytes())['status']=='Pass'
note='EDIT-019:20nativeindependentcopies oflabelledPATCHand4layerMIX coverH/Vflips,+90/-90/45turns,+/-20Xskew,+/-15Yskew,andcombined20X/-15Y. AllsourceRasterRGBAbytesexactforflips/quarterturns; everylayerasymmetriccorner, safelyuniformaffineinterior,clearexterior,analyticbounds,unchangedmetadata,andretainedDogstampdefinition/matrixverified. All20wholeprojectUndoRedo/nativefile-reopens exact. PATCHquarter/flipcompositePNGexact; MIXdirectemoji re-render differsinsideanalyticDogboundsplus2pxAA, withallRasterbytesandallothercompositepixelsexact. No kernelidentityclaimfornonuniformarbitraryresamplingboundaries. Original5skewPNG-reopenmismatchesretainedandcorrectedbyLIVE-043; sixnativefixedretestsallPNG/projectexact.'
fix='LIVE-043: nativewhole-image skews exposed1–4PNGpixels changing1–2channellevels afterprojectreopen despiteunchangedprojectdata. Export now snapshots sourceRGBA and readsbackthetemporarystoredresult oncebeforecompositing, matchingthecanonicalpixelsretainedbyprojects. Initialone-readbackattemptfailedallfiveaffectedcasesandisretained. Correctedtwo-readbackattempt passesallfiveplusnegative-skewcontrolonfreshMIX/PATCHoperations,withoutchanginganysourceprojectbytes; sixrealnativeproject/PNG reopensexact. Headlessgenerated-blockregressionpassesbeforeaswellasafterandisnottheredproof; liveproductiondownloadsprovidethatproof. Full701checks,TypeScript/build,diffcheckpass. Extraexport-onlyreadbackhasaboundedfull-layerpixelcopycost; drawing/historysourceunchanged.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));case=next(c for c in ledger['cases'] if c['id']=='EDIT-019');case['status']='Pass'
for item in [note,fix]:
 if item not in case['observations']:case['observations'].append(item)
for name in ['edit-whole42-verification.json','edit-whole42-evidence.json','edit-whole42-composite-transpose-hypothesis.json','export-canonical43-verification.json','export-canonical43-evidence.json','export-canonical43-live-result.jpg']:
 path='test-results/audit-2026-11-05/mouse/'+name
 if path not in case['evidence']:case['evidence'].append(path)
for item in ledger['cases']:
 if item['id'] not in ['FILE-006','FILE-007','FILE-014']:continue
 if fix not in item['observations']:item['observations'].append(fix)
 path='test-results/audit-2026-11-05/mouse/export-canonical43-verification.json'
 if path not in item['evidence']:item['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':85,'Partial':261,'Blocked':3}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**84 Pass, 262 Partial','**85 Pass, 261 Partial').replace('after all forty-two fixes passes **697 checks','after all forty-three fixes passes **701 checks').replace('(`all-forty-two-fixes/report.json`)','(`all-forty-three-fixes-pass2/report.json`)')
if '## LIVE-043:' not in text:text+='\n## LIVE-043: stable export pixels after project reopen\n\n'+fix+'\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
if not any(f['path']=='src/layers.ts' for f in env['dirty_source']):env['dirty_source'].append({'path':'src/layers.ts'})
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=43;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-forty-three-fixes-pass2/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==701
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':43,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()};ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(counts);print(env['latest_regression'])
