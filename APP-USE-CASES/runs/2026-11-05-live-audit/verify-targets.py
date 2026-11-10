"""Native paint/hidden/piece/solid target and real name-key preservation."""
import copy,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(stage):
 name='mouse-audit-target-'+stage+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data)
 hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
baseline=doc('caption-before-name')
assert baseline['active']==104 and len(baseline['layers'])==5
for stage in ['caption-after-name','cad-after-name','final-caption']:assert doc(stage)==baseline,stage
paper=copy.deepcopy(baseline);paper['active']=101
assert 'clip' not in paper['layers'][1]['live']['strokes'][0]
paper['layers'][1]['live']['strokes'][0]['clip']=None
assert doc('paper')==paper
hidden=copy.deepcopy(baseline);hidden['active']=102;hidden['layers'][1]['visible']=False
assert doc('hidden-before')==hidden
keys=json.loads((out/'target-name-keyboard-evidence.json').read_bytes())
assert keys['layer']=={'name':'bersfgt','tool':'scissors'}
assert keys['cad']=={'name':'wer','tool':'translate','deleteDisabled':False}
assert keys['cadSheetActivatesWorkshop'] and keys['photoActionAbsentFromWorkshopAX']
result={'hidden_sheet_changes_only_intended_visibility_and_target':True,
 'paint_and_cad_real_name_keys_do_not_trigger_shortcuts':True,'whole_document_exact_after_name_and_target_navigation':True,
 'selecting_cad_sheet_enters_distinct_workshop_controls':True,
 'native_ui_observations':'Paper and Backdrop named; hidden Backdrop says tap its eye to see paint (hidden-layer painting is allowed). Caption dog stamp selected by native click and named in Piece picker. CAD sheet activates workshop; ordinary Photo action absent from its AX tree.',
 'initial_live_activation_normalization':'Backdrop activation omits optional clip:null from its conveyor stroke; both mean no clip. All other data exact. Whole-JSON comparisons after that activation require no normalization.',
 'diagnostic':'An early Paint-save helper was used while workshop active, closing it at the overlapping Paint button; corrected actual workshop screenshot retained separately. Helper now rejects wrong contexts.',
 'sha256':hashes}
(out/'targets-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='sha256'},indent=2))
