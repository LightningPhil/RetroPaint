"""Queued latest geometry, genuine stale callback, actual pixels and source."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from PIL import Image
from geometry_oracle import verify_geometry,project_source
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-combo144-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=load('baseline');latest=load('latest');assert load('reopened')==latest and load('cancelled')==latest;ui=json.loads((out/'combo144-ui.json').read_text(encoding='utf-8'));s=copy.deepcopy(json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text(encoding='utf-8'))['layers'][0]['photo']['settings']);s.update({k:ui[k] for k in ['angle','zoom','vertical','horizontal','distortion','aberration']});c=ui['crop'];crop=dict(x=c['x']/960,y=c['y']/640,width=c['width']/960,height=c['height']/640);s['crop']=crop;expected=copy.deepcopy(base);expected['crop']=crop;expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert latest==expected
image=load('latest','png');assert np.array_equal(load('reopened','png'),image) and np.array_equal(load('cancelled','png'),image);mapping=verify_geometry(image,project_source(base),s,(c['x'],c['y'],c['width'],c['height']))
assert ui['pendingStatus']=='Updating preview…' and ui['cancelDraft']['status']=='Updating preview…';assert 'photo reply held' in ui['heldLog'] and 'photo replies released: {"count":1}' in ui['releasedLog'];assert 'photo reply held' in ui['cancelHeldLog'] and 'photo replies released: {"count":1}' in ui['cancelReleasedLog']
def paper_image(name,rect):
    a=np.array(Image.open(out/name));x0=math.ceil(rect['x'])+3;y0=math.ceil(rect['y'])+3;x1=math.floor(rect['x']+rect['w'])-3;y1=math.floor(rect['y']+rect['h'])-3;return a[y0:y1,x0:x1]
assert ui['previewPaper']==ui['reopenedPaper']==ui['cancelPaper']
preview=paper_image('combo144-latest-preview.jpg',ui['previewPaper']);reopened=paper_image('combo144-reopened-preview.jpg',ui['reopenedPaper']);before=paper_image('combo144-cancel-before-release.jpg',ui['cancelPaper']);after=paper_image('combo144-cancel-after-release.jpg',ui['cancelPaper'])
assert np.array_equal(before,after),'Retired reply changed the restored visible paper'
assert np.array_equal(preview,reopened),'Latest queued preview differs from fresh saved-recipe preview'
assert np.array_equal(reopened,before),'Cancelled draft leaked into restored paper'
report=dict(status='Pass',native_ten_geometry_edits_while_real_preview_pending=True,latest_recipe_crop_and_source_whole_project_exact=True,full760x520_export_independent_homogeneous_geometry=True,latest_queued_preview_every_display_pixel_equals_fresh_saved_recipe_preview=True,genuine_old_reply_after_Cancel_and_new_session_leaves_paper_pixels_exact=True,cancelled_project_and_fullPNG_every_RGBA_exact_latest=True,source_objects_and_other_settings_preserved=True,mapping=mapping,sha256=hashes)
(out/'combo144-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native latest combined geometry, real stale replies, exact preview/project/full export/source')
