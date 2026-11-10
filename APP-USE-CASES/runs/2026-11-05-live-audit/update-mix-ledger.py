from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];path=folder/'execution.json';ledger=json.loads(path.read_text(encoding='utf-8-sig'));cases={x['id']:x for x in ledger['cases']}
updates={
 'LAYER-010':('Pass','Repeated on exact MIX four-layer960x640fixture (Paper, blueBackdrop, red/greenCharacter, text/dogCaption). Initial exported PNG pixel-exact to independent Pillow/reference stamp composition. Hid Paper and Backdrop, retained foreground, exported PNG/JPEG; repeated after native Character opacity50percent. Independently composed PNGs exact at both opacities, true clear corners and red alpha255/128. JPEGflatwhite with known interior patch within2levels. Whole project before/after each export pair exact; no checkerboard painted into files.'),
 'FILE-004':('Pass','Native Windows Paint opened the known640x480fill-tolerancePNG, selected all and copied image pixels. Actual system Ctrl+V (browser virtual clipboard had no data) inserted640x480floating image into MIX Character50percent. Native drag moved it to280,120; Place committed exact source pixels. Independent comparison proves other three layers unchanged and target equals original plus source at exact position. OneUndo restores whole project. Copied Paint Zoom text100percent and verified real text clipboard by pasting into filename; canvas Ctrl+V originally silent. LIVE-014 now reports Copy an image or use Insert image, unchanged whole project. Paste button on this browser offered Ctrl/Cmd+V or Insert image fallback, again unchanged; no permission setting changed. Text-only/stale-copy regressions pass all four layouts.')
}
for key,(status,note) in updates.items():
    case=cases[key];case['status']=status
    if note not in case['observations']:case['observations'].append(note)
    evidence='test-results/audit-2026-11-05/mouse/mix-and-paste-verification.json'
    if evidence not in case['evidence']:case['evidence'].append(evidence)
ledger['updated']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts={s:sum(x['status']==s for x in ledger['cases']) for s in sorted({x['status'] for x in ledger['cases']})}
readme=folder/'README.md';text=readme.read_text(encoding='utf-8');text=re.sub(r'Current accounting: \*\*\d+ Pass, \d+ Partial, \d+ Not run\*\*',f"Current accounting: **{counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Not run']} Not run**",text)
note='''

## Full MIX fixture, external paste and LIVE-014

[MIX generator](prepare-mix-fixture.py) retains a genuine mouse-created dog
stamp and independently prepares the prescribed named four-layer960x640scene.
The first native export equals its independent reference pixel-for-pixel.
[MIX/paste verifier](verify-mix-and-paste.py) then validates genuine alpha at
100/50percent Character opacity, white-backed JPEG and unchanged source stacks.
LAYER-010 now passes on its full fixture, beyond the earlier neon variant.

Actual Windows Paint image copy and native Chrome Ctrl+V insert exactly the
source pixels at the dragged position. Other layers remain identical; one Undo
restores the full project. Browser-use virtual clipboard was empty, so the
system clipboard shortcut through native Chrome was required for this test.

**LIVE-014:** Text-only clipboard content could silently do nothing or reuse
an older in-app image through the fallback. Explicit non-image clipboard data
now reports guidance and returns without pasting stale artwork. Normal text
field paste remains unaffected. A new regression fails in all four layouts
before the fix and passes afterwards. Native production recheck displays the
guidance and preserves the whole MIX project. The Paste button also offered
its Ctrl/Cmd+V or Insert image fallback without altering the document. No
clipboard permission setting changed. FILE-004 now passes.

TypeScript and the fourteen-fix production build pass. The full regression is
running; retain the thirteen-fix606check report until that run finishes.
'''
if '## Full MIX fixture, external paste' not in text:text+=note
readme.write_text(text,encoding='utf-8')
envpath=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(envpath.read_text(encoding='utf-8-sig'))
for item in env['dirty_source']:item['sha256']=hashlib.sha256((root/item['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=14;env['latest_full_regression_pending']='test-results/audit-2026-11-05/all-fourteen-fixes/report.json';envpath.write_text(json.dumps(env,indent=2)+'\n');print(counts)
