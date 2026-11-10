"""Independent exact-size selection and rejected-input preservation oracle."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-size38-{suffix}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(suffix):return json.loads(actual(suffix))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
before=doc('before');src=image((root/'test-results/audit-2026-11-05/fixtures/patch-labelled.png').read_bytes());assert image(base64.b64decode(before['layers'][0]['image'].split(',',1)[1])).tobytes()==src.tobytes()
assert doc('rejected')==before and doc('boundaries-cancelled')==before and image(actual('rejected','png')).tobytes()==src.tobytes()
expected=src.copy();expected.paste((0,0,0,0),(100,100,200,180));expected.paste((255,0,0,255),(100,100,300,260))
after=doc('pixels');copy=json.loads(json.dumps(before));copy['layers'][0]['image']=after['layers'][0]['image'];assert after==copy and image(base64.b64decode(after['layers'][0]['image'].split(',',1)[1])).tobytes()==expected.tobytes()
for name in ('percent','redone','reopened'):assert doc(name)==after
assert doc('undone')==before
for name in ('pixels','percent','reopened'):assert image(actual(name,'png')).tobytes()==expected.tobytes()
e=json.loads((out/'edit-size38-evidence.json').read_bytes());assert len(e['invalid'])==10 and all(c['size']=='100 × 80 px' and 'between 1 and 4096' in c['status'] for c in e['invalid']);assert e['validSize']==e['percentSize']=='200 × 160 px' and e['validDimensions']==e['percentDimensions']=='960 × 640 pixels · 1 layer · Selection 200 × 160'
assert len(e['boundaries'])==4 and all(c['size'].startswith(f"{c['requested'][0]} × {c['requested'][1]} px") for c in e['boundaries'])
report={'status':'Pass','pixel_and_percent_200x160_exact':True,'paper_and_unrelated_pixel_coordinates_unchanged':True,'ten_invalid_inputs_preserve_whole_project':True,'min_max_both_axes_preview_then_cancel_preserves_source':True,'whole_undo_redo_native_project_png_reopen_exact':True,'sha256':hashes};(out/'edit-size38-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
