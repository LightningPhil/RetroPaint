"""Full-source sharpening oracle using independent 2D integral neighbourhoods."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-detail120-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=json.loads((downloads/'mouse-audit-mono119-normal.retropaint').read_text());d=load('fullsize');a=load('fullsize','png');ui=json.loads((out/'detail120-ui.json').read_text());expected=copy.deepcopy(base)
for key in ['settings','normal']:expected['layers'][0]['photo'][key].update(ui)
expected['layers'][0]['photo']['look']='custom';assert d==expected
source=np.array(Image.open(downloads/'mouse-audit-mono119-normal.png').convert('RGBA')).astype(int);h,w,_=source.shape;assert (w,h)==(2100,1398) and a.shape==source.shape and np.all(source[:,:,3]==255);assert np.array_equal(a[:,:,3],source[:,:,3])
# Sum a square in one operation per pixel, unlike the engine's separable loops.
radius=max(1,round(ui['radius']*w/960));luma=source[:,:,:3]@np.array([.2126,.7152,.0722]);pad=np.pad(luma,radius,mode='edge');integral=np.pad(pad,((1,0),(1,0))).cumsum(0).cumsum(1);size=2*radius+1;blur=(integral[size:,size:]-integral[:-size,size:]-integral[size:,:-size]+integral[:-size,:-size])/(size*size);difference=luma-blur;t=np.clip((abs(difference)-ui['threshold'])/4,0,1);mask=t*t*(3-2*t);predicted=np.rint(np.clip(source[:,:,:3]+(difference*ui['sharpness']/100*1.8*mask)[:,:,None],0,255)).astype(int);error=abs(a[:,:,:3]-predicted);assert error.max()<=1 and error.mean()<.001,(error.max(),error.mean())
assert np.count_nonzero(a[:,:,:3]!=source[:,:,:3])>100000
# Source-sized result is demonstrably different from enlarging a720px cache.
small=Image.fromarray(a.astype('uint8')).resize((720,round(h*720/w)),Image.Resampling.BILINEAR).resize((w,h),Image.Resampling.BILINEAR);preview_error=abs(a[:,:,:3]-np.array(small)[:,:,:3]);assert preview_error.mean()>1 and np.count_nonzero(preview_error.max(axis=2)>10)>10000
report=dict(status='Pass',actual_full2100x1398_dimensions=True,saved_fine_detail_recipe_exact_and_original_source_preserved=True,independent_2D_integral_sharpen_oracle_max_error=int(error.max()),mean_error=float(error.mean()),different_from_enlarged720px_preview_mean_error=float(preview_error.mean()),fine_detail_pixels_different_from_cache=int(np.count_nonzero(preview_error.max(axis=2)>10)),sha256=hashes)
assert np.array_equal(load('reopened','png'),a);report['actual_saved_project_reopen_export_every_RGBA_exact']=True
(out/'detail120-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS source-resolution natural-photo sharpening, exact recipe/source and independent full-size pixels')
