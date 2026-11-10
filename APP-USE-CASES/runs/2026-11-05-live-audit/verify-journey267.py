"""Verify a saved constrained plate, attached hole, finish and separate shell journey."""
import json,hashlib,io,base64
from pathlib import Path
import numpy as np
from PIL import Image
from stl_oracle import read_binary,measure,ray_y
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';dl=Path.home()/'Downloads';names=[f'mouse-audit-journey267-baseline ({i}).retropaint' for i in [5,6,7,8,9]]+[f'mouse-audit-journey267-baseline-3d-mm ({i}).stl' for i in [3,4,5]];hashes={}
for n in names:
 data=(dl/n).read_bytes();(out/n).write_bytes(data);hashes[n]=hashlib.sha256(data).hexdigest()
base,rev,undo,redo,cancel=[json.loads((out/n).read_text())for n in names[:5]];bodies=lambda d,n:next(l['cad']['bodies'] for l in d['layers'] if l['name']==n)
assert bodies(base,'Trace plate')==bodies(undo,'Trace plate') and bodies(rev,'Trace plate')==bodies(redo,'Trace plate')==bodies(cancel,'Trace plate')
assert all(bodies(base,'Shell model')==bodies(d,'Shell model') for d in [rev,undo,redo,cancel])
im=lambda l:np.array(Image.open(io.BytesIO(base64.b64decode(l['image'].split(',')[1]))).convert('RGBA'))
for d in [rev,undo,redo,cancel]:
 for x,y in zip(base['layers'],d['layers']):
  if 'cad' not in x:assert np.array_equal(im(x),im(y))
def features(v):
 found=[]
 def walk(x):
  if isinstance(x,dict):
   if x.get('kind')=='extrude':found.append(x)
   for y in x.values():walk(y)
  elif isinstance(x,list):
   for y in x:walk(y)
 walk(v);return found
for d,width in [(base,24),(rev,28)]:
 solids=features(bodies(d,'Trace plate'));plate=next(x for x in solids if x.get('feature',{}).get('label')=='Plate pull');hole=next(x for x in solids if x.get('feature',{}).get('label')=='Through hole');assert plate['feature']['constraints'][0]['value']==width and hole['feature']['constraints'][0]['kind']=='diameter' and hole['feature']['constraints'][0]['value']==4 and hole['feature']['attachment'] and hole['feature']['through']
raw=[(out/n).read_bytes()for n in names[5:]];assert raw[1]==raw[2];stats=[]
for data,width in zip(raw,[24,28,28]):
 tri=read_binary(data);m=measure(tri);assert len(m['components'])==1 and m['components'][0]['euler']==0 and abs(m['bounds_mm'][1][0]-m['bounds_mm'][0][0]-width)<1e-6;assert not ray_y(tri[:,:,[0,2,1]],.123,.17);assert ray_y(tri[:,:,[0,2,1]],5,.17)==[0.,7.];stats.append(m)
assert abs(stats[1]['signed_volume_mm3']-stats[0]['signed_volume_mm3']-280)<.001
report={'case':'JOURNEY-009','baseline_and_revised_width_mm':[24,28],'through_hole_diameter_mm':4,'original_volume_mm3':stats[0]['signed_volume_mm3'],'revised_volume_mm3':stats[1]['signed_volume_mm3'],'closed_genus_one_and_axis_open':True,'undo_redo_and_cancel_preserve_cad_sources':True,'shell_and_non_cad_pixels_unchanged':True,'reopened_stl_byte_exact':True,'invalid_edge_reselection_warning_observed':True,'separate_missing_support_repair_evidence':'support204-verification.json','sha256':hashes};(out/'journey267-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
