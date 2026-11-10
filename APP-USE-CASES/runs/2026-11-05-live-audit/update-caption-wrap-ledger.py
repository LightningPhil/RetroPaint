"""Close EDIT-023 with layered narrow, long-word, and empty native variants."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/caption-wrap41-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));case=next(c for c in ledger['cases'] if c['id']=='EDIT-023');note='Eight native4layerMIX variants: Raster/Vector narrow120px centredArial24px transparent/secondaryYellowopaque captions,36character unbrokenword,emptyandwhitespaceopaquePlace. Four coherent normal lines and six longword lines staywithin112pxcontentwidth; everyoriginalcharacterretained. Both modes produce identicalsourceclipboardRGBA. IndependentPillow source-layer composite and8bitpremultiplied fullPNGsource-over match everypixel exactly; unchangedallotherlayers/objects/rootfields; transparentpixels preservebusyartworkexactly; opaqueboxuses#fdd835 withalpha255. Pairednativepreview/placedviewsidentical; wholeUndoRedo andall6nativeproject/PNG reopensexact. EmptyandwhitespacePlacecreatenoselectionandchangeneitherwholeprojectnorPNG. Liveviewvisuallyconfirmsreadablewordwrappingwithoutcontroloverflow. FirstinterruptedRasterhelperartifactsretained; onlycompletefreshrepeatcounted.'
case['status']='Pass'
if note not in case['observations']:case['observations'].append(note)
for name in ('caption-wrap41-verification.json','caption-wrap41-evidence.json','caption-wrap41-live-result.jpg'):
 path='test-results/audit-2026-11-05/mouse/'+name
 if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**82 Pass, 264 Partial','**83 Pass, 263 Partial')
if '## EDIT-023: narrow text over layered artwork' not in text:text+='\n## EDIT-023: narrow text over layered artwork\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(Counter(c['status'] for c in ledger['cases']))
