"""Verify visibility and foreground edits are independent document operations."""
from pathlib import Path
from PIL import Image
import copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-layer71-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('before');hidden=doc('hidden');expected=copy.deepcopy(before);expected['layers'][1]['visible']=False;assert hidden==expected
painted=doc('painted');expected=copy.deepcopy(hidden);expected['layers'][2]['image']=painted['layers'][2]['image'];assert expected==painted and painted!=hidden
assert doc('paint-undone')==hidden and doc('hide-undone')==before
expected=copy.deepcopy(painted);expected['layers'][1]['visible']=True;assert doc('shown-painted')==expected
name='mouse-audit-layer71-hidden.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);a=np.array(Image.open(io.BytesIO(data)).convert('RGBA'));assert np.all(a[200:230,300:340]==255)
assert json.loads((out/'layer71-picker.json').read_bytes())['whiteSelected']=='true'
report={'status':'Pass','hidden_pixels_preserved':True,'export_and_picker_ignore_hidden_backdrop':True,'foreground_edit_isolated':True,'Undo_operations_independent':True,'show_retains_foreground_paint':True,'sha256':hashes};(out/'layer71-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS hidden export/picker, isolated foreground and independent history')
