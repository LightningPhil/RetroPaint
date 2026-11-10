"""Check palette/mode transitions preserve the complete saved picture."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(prefix,n):
    name=f'mouse-audit-{prefix}-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('layer71','shown-painted');assert doc('handoff72','cancelled')==before
done=doc('handoff72','done');assert done['active']==103;assert done['layers'][2]['photo']['settings']['temperature']==24
old=copy.deepcopy(before);new=copy.deepcopy(done)
for d in [old,new]:
    d['layers'][2].pop('photo',None);d['layers'][2].pop('image')
assert old==new
for n in ['basic','advanced','phone']:assert doc('handoff72',n)==done
e=json.loads((out/'handoff72-evidence.json').read_bytes());assert all(e.values()),e
report={'status':'Pass','cancel_whole_document_exact':True,'saved_recipe_only_on_target_layer':True,'basic_advanced_phone_whole_document_exact':True,'observed_UI':e,'sha256':hashes};(out/'handoff72-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS desktop/phone palette return and complete recipe retention across Basic/Advanced')
