"""Record LIVE-019 native file-input cancellation scope and current regression."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2]
p=folder/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('The latest full regression after all eighteen fixes passes **619 checks, zero\nfailures and zero page errors** (`all-eighteen-fixes/report.json`). Four added\nclipboard-fallback layout checks also pass existing behavior; no speculative\nclipboard fix was made. TypeScript passes with that added check. Automated\nchecks remain separate from acceptance-case accounting.',
'The latest full regression after all nineteen fixes passes **627 checks, zero\nfailures and zero page errors** (`all-nineteen-fixes/report.json`). This includes\nthe clipboard-fallback and native-chooser cancellation regressions. TypeScript\nand the production build pass. Automated checks remain separate from\nacceptance-case accounting.')
note='''

## LIVE-019: File chooser cancellation closes Code studio

The native file input's bubbling cancel event reached the studio's dialog
cancel listener, which treated it as Escape on the dialog and closed it.
Reopening Edit selected then replaced the unapplied draft with saved source.
Native29mm helper edits visibly reverted to28mm after cancelling the chooser.
The listener now closes only when event.target is the dialog itself.

The targeted test fails before and passes after at all four layouts. Native
folder, standalone source and additional-file chooser cancellation now retains
the29mm draft and11file project; Save .scad retains exact29mm helper bytes.
Explicit Escape on the studio still closes it. Rejected2,000,001byte source,
20,000,001byte dependency, oversized combined dependencies and2,001file folder
retain the draft and allow a valid29mm retry. The applied document remains
whole-JSON exact before/after. Accepted maxima are being checked separately.

Full nineteen-fix regression:276painting +87desktop +3×88compact =627passes,
zero failures and zero page errors. TypeScript and production build pass.
'''
if '## LIVE-019:' not in s:s+=note
p.write_text(s,encoding='utf-8')
p=folder/'supplemental-execution.json';d=json.loads(p.read_text(encoding='utf-8'))
note='LIVE-019: Native picker cancellation bubbled to HTMLdialog cancel and closed Code studio; reopening Edit selected lost unapplied29mm helper and returned28mm. Guard now requires event.target===dialog. Allthree native pickers retain29mm draft/11files; explicit studio Escape still closes. Four-layout red/green regression and full627check suite pass. Native rejected oversized source/dependencies/combined/count preserve draft and successful retry; applied document whole-JSON exact. Accepted maxima still in progress.'
for c in d['cases']:
 if c['id'] in ['CODE-006','CODE-007','CODE-008','CODE-010']:
  if note not in c['observations']:c['observations'].append(note)
  for e in ['test-results/audit-2026-11-05/mouse/chooser-unapplied29-before-live.png','test-results/audit-2026-11-05/mouse/chooser-draft-lost28-before-fix.png','test-results/audit-2026-11-05/mouse/chooser-unapplied29-preserved-after-fix.png','test-results/audit-2026-11-05/mouse/code-import-limit-dom-evidence.json']:
   if e not in c['evidence']:c['evidence'].append(e)
d['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
p=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(p.read_text(encoding='utf-8'))
env['recorded']=datetime.now(timezone.utc).isoformat();env['fix_count']=19
env['latest_regression']={'report':'test-results/audit-2026-11-05/all-nineteen-fixes/report.json','passed':627,'failed':0,'page_errors':0}
env['additional_regression']['note']='Historical four-layout clipboard fallback check; now included in the full627check nineteen-fix run.'
for entry in env['dirty_source']:entry['sha256']=hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
build=root/'test-results/audit-2026-11-05/production-seven-fixes';html=(build/'index.html').read_text(encoding='utf-8')
entry=re.search(r'src="\./(assets/index-[^" ]+\.js)"',html).group(1)
env['production_build']={'fixes':19,'index_sha256':hashlib.sha256((build/'index.html').read_bytes()).hexdigest(),'entry':entry,'entry_sha256':hashlib.sha256((build/entry).read_bytes()).hexdigest()}
p.write_text(json.dumps(env,indent=2)+'\n')
