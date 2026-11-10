"""Record the completed natural-photo, filename, text and recovery workflows."""
from pathlib import Path
from datetime import datetime, timezone
import json
folder=Path(__file__).resolve().parent
path=folder/'execution.json'
ledger=json.loads(path.read_text(encoding='utf-8-sig'))
cases={item['id']:item for item in ledger['cases']}
updates={
 'JOURNEY-004':('Pass','Continuous native photographic journey on a provenanced public-domain 2100x1398 landscape: Natural look, Auto light, reduced exposure0.05EV, contrast11, vibrance12. Inspected Auto WB then reset its green-scene cast. Native crop fields produced x150 y100 width1800 height1200. A separate transparent Landscape caption sheet contains white Georgia64 caption, fully inside crop. Actual project and PNG downloaded, native picker reopened project, whole JSON and repeated PNG pixels exact. Reopened Photo lab recovered all original margins; Cancel preserved entire project. Independent JPEG decoder differs from retained original by at most1 channel level. No private photograph or skin-tone claim.','natural-photo-verification.json'),
 'PHOTO-018':('Partial','Natural 2100x1398 photo with light, colour and detail recipe, shared1800x1200crop and separate caption exported/reopened PNG pixel-exact. Original decoder comparison <=1 channel level and all hidden margins retained. Further prescribed synthetic/full-resolution variants remain.','natural-photo-verification.json'),
 'FILE-012':('Partial','Live cropped two-layer natural photo Print preview contains the finished composition and caption without editing overlays. Saved PDF has one page and independently extracted1800x1200image pixel-exact to PNG. Reopened Print then Cancel; downloaded whole project exactly unchanged. Prescribed MIX fixture and actual physical printer integration remain untested.','natural-photo-verification.json'),
 'EDIT-024':('Pass','Exact PLAY960x640 fixture. Native typing bsfrteagiplm? stayed in Text field with active Text tool; normal Enter inserted a second line. Ctrl+Enter produced the same600x94movable raster selection as Place text, committed through Place. Saved changed project; one Undo returned the entire project exactly to clean baseline. Windows Ctrl variant verified; Cmd is unavailable on this host.','files-and-recovery-verification.json'),
 'FILE-011':('Pass','Exact PLAY960x640. Name mouse-audit-filename.png saved as JPEG produces mouse-audit-filename.jpg, with no doubled extension. All reserved characters <>:"/\\|?* were replaced safely for PNG. Empty name produced retropaint.webp. All three actual files independently decode with expected format and960x640size.','files-and-recovery-verification.json'),
 'FILE-020':('Partial','Native Recent drafts visited all three pages of eight retained own audit entries, with endpoint Previous/Next disabled. Names/sizes/previews distinguish current red stroke, natural photo and CAD variants. Chose journey4-reopened photo; downloaded restored project exactly equals chosen saved project. Damaged/missing-entry branch and exact MIX fixture remain. One CAD preview appeared closed and needs orientation/cache investigation.','files-and-recovery-verification.json'),
 'FILE-021':('Partial','Created red96pxstroke on960x640paper and preserved pre-restore project. Restored chosen2100x1398photo draft; Undo returns entire pre-restore project exactly, Redo returns entire selected photo project exactly. Further MIX editable-content fixture and draft-store independence checks remain.','files-and-recovery-verification.json')
}
for key,(status,note,evidence) in updates.items():
    case=cases[key];case['status']=status
    if note not in case['observations']:case['observations'].append(note)
    evidence='test-results/audit-2026-11-05/mouse/'+evidence
    if evidence not in case['evidence']:case['evidence'].append(evidence)
ledger['updated']=datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts={s:sum(x['status']==s for x in ledger['cases']) for s in sorted({x['status'] for x in ledger['cases']})}
readme=folder/'README.md'
text=readme.read_text(encoding='utf-8')
text=text.replace('**2 Pass, 292 Partial, 55 Not run**','**5 Pass, 296 Partial, 48 Not run**')
note='''

## Natural photo and file workflows

[Photo provenance](photo-provenance.json) records the public-domain natural
2100 x 1398 source. [Independent photo verifier](verify-natural-photo.py)
checks original retention, exact native project reopen and cancelled crop
inspection, separate caption sheet, 1800 x 1200 PNG and repeated output.
The print PDF contains one image pixel-exact to the PNG; cancelling a second
print leaves the whole project unchanged. JOURNEY-004 now passes. The earlier
synthetic photo checks did not substitute for this natural photograph.

[File and recovery verifier](verify-files-and-recovery.py) checks actual
format-aware, reserved-character and empty filenames, exact one-Undo keyboard
text recovery, chosen draft identity and exact recovery Undo/Redo. EDIT-024
and FILE-011 pass. Recovery and printing component cases remain Partial where
their exact MIX fixture or failure branches are still outstanding.
'''
if '## Natural photo and file workflows' not in text:text+=note
readme.write_text(text,encoding='utf-8')
print(counts)
