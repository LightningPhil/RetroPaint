"""Verify actual UI clipboard mixed pieces and honest PNG system fallback."""
from pathlib import Path
from PIL import Image
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-vector83-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('before');pasted=doc('pasted');old=before['layers'][0]['objects'];new=pasted['layers'][0]['objects'];assert len(old)==19 and len(new)==22 and new[:19]==old
assert len({o['id']for o in new})==22
for src,copy_obj in zip([old[i]for i in [2,10,12]],new[19:]):
    a=copy.deepcopy(src);b=copy.deepcopy(copy_obj);assert a.pop('id')!=b.pop('id');am=a.pop('matrix');bm=b.pop('matrix');assert a==b and am[:4]==bm[:4] and bm[4]==am[4]+20 and bm[5]==am[5]+20
assert pasted==doc('reopened')
formats=json.loads((out/'vector83-clipboard-formats.json').read_bytes());assert formats==[['image/png','text/plain']]
im=Image.open(out/'vector83-clipboard-fallback.png');assert im.format=='PNG' and im.width>0 and im.height>0
report={'status':'Pass','mixed_path_stamp_raster_separate_and_exact':True,'group_relative_placement_and_sources_exact':True,'unique_copy_IDs':True,'native_reopen_entire_project_exact':True,'system_clipboard_fallback':'PNG plus plain-text private app marker; no vector interchange advertised','fallback_dimensions':im.size,'sha256':hashes};(out/'vector83-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native mixed clipboard copies, exact placement/materials and honest PNG fallback')
