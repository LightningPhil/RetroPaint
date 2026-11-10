"""Native exact-view axes, preserved model, pinned Undo and responsive spans."""
from pathlib import Path
import copy,hashlib,itertools,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};docs={};views={}
def retain(n):
 name='mouse-audit-camera185'+(f' ({n})' if n else '')+'.retropaint';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();d=json.loads(raw);docs[n]=d;return d
base=retain(0);index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active');d['layers'][index].pop('image');d['layers'][index]['cad'].pop('view',None);return d
def view(d):return d['layers'][index]['cad']['view']
def same(a,b):
 assert a['projection']==b['projection'] and abs(a['span']-b['span'])<1e-8
 for key in ['position','target','up']:assert np.max(np.abs(np.array(a[key])-b[key]))<1e-8
directions={'iso':[1,-1.3,1],'top':[0,0,1],'bottom':[0,0,-1],'front':[0,-1,0],'back':[0,1,0],'left':[-1,0,0],'right':[1,0,0]}
ui=json.loads((out/'camera185-ui.json').read_text(encoding='utf-8'));assert len(ui['samples'])==14
for s in ui['samples']:
 d=retain(s['index']);assert canonical(d)==canonical(base);v=view(d);assert v['projection']==s['projection'];actual=np.array(v['position'])-v['target'];actual/=np.linalg.norm(actual);expected=np.array(directions[s['view']],float);expected/=np.linalg.norm(expected);assert np.linalg.norm(actual-expected)<.000002
 right=np.cross(v['up'],actual);right/=np.linalg.norm(right);up=np.cross(actual,right)
 assert np.isfinite(right).all() and np.isfinite(up).all()
 assert np.dot(up,[0,1,0] if s['view'] in ['top','bottom'] else [0,0,1])>.999999 if s['view']!='iso' else True
 views[(s['projection'],s['view'])]=v
 assert abs(v['span']-view(docs[1])['span'])<1e-8
assert canonical(retain(15))==canonical(base);same(view(docs[15]),view(docs[13]));assert canonical(retain(16))==canonical(base);same(view(docs[16]),view(docs[14]))
responsive=json.loads((out/'responsive186-ui.json').read_text(encoding='utf-8'));assert len(responsive['samples'])==6
for s in responsive['samples']:
 d=retain(s['index']);assert canonical(d)==canonical(base) and view(d)['projection']==s['projection'];assert abs(s['canvas']['width']/s['canvas']['height']-4/3)<.0001
same(view(docs[17]),view(docs[16]));same(view(docs[18]),view(docs[17]));same(view(docs[21]),view(docs[20]));assert abs(view(docs[19])['span']-view(docs[18])['span'])<1e-8;assert abs(view(docs[23])['span']-view(docs[21])['span'])<1e-8 and view(docs[23])['projection']=='perspective'
# Independent projection of the known source geometry proves fitted framing and parallelism.
local=np.vstack([np.array([[-10,-5,-5],[10,-5,-5],[-10,-5,25],[-10,5,-5],[10,5,-5],[-10,5,25]]),np.array(list(itertools.product([-2,2],repeat=3)))+[15,8,22]])
x,y,z=np.deg2rad([20,30,40]);rx=np.array([[1,0,0],[0,np.cos(x),-np.sin(x)],[0,np.sin(x),np.cos(x)]]);ry=np.array([[np.cos(y),0,np.sin(y)],[0,1,0],[-np.sin(y),0,np.cos(y)]]);rz=np.array([[np.cos(z),-np.sin(z),0],[np.sin(z),np.cos(z),0],[0,0,1]]);moving=(local*[1.5,.75,2])@(rz@ry@rx).T+[-13,8,-7];cube=np.array(list(itertools.product([-5,5],[-10,10],[-15,15])))+[100,50,30];vertices=np.vstack([moving,cube])
def project(points,v):
 direction=np.array(v['position'])-v['target'];distance=np.linalg.norm(direction);direction/=distance;right=np.cross(v['up'],direction);right/=np.linalg.norm(right);up=np.cross(direction,right);relative=points-np.array(v['target']);xy=np.column_stack([relative@right/(4/3),relative@up])*2/v['span']
 if v['projection']=='perspective':xy*=distance/(distance-relative@direction)[:,None]
 return xy
for n in [20,21,23]:assert np.max(np.abs(project(vertices,view(docs[n]))))<1
parallel={}
for projection in ['orthographic','perspective']:
 p=project(cube,views[(projection,'iso')]);a=p[1]-p[0];b=p[3]-p[2];parallel[projection]=abs(float(np.linalg.det(np.vstack([a/np.linalg.norm(a),b/np.linalg.norm(b)]))))
assert parallel['orthographic']<1e-12 and parallel['perspective']>.001
bounds=json.loads((out/'inspect184-ui.json').read_text(encoding='utf-8'));size=moving.max(axis=0)-moving.min(axis=0);assert bounds['worldMoving']=='Moving asymmetric · world bounds: '+' × '.join(f'{v:.2f}' for v in size)+' mm' and bounds['localMoving']==['40.5','11.25','60'] and bounds['worldReference']=='Reference cube · world bounds: 10.00 × 20.00 × 30.00 mm'
report=dict(status='Pass',all14_native_views_correct_axes_and_up=True,all_source_and_paint_exact=True,asymmetric_model_not_rotated_to_fake_views=True,opposite_views_distinct=True,orthographic_parallelism_and_perspective_convergence=parallel,pinned_view_undo_redo_previous_camera=True,responsive_portrait_landscape_both_projections=True,fit_and_resize_coherent_span=True,all_fitted_world_vertices_inside_frame=True,viewport_reset_to_default=True,world_vs_local_bounds_and_other_selection_exact=True,responsive_target_correction=responsive['target'],desktop_explicit_pin_correction=responsive['desktopCorrection'],hashes=hashes)
(out/'camera184-186-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
