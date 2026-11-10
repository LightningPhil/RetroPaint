"""Native direct replacement and preservation, separate from HTML-drop capability."""
from pathlib import Path
from PIL import Image
import copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';e=json.loads((out/'conveyor46-evidence.json').read_bytes());hashes={}
old=['#E53935','#FDD835','#1E88E5','#43A047','#1A1A1A','#EF476F','#06D6A0','#118AB2'];new=[*old];new[3]='#9D4EDD'
def actual(label,ext='retropaint'):
    name='mouse-audit-conveyor46-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label):return json.loads(actual(label))
before=doc('before-replacement');failed=doc('failed-replacement');fixed=doc('fixed-replacement')
assert len(before['layers'][0]['live']['strokes'])==1 and len(failed['layers'][0]['live']['strokes'])==2 and len(fixed['layers'][0]['live']['strokes'])==3
assert all(s['spec']['colors']==old for s in failed['layers'][0]['live']['strokes']);assert fixed['layers'][0]['live']['strokes'][-1]['spec']['colors']==new
scoped=copy.deepcopy(failed);scoped['layers'][0]['live']['strokes'].append(fixed['layers'][0]['live']['strokes'][-1]);assert scoped==fixed
assert doc('fixed-undone')==failed and fixed==doc('fixed-redone')==doc('fixed-reopened')==doc('after-rapid-switches')
frames=[np.array(Image.open(io.BytesIO(actual(s,'png'))).convert('RGBA')) for s in ['fixed-time12345','fixed-reopened-time12345','after-rapid-time12345']];assert np.array_equal(frames[0],frames[1]) and np.array_equal(frames[0],frames[2])
attempts={a['kind']:a for a in e['attempts']};assert attempts['before-fix']['before']==attempts['before-fix']['after'] and attempts['before-fix']['draggableAttribute'] is None
for key in ['after-fix','after-fix-native-Windows','after-fix-held-source-plus-native-drag']:assert attempts[key]['after'][3]['background']=='rgb(67, 160, 71)'
assert attempts['fixed-native-right-click-replacement']['after'][3]['background']=='rgb(157, 78, 221)' and attempts['fixed-native-right-click-replacement']['chosenPressed']=='true'
assert attempts['fixed-native-Shift-F10-replacement']['after'][3]['background']=='rgb(255, 209, 102)'
assert attempts['fixed-native-ninth-Add-attempt']['disabled']=='' and sum(s['index'] is not None for s in attempts['fixed-native-ninth-Add-attempt']['after'])==8
def timers(text):return json.loads([s.split('timer counts: ',1)[1] for s in text.splitlines() if s.startswith('timer counts: ')][-1])
a,b=timers(e['timerBefore']),timers(e['timerAfter']);assert a['pendingFrames']==b['pendingFrames']==1 and a['pendingTimeouts']==b['pendingTimeouts']==2 and a['activeIntervals']==b['activeIntervals']==0 and a['created']['intervals']==b['created']['intervals']==0
report={'status':'Pass','native_replacement_mouse_and_keyboard_preserve_other_seven_slots':True,'native_disabled_ninth_Add_keeps_eight':True,'old_two_stroke_definitions_unchanged_new_stroke_has_replaced_colour':True,'native_whole_project_Undo_Redo_and_reopen_exact':True,'controlled_zero_speed_frame_RGBA_exact_after_reopen_and_24_mode_toggles':True,'timer_counts_before':a,'timer_counts_after':b,'HTML_drop_scope':'Visiblelivecolourdraggingwasmissingbeforefix. Correcteddragpayload/dropreplacementpassesfourlayoutcomponentchecks. Threepostfixnativeendpointdragattemptsdidnotdeliverreplacement; retainedasinputlimitation, notnativeHTMLdropPass. NativeRightclickandShiftF10completeactualreplacementflow.','sha256':hashes}
(out/'conveyor46-replacement-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
