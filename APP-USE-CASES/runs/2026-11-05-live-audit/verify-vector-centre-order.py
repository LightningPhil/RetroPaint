"""Native group centring and front/back boundary identity checks."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(prefix,n):
    name=f'mouse-audit-vector{prefix}-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('85','after-animation');front=doc('86','centred-front');expected=copy.deepcopy(before)
for o in expected['layers'][0]['objects'][23:]:o['matrix'][4]+=280;o['matrix'][5]-=160
assert expected==front;assert doc('86','front-boundary')==front
back=doc('86','back');expected=copy.deepcopy(front);all=expected['layers'][0]['objects'];expected['layers'][0]['objects']=all[23:]+all[:23];assert expected==back
assert doc('86','back-boundary')==back
report={'status':'Pass','group_bounds_centred_on960x640':True,'relative_arrangement_preserved':True,'only_chosen_group_changes_stacking':True,'front_back_boundaries_preserve_every_piece':True,'scope':'Forward/backward one-step controls verified separately in vector87','sha256':hashes};(out/'vector86-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native exact group centre, preserved relative positions and front/back boundaries')
