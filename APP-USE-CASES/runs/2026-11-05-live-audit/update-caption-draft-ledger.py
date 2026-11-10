"""Close EDIT-021 using actual draft cancellation and tab-close recovery."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/caption-draft41-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));case=next(c for c in ledger['cases'] if c['id']=='EDIT-021');note='Explicit Cancel leaves whole saved project and opaqueWhitePNG exactly unchanged in Raster and Vector modes. Closing options retains the whole draft preview for editing; reopening thenCancel clears it. Actual nativeClosebutton removes tab722 while an opaqueunfinishedcaption is visible over the4layerMIX; newtab727 RecentdraftResume returns exactoriginal4layerproject andPNG, withoutpartiallettersorbackgroundbox. EarlierCtrlW attemptdidnotclose719 and was not counted; actualtabremovalverifiedbyinventory. Main two-line native placement,move,completeUndoRedo and18project/PNG reopens independently verified by caption-font41-verification.json.'
case['status']='Pass'
if note not in case['observations']:case['observations'].append(note)
for name in ('caption-draft41-verification.json','caption-draft41-mix-before-close.jpg','caption-draft41-mix-recovered.jpg'):
 path='test-results/audit-2026-11-05/mouse/'+name
 if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**81 Pass, 265 Partial','**82 Pass, 264 Partial')
if '## EDIT-021: unfinished caption drafts' not in text:text+='\n## EDIT-021: unfinished caption drafts\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(Counter(c['status'] for c in ledger['cases']))
