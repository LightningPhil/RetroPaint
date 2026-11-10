"""Close only the two independently verified stamp interaction cases."""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
folder=Path(__file__).resolve().parent
root=folder.parents[2]
ledger_path=folder/'execution.json'
ledger=json.loads(ledger_path.read_text(encoding='utf-8-sig'))
updates={
 'PLAY-015':('stamp-transforms', 'Sixteen actual mouse placements on fresh 960x640 papers: Raster and Editable, all four flip combinations in fixed and automatic rotation, scales 0.4/1/1.4/2.6. Public controls and flip aria-pressed states recorded. Independent pixel classification verifies orientation, size and flip directions; editable object sizes/transforms and exact angles checked, all random angles within plus/minus14 degrees. Every placement has whole-project exact Undo/Redo; both final projects and PNGs reopened through the native picker exactly. Image-fitted angles use a raster-edge uncertainty and are not exact editable-angle measurements; font hinting differs by size.'),
 'PLAY-016':('stamp-preview', 'Native mouse hover in Raster and Editable follows two pointer locations and changes size/flip without placing art. Screenshots measure ghost contrast about40% of committed art, and scaling about2.6x. Keyboard saves while the ghost remains visible yield wholly blank project/PNG outputs. One actual tap creates one footprint/object; moving outside adds nothing. Whole-project Undo/Redo and native project reopen exact in both modes. LIVE-028 adds missing aria-pressed states to both stamp flip controls, verified for all four toggle combinations.')
}
for case in ledger['cases']:
 if case['id'] not in updates:continue
 stem,note=updates[case['id']]
 report=root/'test-results/audit-2026-11-05/mouse'/f'{stem}-verification.json'
 assert json.loads(report.read_text(encoding='utf-8'))['status']=='Pass'
 case['status']='Pass'
 if note not in case['observations']:case['observations'].append(note)
 for evidence in [report.relative_to(root).as_posix(),f'APP-USE-CASES/runs/2026-11-05-live-audit/verify-{stem}.py']:
  if evidence not in case['evidence']:case['evidence'].append(evidence)
ledger['updated']=datetime.now(timezone.utc).isoformat()
ledger_path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
readme=folder/'README.md'
text=readme.read_text(encoding='utf-8').replace('**55 Pass, 291 Partial, 0 Not run, 3 Blocked**','**57 Pass, 289 Partial, 0 Not run, 3 Blocked**')
if '## Stamp preview and transform completion' not in text:
 text+='\n## Stamp preview and transform completion\n\nPLAY-015 and PLAY-016 now pass in both Raster and Editable modes. All sixteen\ntransform placements retain their exact committed orientation through Undo/Redo\nand native project reopen. Hover-only keyboard saves exclude the ghost from\nboth projects and PNGs. Independent verifiers retain measurements and hashes.\nThe transform image comparison was corrected to enlarge small reference features;\nits initial failed attempts are retained. Exact editable angles come from the\nsaved objects; rendered template fitting is an orientation/range check, because\nfont hinting changes with glyph size.\n'
readme.write_text(text,encoding='utf-8')
print(dict(Counter(c['status'] for c in ledger['cases'])))
