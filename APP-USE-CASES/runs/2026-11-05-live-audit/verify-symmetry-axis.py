"""Retain a native axis-opacity failure in both editable and raster drawing."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
from shape_oracle import world_points
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def docs(prefix,n):return[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(n)]
vector=docs('mouse-audit-axis224',6);raster=docs('mouse-audit-axis225',7);assert vector[4]==vector[5]and raster[5]==raster[6]
objects=vector[4]['layers'][0]['objects'];assert len(objects)==4
for i,obj in enumerate(objects):
 assert obj['opacity']==.5 and obj['lineWidth']==3 and obj['stroke']['color'].lower()=='#1e88e5'and obj['fill']is None and len(obj['paths'])==(2 if i%2==0 else 1)
 if i%2==0:
  assert not obj['paths'][0].get('clip')and not obj['paths'][1].get('clip');a=np.array([[p['x'],p['y']]for p in obj['paths'][0]['points']]);b=np.array([[p['x'],p['y']]for p in obj['paths'][1]['points']]);assert a.shape==b.shape and np.max(abs(a-b))<.001
 assert vector[i+1]['layers'][0]['objects']==objects[:i+1]
baseline=copy.deepcopy(vector[0]);baseline['layers'][0].pop('objects',None)
for d in vector:
 c=copy.deepcopy(d);c['layers'][0].pop('objects',None);assert c==baseline
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA'))
assert raster[1]['drawingMode']=='raster'and np.all(pixels(raster[1])==255)
for n,box in [(2,(478,98,483,203)),(3,(78,98,83,203)),(4,(98,318,203,323)),(5,(98,498,203,503))]:
 before,after=pixels(raster[n-1]),pixels(raster[n]);mask=np.zeros((640,960),dtype=bool);x0,y0,x1,y1=box;mask[y0:y1,x0:x1]=True;assert np.array_equal(before[~mask],after[~mask])
results=[];blue=np.array([30,136,229]);white=np.array([255,255,255]);single=(blue+white)/2;double=blue*.75+white*.25
for prefix in ['mouse-audit-axis224','mouse-audit-axis225']:
 images=[]
 for n in range(2):
  name=prefix+(f' ({n})'if n else '')+'.png';retain(name);images.append(np.array(Image.open(out/name).convert('RGBA')))
 assert np.array_equal(*images);im=images[0];values=[im[y,x,:3].astype(float)for x,y in [(480,150),(80,150),(150,320),(150,500)]]
 assert np.max(abs(values[0]-double))<1.1 and np.max(abs(values[2]-double))<1.1 and np.max(abs(values[1]-single))<1.1 and np.max(abs(values[3]-single))<1.1
 assert np.min(values[1]-values[0])>5 and np.min(values[3]-values[2])>5
 results.append(dict(mode='editable vectors'if prefix.endswith('224')else'raster',vertical_axis_rgb=values[0].astype(int).tolist(),vertical_control_rgb=values[1].astype(int).tolist(),horizontal_axis_rgb=values[2].astype(int).tolist(),horizontal_control_rgb=values[3].astype(int).tolist(),intended_same_opacity_as_control=False,reopened_png_pixel_exact=True))
report=dict(status='Partial',case='PLAY-011',deferred_finding='AXIS224/225: coincident symmetry lanes darken50percent marks to approximately75percent opacity in vectors and raster',both_axis_directions_and_both_drawing_modes_confirmed=True,vector_axis_has2coincident_paths_vs1ordinary_control=True,actual_projects_reopen_exact=True,all4pngs_preserve_failure_after_reopen=True,raster_neighbouring_pixels_unchanged=True,intended_axis_no_duplicate_darkening=False,comparisons=results,hashes=hashes)
(out/'axis224-225-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
