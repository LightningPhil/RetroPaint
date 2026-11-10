"""Retain crossed/tiny bounds proof without claiming an undelivered Shift."""
import base64,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];r=root/'test-results/audit-2026-11-05';o=r/'mouse';d=Path.home()/'Downloads';p='mouse-audit-edit-resize38-'
def doc(s):
 b=(d/(p+s+'.retropaint')).read_bytes();(o/(p+s+'.retropaint')).write_bytes(b);return json.loads(b)
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
b=doc('before');a=doc('regrown');s=image((r/'fixtures/patch-labelled.png').read_bytes());e=s.copy();e.paste((0,0,0,0),(100,100,200,180));e.paste((255,0,0,255),(150,100,251,201));assert image(base64.b64decode(a['layers'][0]['image'].split(',',1)[1])).tobytes()==e.tobytes();expected=json.loads(json.dumps(b));expected['layers'][0]['image']=a['layers'][0]['image'];assert a==expected and doc('undone')==b and doc('redone')==a
png=(d/(p+'regrown.png')).read_bytes();(o/(p+'regrown.png')).write_bytes(png);assert image(png).tobytes()==e.tobytes()
evidence=json.loads((o/'edit-resize38-crossed-evidence.json').read_bytes());assert evidence['tinySize']=='1 × 1 px' and evidence['regrownSize']=='101 × 101 px'
report={'status':'Partial','crossed_bounds_clamp_1x1_and_regrow_101x101':True,'whole_RGBA_source_and_regrown_exact':True,'whole_undo_redo_exact':True,'Shift_native_input_observed':False,'remaining':'Held browser Shift did not carry into native drag: actual PointerEvent.shiftKey remained false; no product failure inferred. Aspect-preserving native path remains unproved.'};(o/'edit-resize38-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
