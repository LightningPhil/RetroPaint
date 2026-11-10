"""Explicit Cancel and actual tab close keep unfinished letters out of saves."""
from pathlib import Path
from PIL import Image
import hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(s,ext='retropaint'):
 name=f'mouse-audit-caption-draft41-{s}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(s):return json.loads(actual(s))
assert doc('before')==doc('vector-cancelled') and doc('raster-before')==doc('raster-cancelled')
for s in ['vector-cancelled','raster-cancelled']:
 im=Image.open(io.BytesIO(actual(s,'png'))).convert('RGBA');assert im.size==(960,640) and set(im.getdata())=={(255,255,255,255)}
assert doc('mix-before')==doc('mix-recovered') and len(doc('mix-recovered')['layers'])==4
assert Image.open(io.BytesIO(actual('mix-before','png'))).convert('RGBA').tobytes()==Image.open(io.BytesIO(actual('mix-recovered','png'))).convert('RGBA').tobytes()
report={'status':'Pass','explicit_raster_vector_cancel_whole_project_and_saved_png_exact':True,'actual_tab722_close_then_new_tab727_recent_draft_resume_four_layer_project_and_png_exact':True,'close_options_note':'Closing the options drawer leaves the complete draft preview available for further editing. Reopening and Cancel clears it; the drawer close is not a placement action.','input_recovery_note':'An earlier Ctrl+W attempt left tab719 open; native screenshot Close button subsequently removed it, verified by tab inventory. Strong nonblank recovery proof uses tab722, closed by its observed native Close button before creating tab727.','font_workflow_evidence':'caption-font41-verification.json covers two explicit lines, native tap position/movement, transforms and complete Undo/Redo in both modes.','sha256':hashes}
(out/'caption-draft41-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
