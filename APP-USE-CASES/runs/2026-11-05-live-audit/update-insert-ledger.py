"""Close insertion scope/limits while preserving Vector history distinctions."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/insert43-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));c=next(c for c in ledger['cases'] if c['id']=='FILE-003');c['status']='Pass';note='SixcompletednativeMIXinsertionflows: smalltransparent320x240PNGinRaster/Vector,movedbydelivered150,100to470,300; maximum4096squareinbothmodes;4096x1and1x4096Raster. IndependentsourceRGBA/geometry,onlyactiveCharacteraddition/composite,allotherlayers/objects/metadataexact. LargePlacewarnstrim,keepspaper960x640andexpectedPurplefullframe/row320/column480; originalMIXrestoredbyUndo. Native4097width/heightrejectedwithlimitsmessageandentireprojectunchanged; validinsert/moveafterrejectionworks. Rasterfloatinginsert/move/PlaceoneUndo; Vectormoveandinsertseparategestures, bothUndos/Redosexact. Initialsingle-UndoVectorprobe retainedasMoveUndo, completedv2provesInsertUndo. SixnativePNG reopens exact; VectorprojectsaddonlyunusedliveSize960x640toinsertedRasterwithoutlivedata, strictdocumentednormalization; sourceRGBA/matrices/allotherdataexact.'
if note not in c['observations']:c['observations'].append(note)
for name in ['insert43-verification.json','insert43-evidence.json','insert43-live-result.jpg']:
 path='test-results/audit-2026-11-05/mouse/'+name
 if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**91 Pass, 255 Partial','**92 Pass, 254 Partial')
if '## FILE-003: insertion and source limits' not in text:text+='\n## FILE-003: insertion and source limits\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(Counter(c['status'] for c in ledger['cases']))
