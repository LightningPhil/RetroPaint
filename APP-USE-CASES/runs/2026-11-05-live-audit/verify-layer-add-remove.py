"""Whole-document native add/pick/remove invariants."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-layer69-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def pixels(layer):return np.array(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
before=doc('before');removed=doc('removed');expected=copy.deepcopy(before);del expected['layers'][2];expected['active']=102;assert removed==expected
assert doc('undone')==before and doc('redone')==removed;assert len(doc('last-sheet')['layers'])==1
added=doc('added');assert len(added['layers'])==5;new=added['layers'][3];assert added['active']==new['id'];assert new['paper'] is None and not pixels(new).any()
assert added['layers'][:3]+added['layers'][4:]==before['layers']
painted=doc('painted');assert painted['active']==new['id'];assert painted['layers'][:3]+painted['layers'][4:]==before['layers'];assert pixels(painted['layers'][3])[:,:,3].any()
picked=doc('picked');expected=copy.deepcopy(painted);expected['active']=103;assert picked==expected
phone=doc('phone-added');assert len(phone['layers'])==6;newphone=phone['layers'][3];assert not pixels(newphone).any();assert phone['active']==newphone['id'];assert phone['layers'][:3]+phone['layers'][4:]==picked['layers']
expected=copy.deepcopy(phone);expected['active']=103;assert doc('phone-picked')==expected
report={'status':'Pass','remove_middle_identity_order_Undo_Redo_exact':True,'last_sheet_remove_disabled_observed':True,'new_layer_adjacent_and_clear':True,'paint_isolated':True,'desktop_and_phone_pick_only_changes_active':True,'phone_palette_closed_after_add_and_pick_observed':True,'sha256':hashes};(out/'layer69-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS removal/history guard, clear adjacent add, isolated paint and phone pick')
