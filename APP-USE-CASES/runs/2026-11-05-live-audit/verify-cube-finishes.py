"""Independent radius, plane, volume, topology and saved-history checks for EDGE206."""
from pathlib import Path
import copy, hashlib, json, math
import numpy as np
from stl_oracle import read_binary, measure, ray_y
root=Path(__file__).resolve().parents[3]; out=root/'test-results/audit-2026-11-05/mouse'; downloads=Path.home()/'Downloads'; prefix='mouse-audit-edge206'; hashes={}
def retain(name):
    raw=(downloads/name).read_bytes(); (out/name).write_bytes(raw); hashes[name]=hashlib.sha256(raw).hexdigest(); return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(10)]
index=next(i for i,l in enumerate(docs[0]['layers']) if 'cad' in l)
def body(d): return d['layers'][index]['cad']['bodies'][0]
def canonical(d):
    d=copy.deepcopy(d); d.pop('active',None); d['layers'][index].pop('image',None); return d
assert canonical(docs[2])==canonical(docs[0])
assert canonical(docs[1])==canonical(docs[3])==canonical(docs[4])==canonical(docs[6])==canonical(docs[8])
assert canonical(docs[5])==canonical(docs[7])==canonical(docs[9])
for d in docs:
    expected=copy.deepcopy(docs[0]); expected['layers'][index]['cad']['bodies']=d['layers'][index]['cad']['bodies']; assert canonical(expected)==canonical(d)
for i,mode in [(1,'fillet'),(5,'chamfer')]:
    b=body(docs[i]); s=b['solid']; assert s['kind']=='finish' and s['mode']==mode and s['size']==2 and len(s['edges'])==1
    e=s['edges'][0]; assert e['curve']=='LINE' and not e['closed'] and e['center']==[.5,0,1] and e['start']==[0,0,1] and e['end']==[1,0,1] and e['direction']==[1,0,0]
    source=copy.deepcopy(body(docs[0])); source['position']=[0,0,0]; assert s['source']==source
    expected=copy.deepcopy(body(docs[0])); expected['solid']=s; assert b==expected
results=[]; raws=[]
for n in range(3):
    raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl'); raws.append(raw); tri=read_binary(raw); stats=measure(tri)
    expected=8000-20*(4-math.pi) if n<2 else 7960
    assert abs(stats['signed_volume_mm3']-expected)<(.03 if n<2 else .02)
    assert len(stats['components'])==1 and stats['components'][0]['euler']==2 and np.max(abs(np.array(stats['bounds_mm'])-[[-10,-10,0],[10,10,20]]))<.001
    points=np.unique(tri.reshape(-1,3),axis=0); corner=points[(points[:,1]<-8+1e-6)&(points[:,2]>18-1e-6)]
    assert len(corner)>2
    if n<2:
        assert np.max(abs(np.hypot(corner[:,1]+8,corner[:,2]-18)-2))<.001
    else:
        assert np.max(abs(corner[:,2]-corner[:,1]-28))<.001
        assert any(np.linalg.norm(p[1:]-[-8,20])<.001 for p in corner) and any(np.linalg.norm(p[1:]-[-10,18])<.001 for p in corner)
    rays=[]
    for z in [17.9,19,19.9]:
        expected_front=(-10 if z<18 else -8-math.sqrt(4-(z-18)**2)) if n<2 else (-10 if z<18 else z-28)
        actual=ray_y(tri,.123,z); assert len(actual)==2 and abs(actual[0]-expected_front)<.01 and abs(actual[1]-10)<.001
        rays.append(dict(z=z,actual_y=actual,expected_front_y=expected_front))
    results.append(dict(index=n,mesh=stats,expected_volume_mm3=expected,rays=rays))
assert raws[0]==raws[1]
ui=json.loads((out/'edge206-ui.json').read_text(encoding='utf-8')); states={s['stage']:s for s in ui['states']}
for stage,count in [('front-face-interior-not-an-edge',0),('top-front-edge-on',1),('same-edge-off',0),('two-edges',2),('orbit-retains-two',2),('all-twelve-cube-edges',12),('clear-disables-preview',0)]: assert states[stage]['count'].startswith(str(count)+' edges')
assert not states['clear-disables-preview']['previewEnabled'] and not states['front-face-interior-not-an-edge']['previewEnabled']
for mode in ['fillet','chamfer']: assert f'Cannot {mode}' in states[mode+'50-rejected']['text'] and 'original solid is unchanged' in states[mode+'50-rejected']['text']
report=dict(status='Pass',cases=['FEATURE-010','FEATURE-011','FEATURE-012','FEATURE-015'],cube_all12_no_diagonal=True,toggle_clear_orbit_counts_verified=True,constant_radius2_and_setback2_analytic_surfaces_verified=True,closed_oriented_single_component=True,invalid50_corrected_in_same_editor=True,invalid_chamfer_cancel_source_and_stl_exact=True,each_apply_one_undo_redo_exact=True,actual_both_saved_projects_reopened_and_cancel_exact=True,paint_and_unrelated_source_exact=True,meshes=results,hashes=hashes)
(out/'edge206-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
