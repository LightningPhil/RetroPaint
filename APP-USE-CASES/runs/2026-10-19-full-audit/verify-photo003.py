from pathlib import Path
from datetime import datetime,timezone
import json,math
import numpy as np
from PIL import Image

root=Path(__file__).resolve().parent
folder=root/'evidence'
read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
assert read('PHOTO-003-before.retropaint')==read('PHOTO-003-cancelled.retropaint')
image=lambda name:Image.open(folder/name).convert('RGBA')
assert image('PHOTO-003-before.png').tobytes()==image('PHOTO-003-cancelled.png').tobytes()
r=read('PHOTO-003-view-rect.json')
# Fixed inset excludes the view frame/rounded corners and the paper navigation
# overlay, whose position was recorded in the actual UI screenshot.
box=(math.ceil(r['x'])+8,math.ceil(r['y'])+48,math.floor(r['x']+r['width'])-8,math.floor(r['y']+r['height'])-8)
crop=lambda label:np.asarray(image(label+'-ui.jpg').crop(box))
original=crop('PHOTO-003-original')
before=crop('PHOTO-003-before-comparison')
late=crop('PHOTO-003-before-after-outstanding-render')
draft=crop('PHOTO-003-draft-after')
restored=crop('PHOTO-003-after-comparison')
latest=crop('PHOTO-003-latest-after')
assert np.array_equal(original,before),'Before differs from the originally displayed source'
assert np.array_equal(original,late),'Late render replaced the original comparison'
assert np.array_equal(draft,restored),'After did not restore the current preview'
changed=int(np.any(original!=draft,axis=2).sum())
assert changed>100000,changed
assert np.any(latest!=draft),'Latest noise draft was not displayed by After'
asynchronous=read('PHOTO-003-asynchronous.json')
assert asynchronous['inflight']['busy']=='true'
assert asynchronous['selected']['pressed']=='true' and asynchronous['selected']['busy']=='true'
assert asynchronous['completed']['pressed']=='true' and asynchronous['completed']['busy']=='false'
result=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source_dimensions=[3896,2586],screenshot_source_inset=list(box),before_exact_to_original_source_display=True,after_exact_to_current_draft_display=True,changed_display_pixels=changed,comparison_survives_outstanding_render=True,latest_draft_distinct_and_restored=True,cancel_complete_project_identity=True,cancel_full_size_rgba_exact=True,limitations='Display comparison uses an explicitly bounded screenshot region. Complete original/export pixels are separately compared after Cancel; screenshots are not substituted for full-size exports.')
(folder/'PHOTO-003-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
