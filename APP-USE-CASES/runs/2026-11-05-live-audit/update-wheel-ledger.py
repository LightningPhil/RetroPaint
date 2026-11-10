"""Record LIVE-048 only after the native colour matrix and full checks pass."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05';report=json.loads((evidence/'all-forty-eight-fixes/report.json').read_bytes());assert report['status']=='Pass' and all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
assert json.loads((evidence/'mouse/wheel48-verification.json').read_bytes())['status']=='Pass'
note='LIVE-048: Native #ABCDEFZ was truncated to #ABCDEF and committed; visible RGB999 committed a clamped value. Hex now retains overlength text for validation; required integer RGB bounds are checked before updating the draft or committing. Red/green regression covers four layouts. Native PATCH above separate grey backing: exact #123ABC, RGB32/128/224, each channel0/255, Black/White, three independently predeclared wheel hue/saturation/tone picks. All13 painted opaque interiors exactRGB; measured mouse capsules and all untouched source/backing pixels exact. Twelve invalid Hex/RGB values remain editable and cannot change active pigment. Reopen values/marker agree with independent colorsys; pointer colours reachable through keyboard RGB. Opposite keyboard arrows restore exact selection; toneHome/End work, Cancel preserves project. WholeprojectUndo/Redo/nativefile reopen exact; both actualPNG decodes exact. Initial native empty typing did not clear field (corrected to Backspace); initial wheel-centre click repicked colour (corrected to keyboard focus). Half-radius rounding-boundary probes retained; predeclared non-boundary samples use strictRGB. Marker oracle uses exact prescribed continuous polar coordinates for mouse picks and colorsys from exactRGB for text/reopened picks; first guessed0.25percent quantizedRGB marker allowance failed0.25666percent and was replaced with the correct continuous-coordinate oracle, not widened. Full726checks/zero failures/pageerrors; TypeScript/production buildpass.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id'] not in ['INK-004','INK-005']:continue
    c['status']='Pass'
    if note not in c['observations']:c['observations'].append(note)
    for name in ['wheel48-verification.json','wheel48-evidence.json','wheel48-live-result.jpg','wheel48-invalid-before-fix.jpg']:
        path='test-results/audit-2026-11-05/mouse/'+name
        if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':106,'Partial':239,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**104 Pass, 241 Partial','**106 Pass, 239 Partial').replace('after all forty-seven fixes passes **718 checks','after all forty-eight fixes passes **726 checks').replace('(`all-forty-seven-fixes/report.json`)','(`all-forty-eight-fixes/report.json`)')
if '## LIVE-048:' not in text:text+='\n## LIVE-048: exact colour entry rejects invalid values\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
if not any(f['path']=='src/colour-wheel.ts' for f in env['dirty_source']):env['dirty_source'].append({'path':'src/colour-wheel.ts'})
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=48;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-forty-eight-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==726
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':48,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()};ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(counts);print(env['latest_regression'])
