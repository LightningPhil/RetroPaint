"""Independent right-angle raster clipping and discarded-margin oracle."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-trim38-raster-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))
def exact(d,expected,before):
 assert pixels(d).tobytes()==expected.tobytes();complete=json.loads(json.dumps(before));complete['layers'][0]['image']=d['layers'][0]['image'];assert complete==d
src=image((out.parent/'fixtures/patch-labelled.png').read_bytes());before=doc('before');assert pixels(before).tobytes()==src.tobytes();rotated=src.crop((90,90,210,190)).transpose(Image.Transpose.ROTATE_270);cleared=src.copy();cleared.paste((0,0,0,0),(90,90,210,190))
assert image((out/'mouse-audit-edit-trim38-left-full-copy.png').read_bytes()).tobytes()==rotated.tobytes()
e=json.loads((out/'edit-trim38-evidence.json').read_bytes());assert {c['edge'] for c in e['raster']}=={'left','right','top','bottom','outside'};results=[]
for c in e['raster']:
 edge=c['edge'];cx,cy=c['centre'];expected=cleared.copy();expected.alpha_composite(rotated,(cx-50,cy-60));after=doc(edge+'-placed');exact(after,expected,before);assert image(actual(edge+'-placed','png')).tobytes()==expected.tobytes() and doc(edge+'-undone')==before
 if edge!='left':assert doc(edge+'-redone')==after
 assert c['rotatedSize']=='100 × 120 px' and c['beforePlaceSize']=='100 × 120 px · trims on Place' and not c['selectionVisible'] and c['placementStatus']=='Placed. Off-paper raster pixels were trimmed. Undo brings them back.'
 if edge=='left':
  retained=rotated.crop((40,0,100,120));assert c['retainedSize']=='60 × 120 px' and image((out/'mouse-audit-edit-trim38-left-retained-copy.png').read_bytes()).tobytes()==retained.tobytes();returned=expected.copy();returned.paste((0,0,0,0),(0,260,60,380));returned.alpha_composite(retained,(620,390));returned_doc=doc('left-returned');exact(returned_doc,returned,before);assert image(actual('left-returned','png')).tobytes()==returned.tobytes() and doc('left-return-undone')==after and doc('left-return-redone')==returned_doc
 results.append({'edge':edge,'destination':[cx-50,cy-60],'all_RGBA_exact':True,'whole_undo_redo_exact':True})
assert doc('reopened')==doc('outside-redone') and image(actual('reopened','png')).tobytes()==cleared.tobytes()
report={'status':'Partial','ordinary_raster_matrix_status':'Pass','right_angle_rotation_retains_asymmetric_label_pixels':True,'permanent_trim_four_edges_and_fully_outside_exact':results,'moved_back_fragment_cannot_recover_discarded_pixels':True,'native_project_png_reopen_exact':True,'remaining':'Editable Raster piece transform/source-resolution retention branch remains to test separately.','sha256':hashes};(out/'edit-trim38-raster-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
