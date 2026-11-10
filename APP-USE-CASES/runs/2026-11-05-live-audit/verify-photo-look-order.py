"""All native Photo looks, reverse order and exact manual Normal baseline."""
from pathlib import Path
import copy,hashlib,json,time
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def read(name,kind):
    filename=f'mouse-audit-photo103-{name}.{kind}';path=downloads/filename;end=time.monotonic()+20
    while not path.exists() and time.monotonic()<end:time.sleep(.25)
    data=path.read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data) if kind=='retropaint' else np.array(Image.open(out/filename).convert('RGBA'))
baseline=json.loads((downloads/'mouse-audit-photo93-saved-recipe.retropaint').read_text());manual=baseline['layers'][0]['photo']['settings'];assert manual['brightness']==20 and len(manual['curves']['rgb'])==4
presets={'natural':dict(contrast=8,vibrance=15,clarity=8),'punch':dict(contrast=15,pop=35,vibrance=20),'mono':dict(saturation=-100,contrast=12),'warm':dict(temperature=24,tint=5,grain=12),'cool':dict(temperature=-25,tint=0)}
base_image=read('manual-baseline','png');rows=[]
for name,fields in presets.items():
    a=read('a-'+name,'retropaint');b=read('b-'+name,'retropaint');assert a==b
    expected=copy.deepcopy(baseline);settings=copy.deepcopy(manual);settings.update(fields);expected['layers'][0]['photo']=dict(settings=settings,normal=manual,look=name,lookActive=True);assert a==expected
    x=read('a-'+name,'png');y=read('b-'+name,'png');assert np.array_equal(x,y);assert np.array_equal(x[:,:,3],base_image[:,:,3]);assert not np.array_equal(x,base_image)
    if name=='mono':assert np.array_equal(x[:,:,0],x[:,:,1]) and np.array_equal(x[:,:,1],x[:,:,2])
    rows.append(dict(look=name,whole_project_and_export_order_independent=True,manual_baseline_retained=True))
normal=read('a-normal','retropaint');expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=dict(settings=manual,normal=manual,look='normal',lookActive=False);assert normal==expected;assert np.array_equal(read('a-normal','png'),base_image)
report=dict(status='Pass',looks=rows,first_order=['natural','punch','mono','warm','cool'],second_order=['cool','warm','mono','punch','natural'],normal_restores_earlier_manual_brightness_and_curve=True,normal_export_pixels_exact=True,all_source_and_other_fields_exact=True,sha256=hashes)
(out/'photo103-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS all five native looks, exact reverse-order projects/PNGs and preserved manual Normal baseline')
