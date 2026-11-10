"""Independent native row/radial source series, identity isolation and capacity atomicity."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};results=[]
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
base=retain('mouse-audit-repeat177.retropaint');index=next(i for i,l in enumerate(base['layers']) if 'cad'in l);source=base['layers'][index]['cad']['bodies'][0]
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
def copies_match(before,after,count,circular,angle):
 original=before['layers'][index]['cad']['bodies'];bodies=after['layers'][index]['cad']['bodies'];assert len(bodies)==len(original)+count and bodies[:len(original)]==original
 assert len({b['id'] for b in bodies})==len(bodies)
 for n,b in enumerate(bodies[len(original):],1):
  expected=copy.deepcopy(original[0]);expected.update(id=b['id'],name=expected['name']+' copy',locked=False)
  if circular:
   theta=math.radians(angle*n);x,y,z=expected['position'];expected['position']=[x*math.cos(theta)-y*math.sin(theta),x*math.sin(theta)+y*math.cos(theta),z];expected['rotation'][2]+=angle*n
  else:expected['position']=[v+s*n for v,s in zip(expected['position'],[25,-5,2])]
  assert np.allclose(b['position'],expected['position'],atol=.000001);expected['position']=b['position'];assert b==expected
 expected=copy.deepcopy(before);expected['layers'][index]['cad']['bodies']=bodies;assert canonical(expected)==canonical(after)
ui=json.loads((out/'repeat177-ui.json').read_text(encoding='utf-8'))
for s in ui['samples']:
 after=retain(f"mouse-audit-repeat177 ({s['index']}).retropaint")
 if s['count'] in [0,31]:assert canonical(after)==canonical(base) and 'between' in s['status']
 else:copies_match(base,after,s['count'],s['circular'],s['angle'])
 results.append(s)
assert canonical(retain('mouse-audit-repeat177 (8).retropaint'))==canonical(base)
cap=retain('mouse-audit-repeat177-capacity.retropaint');assert len(cap['layers'][index]['cad']['bodies'])==127
assert canonical(retain('mouse-audit-repeat177-capacity (1).retropaint'))==canonical(cap)
copies_match(cap,retain('mouse-audit-repeat177-capacity (2).retropaint'),1,False,0)
assert canonical(retain('mouse-audit-repeat177-capacity (3).retropaint'))==canonical(cap)
assert '128 pieces' in ui['capacity']['rejected'] and ui['capacity']['acceptedPieces']=='128 pieces'
report=dict(status='Pass',native_series=results,copy_ids_unique=True,originals_and_nested_recipes_exact=True,clockwise_and_anticlockwise=True,counts_0_31_rejected=True,capacity127_plus2_atomic_rejection=True,capacity127_plus1_exact128=True,undo_source_exact=True,hashes=hashes)
(out/'repeat177-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['hashes','native_series']},indent=2))
