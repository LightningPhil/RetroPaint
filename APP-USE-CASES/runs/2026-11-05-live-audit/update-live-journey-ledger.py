from pathlib import Path
from datetime import datetime,timezone
import json,re
folder=Path(__file__).resolve().parent;path=folder/'execution.json';ledger=json.loads(path.read_text(encoding='utf-8-sig'));cases={x['id']:x for x in ledger['cases']}
updates={
 'JOURNEY-003':('Pass','Repeated continuously on exact960x640PLAY at production origin. Water95px strokes100,480to860,480 and100,550to860,550. Explicit RedAddYellowAddBlueAdd conveyor3px/sBlend,22pxstroke160,385to800,385. Rainbow long stroke160,80to800,80 and two short strokes140,150to280,150 and680,150to820,150. Purple1pxSpiro Ring100radius96/30teeth repositioned centre480,240, Wind thenManual stop. All four project transitions retained. Actual finalproject133151bytes and namedPNG saved serially; actual native project reopened and whole JSON exact. Independent two-frame comparisons prove water/conveyor still animate, while baked rainbow and Spiro/static top region remain pixel-exact to retained raster. PNG960640 excludes kit controls. Explicit saved project-versus-still and rainbow-baking exception are now verified; older640development download blocker remains historical only.'),
 'INK-006':('Partial','Exact960x640livejourney: long native Rainbow stroke and two separate short strokes; saved still/project retain path-following multiple hues. Native project reopens with these rainbow strokes baked; independent static-region comparison exact across laterframes. Continuous curved mouse path and its segment-join branch remain untested: available native drag interface exposes straight endpoint drags only.')
}
for key,(status,note) in updates.items():
    case=cases[key];case['status']=status
    if note not in case['observations']:case['observations'].append(note)
    evidence='test-results/audit-2026-11-05/mouse/live-journey-verification.json'
    if evidence not in case['evidence']:case['evidence'].append(evidence)
ledger['updated']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts={s:sum(x['status']==s for x in ledger['cases']) for s in sorted({x['status'] for x in ledger['cases']})}
readme=folder/'README.md';text=readme.read_text(encoding='utf-8');text=re.sub(r'Current accounting: \*\*\d+ Pass, \d+ Partial, \d+ Not run\*\*',f"Current accounting: **{counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Not run']} Not run**",text)
note='''

## Exact live-ink journey completed

The earlier640x480development draft could not download its long project, but
the full journey was repeated at960x640on production. All water, conveyor,
rainbow and Spiro transitions have actual project files, plus final PNG and
native project reopen. [Independent live-journey verifier](verify-live-journey.py)
confirms exact whole-project reopen, supported water/conveyor animation in
two decoded frames, and the explicit rainbow baking exception. The static
rainbow/Spiro region is pixel-exact to the saved raster across all exports.
JOURNEY-003 now passes. The continuous curved-path branch of INK-006 remains
Partial because the native mouse API supplies straight endpoint drags only.
'''
if '## Exact live-ink journey completed' not in text:text+=note
readme.write_text(text,encoding='utf-8');print(counts)
