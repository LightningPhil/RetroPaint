"""Verify saved Fine Mist outputs and the timed, native capture-loss trace."""
import json,hashlib,shutil
from datetime import datetime
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';dl=Path.home()/'Downloads';names=['mouse-audit-spray257.retropaint','mouse-audit-spray257.png','mouse-audit-spray257-sizes.retropaint','mouse-audit-spray257-sizes.png','mouse-audit-spray257-reopened.retropaint','mouse-audit-spray257-image-reopened.png','mouse-audit-spray258-edge.png','mouse-audit-spray258-undo.png','mouse-audit-spray258-redo.png'];hashes={}
for n in names:
 data=(dl/n).read_bytes();(out/n).write_bytes(data);hashes[n]=hashlib.sha256(data).hexdigest()
assert json.loads((out/names[2]).read_text())==json.loads((out/names[4]).read_text())
im=lambda n:Image.open(out/n).convert('RGBA')
a,b,e,u,r=map(im,[names[3],names[5],names[6],names[7],names[8]])
assert a.size==(960,640) and a.tobytes()==b.tobytes()==u.tobytes() and e.tobytes()==r.tobytes()
rgb=a.convert('RGB'); footprints=[]
for left,right in [(0,400),(400,960)]:
 points=[(x,y) for y in range(rgb.height) for x in range(left,right) if rgb.getpixel((x,y))!=(255,255,255)]
 footprints.append((min(x for x,y in points),max(x for x,y in points)))
assert footprints==[(169,274),(478,792)]
bounds=ImageChops.difference(a.convert('RGB'),e.convert('RGB')).getbbox();assert bounds==(0,157,57,263)
records=[json.loads(s).get('event',{}) for s in (root/'test-results/audit-2026-11-05/fault-controls257/requests.jsonl').read_text().splitlines()];samples=[e for e in records if e.get('type')=='view sample'];assert len(samples)==2 and samples[0]['detail']['hash']==samples[1]['detail']['hash'] and samples[0]['detail']['nonwhite']>0
pointers=[e for e in records if e.get('type')=='native pointer'];down=next(e for e in pointers if e['detail']['phase']=='pointerdown');lost=next(e for e in pointers if e['detail']['phase']=='lostpointercapture');up=next(e for e in pointers if e['detail']['phase']=='pointerup');time=lambda e:datetime.fromisoformat(e['at'].replace('Z','+00:00'));assert time(down)<time(lost)<time(samples[0])<time(samples[1])<time(up)
report={'case':'PAINT-010','capture_loss_seconds':(time(lost)-time(down)).total_seconds(),'sample_interval_seconds':(time(samples[1])-time(samples[0])).total_seconds(),'samples_before_mouse_release':True,'fnv1a_hash_equal_outside_wet_drip_columns':samples[0]['detail'],'wet_drips_may_continue_to_settle':True,'project_reopened_exact':True,'png_reopened_rgba_exact':True,'edge_changed_bounds':bounds,'edge_undo_redo_rgba_exact':True,'sha256':hashes};(out/'spray257-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
