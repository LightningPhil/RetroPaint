"""Native mm/cm/in import scaling and optional centring, independent saved meshes."""
from pathlib import Path
import hashlib,json
import numpy as np
from stl_oracle import read_binary,measure
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-units174';hashes={};results=[]
fixture=read_binary((root/'test-results/audit-2026-11-05/fixtures/hollow173/offset-units174.stl').read_bytes())
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
for i,(unit,scale,centre) in enumerate([(u,s,c) for u,s in [('mm',1),('cm',10),('in',25.4)] for c in [False,True]]):
 suffix=f' ({i})' if i else '';tri=read_binary(retain(prefix+'-3d-mm'+suffix+'.stl'))
 expected=fixture*scale;position=np.array([-7.5,7,-11])*scale if centre else np.zeros(3);expected+=position
 actual_vertices=np.unique(tri.reshape(-1,3),axis=0);expected_vertices=np.unique(expected.reshape(-1,3),axis=0)
 maxerror=np.min(np.linalg.norm(actual_vertices[:,None]-expected_vertices[None,:],axis=2),axis=1).max()
 assert len(actual_vertices)==len(expected_vertices)==32 and maxerror<.0001
 stats=measure(tri);assert len(stats['components'])==4 and all(c['euler']==2 for c in stats['components'])
 assert abs(stats['signed_volume_mm3']/(856*scale**3)-1)<.000001
 assert np.allclose(sorted(c['signed_volume_mm3'] for c in stats['components']),np.array([-216,8,64,1000])*scale**3,rtol=.000001)
 project=json.loads(retain(prefix+f' ({i+1}).retropaint'));bodies=[b for l in project['layers'] if 'cad' in l for b in l['cad']['bodies']];assert len(bodies)==1 and bodies[0]['scale']==[1,1,1] and np.allclose(bodies[0]['position'],position)
 results.append(dict(unit=unit,centre=centre,position_mm=position.tolist(),vertex_error_mm=float(maxerror),mesh=stats))
report=dict(status='Pass',six_unit_and_centre_combinations=True,exact_source_placement=True,expected_scales=[1,10,25.4],cavities_preserved=True,results=results,hashes=hashes)
(out/'units174-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['results','hashes']},indent=2))
