"""Geometry and document identity checks across native workshop/layer handoffs."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-cadlayers73-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('before');hidden=doc('guide-hidden-return');phone=doc('phone-return');chosen=doc('chosen-paint');caption=doc('caption');returned=doc('caption-return')
for d in [hidden,phone,chosen,caption,returned]:
    assert [l['id']for l in d['layers']]==[201,202,203,204]
    assert d['layers'][2]['cad']['bodies']==before['layers'][2]['cad']['bodies']
    assert d['layers'][0]==before['layers'][0]
    for key in ['id','name','opacity','paper','image','live']:assert d['layers'][1][key]==before['layers'][1][key]
assert not hidden['layers'][1]['visible'] and phone['layers'][1]['visible']
assert hidden['active']==phone['active']==returned['active']==201
assert chosen['active']==caption['active']==204
assert chosen['layers'][3]==before['layers'][3]
assert len(caption['layers'][3]['objects'])==2
assert caption['layers'][3]['objects'][0]==before['layers'][3]['objects'][0]
assert returned['layers'][3]==caption['layers'][3]
e=json.loads((out/'cadlayers73-evidence.json').read_bytes());assert all(e.values()),e
report={'status':'Pass','all_editable_body_data_exact':True,'guide_visibility_only':True,'chosen_paint_target204':True,'close_fallback_valid_paint201':True,'caption_independent_and_original_object_exact':True,'UI':e,'sha256':hashes};(out/'cadlayers73-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS desktop/phone workshop Layers, guide toggle, chosen target, separate caption, exact geometry')
