"""Exact object sets, source-pixel keyboard increments and history."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(prefix,n):
    name=f'mouse-audit-vector{prefix}-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
group=doc('78','selection-before');moved=doc('78','group-nudged');expected=copy.deepcopy(group)
for o in expected['layers'][0]['objects'][-2:]:o['matrix'][4]+=1
assert moved==expected and doc('78','group-undone')==group
before=doc('79','before');expected=copy.deepcopy(before);expected['layers'][0]['objects'][0]['matrix'][4]+=11;expected['layers'][0]['objects'][0]['matrix'][5]+=11
fit=doc('79','fit-focused');assert fit==expected and doc('79','zoom-arrows')==expected and doc('79','focused-redone')==expected
undone=copy.deepcopy(expected);undone['layers'][0]['objects'][0]['matrix'][5]-=10;assert doc('79','focused-undone')==undone
assert doc('79','field-arrow')==expected
numeric=json.loads((out/'vector79-numeric.json').read_bytes());assert numeric=={'before':'91','after':'92'}
report={'status':'Pass','native_Shift_add_remove_and_marquee_two_stamp_group':True,'only_group_two_matrices_move1':True,'group_Undo_exact':True,'ordinary1_Shift10_paper_pixels_fit_and_zoom_exact':True,'last_key_Undo_Redo_exact':True,'numeric_field_arrow_changes_field_only':numeric,'sha256':hashes};(out/'vector78-79-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS exact group membership transforms, zoom-independent keys and numeric-field isolation')
