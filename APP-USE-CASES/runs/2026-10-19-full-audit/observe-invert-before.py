from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import distances
import numpy as np,json,hashlib,sys
root=Path(__file__).resolve().parent;base=root/'headless/PAINT-017-before';read_json=lambda p:json.loads(p.read_text(encoding='utf-8'));plan=read_json(root/'fixtures/PAINT-017-plan.json');prefix='--completed-prefix' in sys.argv
if not prefix:
    ui=read_json(base/'PAINT-017-ui.json');assert ui['status']=='Core workflows completed; independent oracle required' and not ui['errors'] and len(ui['rows'])==16
rows=[];downloads=[];original=np.asarray(Image.open(root/plan['fixture']).convert('RGBA'));yy,xx=np.mgrid[0:640,0:960]
for row in plan['before_rows']:
    location=base/row['id']
    if prefix and not (location/'native-input.json').exists():continue
    read=lambda name:read_json(location/(name+'.retropaint'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'));before=read('before');source=image('before');assert np.array_equal(source,original);first=read('first');second=read('second');expected=deepcopy(before);expected['layers'][0]['image']=first['layers'][0]['image'];assert first==expected;expected['layers'][0]['image']=second['layers'][0]['image'];assert second==expected;paint=image('first');twice=image('second');alpha_exact=np.array_equal(paint[:,:,3],source[:,:,3]) and np.array_equal(twice[:,:,3],source[:,:,3]);assert alpha_exact
    if row['flow'].endswith('tap'):
        p=source[140,150,:3].astype(float);wanted=np.rint(p+row['strength']*(255-2*p)).astype(int);actual=paint[140,150,:3].astype(int);error=int(np.abs(wanted-actual).max());metrics=dict(expected_core_RGB=wanted.tolist(),actual_core_RGB=actual.tolist(),maximum_core_error=error,chosen_strength_correct=error<=1,core_cells_checked=1,core_cells_wrong=int(error>1));failure=error>1
    else:
        distance=distances([[120,140],[480,140]],xx.ravel(),yy.ravel()).reshape(640,960);core=(distance<27.6)&(source[:,:,3]>0);wanted=255-source[core,:3].astype(int);actual=paint[core,:3].astype(int);error=np.max(np.abs(wanted-actual),axis=1);wrong=error>1;metrics=dict(core_cells_checked=int(core.sum()),core_cells_wrong=int(wrong.sum()),core_cells_unchanged_from_original=int(np.all(paint[core]==source[core],axis=1).sum()),maximum_core_error=int(error.max()),expected_Blue_core_RGB=[255,255,0],actual_Blue_core_RGB=paint[140,450,:3].tolist(),swept_core_complemented_once=not wrong.any());failure=bool(wrong.any())
    for name,ref in [('second-undone','first'),('first-undone','before'),('first-redone','first'),('second-redone','second')]:assert read(name)==read(ref),'Probe history is not one complete gesture'
    native=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in native);assert len([e for e in native if e['type']=='pointerdown'])==len([e for e in native if e['type']=='pointerup'])==2
    for event in read_json(location/'events.json'):
        if event['action']=='download':assert hashlib.sha256(Path(event['path']).read_bytes()).hexdigest()==event['sha256'];downloads.append(event)
    rows.append(dict(**row,**metrics,alpha_exact=True,complete_gesture_history_exact=True,status='Fail' if failure else 'Core probe agrees'))
assert rows and len(downloads)==10*len(rows)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-017',scope='Before-repair core probes only; no acceptance Pass.',decoder='Pillow '+Image.__version__,oracle=plan['oracle'],rows=rows,actual_downloads_verified=len(downloads),status='Fail' if any(r['status']=='Fail' for r in rows) else 'No failure in this completed prefix',complete_16_core_workflows=not prefix)
(root/('evidence/PAINT-017-before-prefix-observations.json' if prefix else 'evidence/PAINT-017-before-observations.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status=report['status'],completed_rows=len(rows),actual_downloads=len(downloads),failures=[dict(id=r['id'],wrong_core_cells=r['core_cells_wrong'],maximum_core_error=r['maximum_core_error']) for r in rows if r['status']=='Fail'])))
