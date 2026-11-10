"""Independent shell opening/thickness edit beneath a retained later fillet."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-shell211';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})' if i else '')+'.retropaint')) for i in range(7)]
def body(d):return next(l['cad']['bodies'][0] for l in d['layers'] if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active',None)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
assert canonical(docs[1])==canonical(docs[2])==canonical(docs[4]) and canonical(docs[3])==canonical(docs[5])==canonical(docs[6])
for d in docs:
 expected=copy.deepcopy(docs[0]);next(l for l in expected['layers'] if 'cad'in l)['cad']['bodies']=[body(d)];assert canonical(expected)==canonical(d)
for i,thickness,normal in [(1,3,[0,0,1]),(3,2,[1,0,0])]:
 s=body(docs[i])['solid'];assert s['kind']=='finish' and s['mode']=='fillet' and s['size']==1 and s['edges'][0]['center']==[.5,0,0]
 shell=s['source']['solid'];assert shell['kind']=='shell' and shell['thickness']==thickness and len(shell['faces'])==1 and shell['faces'][0]['normal']==normal
 assert shell['source']==body(docs[1])['solid']['source']['solid']['source']
 before=copy.deepcopy(body(docs[1]));before['solid']['source']['solid']['thickness']=thickness;before['solid']['source']['solid']['faces']=shell['faces'];assert before==body(docs[i])
raws=[];results=[]
for n in range(4):
 raw=retain(prefix+'-3d-mm'+(f' ({n})' if n else '')+'.stl');raws.append(raw);tri=read_binary(raw);stats=measure(tri);volume=(4668 if n<2 else 3392)-20*(1-math.pi/4)
 assert abs(stats['signed_volume_mm3']-volume)<.03 and len(stats['components'])==1 and stats['components'][0]['euler']==2 and np.max(abs(np.array(stats['bounds_mm'])-[[-10,-10,0],[10,10,20]]))<.001
 vertical=ray_y(tri[:,:,[0,2,1]],.31,.57);assert vertical==([0,3] if n<2 else [0,2,18,20])
 # Swap X/Y so this independent ray measures the right opening along X.
 along_x=ray_y(tri[:,:,[1,0,2]],.31,10);assert along_x==([-10,-7,7,10] if n<2 else [-10,-8])
 fillet=ray_y(tri,.123,.5);assert len(fillet)==2 and abs(fillet[0]-(-9-math.sqrt(.75)))<.01 and abs(fillet[1]-10)<.001
 results.append(dict(index=n,mesh=stats,analytic_volume_mm3=volume,centre_vertical_ray=vertical,mid_height_x_ray=along_x,bottom_fillet_y_ray=fillet))
assert raws[0]==raws[1] and raws[2]==raws[3]
report=dict(status='Pass',case='FEATURE-019',intact_unshelled_source_used_for_reselection=True,opening_top_to_right_and_thickness3_to2=True,later_bottom_fillet_reference_and_radius_preserved=True,independent_cavity_and_fillet_surfaces_rays_volume_verified=True,cancel_previous_opening_thickness_source_and_stl_exact=True,apply_one_undo_redo_exact=True,actual_reopened_history2mm_and_cancel_source_exact=True,reopened_final_stl_byte_exact=True,paint_and_unrelated_source_exact=True,meshes=results,hashes=hashes)
(out/'shell211-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['meshes','hashes']},indent=2))
