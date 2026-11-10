"""Close supported-format import with independent encodings and failure recovery."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/import43-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));c=next(c for c in ledger['cases'] if c['id']=='FILE-002');c['status']='Pass';note='EightnativeOpenimage/draw/UndoRedo/reopenflows: independentlyPillowencodedPNG,JPEG,losslessWebP,BMP,GIF,uncompressedRGBATIFF,EXIF6JPEG,andvalidPNGaftercorruptrejection. Five losslessformatdecodesRGBAexactversusindependentPillow(withcanonicaltransparentRGBzero); JPEG/EXIFRGBmax1,MAE0.0003863withinpredeclaredmean1/max5. EXIF6maps320x240source to240x320portrait. Actual12pxBlackMarkerstrokeverifiedagainstnativepointercoordinates: safecapsuleinteriorexactBlack26alpha255, safeexteriorunchangedexact. All8wholeprojectUndoRedo/nativeprojectandPNG reopens exact. NativepickerEscapeandcorruptPNGleavetheentireportraitprojectunchanged; corruptionexplainsformatsandnextvalidimport/markworks.'
if note not in c['observations']:c['observations'].append(note)
for name in ['import43-verification.json','import43-evidence.json','import43-reopened-live.jpg']:
 path='test-results/audit-2026-11-05/mouse/'+name
 if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**89 Pass, 257 Partial','**90 Pass, 256 Partial')
if '## FILE-002: independent format imports' not in text:text+='\n## FILE-002: independent format imports\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(Counter(c['status'] for c in ledger['cases']))
