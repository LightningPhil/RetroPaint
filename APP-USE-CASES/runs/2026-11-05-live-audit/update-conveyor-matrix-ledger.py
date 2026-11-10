"""Record LIVE-047 and close the native conveyor acceptance matrix."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05';report=json.loads((evidence/'all-forty-seven-fixes/report.json').read_bytes());assert report['status']=='Pass' and all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
for name in ['conveyor46-replacement-verification.json','conveyor46-matrix-verification.json','single47-verification.json']:assert json.loads((evidence/'mouse'/name).read_bytes())['status']=='Pass'
fix='LIVE-047: Nativeone-stopYellowbeltpaintedpreviousordinaryRed, andpigmentpreviewretainedmulticolourgradient. Singlelive stopnowresolvesitsownsolidpigmentforbrush/fill/editablepieces/staticSpray, whileemptybeltkeepsordinaryfallback. Currentink/pointer/brushpreviewsuseeffectivepigmentandrefreshonAdd/Clear/remove/replace. NativebeforeRedfailureandfixedYellow/emptyRedcapsulesretained; all9oldlive definitions anduntouchedRasterpixels exact. WholeUndo/Redo/nativeproject/controlledPNG reopens exact. Redpaintingandfour-layoutpreview regressionsgreenafterfix, includingbucketandVectorfill,emptyfallbackandnoexistingpicturemutation. Full718checks,zero failures/pageerrors; TypeScript/buildpass.'
note='NativePLAYconveyormatrix complete: allcounts0..8addedandremoved; fullmiddlePurplemouse/GoldShiftF10replacementandninthAddguard; speed-8/0/+8eachSnap/JumpandOoze/Blend; prescribed3stopRedYellowBlueinbothmodes; ordinaryRedbeforearmingandGreenafterdisarming. IndependentcyclicphaseandroundedRGBinterpolationmatchevery5x5opaqueendcapat12345and23456ms; zeroSnapcontainsall8chosenstops,Oozeblendsnon-stopcolours. Only4nonzerospeedstrokeschange(42912pixels), everyotherRGBAbyte/staticmarkunchanged, all11capturedlivedefinitionspreservedthroughlaterpalette/mode/speedchangesanddisarming.24rapidmodechangeskeep1rAF/2timeouts/0intervals; normal-clocktwoactualPNGscontinueanimatingwithoutdrawingandentireprojectunchanged. FinalprojectandbothcontrolledPNGframes native-reopenexact.0/1boundaryfixedbyLIVE-047: emptyRedfallback, singleYellowactualYellow, matchingpublicpreviewstyles. Initialradius13/integer-gridfootprinthypothesisretained; intentionalLiveMarkerhaloradius13.992plus1AAwithpixelcentresaccountsfor1916initialoutsidechanges, noRGBtolerancerelaxed. NativeHTMLendpointdragsdidnotestablishdrop; actualreplacementpassesviaRightclick/ShiftF10, componentHTMLdropcoveragekeptseparate.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id'] not in ['INK-015','INK-016','INK-017','INK-019']:continue
    c['status']='Pass'
    for text in [note,fix]:
        if text not in c['observations']:c['observations'].append(text)
    for name in ['conveyor46-matrix-verification.json','conveyor46-evidence.json','conveyor46-initial-footprint-hypothesis.json','single47-verification.json','single47-evidence.json','conveyor47-final-normal-clock.jpg']:
        path='test-results/audit-2026-11-05/mouse/'+name
        if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':103,'Partial':242,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**99 Pass, 246 Partial','**103 Pass, 242 Partial').replace('after all forty-six fixes passes **713 checks','after all forty-seven fixes passes **718 checks').replace('(`all-forty-six-fixes-pass2/report.json`)','(`all-forty-seven-fixes/report.json`)')
if '## LIVE-047:' not in text:text+='\n## LIVE-047: single-stop ink matches its colour\n\n'+fix+'\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
for path in ['src/materials.ts','src/brush-previews.ts','src/draw.ts']:
    if not any(f['path']==path for f in env['dirty_source']):env['dirty_source'].append({'path':path})
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=47;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-forty-seven-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==718
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':47,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()};ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(counts);print(env['latest_regression'])
