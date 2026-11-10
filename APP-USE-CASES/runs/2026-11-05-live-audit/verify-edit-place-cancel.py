"""Independent native raster placement and cancellation checks."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(area,suffix,ext='retropaint'):
 name=f'mouse-audit-edit-{area}38-{suffix}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(area,suffix):return json.loads(actual(area,suffix))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))
def equal(d,expected,before):
 assert pixels(d).tobytes()==expected.tobytes()
 copy=json.loads(json.dumps(before));copy['layers'][0]['image']=d['layers'][0]['image'];assert d==copy
def composite8(background,piece,at):
 # Independent 8-bit premultiplied source-over. Pillow's straight-RGBA
 # composite rounds after unpremultiplication, unlike the canvas backing store.
 b=np.array(background).astype(float);f=np.zeros_like(b);x,y=at;f[y:y+piece.height,x:x+piece.width]=np.array(piece)
 sa=f[:,:,3:4];da=b[:,:,3:4];alpha=np.floor(sa+da*(255-sa)/255+.5)
 sp=np.floor(f[:,:,:3]*sa/255+.5);dp=np.floor(b[:,:,:3]*da/255+.5)
 p=np.floor(sp+dp*(255-sa)/255+.5);rgb=np.floor(p*255/np.maximum(alpha,1)+.5)
 return Image.fromarray(np.concatenate((rgb,alpha),axis=2).clip(0,255).astype('uint8'))
original=image((root/'test-results/audit-2026-11-05/fixtures/patch-labelled.png').read_bytes());before=doc('cancel','before');assert pixels(before).tobytes()==original.tobytes()
for suffix in ('escape','button'):
 assert doc('cancel',suffix)==before and image(actual('cancel',suffix,'png')).tobytes()==original.tobytes()
ce=json.loads((out/'edit-cancel38-evidence.json').read_bytes());assert len(ce['cases'])==2 and all(not c['selectionVisible'] for c in ce['cases']) and [c['size'] for c in ce['cases']]==['110 × 90 px','165 × 135 px']
assert doc('place','before')==before
placed=original.copy();placed.paste((0,0,0,0),(95,95,205,185));placed=composite8(placed,original.crop((95,95,205,185)).resize((220,270),Image.Resampling.BILINEAR),(245,195))
placed_doc=doc('place','placed');equal(placed_doc,placed,before);assert image(actual('place','placed','png')).tobytes()==placed.tobytes()
assert doc('place','undone')==before and doc('place','redone')==placed_doc
settled=placed.copy();settled.paste((0,0,0,0),(395,95,505,185));settled=composite8(settled,original.crop((395,95,505,185)).resize((220,180),Image.Resampling.BILINEAR),(545,395))
settled_doc=doc('place','tool-settled');equal(settled_doc,settled,before);assert image(actual('place','tool-settled','png')).tobytes()==settled.tobytes()
assert doc('place','tool-undone')==placed_doc and doc('place','tool-redone')==settled_doc
assert doc('place','reopened')==settled_doc and image(actual('place','reopened','png')).tobytes()==settled.tobytes()
pe=json.loads((out/'edit-place38-evidence.json').read_bytes());assert len(pe['cases'])==2 and all(not c['selectionVisible'] for c in pe['cases']) and [c['size'] for c in pe['cases']]==['220 × 270 px','220 × 180 px']
report={'status':'Pass','Escape_restores_lifted_source_exactly':True,'Cancel_restores_moved_resized_source_exactly':True,'Place_and_tool_change_settle_once_without_duplicate':True,'unconstrained_corner_resize_independent_width_height':True,'separate_gestures_undo_redo_exact':True,'native_project_png_reopen_exact':True,'sha256':hashes}
(out/'edit-place-cancel38-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
