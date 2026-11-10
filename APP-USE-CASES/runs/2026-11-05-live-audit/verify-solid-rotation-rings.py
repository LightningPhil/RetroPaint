"""Independent axis invariants, snap oracle and all six native wedge meshes."""
from pathlib import Path
import copy,hashlib,json,math,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';ui=json.loads((out/'solid171-ui.json').read_text(encoding='utf-8'));hashes={};metrics={};documents={};angles={}
def retain(name):
    raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
base=json.loads(retain('mouse-audit-solid171-rotation-baseline.retropaint'));index=next(i for i,l in enumerate(base['layers']) if 'cad' in l);original=base['layers'][index]['cad']['bodies'][0];assert original['solid']['shape']=='wedge' and original['scale']==[1,.5,1.5]
def rotation(values):
    x,y,z=np.deg2rad(values);cx,sx,cy,sy,cz,sz=np.cos(x),np.sin(x),np.cos(y),np.sin(y),np.cos(z),np.sin(z);return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
def canonical(d):
    d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');return d
for sample in ui['samples']:
    n=sample['documentIndex'];d=json.loads(retain(f'mouse-audit-solid171-rotation-baseline ({n}).retropaint'));documents[sample['stage']]=d;body=d['layers'][index]['cad']['bodies'][0];assert np.allclose(body['position'],[0,0,10],atol=1e-10) and np.allclose(body['scale'],[1,.5,1.5],atol=1e-10);assert np.max(abs(np.array(body['rotation'])-sample['rotation']))<=.00051;expected=copy.deepcopy(base);expected['layers'][index]['cad']['bodies'][0].update(rotation=body['rotation'],position=body['position'],scale=body['scale']);assert canonical(d)==canonical(expected)
    matrix=rotation(body['rotation']);axis=sample['axis']
    if axis:
        k='XYZ'.index(axis);unit=np.eye(3)[:,k];assert np.allclose(matrix@unit,unit,atol=1e-10)
        angle=math.degrees(math.atan2(matrix[2,1],matrix[1,1])) if axis=='X' else math.degrees(math.atan2(matrix[0,2],matrix[0,0])) if axis=='Y' else math.degrees(math.atan2(matrix[1,0],matrix[0,0]));angles[sample['stage']]=angle
    if 'undoRotation' in sample:assert sample['undoRotation']==[0,0,0]
    if 'meshIndex' not in sample:continue
    suffix=f" ({sample['meshIndex']})" if sample['meshIndex'] else '';name=f'mouse-audit-solid171-rotation-baseline-3d-mm{suffix}.stl';raw=retain(name);count=struct.unpack_from('<I',raw,80)[0];assert count==8 and len(raw)==484;tri=np.array([struct.unpack_from('<12fH',raw,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3);local=np.array([[-10,-5,-15],[10,-5,-15],[-10,-5,15],[-10,5,-15],[10,5,-15],[-10,5,15]]);wanted=local@matrix.T+[0,0,10];vertices=np.unique(tri.reshape(-1,3),axis=0);assert len(vertices)==6;error=float(np.min(np.linalg.norm(vertices[:,None]-wanted[None,:],axis=2),axis=1).max());assert error<.00002;volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert abs(volume-3000)<.01
    edges={}
    for triangle in tri:
        for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
            aa,bb=tuple(a),tuple(b);key=tuple(sorted([aa,bb]));edges.setdefault(key,[]).append(1 if aa<bb else -1)
    assert all(len(v)==2 and sum(v)==0 for v in edges.values());metrics[sample['stage']]=dict(axis=axis,angle_degrees=angles[sample['stage']],max_vertex_error_mm=error,signed_volume_mm3=volume,bounds_mm=[tri.min(axis=(0,1)).tolist(),tri.max(axis=(0,1)).tolist()],outward_closed=True)
reference=angles['free-z-reference'];expected_angles={}
for increment in [1,5,15,45,90]:
    wanted=math.floor(reference/increment+.5)*increment;actual=angles[f'snap-z-{increment}'];assert abs(actual-wanted)<1e-8;expected_angles[str(increment)]=actual
assert len(set(round(v,6) for v in expected_angles.values()))==5
for axis in ['x','y']:
    expected=math.floor(angles['free-'+axis]/15+.5)*15;assert abs(angles['snap-'+axis+'-15']-expected)<1e-8
assert canonical(documents['all-restored'])==canonical(base);assert len(metrics)==6
report=dict(status='Pass',asymmetric_local_dimensions_mm=[20,10,30],pivot_mm=[0,0,10],free_and_snapped_each_axis_meshes=metrics,free_Z_reference_degrees=reference,all_five_snap_angles_degrees=expected_angles,one_gesture_undo_and_final_source_exact=True,paint_and_other_source_fields_exact=True,hashes=hashes,notes='Six actual native STLs, independent ZYX matrices and vertex sets; UI counters corrected against genuine files. Missing initial export was retried after layout/save completion; no missing file is counted.');(out/'solid171-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
