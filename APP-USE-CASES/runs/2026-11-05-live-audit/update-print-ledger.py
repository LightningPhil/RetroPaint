"""Close prescribed MIX print preview; physical printer remains external."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];assert json.loads((root/'test-results/audit-2026-11-05/mouse/print45-verification.json').read_bytes())['status']=='Pass'
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'));c=next(c for c in ledger['cases'] if c['id']=='FILE-012');c['status']='Pass'
note='Prescribed four-layer MIX cropped to200x100: native Print opensChrome one-pagepreview with2:1Red/Bluecomposition. NativeWindows screenshot confirms noeditingcontrols/selectionoverlays inprintedimage; browserheaders/footerareprintsettings. Read-onlyactualiframe srcdocPNG decodedRGBAexacttoactualPNGexport andknownfixtureRed/Blueinteriors. NativeCancel thenactualdownloadedwholeprojectexactbefore/after. Earliernaturalphoto1800x1200PDFimageverificationalsoretained. Physicalprinteroutput/settingsremainexternalintegration, explicitlynotinferredfrompreviewpercasealternative.'
if note not in c['observations']:c['observations'].append(note)
for name in ['print45-verification.json','print45-native-preview-clean.png','print45-iframe-image.png']:
    path='test-results/audit-2026-11-05/mouse/'+name
    if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts=={'Pass':96,'Partial':249,'Blocked':4}
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**95 Pass, 250 Partial','**96 Pass, 249 Partial')
if '## FILE-012: cropped MIX print preview' not in text:text+='\n## FILE-012: cropped MIX print preview\n\n'+note+'\n'
rp.write_text(text,encoding='utf-8');print(counts)
