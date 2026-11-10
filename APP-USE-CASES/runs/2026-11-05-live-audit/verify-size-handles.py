"""Native local handle, snap minimum, shared resize ratios and invalid saved-source checks."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name,mesh=False):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return read_binary(raw) if mesh else json.loads(raw)
base=retain('mouse-audit-size178.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
for n,scale in [(1,[1.9,.5,1.5]),(2,[.1,.5,1.5]),(3,[-.1,.5,1.5])]:
 doc=retain(f'mouse-audit-size178 ({n}).retropaint');actual=doc['layers'][index]['cad']['bodies'][0]['scale'];assert np.allclose(actual,scale)
 expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies'][0]['scale']=actual;assert canonical(doc)==canonical(expected)
assert canonical(retain('mouse-audit-size178 (4).retropaint'))==canonical(base)
tri=retain('mouse-audit-size178-3d-mm.stl',True);stats=measure(tri);expected=np.array([[-19,-5,-5],[19,-5,-5],[-19,-5,25],[-19,5,-5],[19,5,-5],[-19,5,25]]);actual=np.unique(tri.reshape(-1,3),axis=0);assert len(actual)==6 and np.min(np.linalg.norm(actual[:,None]-expected[None,:],axis=2),axis=1).max()==0;assert stats['signed_volume_mm3']==5700 and stats['components'][0]['euler']==2
multi=retain('mouse-audit-size178-multi.retropaint');doc=retain('mouse-audit-size178-multi (1).retropaint');expected=copy.deepcopy(multi)
for b in expected['layers'][index]['cad']['bodies']:b['scale']=(np.array(b['scale'])*[2,.5,1.25]).tolist()
assert canonical(doc)==canonical(expected)
for n in [2,3]:assert canonical(retain(f'mouse-audit-size178-multi ({n}).retropaint'))==canonical(multi)
ui=json.loads((out/'size178-ui.json').read_text(encoding='utf-8'));assert len(ui['invalid'])==4 and all('must be between' in s['status'] for s in ui['invalid'])
report=dict(status='Pass',local_x_handle_mm=[38,10,30],anchor_pose_unchanged=True,actual_closed_mesh=stats,multi_selection_shared_ratios=[2,.5,1.25],other_source_and_paint_exact=True,undo_exact=True,zero_negative_empty_oversize_rejected=True,snapped_near_zero_handle_floor_mm=2,notes='Native near-zero endpoints saved scale+0.1 and -0.1 (both positive physical width2mm); second crosses into supported mirror transform. UI dimensions alone cannot distinguish these: independently decoded source does. Three TransformControls scale snap replaces rounded0 with snap0.1; no singular saved geometry. Exact numeric0/-1 are explicitly rejected. No claim that a singular freehand value was physically reached.',hashes=hashes)
(out/'size178-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['hashes','actual_closed_mesh']},indent=2))
