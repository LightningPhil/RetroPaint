"""Record the native FILL matrix and visible tolerance fix after verification."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05';report=json.loads((evidence/'all-forty-nine-fixes/report.json').read_bytes());assert report['status']=='Pass' and all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
assert json.loads((evidence/'mouse/fill49-verification.json').read_bytes())['status']=='Pass';visible=json.loads((evidence/'mouse/fill49-visible-value.json').read_bytes());assert all(r['visible'] and str(r['requested'])==r['output']==r['input'] for r in visible)
note='Exact prescribed320x240FILL family natively executed on independent copies with separate unrelated grey backing. Closedoutline mask14161pixels; one-pixel(80,20)gap intentionally propagates76321pixels includingoutside,blacklinepreserved. Antialiased13689andtransparent14161 masks; disconnected40x40matchingisland staysunchanged in closedvariants. Deterministicneutral±8noise: tolerance0/23fills4760middle-stripepixels,24/200fills14161wholeinterior. Independent four-neighbourqueue uses observedRGBA-L1<=threshold metric and predeclaredmasks, exactRGBAfor everyfilled/exteriorpixel. Each8case wholeprojectUndo/Redo exact; unrelatedlayer/metadataunchanged, max/minfinishwithoutfreeze. Nativefinalproject/PNG reopensexact. Transparentfixtureimport canonicalizes14161alpha0hiddenRGB232to0; exactalphaandallvisiblebytesretained, allnativebaseline/fill/historycomparisonsrawRGBAexact. LIVE-049: tolerance had no visible number; output now displays exactsetting, native0/23/24/200 allvisibleandmatchinput. Full726regressionchecks,zero failures/pageerrors; TypeScript/productionbuildpass.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id'] not in ['INK-010','INK-011']:continue
    c['status']='Pass'
    if note not in c['observations']:c['observations'].append(note)
    for name in ['fill49-verification.json','fill49-evidence.json','fill49-visible-value.json','fill49-visible-value.jpg']:
        path='test-results/audit-2026-11-05/mouse/'+name
        if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':108,'Partial':237,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**106 Pass, 239 Partial','**108 Pass, 237 Partial').replace('after all forty-eight fixes','after all forty-nine fixes').replace('(`all-forty-eight-fixes/report.json`)','(`all-forty-nine-fixes/report.json`)')
if '## LIVE-049:' not in text:text+='\n## LIVE-049: visible tolerance and exact FILL boundaries\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=49;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-forty-nine-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==726
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':49,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()};ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(counts)
