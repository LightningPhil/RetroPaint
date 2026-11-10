"""Add native delivery and real duplicate-tab evidence; record crop repair."""
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,re
from pathlib import Path
folder=Path(__file__).resolve().parent;root=folder.parents[2]
p=folder/'execution.json';d=json.loads(p.read_text(encoding='utf-8'))
updates={
'FILE-022':('Pass','Actual Chrome tab-menu Duplicate cloned the starting context. Different settled blue/green edits, native reload/resume and saved files remain distinct and whole-project exact to their own pre-refresh copy. Three neighbouring layers and half-opacity preserved; duplicate test tab closed.','tab-isolation-verification.json'),
'DELIVER-001':('Partial','Native empty-stage left drag orbited, wheel zoomed, Fit and Pin persisted the camera in the delivery project. Read-only file comparison proves all solid definitions unchanged. Right-button drag cannot be produced by the supported native drag API, so pan remains unverified.','delivery-set-verification.json'),
'DELIVER-010':('Pass','Native cropped CADMIX background/foreground visibility, surrounding-picture toggle and Guide opacity0.5 inspected. Found uncropped helper sheets (LIVE017); after repair both helpers clip to shared crop, source/camera geometry unchanged. Saved/reopened project is whole-document exact; native repeated768×512PNG pixel-exact. ScopedSTL independently closed/outward,35×20×20mm,6687.853948mm³ with3mm cavity floor.','delivery-set-verification.json'),
'JOURNEY-010':('Pass','Native delivery set: editable project, cropped768×512PNG and scoped1,556-triangleSTL. Reopened each through Windows file picker; project whole-document exact, PNG flattened-layer pixels exact, STL imported into separate new layer with every triangle exact. Geometry closure, winding, dimensions, volume and cavity checked independently. Original solid recipe/photo/text retained.','delivery-set-verification.json')}
for c in d['cases']:
 if c['id'] in updates:
  c['status'],note,e=updates[c['id']]
  if note not in c['observations']:c['observations'].append(note)
  e='test-results/audit-2026-11-05/mouse/'+e
  if e not in c['evidence']:c['evidence'].append(e)
d['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts=Counter(c['status'] for c in d['cases']);print(dict(counts))
p=folder/'README.md';s=p.read_text(encoding='utf-8')
s=re.sub(r'Current accounting: \*\*[^\n]+\*\*',f"Current accounting: **{counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Not run']} Not run, {counts['Blocked']} Blocked**",s,count=1)
note='''

LIVE017 clips both CAD picture-helper canvases to the shared document crop.
Camera coordinates and geometry remain in full-document coordinates. The
targeted test fails before and passes after at all four layouts, checking
transparent outside pixels and independently expected half/quarter opacity.
Native cropped photo/annotation and half-opacity delivery were verified.
Full seventeen-fix regression:618 passed,0 failed,0 page errors.

FILE-022 passes actual native Chrome Duplicate, different edits and separate
reload/resume files (verify-tab-isolation.py). DELIVER-010 and JOURNEY-010 pass
the actual delivery/reopening set (verify-delivery-set.py). CAD orbit, wheel,
Fit and Pin are covered; native right-drag pan is unavailable and is not claimed.
'''
if 'LIVE017 clips' not in s:s+=note
p.write_text(s,encoding='utf-8')
p=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(p.read_text(encoding='utf-8'))
env['fix_count']=17;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-seventeen-fixes/report.json','passed':618,'failed':0,'page_errors':0}
for entry in env['dirty_source']:
 path=root/entry['path']
 if path.exists():entry['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
p.write_text(json.dumps(env,indent=2)+'\n')
