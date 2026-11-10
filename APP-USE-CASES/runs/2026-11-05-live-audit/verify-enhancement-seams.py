"""Decode grid exports and compare native previews with shifted tile origins."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';source=np.array(Image.open(root/'test-results/audit-2026-11-05/fixtures/enhance154-grid.png').convert('RGB')).astype(float);ui=json.loads((out/'enhance154-ui.json').read_text());box=ui['previewBox'];side=round(min(box['w'],box['h']));left=round(box['x']+(box['w']-side)/2);top=round(box['y']+(box['h']-side)/2);metrics={}
for scale in [2,4]:
    name=f'mouse-audit-enhance154-grid-{scale}x-enhanced.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);image=Image.open(out/name).convert('RGBA');assert image.size==(192*scale,160*scale);a=np.array(image);assert np.all(a[:,:,3]==255)
    reduced=np.array(image.convert('RGB').resize((192,160),Image.Resampling.BOX)).astype(float);error=abs(reduced-source).mean(axis=2);mask=np.zeros(error.shape,bool)
    for edge in [64,128]:mask[:,edge-2:edge+2]=True;mask[edge-2:edge+2]=True
    seam_error=float(error[mask].mean());other_error=float(error[~mask].mean());assert seam_error<other_error*2+1
    # A detail job starts at source32,16; full-image tiles start at0,0.
    # Matching the same displayed crop checks seams against different boundaries.
    detail=np.array(Image.open(out/f'enhance154-detail{scale}.png').convert('RGB'))[top+3:top+side-3,left+3:left+side-3].astype(float);full=np.array(Image.open(out/f'enhance154-full{scale}.png').convert('RGB'))[top+3:top+side-3,left+3:left+side-3].astype(float);difference=abs(detail-full);assert difference.mean()<1 and np.quantile(difference,.99)<5,(scale,difference.mean(),np.quantile(difference,.99))
    # Every output row and column carries real structure; no unwritten or repeated strips.
    assert np.all(a[:,:,:3].max(axis=(1,2))>30) and np.all(a[:,:,:3].max(axis=(0,2))>30)
    assert not np.any(np.all(a[1:,:,:3]==a[:-1,:,:3],axis=(1,2))) and not np.any(np.all(a[:,1:,:3]==a[:,:-1,:3],axis=(0,2)))
    metrics[str(scale)]=dict(dimensions=list(image.size),seam_band_source_error=seam_error,other_band_source_error=other_error,shifted_tile_preview_mean_RGB_difference=float(difference.mean()),shifted_tile_preview_99th_percentile=float(np.quantile(difference,.99)),sha256=hashlib.sha256(data).hexdigest())
report=dict(status='Pass',metrics=metrics,scope='Opaque192x160 gradient, irregular grid and diagonal across9GPUtiles; all rows/columns decoded, different tile origins agree. Native rendered comparisons include all four source edges in the full outputs.');(out/'enhance154-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
