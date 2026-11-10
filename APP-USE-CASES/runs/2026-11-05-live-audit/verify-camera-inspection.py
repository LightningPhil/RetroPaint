"""Retain camera red/green native evidence without conflating stale fixture pixels."""
from pathlib import Path
from PIL import Image
import copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def data(label,version=45,ext='retropaint'):
    name=f'mouse-audit-cadmix{version}-{label}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label,version=45):return json.loads(data(label,version))
def png(label):return np.array(Image.open(io.BytesIO(data(label,ext='png'))).convert('RGBA'))
original=doc('orthographic-reopened',44);broken=doc('open-close-only',44)
assert original['layers'][2]['cad']['view']['up']==[0,1,0] and broken['layers'][2]['cad']['view']['up']==[0,0,1]
before=doc('inspection-before');after=doc('inspection-after');assert before['layers'][2]['cad']['view']==after['layers'][2]['cad']['view']==original['layers'][2]['cad']['view']
scoped=copy.deepcopy(before);scoped['active']=201;scoped['layers'][2]['image']=after['layers'][2]['image'];assert scoped==after
canonical=doc('canonical-before');assert canonical==doc('canonical-after') and np.array_equal(png('canonical-before'),png('canonical-after'))
moved=doc('body-v2-moved');undone=doc('body-v2-undone');assert moved==doc('body-v2-redone')
scoped=copy.deepcopy(canonical);scoped['active']=203;assert scoped==undone
scoped=copy.deepcopy(canonical);scoped['layers'][2]['cad']['bodies'][0]['position']=[5,0,0];scoped['layers'][2]['image']=moved['layers'][2]['image'];assert scoped==moved
fixture_script=(root/'APP-USE-CASES/runs/2026-11-05-live-audit/prepare-cadmix-fixtures.py').read_text();assert "body_layer['cad']['view']={'position':[0,0,200]" in fixture_script
report={'status':'Pass','before_fix_no_camera_input_changed_up_and_position':True,'fixed_first_inspection_camera_exact_all_other_fields_unchanged_except_expected_Paint_target_and_CAD_cached_bitmap':True,'canonical_repeated_inspection_whole_project_and_RGBA_exact':True,'fixed_5mm_body_move_and_Undo_Redo_preserve_camera_and_other_definitions_exact':True,'fixture_caveat':'prepare-cadmix-fixtures.pyassignsToporthographicviewwithoutregeneratingoldperspectiveCADcachedbitmap. Firstinspectioncorrectlyregeneratestopbitmap; thisisnotanunchanged-renderclaim. RepeatedcanonicalinspectionhasentireprojectandRGBAidentity. Rawfixturebooleanpaperflagsnormalizeonlytonull; decodedRasterRGBAremainexact.','sha256':hashes}
(out/'camera45-inspection-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
