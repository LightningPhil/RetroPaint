"""Explicitly synthetic v12 format compatibility, native upgrade and Undo."""
import base64,copy,hashlib,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(stage):
 name='mouse-audit-code-legacy12-'+stage+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes()
 (out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def bodies(d):return next(l for l in d['layers'] if l.get('cad'))['cad']['bodies']
fixture=json.loads((out.parent/'fixtures/legacy-code-v12.retropaint').read_bytes())
opened=doc('opened');preview=doc('preview-only');updated=doc('updated13');undone=doc('undone');redone=doc('redone13');reopened=doc('reopened13')
expected=copy.deepcopy(fixture)
for a,b in zip(expected['layers'],opened['layers']):
 assert Image.open(io.BytesIO(base64.b64decode(a['image'].split(',')[1]))).convert('RGBA').tobytes()==Image.open(io.BytesIO(base64.b64decode(b['image'].split(',')[1]))).convert('RGBA').tobytes()
 a['image']=b['image'] # Browser re-encodes the synthetic Pillow PNG losslessly.
assert opened==expected
for d in [preview,undone]:assert d['version']==12 and bodies(d)==bodies(fixture)
assert updated==redone==reopened
assert updated['version']==13
for d in [opened,preview,updated,undone,redone,reopened]:assert d['layers'][:2]==fixture['layers'][:2]
a,b=bodies(fixture)[0],bodies(updated)[0]
for key in ['id','name','position','rotation','scale','color','visible','locked','solid']:assert a[key]==b[key],key
assert a['script']=={'language':'retrocad-1','source':'// Legacy subset model\ncube([2,3,4]);\n'}
assert b['script']=={'language':'openscad','source':a['script']['source'],'entry':'main.scad','files':[]}
report={'fixture_provenance':'Synthetic version12 compatibility data with genuine native 2x3x4 mesh; not represented as a historical download.',
 'native_open_metadata_and_decoded_pixels_exact':True,'preview_keeps_applied_legacy_language_and_format':True,
 'intentional_update_upgrades_only_script_metadata_to_v13':True,'geometry_identity_and_transform_exact':True,
 'one_step_undo_restores_v12':True,'redo_and_whole_native_reopen_exact':True,'paint_photo_neighbours_exact':True,'sha256':hashes}
(out/'code-legacy-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
