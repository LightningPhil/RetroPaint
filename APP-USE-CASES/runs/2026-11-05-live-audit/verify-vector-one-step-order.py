"""Independently verify native one-step stacking without altering any piece."""
from pathlib import Path
import copy, hashlib, json
root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'; hashes={}
def doc(name):
    filename=f'mouse-audit-vector87-{name}.retropaint'
    data=(Path.home()/'Downloads'/filename).read_bytes()
    (out/filename).write_bytes(data); hashes[filename]=hashlib.sha256(data).hexdigest()
    return json.loads(data)
before=doc('before'); objects=before['layers'][0]['objects']; assert len(objects)==25
back=copy.deepcopy(before); back['layers'][0]['objects']=objects[:22]+objects[23:]+objects[22:23]
assert doc('backward')==back
assert doc('forward')==before
assert doc('undone')==back
assert doc('redone')==before
phone=copy.deepcopy(before); phone['layers'][0]['objects']=objects[:1]+objects[23:]+objects[1:23]
assert doc('phone-forward')==phone
controls=json.loads((out/'vector87-controls.json').read_text())
assert all(controls[k] for k in ['frontForwardDisabled','frontBackwardEnabled','afterBackwardForwardEnabled','returnFrontForwardDisabled','bottomBackwardDisabled','bottomForwardEnabled'])
assert controls['phoneForwardTarget']['height']>=44
report=dict(status='Pass',only_array_order_changes=True,selected_group_relative_order_retained=True,undo_redo_whole_document_exact=True,boundary_controls_correct=True,phone_mouse_forward=True,sha256=hashes)
(out/'vector87-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS native one-step group stacking, exact history, boundaries and phone control')
