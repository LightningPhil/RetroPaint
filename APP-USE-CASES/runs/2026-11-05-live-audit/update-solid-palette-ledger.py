"""Close every standard solid swatch with source-pixel evidence."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/palette45-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));c=next(c for c in ledger['cases'] if c['id']=='INK-001');c['status']='Pass'
note='All12 standardnamedpalettecolours nativechosen/aria-pressedtrue andseparate22px100%SqueakyMarkerstroke onpreservedPLAYcontrasting#505050copy; originalwhitePLAYunchanged. Red/Yellow/Blue/Green/Black/Pink/Mint/Teal/Gold/Purple/Orange/White allopaqueinteriorRGBAexacttotheirdeclaredpalettehex. ThirteenthreturnRedstroke verified. Everydeliveredsourcepointmeasuredfromnativepointerevents, capsuleinteriorandunchangedexterior/alloldmarkseverybyteexact; onlyactiveRasterimagechanges, allmetadata/live/objectsunchanged. WholeUndo12colourstate/Redo13/nativeprojectreopenexact; actualPNGprojectdecodedRGBAandnativePNG-reopenexact. Whitevisibleagainstdarkbacking, notinvisiblepass.'
if note not in c['observations']:c['observations'].append(note)
for name in ['palette45-verification.json','palette45-evidence.json','palette45-live-result.jpg']:
    path='test-results/audit-2026-11-05/mouse/'+name
    if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':98,'Partial':247,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**97 Pass, 248 Partial','**98 Pass, 247 Partial')
if '## INK-001: all standard palette swatches' not in text:text+='\n## INK-001: all standard palette swatches\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(counts)
