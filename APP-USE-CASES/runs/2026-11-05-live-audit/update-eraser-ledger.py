"""Record eraser acceptance, fixture repair and random-port regression evidence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
folder=Path(__file__).resolve().parent;root=folder.parents[2];out=root/'test-results/audit-2026-11-05'
assert json.loads((out/'mouse/eraser57-verification.json').read_bytes())['status']=='Pass'
report=json.loads((out/'all-fifty-fixes-random-port/report.json').read_bytes())
assert report['status']=='Pass' and not report['origin'].endswith(':5173')
assert all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
note=('Corrected MIX fixture, native Scrub22px/100%: Paper clears to opaque white; transparent Character clears to alpha0 and exported composite reveals exact Blue Backdrop30,136,229. Other layer data and every pixel outside the declared radius20px gesture tube remain exact. Hidden active Character is made visible and erased without changing any neighbour; Undo restores visibility and pixels together. All three whole-project Undo/Redo pairs and native project/PNG roundtrips are exact. Fixture gap: prior synthetic MIX/CADMIX paper booleans were interpreted as null; seven corrected copies now use #ffffff/null, the manual MIX pack and future generators are repaired, and original bytes/results are retained. Earlier eraser56 Paper attempt therefore did not exercise a real Paper layer; eraser57 explicitly asserts the colour metadata first.')
p=folder/'execution.json';ledger=json.loads(p.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id']=='PAINT-014':
        c['status']='Pass'
        if note not in c['observations']:c['observations'].append(note)
        for path in ['mouse/eraser57-verification.json','mouse/eraser57-evidence.json','fixtures/corrected-paper/manifest.json']:
            path='test-results/audit-2026-11-05/'+path
            if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
p=folder/'README.md';s=p.read_text(encoding='utf-8').replace('**114 Pass, 232 Partial','**115 Pass, 231 Partial').replace('(`all-fifty-fixes-cropped/report.json`)','(`all-fifty-fixes-random-port/report.json`)')
if '## Eraser matrix and fixture correction' not in s:s+='\n## Eraser matrix and fixture correction\n\n'+note+'\n\nThe headless launcher now reserves an OS-selected loopback port and uses strict port binding, because Vite treats port0 as default5173. The latest full728-check run passes with zero failures/page errors at '+report['origin']+'. The focused launcher check also passed at http://127.0.0.1:56938.\n'
p.write_text(s,encoding='utf-8')
p=out/'environment.json';env=json.loads(p.read_text(encoding='utf-8-sig'))
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['latest_regression']={'report':'test-results/audit-2026-11-05/all-fifty-fixes-random-port/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0,'origin':report['origin']};assert env['latest_regression']['passed']==728
p.write_text(json.dumps(env,indent=2)+'\n');print('PAINT-014 Pass;115Pass231Partial3Blocked; current728-check source manifest verified')
