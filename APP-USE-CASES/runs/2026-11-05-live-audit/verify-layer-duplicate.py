"""Native rich paint and CAD sheet duplication, edit isolation and history."""
from pathlib import Path
import copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(prefix,n):
    name=f'mouse-audit-layer{prefix}-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc(89,'before');dup=doc(89,'duplicated');source=before['layers'][2];copied=dup['layers'][3]
assert copied['id']!=source['id'];same=copy.deepcopy(source);same.update(id=copied['id'],name='Character copy');assert same==copied
expected=copy.deepcopy(before);expected['layers'].insert(3,copied);expected['active']=copied['id'];assert expected==dup
visible=doc(89,'copy-visible');expected=copy.deepcopy(dup);expected['layers'][2]['visible']=False;assert expected==visible
for n in ['before','copy-visible']:
    name=f'mouse-audit-layer89-{n}.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
assert np.array_equal(np.array(Image.open(out/'mouse-audit-layer89-before.png')),np.array(Image.open(out/'mouse-audit-layer89-copy-visible.png')))
moved=doc(89,'copy-moved');expected=copy.deepcopy(visible);expected['layers'][3]['objects'][1]['matrix'][4]+=10;assert expected==moved
assert doc(89,'move-undone')==visible and doc(89,'move-redone')==moved and doc(89,'reopened')==moved
cadbefore=doc(90,'before');caddup=doc(90,'duplicated');source=cadbefore['layers'][2];copied=caddup['layers'][3];assert copied['id']!=source['id']
ids=[b['id'] for l in caddup['layers'] if l.get('cad') for b in l['cad']['bodies']];assert len(ids)==len(set(ids))
same=copy.deepcopy(source);same.update(id=copied['id'],name='Shell model copy')
for a,b in zip(same['cad']['bodies'],copied['cad']['bodies']):a['id']=b['id']
assert same==copied
expected=copy.deepcopy(cadbefore);expected['layers'].insert(3,copied);expected['active']=copied['id'];assert expected==caddup
assert doc(90,'undone')==cadbefore and doc(90,'redone')==caddup
report=dict(status='Pass',paint_components_exact=['pixels','objects','live definitions','photo recipe'],new_layer_identity=True,source_invariant_on_copy_edit=True,copy_only_ten_pixel_text_move=True,whole_document_undo_redo_and_reopen_exact=True,equivalent_visible_png_pixels_exact=True,CAD_all_body_ids_unique=True,CAD_source_recipes_exact=True,CAD_history_exact=True,sha256=hashes)
(out/'layer89-90-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native rich sheet and CAD duplication, isolated copy edit, exact visible content/history/reopen')
