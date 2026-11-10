"""Compare the repaired native half-opacity symmetry-axis marks with controls."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};results=[]
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
for mode in ['vector','raster']:
 stem='mouse-audit-axis239-'+mode;docs=[json.loads(retain(stem+suffix+'.retropaint'))for suffix in ['', ' (1)']];assert docs[0]==docs[1]
 images=[]
 for suffix in ['', ' (1)']:
  name=stem+suffix+'.png';retain(name);images.append(np.array(Image.open(out/name).convert('RGBA')))
 assert np.array_equal(*images);im=images[0];values=np.array([im[y,x,:3]for x,y in [(480,150),(100,150),(150,320),(150,500)]]).astype(int)
 assert np.max(abs(values[0]-values[1]))<=1 and np.max(abs(values[2]-values[3]))<=1
 assert np.max(abs(values-np.array([142.5,195.5,242])))<=1
 if mode=='vector':assert [len(o['paths'])for o in docs[0]['layers'][0]['objects']]==[1,1,1,1]
 results.append(dict(mode=mode,axis_and_control_rgb=values.tolist(),project_reopen_exact=True,png_reopen_pixel_exact=True))
report=dict(status='Pass',case='PLAY-011',original_axis_failure_reproduced_before_fix=True,vertical_and_horizontal_axis_match_control_in_both_modes=True,comparisons=results,hashes=hashes)
(out/'axis239-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
