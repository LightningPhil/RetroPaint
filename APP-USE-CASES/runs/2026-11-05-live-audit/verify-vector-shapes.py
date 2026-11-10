"""Independent object identity/definition oracle for native vector shapes."""
from pathlib import Path
from PIL import Image
import copy,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-vector75-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('before');shapes=doc('shapes');resized=doc('resized');objects=shapes['layers'][0]['objects'];original=before['layers'][0]['objects']
assert len(original)==10 and len(objects)==12 and objects[:10]==original
assert objects[10]['kind']==objects[11]['kind']=='path';assert len({o['id']for o in objects})==12
new=resized['layers'][0]['objects'];assert new[:10]==original and new[11]==objects[11]
heart=copy.deepcopy(objects[10]);changed=copy.deepcopy(new[10]);assert heart.pop('matrix')!=changed.pop('matrix');assert heart==changed
assert resized==doc('reopened')==doc('after-export')
name='mouse-audit-vector75-resized.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);im=Image.open(io.BytesIO(data));assert im.size==(960,640)
report={'status':'Pass','complete_mixed_fixture_original10objects_exact':True,'heart_arrow_unique_path_pieces':True,'resize_only_changes_heart_matrix':True,'native_project_reopen_and_export_preserve_all_editability':True,'PNG_dimensions':[960,640],'sha256':hashes};(out/'vector75-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS separate heart/arrow, matrix-only resize, exact project reopening and export preservation')
