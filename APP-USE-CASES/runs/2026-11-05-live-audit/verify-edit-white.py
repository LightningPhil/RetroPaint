"""Check white threshold, retained coloured antialiasing and alpha over blue."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';fixtures=out.parent/'fixtures';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-white38-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))
raw=(fixtures/'patch-white-card.png').read_bytes();provenance=json.loads((fixtures/'patch-white-card-provenance.json').read_bytes());assert hashlib.sha256(raw).hexdigest()==provenance['sha256'];src=image(raw);before=doc('before');assert pixels(before).tobytes()==src.tobytes()
card=src.crop((650,100,690,140));assert image((out/'mouse-audit-edit-white38-copy.png').read_bytes()).tobytes()==card.tobytes()
for suffix,transparent in [('opaque',False),('transparent',True)]:
 patch=np.array(card);removed=np.all(patch[:,:,:3]>=250,axis=2)
 if transparent:patch[removed]=0
 expected=src.copy();expected.alpha_composite(Image.fromarray(patch),(400,100));after=doc(suffix);assert pixels(after).tobytes()==expected.tobytes()==image(actual(suffix,'png')).tobytes()
 complete=json.loads(json.dumps(before));complete['layers'][0]['image']=after['layers'][0]['image'];assert complete==after and doc(suffix+'-undone')==before
assert doc('transparent-redone')==doc('transparent')==doc('reopened') and image(actual('reopened','png')).tobytes()==pixels(doc('transparent')).tobytes()
report={'status':'Pass','copy_source_retained_exactly':True,'white_and_near_white_removed_only_when_all_RGB_at_least_250':True,'one_subthreshold_channel_retained':True,'coloured_antialiased_edges_retained':True,'half_alpha_red_over_blue_exact':True,'both_toggle_outcomes_RGBA_exact':True,'whole_undo_redo_native_project_png_reopen_exact':True,'sha256':hashes};(out/'edit-white38-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
