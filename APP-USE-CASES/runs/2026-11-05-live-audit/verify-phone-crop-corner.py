"""Native narrow-phone wrong corner/stale field, repaired exact crop pixels."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from geometry_oracle import project_source
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(name,ext='retropaint'):
    filename=f'mouse-audit-phone145-{name}.{ext}';data=(downloads/filename).read_bytes();(out/filename).write_bytes(data);hashes[filename]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/filename).convert('RGBA')).astype(int)
base=load('wide-baseline');raw=project_source(base);defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];ui=json.loads((out/'phone145-ui.json').read_text(encoding='utf-8'));assert ui['viewport']==dict(width=320,height=568);assert ui['afterBeforeFix']['width']==480 and ui['rebuiltFieldsBeforeFix']['width']==576 and ui['activeAfter']=='photoCrop-width';assert ui['afterFix']==ui['expectedAfter']==dict(x=192,y=48,width=576,height=24) and ui['activeAfterFix']!='photoCrop-width'
for name,height in [('corner-before',12),('corner-fixed',24)]:
    d=load(name);a=load(name,'png');c=d['crop'];assert np.allclose([c['x']*960,c['y']*240,c['width']*960,c['height']*240],[192,48,576,height],atol=.001,rtol=0);s=copy.deepcopy(defaults);s['crop']=c;expected=copy.deepcopy(base);expected['crop']=c;expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected;assert np.array_equal(a,raw[48:48+height,192:768])
report=dict(status='Pass',native320x568_upper_left_thin_crop_expected576x24=True,before_fix_wrong_lower_corner_saved576x12_and_focused_width_stale480=True,after_fix_nearest_corner_and_all_fields_source_coordinates_correct=True,after_fix_numeric_focus_released=True,actual_both_PNGs_every_RGBA_exact_independent_source_slices=True,source_objects_other_recipe_and_document_fields_exact=True,initial_layout_shift_interpretation_corrected_by_settled_repeat_and_saved_bytes=True,sha256=hashes)
(out/'phone145-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native thin-phone nearest corner, synchronized fields and exact source/PNG dimensions')
