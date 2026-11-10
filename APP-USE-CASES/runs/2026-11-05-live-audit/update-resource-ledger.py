"""Record independently decoded native resource/material/privacy checks."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import json,re
folder=Path(__file__).resolve().parent
p=folder/'execution.json';d=json.loads(p.read_text(encoding='utf-8'))
updates={
'ENHANCE-010':('Pass','Disposable worker OffscreenCanvas WebGL contexts denied, standard CPU backend runs actual ESRGAN2× on fixed16×16 natural detail. Native progress explicitly CPU; cancel remained usable and restart completed.32×32savedCPU/GPUresults pixel-identical and differ from Lanczos. Whole source project exact after missing-model failure, cancellation and successful inference. No substitute filter or physical GPU-permission claim.','enhancement-boundary-verification.json'),
'ENHANCE-011':('Pass','Window/worker/resource/server metadata proves no model request before enhancement worker starts, all models from app origin. Visible503 model-download control fails recoverably without changing whole document; native retry loads actual network and succeeds. Cached repeat returns eight304responses with model/shard transfer300bytes and original body sizes. No image upload/API account.','local-request-verification.json'),
'ENHANCE-012':('Partial','Native4096²transparent source accepts both2×8192²(67,108,864pixels) and4×16384²(268,435,456pixels). StreamedPNGCRC/chunks/zlib/everyrow independently decoded bounded-memory; complete all-clear RGBA and sourceproject whole-document exact. This proves transparent fast-path streaming/edge/no32Mcap; near-limit opaque neural inference and controlled large-job resource failure remain unverified.','enhancement-boundary-verification.json'),
'VECTOR-017':('Pass','Native water-filled vector moved, rotated90 and doubled while main-window art clock visibly fixed12345ms. Independent whole-PNG quarterturn exact, exactmatrix2× and unchanged outsidebounds; scaled64pxmaterialperiod119.16355 with expected autocorrelation. Alpha fixture replaces only white rasterbacking with independently clear PNG; native reopen/export has exact128×256opaque mask at700,350 and zeroalphaelsewhere. Unrelated liveobject exactatfixedtime, animatesafterresume; source/ink definitions retained. Nativeclipboard issue investigated: focused regression proves fallback already works; no speculative source fix.','moving-material-verification.json'),
'ACCESS-015':('Pass','Controlled application-window/worker/server request metadata across local image/project open, painting, Photo brightness12/Done, project save, CADCube/CheckPrint/STL and actual neural enhancement; repeated cached-model workflow. All recorded application URLs use loopbackapporigin; GETs are assets, onlyPOSTs explicitly identified auditmetadata, no art/modelpayload uploads. File bytes independently decoded; sourcephoto exact. Browser extension/host traffic excluded, as case boundary requires.','local-request-verification.json')}
for c in d['cases']:
 if c['id'] not in updates:continue
 c['status'],note,e=updates[c['id']]
 if note not in c['observations']:c['observations'].append(note)
 e='test-results/audit-2026-11-05/mouse/'+e
 if e not in c['evidence']:c['evidence'].append(e)
d['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts=Counter(c['status'] for c in d['cases']);print(dict(counts))
p=folder/'README.md';s=p.read_text(encoding='utf-8');s=re.sub(r'Current accounting: \*\*[^\n]+\*\*',f"Current accounting: **{counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Not run']} Not run, {counts['Blocked']} Blocked**",s,count=1)
note='''

verify-enhancement-boundaries.py decodes actual native32×32CPU/GPUESRGAN
copies pixel-exact, plus8192²/16384²transparent streamedPNGs with every CRC,
zlib completion and row checked. Source projects remain whole-document exact.
The large transparent path does not prove near-limit opaque neural inference.

verify-moving-material.py checks native fixed-time transforms, material period,
alpha clipping on an explicitly prepared clear-backing fixture, unchanged
neighbouring live artwork and animation after clock resume. The native Paste
failure was investigated: a focused regression passes existing fallback behavior;
no speculative clipboard source change was made. The four new layout checks
supplement the619-check full eighteen-fix regression.

verify-local-requests.py checks application-window/worker/server request capture,
deferred local models, recoverable503, eight cached304model resources, saved
Photo/painting/CAD/enhancement files and no external application requests.
Browser extensions and host traffic are outside this case's stated boundary.
'''
if 'verify-enhancement-boundaries.py decodes' not in s:s+=note
p.write_text(s,encoding='utf-8')
