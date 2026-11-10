"""Close the exact-size and complete native wand matrix; retain Shift limitation."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2];out=root/'test-results/audit-2026-11-05/mouse'
for name in ('wand38-verification.json','edit-size38-verification.json'):assert json.loads((out/name).read_bytes())['status']=='Pass'
notes={
 'EDIT-003':('Pass','Sixteen native Colour wand runs on all five prescribed320×240 FILL variants. A separate deque BFS implements the documented four-connected seed-relative L1 RGBA metric, including transparent-pixel equality. Exact actual clipboard crops, deleted PNGs, whole project Undo/Redo and native final project/PNG reopen. Closed border excludes the second matching island even at200. One-pixel gap excludes outside at68 and leaks at69; AA ring excluded143/included144; deterministic ±8 variation selects one column at0 and full interior at24. Transparent40×40 centre remains distinct at0/200; half-alpha ring grows from164pixels at129 to12561 at130. Independent eight-bit premultiplication predicts imported grey232 alpha128 becoming231 alpha128, hence threshold130. Initial integer-coordinate variation clicks landed just below the requested pixel boundary; recorded delivered seeds explain the16-column result. Both attempts retained and repeated at pixel centres; no oracle tolerance or fixture simplification.', ['wand38-verification.json','wand38-evidence.json']),
 'EDIT-009':('Pass','Native labelled PATCH100×80 Red selection resized to200×160 through Image controls in Pixels and200Percent, with Keep proportions. Exact selection size;960×640paper unchanged; all pixels outside the resulting footprint keep their positions. Blank,zero,negative,text and4097 rejected on both axes before edit, with actionable message and unchanged whole project/PNG. Positive1/4096limits on each axis reach requested preview bounds; cancelling every preview restores exact original project. Whole Undo/Redo and actual native project/PNG reopen exact.', ['edit-size38-verification.json','edit-size38-evidence.json','edit-size38-invalid-evidence.json']),
 'EDIT-008':('Partial','Native free resize independently changes110×90 into220×270; exact Place/source/Undo/Redo verified. Crossing the opposite corner clamps100×80 to1×1; the tiny corner can be dragged again to101×101 and placed with exact RGBA and whole Undo/Redo. A browser-held Shift plus native mouse drag was explicitly probed: actual PointerEvent.shiftKey remained false and resize was unconstrained. This is an input-capability limitation, not evidence of a product Shift defect or a successful Shift path. Native Shift-constrained aspect test remains unproved.', ['edit-resize38-verification.json','edit-resize38-shift-capability-probe.json','edit-resize38-crossed-evidence.json','edit-place-cancel38-verification.json'])}
lp=folder/'execution.json';ledger=json.loads(lp.read_text(encoding='utf-8-sig'))
for case in ledger['cases']:
 if case['id'] not in notes:continue
 status,note,names=notes[case['id']];case['status']=status
 if note not in case['observations']:case['observations'].append(note)
 for name in names:
  path='test-results/audit-2026-11-05/mouse/'+name
  if path not in case['evidence']:case['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();lp.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');counts=Counter(c['status'] for c in ledger['cases']);assert counts==Counter({'Pass':71,'Partial':275,'Blocked':3})
rp=folder/'README.md';text=rp.read_text(encoding='utf-8').replace('**69 Pass, 277 Partial, 0 Not run, 3 Blocked**','**71 Pass, 275 Partial, 0 Not run, 3 Blocked**')
if '## Native wand and exact-size matrix' not in text:text+='\n## Native wand and exact-size matrix\n\n'+'\n\n'.join(n[1] for n in notes.values())+'\n'
rp.write_text(text,encoding='utf-8');print(dict(counts))
