from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np
import json,hashlib
root=Path(__file__).resolve().parent;base=root/'headless/ERASER-calibration';ui=json.loads((base/'ERASER-calibration-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'];yy,xx=np.mgrid[:640,:960];radii=[]
for row in ui['rows']:
    file=base/f"cursor-{row['size']}.png";image=np.asarray(Image.open(file).convert('RGBA'));cx,cy=row['source_point'];distance=np.hypot(xx+.5-cx,yy+.5-cy);dark=(image[:,:,:3].max(axis=2)<220)&(image[:,:,3]>150)&(distance>(0 if row['size']==1 else 3*row['source_per_CSS_pixel']));assert dark.sum()>5;radius=float(np.median(distance[dark]));expected=max(2.5*row['source_per_CSS_pixel'],.575*row['size'] if row['size']<=4 else .575*max(18,1.4*row['size']));assert abs(radius-expected)<=1,(row['size'],radius,expected);radii.append(dict(size=row['size'],independently_measured_dark_ring_median_radius=radius,planned_physical_erase_radius=.575*row['size'] if row['size']<=4 else .575*max(18,1.4*row['size']),visible_cursor_radius=expected,minimum_CSS_cursor_cue=row['size']==1,dark_ring_pixels=int(dark.sum()),public_canvas_sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
samples=ui['native_alpha_samples'];assert len(samples)==256;source=np.array([229,57,53],float);errors=[];straight=[]
for sample in samples:
    colour=np.array(sample['RGBA'][:3]);alpha=sample['RGBA'][3];error=float(np.abs((colour-source)*alpha/255).max());assert error<=1,(sample,error);errors.append(error)
    if alpha>0:straight.append(dict(alpha=alpha,maximum_straight_RGB_difference=float(np.abs(colour-source).max())))
assert max(r['maximum_straight_RGB_difference'] for r in straight)>2;report=dict(at=datetime.now(timezone.utc).isoformat(),status='Independent calibration verified; not an acceptance result',public_cursor_measurements=radii,native_8bit_destination_out_samples=256,maximum_premultiplied_channel_error=max(errors),maximum_unpremultiplied_RGB_difference=max(r['maximum_straight_RGB_difference'] for r in straight),source_RGB=[229,57,53],oracle='Actual public transparent cursor pixels measured with Pillow/NumPy, source/CSS geometry observed from public view, and application-free browser-native one-cell destination-out operations. At low alpha, compare associated colour within1 byte; complete source/history equality elsewhere remains exact. Existing minimum1px pointer cue is larger on-screen than its actual paint footprint. No app erase kernel supplies expected pixels.')
(root/'evidence/ERASER-independent-calibration.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
