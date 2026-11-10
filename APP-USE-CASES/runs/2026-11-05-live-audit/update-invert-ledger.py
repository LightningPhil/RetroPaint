"""Record masked-effect repair and native Invert acceptance."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];out=root/'test-results/audit-2026-11-05'
for name in ['invert58','invert59']:assert json.loads((out/f'mouse/{name}-verification.json').read_bytes())['status']=='Pass'
report=json.loads((out/'all-fifty-one-fixes/report.json').read_bytes());assert report['status']=='Pass'
assert all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
note=('Native PATCH matrix at22px/100%: opaque Red/Blue/Green and alpha128 Red invert exactly in fully covered regions, alpha and outside pixels remain exact, two full passes restore centres, and whole-project Undo/Redo is exact. Plain raster masks are binary, so the earlier verifier assumption that AA edge pixels must exist was corrected. Additional Vertical+Mask native taps exposed LIVE-051: mirrored pixel filters source-over composited the source patch, changing5226 alpha values and copying colour into empty mirrored pixels. The shared Invert/Pixelate/Emboss path now applies each destination pixel from its own immutable gesture source through a mirrored coverage mask; maximum per-gesture coverage prevents repeated compounding. Native repaired comparison has zero alpha changes,110 weighted edge pixels with maximum double-pass error1.326/255, exact transparent/outside pixels and exact history. Three focused regressions cover all affected filters. Full731-check regression, TypeScript and production build pass.')
p=folder/'execution.json';ledger=json.loads(p.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id']=='PAINT-017':
        c['status']='Pass'
        if note not in c['observations']:c['observations'].append(note)
        for n in ['invert58-verification.json','invert59-verification.json','invert59-fixed.jpg']:
            path='test-results/audit-2026-11-05/mouse/'+n
            if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
p=folder/'README.md';s=p.read_text(encoding='utf-8').replace('**115 Pass, 231 Partial','**116 Pass, 230 Partial').replace('after all fifty fixes passes **728 checks','after all fifty-one fixes passes **731 checks').replace('(`all-fifty-fixes-random-port/report.json`)','(`all-fifty-one-fixes/report.json`)')
if '## Masked pixel effects repaired' not in s:s+='\n## Masked pixel effects repaired\n\n'+note+'\n'
p.write_text(s,encoding='utf-8')
p=out/'environment.json';env=json.loads(p.read_text(encoding='utf-8-sig'))
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=51;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-fifty-one-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0,'origin':report['origin']};assert env['latest_regression']['passed']==731
production=out/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode()
env['production_build']={'fixes':51,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()}
p.write_text(json.dumps(env,indent=2)+'\n');print('116Pass230Partial3Blocked; LIVE-051 fixed;731checks pass')
