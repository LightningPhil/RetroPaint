"""Native captured-frame merge scope, restoration and CAD guard verification."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n,prefix=91):
    name=f'mouse-audit-layer{prefix}-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('before');merged=doc('merged');expected=copy.deepcopy(before);del expected['layers'][2];lower=expected['layers'][1];lower['image']=merged['layers'][1]['image'];lower['opacity']=1;lower['visible']=True;lower['live']={k:[] for k in ['strokes','fills','sparkles']};lower.pop('photo',None);lower.pop('objects',None);expected['active']=lower['id'];assert expected==merged
assert before['layers'][2]['objects'][0]['live']['strokes'];assert before['layers'][2]['photo'] and before['layers'][1]['photo']
assert doc('undone')==before and doc('redone')==merged and doc('reopened')==merged
images=[]
for n in ['before','merged']:
    name=f'mouse-audit-layer91-{n}.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();images.append(np.array(Image.open(out/name).convert('RGBA')).astype(int))
error=int(np.max(abs(images[0]-images[1])));assert error<=2 # Existing predeclared LAYER-009 alpha-flattening tolerance.
cad=doc('before',90);neighbour=doc('cad-neighbour');expected=copy.deepcopy(cad);expected['active']=cad['layers'][3]['id'];assert neighbour==expected;assert doc('cad-active')==cad
report=dict(status='Pass',only_adjacent_two_sheets_combined=True,static_unit_opacity_lower_scope=True,unrelated_layers_exact=True,live_photo_and_objects_restored_exactly_by_undo=True,redo_and_reopen_whole_document_exact=True,captured_frame_max_rgba_error=error,predeclared_alpha_flattening_tolerance=2,paint_into_CAD_and_CAD_merge_controls_disabled=True,CAD_guard_documents_exact_except_chosen_active_target=True,sha256=hashes)
(out/'layer91-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native merge scope/frame, exact history/reopen and CAD merge guards')
