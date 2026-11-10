"""Independent affine and native input-validity check for LIVE-039."""
from pathlib import Path
from PIL import Image
import hashlib,io,json,math
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-fractional39-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def near(a,b):assert len(a)==len(b) and max(abs(x-y) for x,y in zip(a,b))<1e-9
def bounds(m,w,h):
 corners=[(m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]) for x,y in [(0,0),(w,0),(w,h),(0,h)]];xs,ys=zip(*corners);return min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
before=doc('before');assert before==json.loads((out/'mouse-audit-edit-vector-overhang38-before.retropaint').read_bytes());objects=before['layers'][0]['objects'];i=next(i for i,o in enumerate(objects) if o['kind']=='text');o=objects[i];m=o['matrix'];x,y,w,h=bounds(m,o['width'],o['height']);sx=180.5/w;sy=120.25/h
resized=[sx*m[0],sy*m[1],sx*m[2],sy*m[3],x+sx*(m[4]-x),y+sy*(m[5]-y)];moved=resized[:4]+[resized[4]+330.5-x,resized[5]+278.5-y];cx=330.5+180.5/2;cy=278.5+120.25/2;r=math.pi/8;c=math.cos(r);s=math.sin(r);turned=[c*moved[0]-s*moved[1],s*moved[0]+c*moved[1],c*moved[2]-s*moved[3],s*moved[2]+c*moved[3],cx+c*(moved[4]-cx)-s*(moved[5]-cy),cy+s*(moved[4]-cx)+c*(moved[5]-cy)]
for suffix,expected in [('move-undone',resized),('resize-redone',resized),('turn-undone',moved),('move-redone',moved),('turned',turned),('turn-redone',turned),('reopened',turned)]:
 d=doc(suffix);actual_m=d['layers'][0]['objects'][i]['matrix'];near(actual_m,expected);complete=json.loads(json.dumps(before));complete['layers'][0]['objects'][i]['matrix']=actual_m;assert d==complete
assert doc('resize-undone')==before and doc('move-undone')==doc('resize-redone') and doc('turn-undone')==doc('move-redone') and doc('turned')==doc('turn-redone')==doc('reopened')
assert image(actual('turned','png')).tobytes()==image(actual('reopened','png')).tobytes()
e=json.loads((out/'edit-fractional39-evidence.json').read_bytes());assert {c['id'] for c in e['fields']}=={'objectWidth','objectHeight','objectX','objectY','objectAngle'} and all(c['valid'] and not c['stepMismatch'] and c['step']=='any' for c in e['fields'])
old=json.loads((out/'edit-vector-overhang38-evidence.json').read_bytes());assert any(not field['valid'] and field['stepMismatch'] for case in old['cases'] for field in case['returnFields'])
report={'status':'Pass','five_native_typed_fractional_fields_valid':True,'independent_size_position_centre_rotation_math_exact':True,'all_other_piece_geometry_materials_pixels_and_document_fields_unchanged':True,'separate_undo_redo_and_native_project_png_reopen_exact':True,'sha256':hashes};(out/'edit-fractional39-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
