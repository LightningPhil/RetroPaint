"""Record successful native folder fallback and remaining locked-desktop work."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2]
p=folder/'supplemental-execution.json';d=json.loads(p.read_text(encoding='utf-8'))
updates={
'CODE-006':('Partial','Native Save .scad while editing config.scad exports that helper, not entry main.scad. Actual helper files for widths24/28mm are independently byte-exact, including LF. Standalone source Open/cancel/Unicode/2MB boundaries remain pending; fixtures prepared when Windows locked.'),
'CODE-007':('Pass','Native Windows Open folder and browser11-file confirmation import real nested include/use/import dependencies without file-URL permission changes. Main20mm, helper24mm and alternate entry34mm work independently of Edit file config.scad. Same-path Add files replacement28mm changes only target model; Undo/Redo source/geometry exact and other copied models retain24mm helper. Missing STL blocks Add/Update with file/line; restoration retries. Actual whole saved8-solid project reopened exact and original pad rebuilt from preserved files. All source/dependency bytes checked independently; nine scoped closed STLs have analytic/font oracles.'),
'CODE-008':('Partial','Native folder and Add files deliver STL, SVG, nested sources, numeric heightmap, bundled MCAD and an independently supplied Courier font. Fourteen files saved/reopened byte-exact; SVG/STLvolume920mm³, heightmap8mm³, roundedMCAD1434.819291mm³, two fonts checked against independent TrueType outlines. Missing STL recovered. Valid/invalid file-count and byte boundaries are prepared but NOT executed: Windows locked before those chooser tests.'),
'CODE-009':('Partial','Native missing assets/missing.stl produces file/line warning, No valid preview and disabled Add/Update; restore correct path and Preview succeeds. Echo containing ERROR stays an ECHO and MCAD model remains Ready. Scene neighbours/source recipes retained by independent outputs. Remaining bounded-output/2D/empty variants are not closed by these checks.'),
'CODE-011':('Partial','Actual8-solid project containing11/14-file nested source/font/SVG/STL/heightmap dependencies saved, native reopened and saved again whole-document exact. Reopened pad rebuilt24mm from retained helper; replacement28mm native Update, Undo/Redo and source bytes exact, unrelated models unchanged. Older script-format and unapplied-draft variants remain pending.')}
for c in d['cases']:
 if c['id'] not in updates:continue
 c['status'],note=updates[c['id']]
 if note not in c['observations']:c['observations'].append(note)
 e='test-results/audit-2026-11-05/mouse/code-folder-verification.json'
 if e not in c['evidence']:c['evidence'].append(e)
d['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('supplemental',dict(Counter(c['status'] for c in d['cases'])))
p=folder/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('The latest full regression after all twelve fixes passes **605 checks, zero\nfailures and zero page errors** (`all-twelve-fixes/report.json`). The production\nreopen check also confirms LIVE-012 no longer reports a false paused workshop.\nThese automated checks remain separate from acceptance-case accounting.',
'The latest full regression after all eighteen fixes passes **619 checks, zero\nfailures and zero page errors** (`all-eighteen-fixes/report.json`). Four added\nclipboard-fallback layout checks also pass existing behavior; no speculative\nclipboard fix was made. TypeScript passes with that added check. Automated\nchecks remain separate from acceptance-case accounting.')
s=s.replace('The separate production origin multiple-download prompt still awaits permission.','The development tab\'s multiple-download prompt was left unchanged; serialized production downloads work. No browser permission or security setting was changed.')
note='''

## Native folder fallback and current desktop blocker

CODE-007 now passes through the Windows folder chooser, without enabling
extension file-URL access. verify-code-folder.py checks every source/dependency
byte, independent entry/helper selection, same-path replacement, exact native
reopen, targeted Update/Undo/Redo, nine closed STL outputs and unchanged models.
The accepted fourteen-file set includes custom Courier, nested modules, SVG,
STL and a heightmap; MCAD loads from the local bundled library. Independent
TrueType outlines use fontTools4.68.0 installed only in ignored audit tooling.

Windows switched to its secure lock screen while opening the next folder
chooser. Live native input requires the owner to unlock Windows; no credential
entry or security bypass is attempted. File-count/byte-boundary fixtures under
fixtures/code-limits are prepared, not executed. The current browser/file-picker
state is retained for continuation. The audit is not complete; Partial statuses
still mean required criteria or variants remain unverified.
'''
if '## Native folder fallback and current desktop blocker' not in s:s+=note
p.write_text(s,encoding='utf-8')
p=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(p.read_text(encoding='utf-8'))
env['recorded']=datetime.now(timezone.utc).isoformat()
env['additional_regression']={'report':'test-results/audit-2026-11-05/vector-clipboard-before/report.json','passed':4,'failed':0,'page_errors':0,'note':'New fallback test passes existing app behavior. Runtime app source unchanged after eighteen-fix619-check full run; only this test was added later.'}
env['desktop_blocker']='Windows secure lock screen observed during native folder chooser. Owner unlock requested; native work pending. No credential entry attempted.'
for entry in env['dirty_source']:entry['sha256']=hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
p.write_text(json.dumps(env,indent=2)+'\n')
p=folder/'execution.json';main=json.loads(p.read_text(encoding='utf-8'))
main['execution_blocker']={'observed':datetime.now(timezone.utc).isoformat(),'reason':'Windows secure lock screen prevents further native mouse/file-picker actions. Owner unlock requested. Independent saved-file checks continue.','prepared_not_executed':'CODE006/008 source2MB, dependencies20MB and2000-file boundaries'}
p.write_text(json.dumps(main,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
