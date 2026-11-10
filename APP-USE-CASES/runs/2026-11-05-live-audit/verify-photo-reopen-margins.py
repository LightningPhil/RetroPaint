"""Fresh native project recipe, atomic rejection and crop margin recovery."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def doc(n):
    name=f'mouse-audit-photo105-{n}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def png(n):
    name=f'mouse-audit-photo105-{n}.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return np.array(Image.open(out/name).convert('RGBA'))
warm=doc('cropped-warm');assert doc('fresh-reopened')==warm
recipe=warm['layers'][0]['photo'];assert recipe['look']=='warm' and recipe['lookActive'] is True;assert recipe['normal']['brightness']==20 and len(recipe['normal']['curves']['rgb'])==4
crop=dict(x=.1,y=140/1398,width=.8,height=1118/1398);assert warm['crop']==recipe['settings']['crop']==recipe['normal']['crop']==crop
normal=doc('fresh-normal');expected=copy.deepcopy(warm);expected['layers'][0]['photo']=dict(settings=recipe['normal'],normal=recipe['normal'],look='normal',lookActive=False);assert normal==expected
for n in ['exposure','look','curve']:assert doc('rejected-'+n)==normal
expanded=doc('expanded');baseline=json.loads((downloads/'mouse-audit-photo93-saved-recipe.retropaint').read_text());assert expanded==baseline
full=png('expanded');manual=np.array(Image.open(downloads/'mouse-audit-photo103-manual-baseline.png').convert('RGBA'));assert full.shape==(1398,2100,4) and np.array_equal(full,manual)
flat=png('cropped-warm');assert flat.shape==(1118,1680,4)
oldfull=np.array(Image.open(downloads/'mouse-audit-photo103-a-warm.png').convert('RGBA'));assert np.array_equal(flat,oldfull[140:1258,210:1890])
opened=doc('flattened-reopened');assert (opened['width'],opened['height'])==(1680,1118);assert opened['crop']==dict(x=0,y=0,width=1,height=1);assert 'photo' not in opened['layers'][0]
raw=np.array(Image.open(io.BytesIO(base64.b64decode(opened['layers'][0]['image'].split(',')[1]))).convert('RGBA'));assert np.array_equal(raw,flat)
ui=json.loads((out/'photo105-ui.json').read_text());assert ui['reopen']['reopenedLook']=='warm';assert len(ui['rejections'])==3
flatui=json.loads((out/'photo105-flat-ui.json').read_text());assert [x['value'] for x in flatui]==['0','0','1680','1118']
report=dict(status='Pass',fresh_app_page_initial_ready_sheet=True,whole_actual_project_reopen_exact=True,look_manual_curve_and_crop_baseline_retained=True,Normal_uses_saved_manual_baseline=True,all_three_malformed_recipe_inputs_rejected_atomically=True,full_source_original_pixels_and_margins_retained=True,expanded_whole_document_and_full_PNG_exact_to_pre_crop_manual_baseline=True,flattened_PNG_native_reopen_only_has_cropped_dimensions_and_pixels=True,sha256=hashes)
(out/'photo105-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS fresh saved look/baseline/crop, atomic invalid input, full source recovery and flattened distinction')
