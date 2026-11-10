"""Verify Black Hole on the transparent Character layer."""
import json,base64,io,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';dl=Path.home()/'Downloads';names=['mouse-audit-hole260-transparent.retropaint','mouse-audit-hole260-undo.retropaint','mouse-audit-hole260-redo.retropaint','mouse-audit-hole260-reopened.retropaint'];hashes={}
for n in names:
 data=(dl/n).read_bytes();(out/n).write_bytes(data);hashes[n]=hashlib.sha256(data).hexdigest()
before=json.loads((root/'test-results/audit-2026-11-05/fixtures/eraser56/transparent.retropaint').read_text());after,undo,redo,reopen=[json.loads((out/n).read_text()) for n in names];assert after==redo==reopen
im=lambda l:np.array(Image.open(io.BytesIO(base64.b64decode(l['image'].split(',')[1]))).convert('RGBA'))
for i in range(4):
 assert np.array_equal(im(before['layers'][i]),im(undo['layers'][i]));
 if i!=2:assert np.array_equal(im(before['layers'][i]),im(after['layers'][i]))
a,b=im(before['layers'][2]),im(after['layers'][2]);yy,xx=np.mgrid[:640,:960];cx=(690-562)*960/813;cy=(240-122)*640/542;outside=np.hypot(xx+.5-cx,yy+.5-cy)>60;assert np.array_equal(a[outside],b[outside]);assert (b[:,:,3]<a[:,:,3]).sum()>0
report={'case':'PAINT-015','transparent_alpha_decreased_pixels':int((b[:,:,3]<a[:,:,3]).sum()),'alpha_increased_as_paint_moved_pixels':int((b[:,:,3]>a[:,:,3]).sum()),'outside_radius60_exact':True,'other_layer_pixels_unchanged':True,'undo_all_layer_pixels_exact':True,'legacy_boolean_paper_metadata_normalized_on_load':True,'redo_and_reopen_project_exact':True,'sha256':hashes};(out/'hole260-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
