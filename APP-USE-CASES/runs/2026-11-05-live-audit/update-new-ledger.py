"""Close New picture including independent dimension and history boundaries."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/new43-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));c=next(c for c in ledger['cases'] if c['id']=='FILE-001');c['status']='Pass';note='Twelve nativeinvalidwidth/height attempts(blank,0,-1,1.5,4097,nativeabc→empty) retaindialog,explainwholepixel1..4096limits,andpreserveentireoriginalprojectafterCancel. Eightvalidsizes1x1,1x240,320x1,320x240,960x640,4096x1,1x4096,4096square produceexactopaqueWhiteRGBAcleanPaper,validactiveID,emptylive/objectsandrequestedresolution. Nativemarkerfootprintalignswithdeliveredpapercoordinates; allneighboursunchanged. DrawingUndo andNewpictureUndo areseparatestepsexact; bothRedosrestoreexactblank/markedprojects. All8nativeproject/PNG reopens exact. ThinaxeszoomedthroughActualpixels+3Zoominto3.375CSSpxbeforemouseinput; resolutionunchanged.'
if note not in c['observations']:c['observations'].append(note)
for name in ['new43-verification.json','new43-evidence.json','new43-maximum-reopened.jpg']:
 path='test-results/audit-2026-11-05/mouse/'+name
 if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**90 Pass, 256 Partial','**91 Pass, 255 Partial')
if '## FILE-001: new-paper boundaries' not in text:text+='\n## FILE-001: new-paper boundaries\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(Counter(c['status'] for c in ledger['cases']))
