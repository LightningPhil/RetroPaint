"""Record LIVE-020 and independently verified native Code/workshop cases."""
import hashlib,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
run=Path(__file__).resolve().parent;root=run.parents[2]
p=run/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('all nineteen fixes passes **627 checks','all twenty fixes passes **631 checks').replace('(`all-nineteen-fixes/report.json`). This includes','(`all-twenty-fixes/report.json`). This includes')
note='''
## LIVE-020: Signed exponent parameter appears blank

OpenSCAD accepts `width = +1e1`; HTML number inputs reject the leading plus.
The live model rendered10mm while its width control was blank. Parameter
controls now display the parsed numeric value, preserving the original source
notation until an intentional edit. Four layout checks fail before and pass
after. Native production shows10, then a real parameter edit replaces only
that literal; comments, strings, repeated names, expressions and module-local
constants remain exact. Empty/non-finite entries preserve valid source.

Native Update of a scaled, rotated, placed and purple code model retains ID,
name, colour and all transforms. One-step Undo/Redo restores exact source and
geometry. Native Join/Cut retains both original code recipes, transforms and
all neighbouring photo/paint/model data. Actual full project reopen is exact.
Independent binary STL checks verify375/3600/8592/2592mm³, closed outward
meshes, bounds and removed/retained-point ray probes. See
[independent verifier](verify-code-workshop.py).

The full twenty-fix suite passes276painting +88desktop +3×89compact =631,
zero failures and zero page errors. TypeScript and production build pass.
Supplemental CODE-003/004/012 now pass:8Pass and14Partial overall.
'''
if '## LIVE-020:' not in s:s+='\n'+note
p.write_text(s,encoding='utf-8')
p=run/'supplemental-execution.json';d=json.loads(p.read_bytes())
notes={
'CODE-003':'LIVE-020 fixed blank +1e1 numeric control. Native signed exponent fixture exposes only width/depth/height; repeated names, comments, strings, expressions and module locals excluded. Native13.5 then2.5e1 edits replace only width literal. Empty and1e999 input leaves source intact. Actual Save.scad bytes exact;25x5x3mm STL volume375mm^3. Four-layout red/green regression plus full631check suite pass.',
'CODE-004':'Native code model Update retains bodyID, name, position[37,-11,8], rotationZ90, scale[2,2,2] and purple#9f89dc. Stale Add/Update disabled until Preview. Source width25->30 updates actual scaled STL10x60x6/3600mm^3; one-step Undo/Redo exact sources/meshes and neighbour models unchanged. Actual project reopen retains all.',
'CODE-012':'Native workshop Join and Subtract cutters combine transformed code models; actual STLs have independently analytic8592/2592mm^3 volumes, exact bounds and closed outward edge incidence. Independent ray probes prove removed notch and retained arms. Boolean child source bytes/transforms exact. One-step Undo/Redo and actual native whole-project reopen exact; all previous12models, photo recipe and blue paint annotation sheet unchanged.'}
for c in d['cases']:
 if c['id'] in notes:
  c['status']='Pass'
  if notes[c['id']] not in c['observations']:c['observations'].append(notes[c['id']])
  for e in ['test-results/audit-2026-11-05/mouse/code-workshop-verification.json','test-results/audit-2026-11-05/mouse/code-boolean-history-reopened.png']:
   if e not in c['evidence']:c['evidence'].append(e)
d['updated']=datetime.now(timezone.utc).isoformat();d['counts']=dict(Counter(c['status'] for c in d['cases']))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=run/'COVERAGE-GAPS.md';s=p.read_text(encoding='utf-8').replace('CODE-001/006/007/008/009 pass\nand the other17 remain Partial.','CODE-001/003/004/006/007/008/009/012 pass\nand the other14 remain Partial.')
p.write_text(s,encoding='utf-8')
p=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(p.read_bytes())
env['recorded']=datetime.now(timezone.utc).isoformat();env['fix_count']=20
env['latest_regression']={'report':'test-results/audit-2026-11-05/all-twenty-fixes/report.json','passed':631,'failed':0,'page_errors':0}
for entry in env['dirty_source']:entry['sha256']=hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
build=root/'test-results/audit-2026-11-05/production-seven-fixes';html=(build/'index.html').read_text(encoding='utf-8')
entry=re.search(r'src="\./(assets/index-[^" ]+\.js)"',html).group(1)
env['production_build']={'fixes':20,'index_sha256':hashlib.sha256((build/'index.html').read_bytes()).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((build/entry).read_bytes()).hexdigest()}
p.write_text(json.dumps(env,indent=2)+'\n')
print(json.dumps(d['counts']))
