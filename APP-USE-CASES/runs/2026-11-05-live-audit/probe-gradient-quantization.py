"""Retain the initial exact-stop hypothesis and measure interpolation discrepancy."""
from pathlib import Path
from PIL import Image
from datetime import datetime
import json,base64,io,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';p=json.loads((root/'test-results/audit-2026-11-05/fixtures/gradient50/plan.json').read_bytes());e=json.loads((out/'gradient50-evidence.json').read_bytes());events=[]
for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text().splitlines():
    event=json.loads(line).get('event',{})
    if event.get('type')=='native pointer':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,event['detail']))
def point(q):
    r=q.get('paperRect',q['rect']);return np.array([(q['clientX']-r['x'])*320/r['width'],(q['clientY']-r['y'])*240/r['height']])
rows=[];yy,xx=np.indices((240,320));xy=np.stack([xx+.5,yy+.5],axis=-1)
for row in e['presets']:
    name=row['name'];g=row['gesture'];events1=[q for at,q in events if g['start']<=at<=g['end'] and q.get('target')=='view'];start=point(next(q for q in events1 if q['phase']=='pointerdown'));end=point(next(q for q in reversed(events1) if q['phase']=='pointerup'));delta=end-start
    stops=np.array([[int(s[i:i+2],16) for i in [1,3,5]] for s in p['presets'][name]]);t=np.clip(np.sum((xy-start)*delta,axis=-1)/sum(delta*delta),0,1);wanted=np.stack([np.interp(t,np.linspace(0,1,len(stops)),stops[:,i]) for i in range(3)],axis=-1)
    d=json.loads((Path.home()/'Downloads'/('mouse-audit-gradient50-'+name+'.retropaint')).read_bytes());actual=np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][1]['image'].split(',')[1]))))[:,:,:3];mask=np.zeros((240,320),dtype=bool);mask[21:140,21:140]=True
    samples=[{'x':30+int(i*90/(len(stops)-1)),'wanted':s.tolist(),'actual':actual[80,30+int(i*90/(len(stops)-1))].tolist()} for i,s in enumerate(stops)]
    rows.append({'name':name,'measured_start':start.tolist(),'measured_end':end.tolist(),'initial_exact_stop_samples':samples,'maximum_error_from_real_valued_interpolation':float(np.abs(actual[mask]-wanted[mask]).max()),'outside_floor_ceil_interval_channels':int(((actual<np.floor(wanted))|(actual>np.ceil(wanted)))[mask].sum())})
(out/'gradient50-initial-stop-hypothesis.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows,indent=2))
