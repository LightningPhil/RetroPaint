"""Confirm stamp geometry remains independently editable after flip/reopen."""
from pathlib import Path
import copy,hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-vector77-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('before');two=doc('two-stamps');flipped=doc('flipped');old=before['layers'][0]['objects'];objects=two['layers'][0]['objects'];new=flipped['layers'][0]['objects']
assert len(objects)==len(old)+2 and objects[:-2]==old;assert objects[-1]['kind']==objects[-2]['kind']=='stamp'
assert objects[-1]['id']!=objects[-2]['id'];assert new[:-1]==objects[:-1]
a=copy.deepcopy(objects[-1]);b=copy.deepcopy(new[-1]);am=a.pop('matrix');bm=b.pop('matrix');assert a==b;assert am[0]>0 and bm[0]==-am[0] and am[3]==bm[3] and am[5]==bm[5]
reopened=doc('reopened');normalized=copy.deepcopy(flipped)
# The parser omits the optional false wet flag on settled raster gestures.
# Absence and false both mean settled; retain strict equality for all other data.
normalizations=[]
for i,o in enumerate(normalized['layers'][0]['objects']):
    if o.get('wet') is False and 'wet' not in reopened['layers'][0]['objects'][i]:
        o.pop('wet');normalizations.append(i)
assert normalized==reopened
report={'status':'Pass','two_independent_stamp_IDs':True,'only_second_matrix_flipped':True,'stamp_definition_and_all_neighbours_exact':True,'native_reopen_exact_except_optional_false_wet':normalizations,'platform':'Windows Chrome; dolphin emoji glyph retained on this platform. Cross-platform glyph appearance is not assumed identical.','sha256':hashes};(out/'vector77-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS independent stamps, isolated flip, preserved definitions and project reopening (optional false wet normalized)')
