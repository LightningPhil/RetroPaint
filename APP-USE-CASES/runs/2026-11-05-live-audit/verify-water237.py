"""Watercolour overlap, soft edge and low-strength preservation."""
from pathlib import Path
import base64,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-water237';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(7)]
assert docs[4]==docs[5]==docs[6]
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA'))
images=[pixels(d)for d in docs];means=[a[240:260,380:470,:3].mean((0,1))for a in images[1:4]];assert means[0][0]>means[1][0]>means[2][0]and means[0][1]>means[1][1]>means[2][1]
sample=images[1][:,300,0];assert sample[300]==255 and sample[290]>sample[280]>sample[250] and sample[210]>sample[220]>sample[250]
light=images[4][400:440,250:550,:3];assert light[:,:,0].min()>200 and light[:,:,0].mean()<250
for n in range(2):
 name=prefix+(f' ({n})'if n else '')+'.png';retain(name);assert np.array_equal(np.array(Image.open(out/name).convert('RGBA')),images[5+n])
report=dict(case='PAINT-005',status='Pass',strength=.2,low_strength=.15,overlap_mean_rgb=[x.tolist()for x in means],soft_edge_red_samples={str(y):int(sample[y])for y in [210,220,250,280,290,300]},light_wash_mean_rgb=light.mean((0,1)).tolist(),tool_change_and_actual_reopen_project_exact=True,both_saved_pngs_pixel_exact=True,hashes=hashes)
(out/'water237-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
