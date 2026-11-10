"""Close actual obsolete-worker branches; keep remaining variants explicit."""
import json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
run=Path(__file__).resolve().parent
note='Native visible local harness stalls two actual precision jobs; production45s timers measured45.012751/45.014281seconds. Old terminated CAD message/error handlers explicitly invoked with current new requestID26; busy job remains intact and next successful CheckPrint returns10x60x6mm/2.59cm^3/20triangles. Old OpenSCAD message/error handlers invoked during different active fib(44)job leave new source/Rendering/Adddisabled intact; cancel and valid11x7x3retry succeeds. Downloaded whole project exact before/after. Independent verify-stale-workers.py passes. Earlier no-effect attempts while harness was outside workshop isolation were corrected by relocating only labelled harness controls into visible workshop/dialog; successful deliveries are logged.'
for filename,case in [('execution.json','FEATURE-029'),('supplemental-execution.json','CODE-010')]:
 p=run/filename;d=json.loads(p.read_bytes());c=next(c for c in d['cases'] if c['id']==case);c['status']='Pass'
 if note not in c['observations']:c['observations'].append(note)
 for e in ['test-results/audit-2026-11-05/mouse/stale-workers-verification.json','test-results/audit-2026-11-05/mouse/cad-stale-old-worker-current-request.png','test-results/audit-2026-11-05/mouse/openscad-old-error-new-render-untouched.png']:
  if e not in c['evidence']:c['evidence'].append(e)
 d['updated']=datetime.now(timezone.utc).isoformat()
 if filename.startswith('supplemental'):d['counts']=dict(Counter(c['status'] for c in d['cases']))
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=run/'README.md';s=p.read_text(encoding='utf-8').replace('**36 Pass, 309 Partial, 0 Not run, 4 Blocked**','**37 Pass, 308 Partial, 0 Not run, 4 Blocked**')
heading='## Obsolete worker handlers and current requests'
if heading not in s:s+='\n'+heading+'\n\n'+note+'\n\nFEATURE-029 and CODE-010 now pass; supplemental9Pass/13Partial.\n'
p.write_text(s,encoding='utf-8')
p=run/'COVERAGE-GAPS.md';s=p.read_text(encoding='utf-8').replace('CODE-001/003/004/006/007/008/009/012 pass\nand the other14 remain Partial.','CODE-001/003/004/006/007/008/009/010/012 pass\nand the other13 remain Partial.');p.write_text(s,encoding='utf-8')
