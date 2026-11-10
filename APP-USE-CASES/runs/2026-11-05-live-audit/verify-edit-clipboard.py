"""Compare actual native clipboard workflows with independent labelled RGBA."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(suffix,ext='retropaint',version=38):
 name=f'mouse-audit-edit-clipboard{version}-{suffix}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(suffix,version=38):return json.loads(actual(suffix,version=version))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))
def equal(d,expected,before):
 assert pixels(d).tobytes()==expected.tobytes()
 copy=json.loads(json.dumps(before));copy['layers'][0]['image']=d['layers'][0]['image'];assert d==copy
original=image((root/'test-results/audit-2026-11-05/fixtures/patch-labelled.png').read_bytes());before=doc('before');assert pixels(before).tobytes()==original.tobytes()
red=original.crop((95,95,205,185));blue=original.crop((395,95,505,185));green=original.crop((95,295,205,385))
copied=original.copy();copied.alpha_composite(red,(645,405))
for version in (37,38):
 for suffix in ('blue-sentinel','after-denial-system'):
  assert image((out/f'mouse-audit-edit-clipboard{version}-{suffix}.png').read_bytes()).tobytes()==blue.tobytes()
 placed=doc('denied-placed',version);equal(placed,copied,before);assert image(actual('denied-placed','png',version)).tobytes()==copied.tobytes()
assert doc('denied-undone')==before and doc('denied-redone')==doc('denied-placed')
e=json.loads((out/'edit-clipboard38-evidence.json').read_bytes());assert 'System clipboard is unavailable' in e['status'] and 'from this session' in e['status'] and 'clipboard API denied: write' in e['controls'] and 'clipboard API denied: read' in e['controls']
old=json.loads((out/'edit-clipboard37-denied-evidence.json').read_bytes());assert old['status']=='Copied. Paste makes another piece.'
assert image((out/'mouse-audit-edit-clipboard38-normal-red.png').read_bytes()).tobytes()==red.tobytes()
copy_doc=doc('copy-placed');equal(copy_doc,copied,before);assert image(actual('copy-placed','png')).tobytes()==copied.tobytes()
cut=copied.copy();cut.paste((0,0,0,0),(95,295,205,385));cut_doc=doc('cut');equal(cut_doc,cut,before);assert image(actual('cut','png')).tobytes()==cut.tobytes()
pasted=cut.copy();pasted.alpha_composite(green,(645,155));paste_doc=doc('cut-pasted');equal(paste_doc,pasted,before);assert image(actual('cut-pasted','png')).tobytes()==pasted.tobytes()
assert doc('paste-undone')==cut_doc and doc('cut-undone')==copy_doc and doc('cut-redone')==cut_doc and doc('paste-redone')==paste_doc
assert doc('reopened')==paste_doc and image(actual('reopened','png')).tobytes()==pasted.tobytes()
report={'status':'Pass','denied_local_red_paste_exact_and_system_blue_unchanged':True,'unavailable_clipboard_message_explains_session_fallback':True,'normal_copy_retains_source':True,'cut_removes_only_selected_green':True,'both_pasted_instances_moved_to_expected_locations':True,'separate_cut_paste_undo_redo_exact':True,'native_project_png_reopen_exact':True,'sha256':hashes}
(out/'edit-clipboard38-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
