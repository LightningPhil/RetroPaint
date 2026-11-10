"""Record visible controlled failures separately from normal-production evidence."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2]
p=folder/'execution.json';d=json.loads(p.read_text(encoding='utf-8'))
updates={
'FILE-017':('Pass','Visible disposable encoder gate held two first-batch canvases after production projectDocument snapshot. Native later green gesture remained in working file; captured save and native reopened copy whole-document exact to pre-edit state. Three disabled Save clicks produced only one file. Four-layer fixture retains other layers and half opacity.','fault-file-verification.json'),
'FILE-018':('Pass','Visible one-shot null encoder seam produced failure without a file or success claim; Save became usable and native retry produced independently decoded PNG and project. Found misleading PNG→ChoosePNG message; LIVE018 separates resource encode failure from unsupported MIME format and offers retry/smaller picture/SaveProject. Targeted test fails before and passes after; corrected native feedback verified. Raster regions match independent composition within premultiplied rounding; unchanged editable stamp excluded from raster oracle.','fault-file-verification.json'),
'FILE-023':('Pass','Disposable page denied IndexedDB.open and local/sessionStorage methods without changing browser settings. No Draft saved claim; Save a project offered, native painting stayed usable and separate project copies retained changes only on working layer. Repeated strokes did not produce modal interruptions.','fault-file-verification.json'),
'DELIVER-013':('Pass','Both perspective and orthographic cropped-photo/recipe/text/Shell projects saved and reopened with native picker. Each reopened solid Preview/Apply3→2.5mm, camera and non-CAD layers exact; Undo whole-document exact and repeated768×512PNG pixel-exact. Perspective edited STL independently closed/outward35×20×20mm.','cadmix-photo-verification.json'),
'FEATURE-029':('Partial','Visible disposable control stalls one real CAD worker request immediately after started; actual unshortened45s production timer shows practical simplify/retry notice. Restarted worker CheckPrint succeeds35×20×20mm. Saved full document exact except regenerated CAD preview raster; all recipes/camera/nonCADpixels exact. A deliberately injected obsolete message from terminated worker remains unverified.','fault-file-verification.json'),
'ACCESS-013':('Partial','Foreground document.visibilityState verified. Visible API counters for five-second windows: static view2/ui1 draw/clear calls (one picture redraw after measurement click); cursor-only native drag from outside into paper view4/ui9, saved source remains blank; settled water stroke view1184/ui592 continues animation. Active preview branch and exact final-short-stroke oracle remain pending.','mouse-audit-fault-log (1).json'),
'PAINT-020':('Blocked','Supported native mouse API supplies only straight two-endpoint drag and click. It cannot produce a continuous multi-point fast pen curve, coalesced hardware samples or physical pressure. Straight native brushes and independent software regression are covered elsewhere; no physical pen/continuous-curve pass is claimed.',''),
'EDIT-002':('Blocked','Native selection controls are reachable, but the available mouse drag API supports exactly two endpoints and cannot trace a continuous irregular freehand lasso boundary around the required subject. Repeated separate straight drags cannot substitute for this gesture.',''),
'ACCESS-012':('Blocked','Native gesture tests elsewhere complete normally. Available mouse API executes drag atomically and exposes no held-pointer down/move/up sequence, so window blur/pointer cancellation during a held brush/selection/Spiro/crop/CAD gesture cannot be induced faithfully. Synthetic cancellation is supplemental only.','')}
for c in d['cases']:
 if c['id'] not in updates:continue
 c['status'],note,e=updates[c['id']]
 if note not in c['observations']:c['observations'].append(note)
 if e:
  e='test-results/audit-2026-11-05/mouse/'+e
  if e not in c['evidence']:c['evidence'].append(e)
d['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts=Counter(c['status'] for c in d['cases']);print(dict(counts))
p=folder/'README.md';s=p.read_text(encoding='utf-8');s=re.sub(r'Current accounting: \*\*[^\n]+\*\*',f"Current accounting: **{counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Not run']} Not run, {counts['Blocked']} Blocked**",s,count=1)
note='''

## Explicit failure and resource controls

fault-server.py serves production bytes on a random loopback origin with
visible acceptance controls. Original production files remain unchanged.
Seams wrap standard browser APIs, never inspect or mutate application state:
project encoder gate/null, disposable storage denial, one stalled CAD request,
worker WebGL denial and request metadata/canvas-call counters. These runs are
labelled controlled failures, distinct from normal production mouse runs.

verify-fault-files.py checks actual native snapshot/reopen, later working edit,
failure retries and source preservation. The unshortened CAD45s timeout and
successful restarted worker were observed. Obsolete-message injection remains.

LIVE018 corrects a null PNG encoder's misleading “Choose PNG” message. A
targeted independent failure/retry test fails before and passes after; native
fixed feedback/retry, TypeScript/build and all619 regression checks pass.
'''
if '## Explicit failure and resource controls' not in s:s+=note
p.write_text(s,encoding='utf-8')
p=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(p.read_text(encoding='utf-8'))
env['fix_count']=18;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-eighteen-fixes/report.json','passed':619,'failed':0,'page_errors':0}
paths={e['path'] for e in env['dirty_source']}
if 'src/export.ts' not in paths:env['dirty_source'].append({'path':'src/export.ts'})
for entry in env['dirty_source']:entry['sha256']=hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
env['controlled_fault_origin']='http://127.0.0.1:65487/'
p.write_text(json.dumps(env,indent=2)+'\n')
