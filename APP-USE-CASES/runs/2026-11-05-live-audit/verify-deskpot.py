"""Prescribed20mm desk-container journey: real cavity, picture caption, saved source."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-deskpot231';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
ds=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(5)]
def canonical(d):
 d=copy.deepcopy(d)
 for l in d['layers']:
  if 'cad'in l:l.pop('image',None)
 return d
assert canonical(ds[3])==canonical(ds[4]);cad=ds[3]['layers'][1]['cad'];body=cad['bodies'][0];shell=body['solid'];assert shell['kind']=='shell'and shell['thickness']==3 and len(shell['faces'])==1 and shell['faces'][0]['normal']==[0,0,1]
cube,cylinder=shell['source']['solid']['children'];assert cube['solid']['shape']=='box'and cylinder['solid']['shape']=='cylinder'
assert all(o['solid']['size']==[20,20,20]and o['scale']==[1,1,1]for o in [cube,cylinder]);assert cube['position']==[0,0,10]and cylinder['position']==[15,0,10]
assert all(d['layers'][1]['cad']['bodies']==cad['bodies']for d in ds);assert ds[1]['layers'][1]['cad']['view']==cad['view'];assert ds[3]['layers'][2]['name']=='Paint above 3D'and 'cad'not in ds[3]['layers'][2]
caption=np.array(Image.open(io.BytesIO(base64.b64decode(ds[3]['layers'][2]['image'].split(',')[1]))).convert('RGBA'));mask=caption[:,:,3]>0;assert mask.sum()>1000 and np.all(caption[caption[:,:,3]==255,:3]==26) and np.all(caption[mask,:3]<=32);assert np.array_equal(caption,np.array(Image.open(io.BytesIO(base64.b64decode(ds[4]['layers'][2]['image'].split(',')[1]))).convert('RGBA')))
meshes=[retain(prefix+'-3d-mm'+(f' ({i})'if i else '')+'.stl')for i in range(3)];assert meshes[0]==meshes[1]==meshes[2]==(out/'mouse-audit-shell20-top-3d-mm.stl').read_bytes();tri=read_binary(meshes[0]);stats=measure(tri);assert len(stats['components'])==1 and stats['components'][0]['euler']==2
assert np.allclose(stats['bounds_mm'],[[-10,-10,0],[25,10,20]],atol=1e-5);walls=ray_y(tri[:,:,[1,0,2]],0,10);floor=ray_y(tri[:,:,[0,2,1]],0,.123);assert np.allclose(walls,[-10,-7,22,25],atol=1e-5)and np.allclose(floor,[0,3],atol=1e-5)
images=[]
for i in range(2):
 name=prefix+(f' ({i})'if i else '')+'.png';retain(name);images.append(np.array(Image.open(out/name).convert('RGBA')))
assert np.array_equal(*images);assert np.sum(np.all(images[0][:,:,:3]==26,axis=2))>500
report=dict(status='Pass',case='JOURNEY-007',prescribed_unscaled_cube20_cylinder20_atX15=True,complex_top_shell3=True,closed_outward_mesh=True,actual_bounds_mm=stats['bounds_mm'],straight_curved_wall_intersections_mm=walls,floor_intersections_mm=floor,geometry_exact_before_after_caption_and_reopen=True,all3stls_byte_exact_prior_independently_verified_shell=True,pinned_view_preserved=True,caption_on_separate_paint_sheet_above_CAD=True,caption_source_and_noncache_project_exact_after_reopen=True,reopened_png_pixel_exact=True,cached_cad_preview_only_regenerated_on_reopen=True,mesh=stats,hashes=hashes)
(out/'deskpot231-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k not in ['hashes','mesh']},indent=2))
