"""Switching loft side style preserves driving constraints and profile placement."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-loft214';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(5)]
def body(d):return next(l['cad']['bodies'][0] for l in d['layers'] if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
assert canonical(docs[0])==canonical(docs[2]) and canonical(docs[1])==canonical(docs[3])==canonical(docs[4])
expected=copy.deepcopy(docs[0]);b=next(l['cad']['bodies'][0] for l in expected['layers'] if 'cad'in l);b['solid']['ruled']=False;b['solid']['feature']={'label':'Loft'};assert canonical(expected)==canonical(docs[1])
constraints=body(docs[1])['solid']['profiles'][1]['constraints'];assert len(constraints)==2 and constraints[0]['kind']=='length' and constraints[0]['value']==35 and constraints[1]['kind']=='horizontal'
results=[]
for n in range(2):
 raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');tri=read_binary(raw);stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==2 and abs(stats['signed_volume_mm3']-8250)<.05
 for z in [.001,15,29.999]:
  cx=5*z/30;w=20+15*z/30;xx=ray_y(tri[:,:,[1,0,2]],.123,z);yy=ray_y(tri,cx,z);assert len(xx)==len(yy)==2 and np.max(abs(np.array(xx)-[cx-w/2,cx+w/2]))<.003 and np.max(abs(np.array(yy)-[-5,5]))<.003
 results.append(dict(index=n,mesh=stats,analytic_volume_mm3=8250))
ui=json.loads((out/'loft214-ui.json').read_text(encoding='utf-8'));text=next(s for s in ui['states'] if s['stage']=='actual-smooth-reopened-driven-top')['text'];assert '2 constraints' in text and '35 mm' in text
geometry=json.loads((out/'loft213-verification.json').read_text());assert geometry['smooth_interpolates_all_profiles_with_continuous_waist_slope']
report=dict(status='Pass',case='FEATURE-023',three_profile_smooth_vs_ruled_surface_oracle='loft213-verification.json',two_profile_style_switch_preserves_every_point_plane_turn_and_constraint_id=True,both_closed_and_exact8250mm3_with_linear_sections=True,one_undo_redo_source_exact=True,actual_smooth_reopen_two_solved_constraints_and35mm_label=True,reopen_cancel_whole_source_exact=True,meshes=results,hashes=hashes)
(out/'loft214-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))

