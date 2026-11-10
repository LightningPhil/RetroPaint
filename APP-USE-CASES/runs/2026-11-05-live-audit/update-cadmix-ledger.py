"""Close mixed-project live reopening and record the camera inspection fix."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];evidence=root/'test-results/audit-2026-11-05'
report=json.loads((evidence/'all-forty-five-fixes/report.json').read_bytes());assert report['status']=='Pass' and all(hashlib.sha256((root/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in report['source_files'])
for name in ['cadmix44-reopen-verification.json','camera45-inspection-verification.json']:assert json.loads((evidence/'mouse'/name).read_bytes())['status']=='Pass'
fix='LIVE-045: Native CADMIX saved Top orthographic camera changed upY to upZ and nudged position merely opening/closing workshop. Four-layout minimal no-camera-input regression reproduces. Tool switching no longer resets camera.up; OrbitControls is rebuilt when camera/plane basis changes (its orbit quaternion is fixed at construction), disposing prior native listeners. Perspective camera reconstruction also restores saved span through zoom, preserving framing when changing projections. Native canonical repeated inspection whole-project/PNG exact; native5mm solid move/UndoRedo retains exact camera. Focused regression and full709checks pass; TypeScript/build pass. Firstpatchstillfailedperspective-span case; retained before/firstattempt/finalreports.'
note='FILE-014 native CADMIX source has four layers, editable Cube/Cylinder/Join/3mmShell history and callout. Actual picker reopen/resave restores layer order,target,allrecipe/object/body/camera definitions exactly in both orthographic and perspective variants. +1EV Photo recipe and sharedcrop96,64,768,512 reopen with exactproject and768x512RGBA. Afterreopen: Photoexposure+.5,22pxBluePaperstroke,andVectorcallout+80,-40 are independently scoped to intended fields/sourceRGBA, with entire Undo/Redo states exact; combinededitedproject/PNG realreopenexact. Solid5mm edit/UndoRedo retestedafterLIVE-045 preserves exactcamera. Photo drafts committed withDone, workshop deliberately closed beforeSave. Fixturecaveats explicitly verified: booleanpaperflagsbecomenull (notcolourdefinitions); everyRasterRGBAexact. SyntheticTopcameraassignmentretainedolderperspectivebitmap, sofirstworkshopinspectionrebuildsexpectedTopcache; canonicalsecondinspectionproject/PNGexact. Originalfailedinput/cropentryattempts retained andnotcounted; nativecoordinateentrycompletedboth.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id']!='FILE-014':continue
    c['status']='Pass'
    for text in [note,fix]:
        if text not in c['observations']:c['observations'].append(text)
    for name in ['cadmix44-reopen-verification.json','camera45-inspection-verification.json','cadmix44-perspective.jpg','cadmix44-orthographic-reopened.jpg']:
        path='test-results/audit-2026-11-05/mouse/'+name
        if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':95,'Partial':250,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**94 Pass, 251 Partial','**95 Pass, 250 Partial').replace('after all forty-four fixes passes **705 checks','after all forty-five fixes passes **709 checks').replace('(`all-forty-four-fixes/report.json`)','(`all-forty-five-fixes/report.json`)')
if '## LIVE-045:' not in text:text+='\n## LIVE-045: preserve saved camera during workshop inspection\n\n'+fix+'\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');ep=evidence/'environment.json';env=json.loads(ep.read_text(encoding='utf-8-sig'))
for path in ['src/cad-camera.ts','src/cad-viewport.ts']:
    if not any(f['path']==path for f in env['dirty_source']):env['dirty_source'].append({'path':path})
for f in env['dirty_source']:f['sha256']=hashlib.sha256((root/f['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=45;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-forty-five-fixes/report.json','passed':sum(s['passed'] for s in report['suites'])+1,'failed':0,'page_errors':0};assert env['latest_regression']['passed']==709
production=evidence/'production-seven-fixes';index=(production/'index.html').read_bytes();entry=re.search(rb'<script[^>]+src="([^"]+)"',index).group(1).decode();env['production_build']={'fixes':45,'index_sha256':hashlib.sha256(index).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((production/entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()};ep.write_text(json.dumps(env,indent=2)+'\n',encoding='utf-8');print(counts);print(env['latest_regression'])
