"""Native selection/delete/lock/hide recovery and independent scoped STL decoding."""
from pathlib import Path
import copy,hashlib,json,struct
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def load(stage,prefix='solid163'):
    d=json.loads(retain(f'mouse-audit-{prefix}-{stage}.retropaint'));d.pop('active');
    for l in d['layers']:
        if 'cad' in l:l.pop('image')
    return d
base=load('baseline');index=next(i for i,l in enumerate(base['layers']) if 'cad' in l);deleted=copy.deepcopy(base);deleted['layers'][index]['cad']['bodies']=deleted['layers'][index]['cad']['bodies'][:1]
assert load('deleted')==load('redone')==deleted;assert load('undone')==load('restored')==load('empty-selection')==base
locked=copy.deepcopy(base);locked['layers'][index]['cad']['bodies'][1]['locked']=True;assert load('locked-after-delete-key')==locked
hidden=copy.deepcopy(base);hidden['layers'][index]['cad']['bodies'][1]['visible']=False;assert load('copy-hidden')==hidden
layer_hidden=copy.deepcopy(base);layer_hidden['layers'][index]['visible']=False;assert load('layer-hidden-before')==load('layer-hidden-after')==layer_hidden;assert load('visible-restored','solid164')==base
ui=json.loads((out/'solid163-ui.json').read_text());assert ui['one']==['Joined solid'] and ui['two']==ui['repeatUnique']==ui['all']==['Joined solid','Joined solid copy'] and ui['blank']==ui['emptyFinal']==[] and ui['emptyDeleteDisabled'];assert all(ui['locked'][k] for k in ['deleteDisabled','sizeDisabled','positionDisabled'])
fixed=json.loads((out/'solid164-ui.json').read_text());assert all('Add a visible solid' in item['status'] for item in fixed['hiddenScopes']);assert 'Add a visible solid' in fixed['hiddenCheck'] and 'Add a visible solid' in fixed['hiddenExport'];assert not (downloads/'mouse-audit-solid164-hidden-layer-3d-mm.stl').exists()
metrics={}
for name,expected_lo,expected_hi,expected_volume in [('mouse-audit-solid163-copy-hidden-3d-mm.stl',[-10,-10,0],[25,10,20],6688.252),('mouse-audit-solid164-visible-restored-3d-mm.stl',[-10,-30,0],[130,10,25],3*6688.252),('mouse-audit-solid164-visible-restored-3d-mm (1).stl',[-10,-30,0],[130,10,25],3*6688.252),('mouse-audit-solid164-visible-restored-3d-mm (2).stl',[-10,-10,0],[25,10,20],6688.252)]:
    raw=retain(name);count=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*count;tri=np.array([struct.unpack_from('<12fH',raw,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3);lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));volume=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6);assert np.allclose(lo,expected_lo,atol=.001) and np.allclose(hi,expected_hi,atol=.001) and abs(volume-expected_volume)<3;metrics[name]=dict(bounds_mm=[lo.tolist(),hi.tolist()],volume_mm3=volume,triangles=count)
report=dict(status='Pass',selective_delete_undo_redo_source_exact=True,unique_selection_and_blank_preserve_geometry=True,locked_piece_protected=True,piece_and_layer_eyes_restore_exact_source=True,all_hidden_scopes_rejected_after_fix=True,scoped_meshes=metrics,hashes=hashes,notes='Source comparison excludes regenerated CAD preview PNG and active-sheet selection; all paint sheets and full nested solid recipes/transforms/IDs compared exactly. Multilayer overlapping BOOLEAN scope fixture remains for DELIVER-020.');(out/'solid163-164-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
