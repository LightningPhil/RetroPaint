from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
folder=Path(__file__).resolve().parent;root=folder.parents[2];path=folder/'execution.json';ledger=json.loads(path.read_text(encoding='utf-8-sig'));cases={x['id']:x for x in ledger['cases']}
updates={
 'ACCESS-005':('Pass','Native Windows keyboard navigation on MIX fixture: Paint toolbox Right/Left/Home/End and wrapping, then Basic mode hides Advanced and Right skips directly Image toView. Restored Advanced. Preferences Sound/Yourdesk, Shortcuts Tools/Editing/Paper, all nineCADtooltabs and Piececontrols Size/Position/Arrange traversed by native keys with selected/focused AX and corresponding panels checked. KeyboardTab reachedShowrulers, Spaceenabled thenrestored. ArrowUp/Right inPhotoCurveOutput changes onlynumeric output; Cancel restored entire MIX. Right/Home/End inpiecePositionfield didnotnavigate tabs. Whole MIX before/afterexact; all five layer data andCADrecipe unchanged afterCAD/piece tabs.','keyboard-preservation-verification.json'),
 'ACCESS-007':('Pass','Native Paint keys B S R E F I A G T, PPhotoLab/Cancel, LLayers, Mmute/unmute eachreachedintendedvisibletool; soundrestored. Text shortcutletters/newline/CtrlEnter already verified inEDIT-024. Preferences modal ignoredBSRTEF, retainingBrushes. CADCtrlAselectsCube, W/E/RselectMove/Rotate/Size, Ffits; nativeWERFBtypedintobodyname field stayedtext andleftMoveactive; restoredoriginalname. CADhelp modal ignoredERFDelete, retainingoneCube andMove. NativeCtrlS inPaint saved actualPNGpixel-exact toMIXreference; inCAD saved genuineproject withidenticallayerdata. Finalentireproject exacttopre-shortcutsourceapartfromintentionallyselectedactive layer. WindowsCtrlvariant only; Cmdunavailable.','keyboard-preservation-verification.json'),
 'FILE-005':('Blocked','Prepared disposable supportedPNG, truncatedPNG andunsupportedTXT in own drop-fixtures folder. OpenedFileExplorer andpositioned itbesideChrome withmouse. Nativecross-windowdrag wasrejectedbytoolwindow-targetguardbeforethelocalfilecouldbedropped. TriedChromeownactualdownloadedPNGpanel as same-application alternative: native row andfile-icon drags produced no importedselection. No genuine Filesdrop was established, so neitherappfailure norsuccess isclaimed; placing/Undo/corruptdrop branches remain unverified. NativeOpen/Insert/OSclipboard routes work andhave separate evidence.','Live Chrome and native tool history in this chat')
}
for key,(status,note,evidence) in updates.items():
    case=cases[key];case['status']=status
    if note not in case['observations']:case['observations'].append(note)
    if evidence.endswith('.json'):evidence='test-results/audit-2026-11-05/mouse/'+evidence
    if evidence not in case['evidence']:case['evidence'].append(evidence)
ledger['updated']=datetime.now(timezone.utc).isoformat();path.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
counts={s:sum(x['status']==s for x in ledger['cases']) for s in sorted({x['status'] for x in ledger['cases']})}
readme=folder/'README.md';text=readme.read_text(encoding='utf-8');text=re.sub(r'Current accounting: \*\*[^\n]+\*\*',f"Current accounting: **{counts['Pass']} Pass, {counts['Partial']} Partial, {counts['Not run']} Not run, {counts['Blocked']} Blocked**",text,count=1)
text=text.replace('TypeScript and the fourteen-fix production build pass. The full regression is\nrunning; retain the thirteen-fix606check report until that run finishes.','TypeScript and the fourteen-fix production build pass. The full regression\nafter fourteen fixes passes **610 checks, zero failures and zero page errors**\n(`all-fourteen-fixes/report.json`).')
note='''

## Keyboard navigation, shortcut scope and native drop limitation

ACCESS-005 and ACCESS-007 pass on Windows. All five actual tablists were
exercised, including all nine CAD tabs, Home/End/wrapping and the hidden Basic
Advanced-tab skip. Field arrows stayed in their editors. Paint and CAD modal
dialogs blocked background shortcuts. All named Paint tools and CAD W/E/R/F
reached their intended controls. Actual Ctrl+S files differ appropriately:
Paint PNG versus CAD editable project. [Keyboard preservation verifier](verify-keyboard-preservation.py)
checks those bytes and unchanged multilayer/model data.

FILE-005 is Blocked by native cross-application drag targeting. File Explorer
was opened to disposable fixtures and positioned beside Chrome; the tool
rejected the drag into another application. Same-window Chrome downloaded-file
row/icon drags did not establish a real Files drop. This is not evidence of an
application defect or a successful drop. Open/Insert/system-clipboard routes
are independently verified. No original file was moved or removed.
'''
if '## Keyboard navigation, shortcut scope' not in text:text+=note
readme.write_text(text,encoding='utf-8')
envpath=root/'test-results/audit-2026-11-05/environment.json';env=json.loads(envpath.read_text(encoding='utf-8-sig'))
for item in env['dirty_source']:item['sha256']=hashlib.sha256((root/item['path']).read_bytes()).hexdigest()
env['recorded']=ledger['updated'];env['fix_count']=14;env['latest_regression']={'report':'test-results/audit-2026-11-05/all-fourteen-fixes/report.json','passed':610,'failed':0,'page_errors':0};env.pop('latest_full_regression_pending',None);envpath.write_text(json.dumps(env,indent=2)+'\n');print(counts)
