"""Append native import-limit and render-recovery evidence without rewriting history."""
import json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
run=Path(__file__).resolve().parent
p=run/'supplemental-execution.json';d=json.loads(p.read_bytes())
notes={
'CODE-001':('Pass','Native Preview, F5 syntax-error render and Ctrl+Enter valid recovery exercised; exact broken second line selected. Mouse orbit and Fit captured; Close/reopen retains draft and rerenders. Independent whole-project before/after shortcuts comparison confirms preview does not apply changes.'),
'CODE-006':('Pass','Native standalone Open and actual Save downloads preserve Unicode filename/source UTF-8 and exact 2,000,000-byte ASCII source. 2,000,001-byte source rejected while preserving draft; actual invalid file reports line2 and valid retry succeeds. Allthree chooser cancellation paths verified after LIVE-019. Native full project reopen retains source exact and max source re-renders. Independent verify-code-limits.py passes.'),
'CODE-008':('Pass','Native accepted 2,000-file folder and exact20,000,000-byte dependency folder render2x3x4mm; 2,001files,20,000,001bytes and combined-over-limit imports reject without draft loss. Native full saved project reopened, all dependency bytes verified, accepted boundary models rebuilt. Each scoped STL has12triangles, closed outward edges and exact24mm^3. Existing native MCAD/SVG/STL/font/heightmap/project-relative library checks verified by verify-code-folder.py.'),
'CODE-009':('Pass','Native invalid.scad parser error selects broken line2; correct entry/file shown. Actual missing-STL diagnostic previously recovered. Echo with quoted ERROR remains Ready. 10,001echoes bounded to52,980displayed characters with explicit truncation marker; 2Dcircle and emptydifference disable Add/Update and explain extrusion/emptyintersection. Valid retry succeeds. Preview/error/cancel sequence leaves whole applied project exact.'),
'CODE-010':('Partial','Native Auto preview starts low-memory CPU-bound fib(45) render; Cancel immediately acknowledges and valid automatic retry succeeds. Close during rendering terminates job; reopen rerenders retained draft. Native replacement source wins; an oversized source imported while rendering stops old job and preserves current draft, followed by automatic9x5x3mm retry. Whole applied scene remains exact. Adversarial late-message injection remains pending.'),
'CODE-011':('Partial','Native37MB twelve-model saved project reopens whole-JSON exact, including2000files,20MBdependency and2MBsource models and Unicode source. Each boundary model rebuilds from reopened source/assets. Unapplied29mm helper cancellation and later CPU/error drafts do not replace applied source. Older script-format mapping remains pending.')}
for c in d['cases']:
 if c['id'] in notes:
  status,note=notes[c['id']];c['status']=status
  if note not in c['observations']:c['observations'].append(note)
  for e in ['test-results/audit-2026-11-05/mouse/code-import-limit-dom-evidence.json','test-results/audit-2026-11-05/mouse/code-limits-verification.json']:
   if e not in c['evidence']:c['evidence'].append(e)
d['updated']=datetime.now(timezone.utc).isoformat();d['counts']=dict(Counter(c['status'] for c in d['cases']))
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
readme=run/'README.md'
text=readme.read_text(encoding='utf-8')
section='''
## Exact Code import boundaries and recovery

Native Windows pickers accepted exactly2,000files,20,000,000dependency bytes
and2,000,000source bytes. Counts/sizes one above the limits and combined
over-budget additions reject without losing the draft. Unicode filename and
source export bytes are exact. The complete37MB,12-model project was actually
reopened and saved again: whole JSON is identical. Allthree boundary models
rebuilt from their reopened sources. Four selected STLs have independently
verified12-triangle closed outward meshes and exact24/105mm³ volumes.
See [verifier](verify-code-limits.py) and
`test-results/audit-2026-11-05/mouse/code-limits-verification.json`.

Native F5/Ctrl+Enter, error-line selection, bounded echo output, pure2D/empty
geometry errors, automatic preview, CPU-render cancellation, close/reopen,
replacement source and failed import while rendering were exercised. The
whole applied document remains unchanged after these draft-only operations.
The screenshot/DOM evidence is retained. CODE-001/006/008/009 now pass;
CODE-010 remains Partial pending adversarial late-message delivery. The
supplemental ledger has5Pass/17Partial; the main349-case counts are unchanged.
The source-length string returned by the observation transport was truncated
in one record; the in-page length computation and independent downloaded
bytes both establish exactly2,000,000, without relying on that truncated string.
'''
if '## Exact Code import boundaries and recovery' not in text:readme.write_text(text+'\n'+section,encoding='utf-8')
g=run/'COVERAGE-GAPS.md';text=g.read_text(encoding='utf-8')
text=text.replace('CODE-007 passes\nand the other21 remain Partial.','CODE-001/006/007/008/009 pass\nand the other17 remain Partial.')
g.write_text(text,encoding='utf-8')
print(json.dumps(d['counts']))
