"""Prepare genuine fixtures and human-input instructions without desktop control."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,html
root=Path(__file__).resolve().parents[3];audit=root/'test-results/audit-2026-11-05';kit=audit/'manual-blockers';kit.mkdir(exist_ok=True)
old=root/'APP-USE-CASES/runs/2026-10-19-full-audit';manifest=json.loads((old/'legacy/producer-manifest.json').read_bytes());files=[]
def retain(source,name):
    data=source.read_bytes();target=kit/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);files.append({'path':name,'source':str(source),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
for producer in manifest['producers']:
    source=old/producer['fixture'];assert hashlib.sha256(source.read_bytes()).hexdigest()==producer['fixture_sha256'];retain(source,'legacy/'+source.name)
retain(audit/'mouse/mouse-audit-play-960-baseline.retropaint','PLAY.retropaint')
retain(audit/'fixtures/corrected-paper/mix-half-character.retropaint','MIX.retropaint')
retain(audit/'mouse/photo-natural-original.jpg','PHOTO.jpg')
for name in ['drag-source.png','corrupt.png','unsupported.txt']:retain(audit/'drop-fixtures'/name,'drop/'+name)
history=subprocess.check_output(['git','log','--all','--format=%H %s','--','src/project.ts'],cwd=root,text=True)
(kit/'producer-history.txt').write_text(history,encoding='utf-8')
cases=[
('PAINT-020','Fast continuous curve','Open PLAY.retropaint. Choose Squeaky Marker, 22 px, Strength100%. Save a before project. With your mouse held down, draw one fast looping curve; save project and PNG, Undo, save undone, Redo and save redone. Repeat with a real pen if available, recording device and pressure support; repeat while animation is active. Check continuity and unchanged960×640 dimensions. Coalesced-event fallback and input samples still require the instrumentation/software checks recorded in the main protocol. A mouse pass does not certify physical pen input.','Ready for human mouse input; physical pen branch needs hardware.'),
('EDIT-002','Irregular lasso','Open PHOTO.jpg, save a before project, choose Select then Lasso. Trace an irregular subject continuously, move it, and Place. Save project and PNG; Undo and save undone; Redo and save redone. Repeat on fresh copies ending near the starting point and releasing outside the paper. Retain screenshots of the outline before moving. Check that only the enclosed pixels move and no enormous stray region appears.','Ready for human mouse input.'),
('FILE-005','Real file drop','Open MIX.retropaint and save before. In Windows File Explorer open the drop folder beside the browser. Drag drag-source.png from Explorer onto the paper. Check the browser stays on RetroPaint, position the insertion and Place; save project and PNG, Undo/save undone, Redo/save redone. On independent fresh copies, drop corrupt.png and unsupported.txt. Check an explanation, no stuck overlay and no document change, then retry the valid image. Save after each rejection for whole-project comparison.','Ready for human cross-window input.'),
('FILE-015','Authentic earlier versions','The legacy folder contains the three hash-verified historical UI downloads v1,v2,v9. Open each, save upgraded project and PNG, reopen the upgraded project and save both again. Compare original editable content and current round trips. Existing audit evidence already covers these and future-version999 rejection. Authenticv3–8 remain unavailable: supply an original project or the historical producer source to cover them. Do not change a modern file version field and count that as historical evidence.','Partly prepared; authenticv3–8 remain blocked.')]
sections=''.join('<section><h2>'+cid+' — '+title+'</h2><p><strong>'+status+'</strong></p><p>'+html.escape(steps)+'</p></section>' for cid,title,steps,status in cases)
links=''.join('<li><a href="'+html.escape(f['path'])+'">'+html.escape(f['path'])+'</a></li>' for f in files)
(kit/'START.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>RetroPaint — manual blocker test pack</title><style>body{font:18px/1.6 system-ui;max-width:950px;margin:40px auto;padding:20px;color:#182532}section{border-top:1px solid #ccc;margin-top:30px}a{color:#164fa0}</style><h1>Four blocked cases: preparation for human testing</h1><p>This pack does not mark any case passed. Use the current RetroPaint build on its dedicated test origin. Open project files through More → File → Open project, and PHOTO through Open image. Keep originals untouched. Name downloads with the case ID and step so independent comparison is possible.</p>'+sections+'<h2>Fixtures</h2><ul>'+links+'</ul><p>Checksums and provenance: <a href="manifest.json">manifest.json</a>. Record browser version, input device, result, filenames and any failure in results.json. Testing output remains separate from fixture originals.</p></html>',encoding='utf-8')
(kit/'manifest.json').write_text(json.dumps({'prepared':datetime.now(timezone.utc).isoformat(),'files':files,'missing_authentic_versions':[3,4,5,6,7,8],'desktop_control_used':False},indent=2)+'\n',encoding='utf-8')
results=kit/'results.json'
if not results.exists():results.write_text(json.dumps({'cases':[{'id':cid,'status':'Not run in this pack','browser':'','input_device':'','evidence_files':[],'observations':[]} for cid,*_ in cases]},indent=2)+'\n',encoding='utf-8')
for f in files:assert hashlib.sha256((kit/f['path']).read_bytes()).hexdigest()==f['sha256']
print(f'Prepared and hash-verified {len(files)} fixtures: {kit / "START.html"}')
