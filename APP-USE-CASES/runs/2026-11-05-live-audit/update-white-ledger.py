"""Close the independently verified transparent-white placement case."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];out=root/'test-results/audit-2026-11-05/mouse';assert json.loads((out/'edit-white38-verification.json').read_bytes())['status']=='Pass'
note='Native PATCH opaque-white backing plus independently generated40×40copy card: white surround, red20×20subject, RGB249/250 and mixed-channel near-whites, coloured AA side edges and red alpha128row. Actual copyPNG exactly matches source. Copy/paste/move to400,100 over Blue with Transparent off and on, including toggling off/on while floating. Every final RGBA pixel matches separate expected source-over; copied source and all neighbours unchanged. Policy documented before test: remove alpha only if each RGB channel>=250; a single249channel retains the pixel. Half-alpha red remains and blends exactly over Blue. Whole Undo/Redo and native project/PNG reopen exact.'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));case=next(c for c in ledger['cases'] if c['id']=='EDIT-010');case['status']='Pass'
if note not in case['observations']:case['observations'].append(note)
for name in ('edit-white38-verification.json','edit-white38-evidence.json','edit-white38-preview-off.jpg','edit-white38-preview-on.jpg'):
 path='test-results/audit-2026-11-05/mouse/'+name
 if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts==Counter({'Pass':72,'Partial':274,'Blocked':3})
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**71 Pass, 275 Partial, 0 Not run, 3 Blocked**','**72 Pass, 274 Partial, 0 Not run, 3 Blocked**')
if '## Transparent-white threshold and alpha' not in text:text+='\n## Transparent-white threshold and alpha\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(dict(counts))
