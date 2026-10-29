from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
root=Path(__file__).resolve().parent;rows=[]
for i in range(1,5):
    folder=root/f'headless/INK-003-secondary/v{i}';data=json.loads((folder/'native-input.json').read_text(encoding='utf-8'));parts=[]
    for phase in ['right-draw','right-sample','left-draw']:
        events=[e for e in data if e['phase']==phase];parts.append(dict(phase=phase,types=dict(Counter(e['type'] for e in events)),downs=[e for e in events if e['type']=='pointerdown'],ups=[e for e in events if e['type']=='pointerup'],held_moves=[e for e in events if e['type']=='pointermove' and e['buttons']]))
    rows.append(dict(id=f'v{i}',phases=parts))
report=dict(at=datetime.now(timezone.utc).isoformat(),rows=rows);(root/'evidence/INK-003-native-input-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps([dict(id=r['id'],phases=[dict(phase=p['phase'],types=p['types'],downs=[dict(button=e['button'],buttons=e['buttons'],source=e['source']) for e in p['downs']],ups=[dict(button=e['button'],buttons=e['buttons'],source=e['source']) for e in p['ups']],held_moves=len(p['held_moves'])) for p in r['phases']]) for r in rows]))
