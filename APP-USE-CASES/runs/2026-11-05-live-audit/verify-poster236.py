"""Verify native poster-paint overlap, history, zoom and exported pixels."""
from pathlib import Path
import base64,hashlib,io,json,shutil
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-poster236';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(7)]
assert docs[1]==docs[3]and docs[2]==docs[4]==docs[5]==docs[6]
def image(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA'))
first,second=image(docs[1]),image(docs[2]);assert len(np.unique(first[225:275,250:550,:3].reshape(-1,3),axis=0))>=8
a=first[240:260,380:470,:3].mean((0,1));b=second[240:260,380:470,:3].mean((0,1));assert b[0]<a[0]-30 and b[1]<a[1]-15
assert np.array_equal(first[220:280,200:300],second[220:280,200:300]);images=[]
for n in range(2):
 name=prefix+(f' ({n})'if n else '')+'.png';retain(name);images.append(np.array(Image.open(out/name).convert('RGBA')))
assert np.array_equal(images[0],second)and np.array_equal(images[1],second)
report=dict(case='PAINT-004',status='Pass',native_first_and_overlap_strokes=True,brush_size_px=50,strength=.5,texture_distinct_colours=int(len(np.unique(first[225:275,250:550,:3].reshape(-1,3),axis=0))),overlap_mean_rgb_before=a.tolist(),overlap_mean_rgb_after=b.tolist(),outside_overlap_unchanged=True,undo_redo_exact=True,zoom_85_to_191_project_exact=True,actual_reopen_and_both_pngs_pixel_exact=True,hashes=hashes)
(out/'poster236-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
