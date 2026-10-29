from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import components
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/ACCESS-003-direction-final';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'ACCESS-003-ui.json');plan=read_json(root/'fixtures/ACCESS-003-plan.json');assert ui['status']=='Pass' and not ui['errors'] and [r['viewport'] for r in ui['rows']]==plan['viewports'];fixture=(root/plan['fixture']).read_bytes();assert hashlib.sha256(fixture).hexdigest()==plan['fixture_sha256'];original=np.asarray(Image.open(io.BytesIO(fixture)).convert('RGBA'));rows=[];downloads=[]
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
for row in ui['rows']:
    location=folder/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and np.array_equal(blank,original) and len(before['layers'])==1 and np.array_equal(decoded(before),original)
    for label in ['zoomed','hand-pan','space-pan','wheel-slider','wheel-dialog','marked-undone']:assert read(label)==before and np.array_equal(image(label),blank),(row['id'],label,'view controls paint/change saved source')
    marked=read('marked');expected=deepcopy(before);expected['layers'][0]['image']=marked['layers'][0]['image'];assert marked==expected;pixels=image('marked');assert np.array_equal(pixels,decoded(marked));mask=(pixels!=blank).any(axis=2);assert components(mask)==1;ys,xs=np.where(mask);assert np.hypot(xs+.5-450,ys+.5-140).max()<=13 and pixels[140,450].tolist()==plan['ink'];assert np.array_equal(pixels[:,:,3],blank[:,:,3]),'Tap changes unrelated alpha'
    for label in ['actual-pixels','fit','marked-redone','fresh/reopened']:assert read(label)==marked and np.array_equal(image(label),pixels),(row['id'],label,'view/history/fresh loses complete source')
    actual=row['actual'];assert abs(actual['rectangle']['width']-960)<.1 and abs(actual['rectangle']['height']-640)<.1 and actual['readout'].endswith('100%');assert row['zoomed']['rectangle']['width']>row['initial']['rectangle']['width']*1.3 and row['fit']['rectangle']['width']<960
    events=read_json(location/'events.json');pans=[e for e in events if e['action']=='native-paper-pan'];assert {p['mode'] for p in pans}=={'hand','space'}
    for pan in pans:assert abs(pan['after']['rectangle']['x']-pan['before']['rectangle']['x'])+abs(pan['after']['rectangle']['y']-pan['before']['rectangle']['y'])>1
    wheel=[e for e in events if e['action']=='native-ctrl-wheel'];assert [e['label'] for e in wheel]==['paper1','paper2','slider','dialog']
    for e in wheel[2:]:assert e['before']['window']==e['after']['window'] and e['before']['readout']==e['after']['readout'] and e['before']['rectangle']==e['after']['rectangle']
    inputs=read_json(location/'native-input.json');assert all(e['trusted'] for e in inputs);downs=[e for e in inputs if e['type']=='pointerdown' and not e['movingPaper']];ups=[e for e in inputs if e['type']=='pointerup' and not e['movingPaper']];assert len(downs)==len(ups)==1 and np.abs(np.array(downs[0]['source'])-plan['source_point']).max()<.01;assert len([e for e in inputs if e['type']=='pointerdown' and e['movingPaper']])==len(pans)
    for file in [location/'events.json',location/'fresh/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
    rows.append(dict(viewport=row['viewport'],source_dimensions=[960,640],known_fixture_alpha_RGBA_exact=True,native_pans=[dict(mode=p['mode'],label=p['label'],before=p['before']['rectangle'],after=p['after']['rectangle']) for p in pans],actual_CSS_source_scale=[actual['rectangle']['width']/960,actual['rectangle']['height']/640],slider_and_modal_ctrl_wheel_preserve_view=True,marker_changed_pixels=int(mask.sum()),marker_center_RGBA=pixels[140,450].tolist(),all_view_only_history_and_fresh_complete_source_RGBA_exact=True))
assert len(downloads)==96
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),all_four_planned_rows_verified=True,oracle=plan['oracle'],execution=ui['execution'],prior_failure_retained='headless/ACCESS-003-complete; its Space drag tried farther into the positive clamp after the hand pan. The complete rerun drags inward, retaining the same fixture/source patch and every wheel/scale branch.')
(root/'evidence/ACCESS-003-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='ACCESS-003',rows=len(rows),downloads=len(downloads))))
