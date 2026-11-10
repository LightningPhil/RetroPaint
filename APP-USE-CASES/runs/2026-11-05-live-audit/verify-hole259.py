"""Verify native Black Hole capture loss, source bounds and history."""
from pathlib import Path
from datetime import datetime
import json,base64,io,hashlib
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';dl=Path.home()/'Downloads';names=['mouse-audit-hole259.retropaint','mouse-audit-hole259-undo.retropaint','mouse-audit-hole259-redo.retropaint','mouse-audit-hole259-reopened.retropaint','mouse-audit-hole259-reopened.png','mouse-audit-hole259-image-reopened.png'];hashes={}
for n in names:
 data=(dl/n).read_bytes();(out/n).write_bytes(data);hashes[n]=hashlib.sha256(data).hexdigest()
before=json.loads((out/'mouse-audit-hole64-before.retropaint').read_text());after,undo,redo,reopened=[json.loads((out/n).read_text()) for n in names[:4]];assert before==undo and after==redo==reopened
pixels=lambda d:np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',')[1]))).convert('RGBA'))
a,b=pixels(before),pixels(after);changed=np.any(a!=b,axis=2);assert changed.any();yy,xx=np.mgrid[:640,:960];cx=(1100-562)*960/813;cy=(400-122)*640/542;outside=np.hypot(xx+.5-cx,yy+.5-cy)>60;assert np.array_equal(a[outside],b[outside]);assert np.all(b[:,:,3]==255)
assert Image.open(out/names[4]).convert('RGBA').tobytes()==Image.open(out/names[5]).convert('RGBA').tobytes()
records=[json.loads(s).get('event',{}) for s in (root/'test-results/audit-2026-11-05/fault-controls259/requests.jsonl').read_text().splitlines()];start=next(i for i,e in enumerate(records) if e.get('type')=='view samples scheduled');end=next(i for i in range(start,len(records)) if records[i].get('type')=='native pointer' and records[i]['detail']['phase']=='pointerup');records=records[start:end+1];samples=[e for e in records if e.get('type')=='view sample'];assert len(samples)==2 and samples[0]['detail']['hash']==samples[1]['detail']['hash'] and samples[0]['detail']['excludedColumns']==[]
p=[e for e in records if e.get('type')=='native pointer'];phase=lambda k:next(e for e in p if e['detail']['phase']==k);time=lambda e:datetime.fromisoformat(e['at'].replace('Z','+00:00'));down,lost,up=map(phase,['pointerdown','lostpointercapture','pointerup']);assert time(down)<time(lost)<time(samples[0])<time(samples[1])<time(up)
report={'case':'PAINT-015','capture_loss_seconds':(time(lost)-time(down)).total_seconds(),'sample_interval_seconds':(time(samples[1])-time(samples[0])).total_seconds(),'full_view_fnv1a_hash_equal_before_release':samples[0]['detail']['hash'],'changed_pixels':int(changed.sum()),'outside_radius60_exact':True,'paper_alpha_opaque':True,'undo_redo_and_project_reopen_exact':True,'sha256':hashes};(out/'hole259-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
