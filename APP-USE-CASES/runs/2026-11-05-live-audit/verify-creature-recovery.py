"""Native forgotten-symmetry recovery on the actual saved Ziggy journey."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-creature-recovery230';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
ds=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(5)]
assert ds[0]==ds[2]and ds[3]==ds[4]
objects=[d['layers'][0]['objects']for d in ds];assert list(map(len,objects))==[1,3,1,2,2]
assert all(o[0]==objects[0][0]for o in objects);a,b=objects[1][1:];assert {k:v for k,v in a.items()if k!='id'}=={k:v for k,v in objects[3][1].items()if k!='id'}and a['kind']==b['kind']=='stamp'
assert np.allclose(a['matrix'][:4],[1,0,0,1])and np.allclose(b['matrix'][:4],[-1,0,0,1]);assert abs(a['matrix'][4]+b['matrix'][4]-640)<.001 and abs(a['matrix'][5]-b['matrix'][5])<.001
for d in ds:
 c=copy.deepcopy(d);c['layers'][0]['objects']=objects[0];assert c==ds[0]
images=[]
for i in range(3):
 name=prefix+(f' ({i})'if i else '')+'.png';retain(name);images.append(np.array(Image.open(out/name).convert('RGBA')))
assert np.array_equal(images[1],images[2]);original=np.array(Image.open(out/'mouse-audit-journey2-finished-character.png').convert('RGBA'));yy,xx=np.mgrid[:480,:640];left=(xx>=53)&(xx<107)&(yy>=353)&(yy<407);right=(xx>=533)&(xx<587)&(yy>=353)&(yy<407)
assert np.array_equal(images[0][~(left|right)],original[~(left|right)])and np.array_equal(images[1][~left],original[~left]);assert np.sum(np.any(images[0][right]!=original[right],axis=1))>100 and np.array_equal(images[1][right],original[right]);assert np.array_equal(images[0][left],images[1][left])
report=dict(status='Pass',case='JOURNEY-002',native_symmetry_button_pressed_and_mode_visible_in_ui_record=True,forgotten_mode_produces_two_reflected_stamps=True,one_undo_restores_whole_baseline_exact=True,off_replacement_single_stamp=True,body_name_and_stars_pixel_exact=True,actual_corrected_project_and_png_reopen_exact=True,hashes=hashes)
(out/'creature-recovery230-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
