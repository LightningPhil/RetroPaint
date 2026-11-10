"""Record the native brush-size and cursor matrix."""
from pathlib import Path
from datetime import datetime,timezone
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2]
assert json.loads((root/'test-results/audit-2026-11-05/mouse/size55-verification.json').read_bytes())['status']=='Pass'
note=('Native Blue marker sizes1/22/96 on960x640PLAY at85% and127% zoom. Six actual saved strokes independently satisfy declared source footprint radii+2pxAA, increasing source heights, unchanged outside pixels and exact metadata; same-sized source heights at both zooms differ by at most2AApixels. Three rapid Home/End cycles do not change whole project data; return-to-fit preserves it exactly. Native cursor screenshots show22/96rings matching paint footprint at both zooms and a visible5px minimum cue for1px. An obscured initial minimum-cursor screenshot was supplemented by a separate native tap and exact Undo. An immediate End-key read caught the previous22px label before repaint; the retained follow-up waits for and verifies visible96px with input96. No application defect found.')
p=folder/'execution.json';ledger=json.loads(p.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id']=='PAINT-008':
        c['status']='Pass'
        if note not in c['observations']:c['observations'].append(note)
        for name in ['size55-verification.json','size55-evidence.json']:
            path='test-results/audit-2026-11-05/mouse/'+name
            if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
p=folder/'README.md';s=p.read_text(encoding='utf-8').replace('**113 Pass, 233 Partial','**114 Pass, 232 Partial')
if '## Brush size matrix completed' not in s:s+='\n## Brush size matrix completed\n\n'+note+'\n'
p.write_text(s,encoding='utf-8');print('PAINT-008 Pass;114Pass232Partial3Blocked')
