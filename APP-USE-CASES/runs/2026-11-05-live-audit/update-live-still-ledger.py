"""Close live still export using independent dynamic phases and a real viewer."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/still47-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));c=next(c for c in ledger['cases'] if c['id']=='INK-018');c['status']='Pass'
note='Actualfour-layerMIXPhoto+1EV/Conveyor/twoWaterfills/nineVectorpieces/CaptionDog nativePNGexportsat12345and23456ms. BothfullRGBAframesexacttopreserved44reference, wholeeditableprojectbefore/afterexact. IndependentcyclicRGBphaseandlinear-sRGB+1EVmatchconveyoropaqueendcapRGB138,149,228then238,255,158. MathematicalWaterpolylinegeometryselectsunambiguousstroke/backgroundpoints(786,473)and(786,537), masksproveonepointineachdisjointfill; bothmatchsameclock+exposureRGB101,255,255then0,164,248. PNGformatoneframe/notanimated. ActualdownloadopenedthroughnativeChromeCtrlT/localfileURLinseparateimageviewer; filenameand960x640title/nativecompositionobserved, imageareaexactbetweentwoScreens. DecodedPNGbytesarepixeloracle,notGUIresampling. Temporaryviewertab734closedandabsenceverified; originalaudittabretained. Nophysicalprinterorinferredanimationclaim.'
if note not in c['observations']:c['observations'].append(note)
for name in ['still47-verification.json','still47-viewer-evidence.json','still47-native-viewer-a.png','still47-native-viewer-b.png']:
    path='test-results/audit-2026-11-05/mouse/'+name
    if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':104,'Partial':241,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**103 Pass, 242 Partial','**104 Pass, 241 Partial')
if '## INK-018: coherent live still in an independent viewer' not in text:text+='\n## INK-018: coherent live still in an independent viewer\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(counts)
