"""Independently decode full multilayer neural export and check spatial coverage."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return out/name
before=json.loads(retain('mouse-audit-enhance153-mix-baseline.retropaint').read_text(encoding='utf-8'));after=json.loads(retain('mouse-audit-enhance153-mix-after.retropaint').read_text(encoding='utf-8'));assert before==after and len(before['layers'])==5 and not next(l for l in before['layers'] if l['name']=='Hidden reference')['visible']
actual=Image.open(retain('mouse-audit-enhance153-mix-baseline-2x-enhanced.png')).convert('RGBA');assert actual.size==(1600,1120)
reference=Image.open(downloads/'mouse-audit-enhance147-hidden-baseline.png').convert('RGBA');assert reference.size==(800,560);a=np.array(actual.resize(reference.size,Image.Resampling.BOX)).astype(float);b=np.array(reference).astype(float);assert np.all(a[:,:,3]==255) and np.all(b[:,:,3]==255)
error=abs(a[:,:,:3]-b[:,:,:3]);correlation=float(np.corrcoef(a[:,:,:3].ravel(),b[:,:,:3].ravel())[0,1]);bands=[]
for y in range(0,560,64):
    for x in range(0,800,64):bands.append(float(error[y:y+64,x:x+64].mean()))
assert error.mean()<8 and correlation>.98 and max(bands)<25,(error.mean(),correlation,max(bands))
report=dict(status='Pass',dimensions=list(actual.size),original_project_exact=True,retained_sheets=5,hidden_reference_excluded=True,full_RGB_correlation=correlation,mean_RGB_error=float(error.mean()),worst_source_tile_mean_error=max(bands),covered_source_tiles=len(bands),hashes=hashes,limitation='Reference PNG uses the frozen caption frame; this run used a running art clock. Spatial comparison tolerates neural detail and small live-ink differences, and does not claim pixel identity with that reference.')
(out/'enhance153-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
