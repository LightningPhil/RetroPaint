"""Analytic overlapping boxes, ownership moves, destination and layer capacities."""
from pathlib import Path
import copy,hashlib,json,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def load(stage):return json.loads(retain(f'mouse-audit-solid163-{stage}.retropaint'))
def canonical(d):
    d=copy.deepcopy(d);d.pop('active');
    for l in d['layers']:
        if 'cad' in l:l.pop('image')
    return d
base=load('boolean165-baseline');a=next(l for l in base['layers'] if l['name']=='Boolean pair');b=next(l for l in base['layers'] if l['name']=='Far cubes');assert [x['name'] for x in a['cad']['bodies']]==['A1','A2'] and [x['position'] for x in a['cad']['bodies']]==[[0,0,10],[10,0,10]];assert [x['position'] for x in b['cad']['bodies']]==[[100,0,10],[-100,0,10]] and not b['cad']['bodies'][1]['visible']
for layer in [a,b]:
    for body in layer['cad']['bodies']:assert body['solid']['shape']=='box' and body['solid']['size']==[20,20,20] and body['scale']==[1,1,1]
metrics={}
for n,scope,lo,hi,volume,components in [(0,'all_visible',[-10,-10,0],[110,10,20],20000,2),(1,'current_layer',[-10,-10,0],[20,10,20],12000,1),(2,'selected_A1',[-10,-10,0],[10,10,20],8000,1),(3,'far_layer_hidden',[-10,-10,0],[20,10,20],12000,1)]:
    suffix=f' ({n})' if n else '';name=f'mouse-audit-solid163-boolean165-baseline-3d-mm{suffix}.stl';raw=retain(name);count=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*count;tri=np.array([struct.unpack_from('<12fH',raw,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3);actual=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert np.array_equal(tri.min(axis=(0,1)),lo) and np.array_equal(tri.max(axis=(0,1)),hi) and abs(actual-volume)<.001
    vertices=set();edges={}
    for triangle in tri:
        for x,y in zip(triangle,np.roll(triangle,-1,axis=0)):
            xx,yy=tuple(x),tuple(y);vertices.update([xx,yy]);key=tuple(sorted([xx,yy]));edges[key]=edges.get(key,0)+1
    assert set(edges.values())=={2} and len(vertices)-len(edges)+count==2*components
    if n!=2:
        normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);x_faces=(abs(normal[:,0])>1e-8)&(abs(normal[:,1])<1e-8)&(abs(normal[:,2])<1e-8);assert not np.any(x_faces&((tri[:,0,0]==0)|(tri[:,0,0]==10)))
    metrics[scope]=dict(bounds_mm=[lo,hi],signed_volume_mm3=actual,triangles=count,closed=True,no_internal_overlap_faces=n!=2)
assert canonical(load('move166-undone'))==canonical(base);moved=load('move166-moved');expected=copy.deepcopy(base);aa=next(l for l in expected['layers'] if l['name']=='Boolean pair');bb=next(l for l in expected['layers'] if l['name']=='Far cubes');bb['cad']['bodies']+=aa['cad']['bodies'];aa['cad']['bodies']=[];assert canonical(moved)==canonical(expected)
capacity=[]
for stage in ['before','after']:
    name=f'mouse-audit-solid166-capacity-{stage}.retropaint';capacity.append(json.loads(retain(name)))
assert canonical(capacity[0])==canonical(capacity[1]);assert len(next(l for l in capacity[0]['layers'] if l['name']=='Far cubes')['cad']['bodies'])==127
full=load('layers167-full');restored=load('layers167-restored');assert len(full['layers'])==16 and sum('cad' in l for l in full['layers'])==15 and len({l['id'] for l in full['layers']})==16;assert canonical(restored)==canonical(capacity[1]);original_ids={l['id'] for l in capacity[1]['layers']};assert all(not l['cad']['bodies'] for l in full['layers'] if l['id'] not in original_ids);assert canonical(dict(capacity[1],layers=[l for l in full['layers'] if l['id'] in original_ids]))==canonical(capacity[1])
ui=json.loads((out/'solid166-ui.json').read_text());assert 'different destination' in ui['sameDestination'] and 'full' in ui['capacityStatus'];limits=json.loads((out/'solid167-ui.json').read_text());assert limits['full']==dict(cadLayers=15,newCadDisabled=True,newPaintDisabled=True) and limits['restored']['cadLayers']==2;scope_ui=json.loads((out/'solid165-ui.json').read_text())
report=dict(status='Pass',scoped_meshes=metrics,native_second_layer_ownership_exact=True,move_and_undo_source_exact=True,full_destination_rejection_atomic=True,max16_layers_guarded=True,thirteen_empty_layer_additions_undo_exact=True,hashes=hashes,notes='127-piece destination is a declared modern disposable fixture built from native valid Boolean scene, not a claim of physical UI creation of125 filler pieces. Native maximum-layer creation and all live moves/exports retained. Initial hidden-Far selection status was stale and is excluded; actual fourth STL proves hidden-layer omission, and selected-hidden-layer rejection is independently retained in solid163-164 report.');(out/'solid165-167-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
