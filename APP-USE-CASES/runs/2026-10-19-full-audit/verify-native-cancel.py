from pathlib import Path
import json
from datetime import datetime,timezone
from PIL import Image

root=Path(__file__).resolve().parent
e=root/'evidence'
read=lambda name:json.loads((e/name).read_text(encoding='utf-8'))
reference=read('PHOTO-002-short-resumed-before.retropaint')
pixels=Image.open(e/'PHOTO-002-short-resumed-before.png').convert('RGBA')
before=read('PHOTO-001-native-cancel-draft-before.json')
after=read('PHOTO-001-native-cancel-draft-after.json')
assert before['group']==after['group']=='colour-balance' and before['values']==after['values']
assert {v['name']:v['value'] for v in after['values']}=={'Temperature · cool / warm':'100','Tint · green / magenta':'0'}
assert {v['name']:v['value'] for v in after['light']}=={'Exposure':'-4','Brightness':'-100','Contrast':'0'}
for opened,closed in [('PHOTO-001-native-picker-open.txt','PHOTO-001-native-picker-cancelled.txt'),('FILE-002-native-plain-picker-open.txt','FILE-002-native-plain-picker-cancelled.txt')]:
    assert 'dialogue Open' in (e/opened).read_text(encoding='utf-8')
    assert 'dialogue Open' not in (e/closed).read_text(encoding='utf-8')
for prefix in ['FILE-002-native-cancel-after','FILE-002-native-plain-cancel-after']:
    assert read(prefix+'.retropaint')==reference
    output=Image.open(e/(prefix+'.png')).convert('RGBA')
    assert output.size==pixels.size and output.tobytes()==pixels.tobytes()
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,actual_windows_choosers_observed=2,photo_draft_group_and_all_experiment_values_restored=True,ordinary_open_image_does_not_reopen_photo_lab=True,complete_saved_project_exact=True,full_size_rgba_exact=True,dimensions=pixels.size,method='Actual Open dialogs, native filename focus and Escape, then real project/PNG downloads. Separate Photo lab Open photo and More/File/Open image paths.')
(e/'NATIVE-cancel-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
