"""Finished monochrome output and exact editable earlier colour recovery."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-mono119-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA'))
baseline=json.loads((downloads/'mouse-audit-photo105-expanded.retropaint').read_text());mono=load('refined');normal=load('normal');a=load('refined','png');b=load('normal','png');reference=np.array(Image.open(downloads/'mouse-audit-photo105-expanded.png').convert('RGBA'))
ui=json.loads((out/'mono119-ui.json').read_text());assert ui['look']=='custom'
previous=baseline['layers'][0]['photo']['settings'];s=copy.deepcopy(previous);s.update(saturation=-100,contrast=ui['contrast']);s['curves']['rgb']=[dict(x=0,y=0),dict(x=.25,y=.38),dict(x=1,y=1)];expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=dict(settings=s,normal=previous,look='custom',lookActive=True);assert mono==expected
expected=copy.deepcopy(baseline);expected['layers'][0]['photo']=dict(settings=previous,normal=previous,look='normal',lookActive=False);assert normal==expected
assert np.array_equal(b,reference) and b.shape==(1398,2100,4);assert np.array_equal(a[:,:,3],b[:,:,3]);assert np.all(a[:,:,0]==a[:,:,1]) and np.all(a[:,:,1]==a[:,:,2]);assert np.count_nonzero(b[:,:,:3].max(axis=2)!=b[:,:,:3].min(axis=2))>100000
assert np.mean(abs(a.astype(int)-b.astype(int)))>5
report=dict(status='Pass',finished_fullsize_PNG_all_pixels_monochrome=True,manual_contrast_and_curve_retained_in_custom_look=True,actual_project_reopen_Normal_exact_prelook_colour_PNG=True,colour_source_and_manual_baseline_preserved_whole_document=True,flattened_image_not_used_for_recovery=True,sha256=hashes)
(out/'mono119-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS refined monochrome PNG, source/baseline recipe and exact native colour recovery')
