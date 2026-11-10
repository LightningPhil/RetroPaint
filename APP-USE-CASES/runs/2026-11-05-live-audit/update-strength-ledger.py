"""Record the verified native strength matrix."""
from pathlib import Path
from datetime import datetime, timezone
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2]
assert json.loads((root/'test-results/audit-2026-11-05/mouse/strength54-verification.json').read_bytes())['status']=='Pass'
note=('Native 960x640 PLAY white/Blue background, Squeaky Marker22px, Red: full strength and15% on both backgrounds; second weak pass on each. Independent source-over arithmetic verifies9x9centre patches within2/255, and every pixel outside each declared radius13px gesture tube remains exact. Both overlap Undo/Redo pairs preserve whole project JSON exactly. Switching Spray/Bucket/Brushes, reopening brush options and returning to100% all retain matching visible labels and slider values. Control-only changes preserve the document. Native project and PNG roundtrips exact. Initial fixture whole-JSON expectation failed only because Pillow and Chrome compress identical PNG pixels differently; decoded RGBA and all metadata are exact, with native history comparisons still whole-JSON exact. Earlier strength53 exploration is retained separately; strength54 is the fresh complete acceptance matrix.')
p=folder/'execution.json';ledger=json.loads(p.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id']=='PAINT-009':
        c['status']='Pass'
        if note not in c['observations']:c['observations'].append(note)
        for name in ['strength54-verification.json','strength54-states.json','strength54-live-result.jpg']:
            path='test-results/audit-2026-11-05/mouse/'+name
            if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
p=folder/'README.md';s=p.read_text(encoding='utf-8').replace('**112 Pass, 234 Partial','**113 Pass, 233 Partial')
if '## Strength matrix completed' not in s:s+='\n## Strength matrix completed\n\n'+note+'\n'
p.write_text(s,encoding='utf-8');print('PAINT-009 Pass; 113 Pass, 233 Partial, 3 Blocked')
