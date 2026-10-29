from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
import json,math
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parent
folder=root/'evidence'
read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/name).convert('RGBA'))
baseline=read('PHOTO-004-saved-before.retropaint')
baseline_pixels=image('PHOTO-004-saved-before.png')
rows=[]
for stage,brightness,curve in [('first',25,[dict(x=0,y=0),dict(x=.25,y=.18),dict(x=.75,y=.82),dict(x=1,y=1)]),('revised',-15,[dict(x=0,y=.12),dict(x=.5,y=.5),dict(x=1,y=.95)])]:
    original=read('PHOTO-005-'+stage+'-commit.retropaint')
    reopened=read('PHOTO-005-'+stage+'-reopened.retropaint')
    assert original==reopened,stage+' changed on actual downloaded-file reopen'
    recipe=original['layers'][0]['photo']
    assert recipe['settings']['exposure']==1 and recipe['settings']['brightness']==brightness
    assert recipe['settings']['curves']['rgb']==curve
    for channel in ['red','green','blue']:assert recipe['settings']['curves'][channel]==[dict(x=0,y=0),dict(x=1,y=1)]
    without_photo=deepcopy(original);without_photo['layers'][0]['photo']=baseline['layers'][0]['photo']
    assert without_photo==baseline,'An original, neighbour, layer identity or unrelated document field changed'
    rendered=image('PHOTO-005-'+stage+'-commit.png')
    assert np.array_equal(rendered,image('PHOTO-005-'+stage+'-reopened.png'))
    assert int(np.any(rendered!=baseline_pixels,axis=2).sum())>100000
    assert tuple(rendered[1000,1500])==(67,160,71,255),'Separate green paint neighbour changed'
    rows.append(dict(stage=stage,brightness=brightness,rgb_curve=curve,complete_reopened_project_exact=True,full_size_reopened_rgba_exact=True,original_and_neighbour_and_unrelated_fields_exact=True))
first=read('PHOTO-005-first-apply-saving.json');retry=read('PHOTO-005-retry-saving.json');failed=read('PHOTO-005-failed-apply.json');completed=read('PHOTO-005-retry-completed.json')
for state in [first,retry]:
    assert state['panelVisible'] and state['doneDisabled'] and state['status']=='Saving editable adjustments…'
    assert 'Photo adjustments saved' not in state['editor'],'Premature success message'
assert failed['panelVisible'] and not failed['doneDisabled'] and failed['editor']=='Audit injected apply failure; the draft should remain available.'
assert {v['label']:v['value'] for v in failed['light']}==dict(Exposure='1',Brightness='25',Contrast='0')
assert failed['curveChannel']=='rgb' and failed['curveInput']=='0' and failed['curveOutput']=='0'
assert not completed['panelVisible'] and completed['editor']=='Photo adjustments saved. Your original is kept; reopen Photo lab to change them.'
r=read('PHOTO-005-curve-rect.json')
box=(math.ceil(r['x'])+2,math.ceil(r['y'])+2,math.floor(r['x']+r['width'])-2,math.floor(r['y']+r['height'])-2)
crop=lambda name:np.asarray(Image.open(folder/(name+'-ui.jpg')).convert('RGBA').crop(box))
assert np.array_equal(crop('PHOTO-005-before-failed-apply'),crop('PHOTO-005-failed-apply')),'Failed apply changed the actual displayed curve'
manifest=read('PHOTO-005-fault-manifest.json')
assert manifest['source_worker_unchanged'] and manifest['original_sha256']!=manifest['served_sha256']
result=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source_dimensions=[3896,2586],rows=rows,controlled_full_size_apply_failure_preserves_draft=True,displayed_curve_exact_after_failure=True,retry_commits_same_retained_draft=True,no_success_reported_before_commit=True,fault_scope=manifest['behavior'],notes='One locator wait timed out before the subsequent observation showed actual completion. It was not retried as an extra apply and is not classified as an application defect. Initial server reachability attempts are excluded. Fault worker is a retained, explicitly modified test fixture; the ordinary production build is unchanged.')
(folder/'PHOTO-005-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
