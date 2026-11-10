"""Compare native reorder operations against unchanged layer identities/data."""
from pathlib import Path
from PIL import Image
import copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-layer70-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('before');layers={l['id']:l for l in before['layers']}
def expected(ids,active=103):
    d=copy.deepcopy(before);d['layers']=[layers[i] for i in ids];d['active']=active;return d
below=expected([101,103,102,104]);top=expected([101,102,104,103])
assert doc('drag-below')==below and doc('drag-top')==top;assert doc('drag-undone')==below
assert doc('noop')==below and doc('noop-undone')==before
assert doc('key-down-focused')==below;assert doc('key-selected')==expected([101,103,102,104],102)
assert doc('key-top')==expected([101,103,104,102],102);assert doc('key-top-boundary')==doc('key-top')
assert doc('key-bottom-boundary')==expected([101,103,104,102],101)
name='mouse-audit-layer70-drag-below.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);a=np.array(Image.open(io.BytesIO(data)).convert('RGBA'));assert np.all(a[120:160,120:180]==[30,136,229,255])
report={'status':'Pass','all_layer_data_and_active_identity_exact':True,'drag_composition_known_patch_exact':True,'noop_has_no_history_step':True,'keyboard_selection_order_focus_and_boundaries':True,'sha256':hashes};(out/'layer70-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native drag/no-op/history; focused keyboard selection/reorder/boundaries')
