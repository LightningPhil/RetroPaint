"""Check select-all and inverse masks against the independent RGBA fixture."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(suffix,ext='retropaint'):
 name='mouse-audit-edit-invert37-'+suffix+'.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(suffix):return json.loads(actual(suffix))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
before=doc('before');original=image((root/'test-results/audit-2026-11-05/fixtures/patch-labelled.png').read_bytes())
assert image(base64.b64decode(before['layers'][0]['image'].split(',',1)[1])).tobytes()==original.tobytes()
assert image((out/'mouse-audit-edit-invert37-all-copy.png').read_bytes()).tobytes()==original.tobytes()
complement=original.copy();complement.paste((0,0,0,0),(95,95,205,185));assert image((out/'mouse-audit-edit-invert37-complement-copy.png').read_bytes()).tobytes()==complement.tobytes()
expected=Image.new('RGBA',original.size);expected.alpha_composite(original.crop((95,95,205,185)),(95,95))
after=doc('deleted');assert image(base64.b64decode(after['layers'][0]['image'].split(',',1)[1])).tobytes()==expected.tobytes()
expected_doc=json.loads(json.dumps(before));expected_doc['layers'][0]['image']=after['layers'][0]['image'];assert expected_doc==after
assert doc('undone')==before and doc('redone')==after and doc('reopened')==after
assert image(actual('deleted','png')).tobytes()==expected.tobytes()==image(actual('reopened','png')).tobytes()
e=json.loads((out/'edit-invert37-evidence.json').read_bytes());assert e['emptyDisabled'] and e['allSize']==e['complementSize']=='960 × 640 px' and 'Draw around a piece' in e['hint']
report={'status':'Pass','select_all_clipboard_rgba_exact':True,'inverse_complement_clipboard_rgba_exact':True,'deleting_complement_leaves_only_selected_red':True,'whole_undo_redo_and_native_project_png_reopen_exact':True,'no_selection_invert_disabled_with_adjacent_selection_instruction':True,'sha256':hashes}
(out/'edit-invert37-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
