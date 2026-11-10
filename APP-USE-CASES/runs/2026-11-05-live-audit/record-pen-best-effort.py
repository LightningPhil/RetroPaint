"""Record user-authorized best-effort pen coverage without a hardware claim."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];audit=root/'test-results/audit-2026-11-05'
reports=['pen-best-effort/report.json','pen-fallback-best-effort/report.json']
for name in reports:assert json.loads((audit/name).read_bytes())['status']=='Pass'
note='User has no local pen and explicitly accepts best-effort software coverage, with optional physical iPad/tablet testing later. Physical hardware validation is deferred, not passed. Isolated Chrome regression confirms coalesced intermediate pen samples preserve the curve. New regression confirms ordinary curved pen input with coalesced API absent or returning empty samples, pressures0.1/0.3/0.9/1 and release0, retains intermediate points without a shortcut or document-scale change. Both focused checks pass with zero page errors. This is synthetic PointerEvent coverage, not physical pressure, palm rejection, tilt, latency or Safari certification. Remaining live continuous mouse/busy-path work stays open.'
path=folder/'execution.json';ledger=json.loads(path.read_text(encoding='utf-8-sig'));case=next(c for c in ledger['cases'] if c['id']=='PAINT-020');case['status']='Partial'
if note not in case['observations']:case['observations'].append(note)
for name in reports:
    evidence='test-results/audit-2026-11-05/'+name
    if evidence not in case['evidence']:case['evidence'].append(evidence)
ledger['updated']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
readme=folder/'README.md';text=readme.read_text(encoding='utf-8').replace('**111 Pass, 234 Partial, 0 Not run, 4 Blocked**','**111 Pass, 235 Partial, 0 Not run, 3 Blocked**');readme.write_text(text,encoding='utf-8')
checklist={'policy':'Physical pen verification deferred at user request; software coverage only.','optional_later_tablet_check':['Open the app in the tablet browser and record device, stylus and browser.','Draw slow and fast loops with light and firm pressure. Check continuity and unchanged picture dimensions.','Lift the pen, leave/re-enter the paper and draw again; ensure no stuck drawing.','Try touching the screen with a resting palm; record unintended marks rather than assume palm rejection.','Undo/Redo each gesture, save PNG and project, reopen and compare.'],'limitations':['No hardware pressure/tilt or palm rejection claim.','Desktop Chromium software tests do not certify iPad Safari.'],'regression_reports':reports}
(audit/'manual-blockers/pen-best-effort.json').write_text(json.dumps(checklist,indent=2)+'\n',encoding='utf-8')
guide=audit/'manual-blockers/START.html';text=guide.read_text(encoding='utf-8');text=text.replace('Ready for human mouse input; physical pen branch needs hardware.','Software pen curve and fallback checks pass. Physical pen validation is deferred at your request; continuous live mouse testing remains. Optional later tablet checklist: pen-best-effort.json.');guide.write_text(text,encoding='utf-8')
print(Counter(c['status'] for c in ledger['cases']))
