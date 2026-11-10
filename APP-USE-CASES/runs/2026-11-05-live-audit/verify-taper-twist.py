"""Independent ring geometry and continuous-volume oracle; preserve known discrepancy."""
from pathlib import Path
import copy, hashlib, json, math
import numpy as np
from stl_oracle import read_binary, measure

root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads'
prefix='mouse-audit-taper193'
ui=json.loads((out/'taper193-ui.json').read_text(encoding='utf-8'))
hashes={}
def retain(name):
 raw=(downloads/name).read_bytes(); (out/name).write_bytes(raw)
 hashes[name]=hashlib.sha256(raw).hexdigest(); return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(9)]
index=next(i for i,l in enumerate(docs[0]['layers']) if 'cad' in l)
def canonical(doc):
 d=copy.deepcopy(doc); d.pop('active',None); d['layers'][index].pop('image',None); return d
assert canonical(docs[3])==canonical(docs[4])==canonical(docs[6])
assert canonical(docs[5])==canonical(docs[7])
results=[]; meshes=[]
points=np.array([[0,0],[20,0],[20,10],[0,10]])
for sample in ui['samples']:
 body=docs[sample['docIndex']]['layers'][index]['cad']['bodies'][0]
 recipe=body['solid']; assert recipe['height']==30 and recipe['taper']==sample['taper'] and recipe['twist']==sample['twist']
 assert np.array_equal(recipe['points'],points)
 assert body['position']==body['rotation']==[0,0,0] and body['scale']==[1,1,1]
 suffix=f" ({sample['stlIndex']})" if sample['stlIndex'] else ''
 raw=retain(prefix+'-3d-mm'+suffix+'.stl'); meshes.append(raw); tri=read_binary(raw); stats=measure(tri)
 assert len(stats['components'])==1 and stats['components'][0]['euler']==2
 vertices=np.unique(tri.reshape(-1,3),axis=0); levels=np.unique(vertices[:,2]); max_error=0
 for z in levels:
  f=z/30; scale=1+(sample['taper']-1)*f; angle=math.radians(sample['twist'])*f
  rotation=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
  wanted=points@rotation.T*scale; actual=vertices[vertices[:,2]==z,:2]
  assert len(actual)==4
  error=np.min(np.linalg.norm(actual[:,None]-wanted[None,:],axis=2),axis=1).max(); max_error=max(max_error,float(error))
 assert max_error<.00001
 s=sample['taper']; expected=200*30*(1+s+s*s)/3
 error=stats['signed_volume_mm3']-expected
 if not sample['twist']: assert abs(error)<.001
 results.append(dict(stage=sample['stage'],mesh=stats,z_levels=len(levels),maximum_ring_error_mm=max_error,continuous_volume_mm3=expected,volume_error_mm3=error,relative_error_percent=100*error/expected,within_original_point_one_percent_tolerance=abs(error)/expected<=.001))
assert meshes[0]==meshes[-1]
assert all(x['editorOpen'] and x['pieces']=='1 piece' for x in ui['invalid'])
report=dict(status='Partial',deferred_finding='TAPER-193: twisted mesh volume differs from continuous analytic solid beyond 0.1% acceptance tolerance',untwisted_taper_exact=True,every_ring_matches_linear_scale_and_angle=True,neutral_restored_stl_byte_exact=True,invalid_drafts_cancel_source_exact=True,multiple_previews_one_undo_redo_source_exact=True,samples=results,hashes=hashes)
(out/'taper193-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['samples','hashes']},indent=2))
for result in results: print(result['stage'],result['volume_error_mm3'],result['relative_error_percent'])
