from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
import json,re
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent
folder=root/'evidence'
read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
base=read('PHOTO-004-saved-before.retropaint')
group=read('PHOTO-007-group-reset.retropaint');single=read('PHOTO-007-single-reset.retropaint')
for doc in [group,single]:
    copy=deepcopy(doc);copy['layers'][0]['photo']=base['layers'][0]['photo'];assert copy==base
    s=doc['layers'][0]['photo']['settings']
    assert (s['saturation'],s['vibrance'],s['hue'])==(-100,100,45)
assert (group['layers'][0]['photo']['settings']['exposure'],group['layers'][0]['photo']['settings']['brightness'],group['layers'][0]['photo']['settings']['contrast'])==(0,0,0)
assert (single['layers'][0]['photo']['settings']['exposure'],single['layers'][0]['photo']['settings']['brightness'],single['layers'][0]['photo']['settings']['contrast'])==(1,0,30)
expected=deepcopy(group)
for settings in ['settings','normal']:
    expected['layers'][0]['photo'][settings]['exposure']=1
    expected['layers'][0]['photo'][settings]['contrast']=30
assert expected==single,'Single slider reset changed unrelated recipe fields'
assert single==read('PHOTO-007-reopened.retropaint')
image=lambda name:np.asarray(Image.open(folder/name).convert('RGBA'))
assert np.array_equal(image('PHOTO-007-single-reset.png'),image('PHOTO-007-reopened.png'))
assert np.any(image('PHOTO-007-group-reset.png')!=image('PHOTO-004-saved-before.png'))
assert np.any(image('PHOTO-007-single-reset.png')!=image('PHOTO-007-group-reset.png'))
def sliders(label):
    text=(folder/(label+'.txt')).read_text(encoding='utf-8')
    return dict(re.findall(r'slider .*Description: ([^,]+), Value: ([^\r\n]+)',text))
for label in ['PHOTO-007-light-after-group-reset']:
    values=sliders(label);assert {k:values[k] for k in ['Exposure','Brightness','Contrast']}==dict(Exposure='0',Brightness='0',Contrast='0')
for label in ['PHOTO-007-colour-before-group-reset','PHOTO-007-colour-after-other-group-reset','PHOTO-007-colour-after-single-reset','PHOTO-007-reopened-colour']:
    values=sliders(label);assert {k:values[k] for k in ['Saturation','Vibrance','Hue']}==dict(Saturation='-100',Vibrance='100',Hue='45')
for label in ['PHOTO-007-after-single-reset','PHOTO-007-reopened-light']:
    values=sliders(label);assert {k:values[k] for k in ['Exposure','Brightness','Contrast']}==dict(Exposure='1',Brightness='0',Contrast='30')
result=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,light_group_defaults=[0,0,0],colour_values_preserved=[-100,100,45],single_brightness_reset_only=True,visible_values_equal_saved_recipe=True,originals_neighbour_and_unrelated_fields_exact=True,actual_fresh_project_reopen_full_json_and_rgba_exact=True,scope='Light basic group reset; Colour settings retained; individual Brightness double-click reset. This tests reset scope, not colour processing mathematics or every scalar family endpoint.')
(folder/'PHOTO-007-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
