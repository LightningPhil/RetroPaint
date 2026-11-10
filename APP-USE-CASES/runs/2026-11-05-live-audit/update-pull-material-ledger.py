from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2]
path=folder/'execution.json';ledger=json.loads(path.read_text(encoding='utf-8-sig'));cases={x['id']:x for x in ledger['cases']}
updates={
 'SKETCH-007':('Pass','Exact JOIN fixture: unscaled20cube centre0,0,10, fixedXYcentred10x10rectangle. Native +30Join saved/exported; actual project reopened. History initially displayed29.98 instead of saved30: LIVE-013 fixed legacy misclassification. Rebuilt production now shows30 without attachment. Edited a separate copy to10 Inwards, retaining union; saved/exported and native reopened, History10Inwards. Independent binary STL edge/winding/bounds/volume: positiveZ0..30, negativeZ-10..20, each9000mm3, closed outward28tri. Entire negative reopened project equals original.','fixed-pull-verification.json'),
 'JOURNEY-009':('Partial','Opened the actual saved30mmfixed-plane joined design; revised original extrusion to10mmInwards and applied downstream union. Saved, exported STL, native reopened revised project and checked History10Inwards; entire project equal. Prescribed nested HISTORY fixture, downstream holes/finishes and failure branches remain.','fixed-pull-verification.json'),
 'INK-007':('Pass','Started exact PLAY960x640. Black bucket background, separate transparent foreground. Blue thenNeon22px horizontal stroke from150,220to800,220; Pink thenNeon from150,420to800,420. Blue region remains pixel-exact after tint change. Actual PNG has bright centres and selected-colour translucent halos with clear rounded margins; transparent export exactly equals foreground layer. JPEGwhite backing and project preservation also independently checked.','material-verification.json'),
 'INK-008':('Pass','Gold thenGlitter95px broad stroke from180,320to780,320 on a separate clear layer, with earlier layers hidden. Waited while running independent export checks, zoomed73to109percent, re-exported. PNGpixels exactly unchanged, source has no animated live entries. Independent export checks show211opaque pigment colours, exact opaque pixels/alpha, and at most1premultiplied channel rounding in translucent compositing. Tint and clear margins retained.','material-verification.json'),
 'LAYER-010':('Partial','Two-layer neon scene: hid black Paper, exported genuine-alpha PNG and JPEGwhitebacking. PNG equals foreground pixels exactly, including translucent halo and clear corners; no checkerboard bytes. Whole project before and after exports exactly equal. Required full MIX stack and named opacity variants remain.','material-verification.json')
}
for key,(status,note,evidence) in updates.items():
    case=cases[key];case['status']=status
    if note not in case['observations']:case['observations'].append(note)
    evidence='test-results/audit-2026-11-05/mouse/'+evidence
    if evidence not in case['evidence']:case['evidence'].append(evidence)
ledger['updated']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts={s:sum(x['status']==s for x in ledger['cases']) for s in sorted({x['status'] for x in ledger['cases']})}
readme=folder/'README.md';text=readme.read_text(encoding='utf-8');text=re.sub(r'Current accounting: \*\*\d+ Pass, \d+ Partial, \d+ Not run\*\*',f"Current accounting: **{counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Not run']} Not run**",text)
note='''

## Fixed-plane History correction and material checks

**LIVE-013:** Opening History converted a current fixed-plane pull of30mm
to a face-attached29.98mm feature. Legacy upgrade inference now requires the
old signed0.02mm contact offset and skips modern sketch metadata. The new
regression fails before the fix and passes afterwards; the older face-tool
upgrade regression still passes. Production live History shows30mm exactly.
[Independent pull verifier](verify-fixed-pulls.py) validates both prescribed
positive and negative STL endpoints,9000mm3volumes, closure and winding, saved
pulls and exact native negative-project reopen. SKETCH-007 now passes.

The full regression after thirteen fixes passes **606 checks, zero failures
and zero page errors** (`all-thirteen-fixes/report.json`). TypeScript and build
pass. The production output folder retains its historical seven-fixes name.

[Material verifier](verify-materials.py) checks separate blue/pink neon tints,
unchanged earlier pigment, actual translucent PNG halos, white-backed JPEG,
unchanged editable project and stationary gold glitter across waiting/zooming.
INK-007 and INK-008 now pass. Glitter opaque pixels and alpha are exact; low-alpha
Canvas compositing differs by at most1premultiplied channel level.
'''
if '## Fixed-plane History correction' not in text:text+=note
readme.write_text(text,encoding='utf-8')
envpath=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(envpath.read_text(encoding='utf-8-sig'))
if not any(x['path']=='src/cad-features.ts' for x in env['dirty_source']):env['dirty_source'].append({'path':'src/cad-features.ts'})
for item in env['dirty_source']:item['sha256']=hashlib.sha256((root/item['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=13;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-thirteen-fixes/report.json','passed':606,'failed':0,'page_errors':0}
envpath.write_text(json.dumps(env,indent=2)+'\n');print(counts)
