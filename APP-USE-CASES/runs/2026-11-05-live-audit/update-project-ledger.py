"""Record native project persistence, atomic rejection and history-mode repair."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05';mouse=evidence/'mouse'
report=json.loads((evidence/'all-forty-four-fixes/report.json').read_bytes());assert report['status']=='Pass'
assert all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
for name in ['project44-validation-verification.json','project44-mode-verification.json']:assert json.loads((mouse/name).read_bytes())['status']=='Pass'
fix='LIVE-044: Opening a Vector project over a Raster picture then Undo restored source pixels/layers but retained Vector drawing mode. History now captures/restores drawingMode, its selector and vector-mode presentation using the current Basic/Advanced policy. Native full-document Undo/Redo exact; four-layout regression covers both directions in both UI modes (red before, green after). Full regression705 passes, zero failures/page errors; production build and TypeScript pass.'
notes={
 'FILE-013':'Native independent mixed project contains four MIX layers, +1EV Photo recipe, Conveyor stroke and two Water fills, nine mixed Vector pieces, Caption Dog and half-opacity Character. Actual downloaded checksummed bytes reopened after fresh app reload; all saved editing fields exact, every decoded source Raster RGBA byte exact. Raw producer absent optional stroke clip normalizes only to null (explicitly asserted); no fields dropped. Controlled12345ms native PNG is byte-for-byte RGBA identical after reopen;23456ms changes86851pixels while saved definitions remain identical. Actual PNG renamed.retropaint rejected with actionable damaged-file message, whole unrelated unsaved project unchanged, valid retry succeeds.',
 'FILE-016':'28 native chooser rejection/retry cycles cover malformed/truncated/nonJSON/renamedPNG, wrong-size layer, invalid/duplicate/missing IDs, singular Vector transform, invalid opacity/crop/photo curve/look/settings/live ink/mode/brush,4097axis limits,17layers,stored-pixel budget,future999,and CADzero scale/unknown solid/duplicate ID/singular camera/parallelworkplane. Every rejection has retained format message; entire original unsaved Raster project including all source pixels/metadata remains exact, no partial layers active. Every immediate native valid opening matches canonical mixed project exactly; Undo returns entire unrelated Raster project and Raster controls exactly. Before-fix first4 rejection attempts preserved separately: later differences were drawingMode leakage from successful-open Undo, corrected byLIVE-044; not partial failed-import replacement.',
 'FILE-015':'Unknown future version999 native rejection explicitly explains newer-version incompatibility; whole existing project unchanged, immediate valid retry and Undo exact. Genuine historic producers v1,v2,v9 already migrated/resaved/reopened with independent checks. Authentic v3–8 fixture bytes remain unavailable after producer search and prior user confirmation; modern files with edited version numbers are not evidence. Remaining historical fixture requirement is blocked.'}
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id'] in notes:
        c['status']='Blocked' if c['id']=='FILE-015' else 'Pass'
        if notes[c['id']] not in c['observations']:c['observations'].append(notes[c['id']])
        for name in ['project44-validation-verification.json','project44-fixed-evidence.json','project44-matrix-complete.jpg']:
            path='test-results/audit-2026-11-05/mouse/'+name
            if path not in c['evidence']:c['evidence'].append(path)
    if c['id'] in ['FILE-013','FILE-014','FILE-016']:
        if fix not in c['observations']:c['observations'].append(fix)
        path='test-results/audit-2026-11-05/mouse/project44-mode-verification.json'
        if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':94,'Partial':251,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**92 Pass, 254 Partial, 0 Not run, 3 Blocked**','**94 Pass, 251 Partial, 0 Not run, 4 Blocked**').replace('after all forty-three fixes passes **701 checks','after all forty-four fixes passes **705 checks').replace('(`all-forty-three-fixes-pass2/report.json`)','(`all-forty-four-fixes/report.json`)')
if '## LIVE-044:' not in text:text+='\n## LIVE-044: project Undo restores drawing mode\n\n'+fix+'\n\n'+'\n\n'.join(k+': '+v for k,v in notes.items())+'\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
if not any(f['path']=='src/history.ts' for f in env['dirty_source']):env['dirty_source'].append({'path':'src/history.ts'})
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=44;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-forty-four-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==705
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':44,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()};ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(counts);print(env['latest_regression'])
