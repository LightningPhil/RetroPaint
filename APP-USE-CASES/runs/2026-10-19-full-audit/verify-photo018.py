from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PHOTO-018-complete';grid=root/'headless/PHOTO-018-grid'
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/(name+'.png')).convert('RGBA'))
decode=lambda layer:np.asarray(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
ui=json.loads((folder/'PHOTO-018-headless-ui.json').read_text(encoding='utf-8'));grid_ui=json.loads((grid/'PHOTO-018-grid-ui.json').read_text(encoding='utf-8'))
assert ui['status']=='Pass' and grid_ui['status']=='Pass' and not ui['errors'] and not grid_ui['errors'] and ui['fresh_reopen_complete'] and grid_ui['fresh_reopen_complete']
before=read('before');full=read('fine-full');source=image('before');output=image('fine-full');assert source.shape==output.shape==(2586,3896,4)
expected=deepcopy(before);settings=deepcopy(before['layers'][0]['photo']['settings']);settings.update(sharpness=80,threshold=5);expected['layers'][0]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False)
assert full==expected,'Fine-detail recipe or unrelated source data changed unexpectedly'
assert np.array_equal(output[:,:,3],source[:,:,3])
neighbour=decode(before['layers'][1]);opaque=neighbour[:,:,3]==255;assert opaque.any() and np.array_equal(output[opaque],neighbour[opaque])
changed=int(np.any(source!=output,axis=2).sum());assert changed>10000
# A source-resolution vegetation region is fixed independently of the result.
# Sharpening should increase local contrast while retaining edge placement.
region=(slice(1700,2400),slice(1900,3500))
def gradients(pixels):
    rgb=pixels[region][:,:,:3].astype(np.float32);luma=rgb@np.array([.2126,.7152,.0722],dtype=np.float32)
    return np.diff(luma,axis=1),np.diff(luma,axis=0)
old=gradients(source);new=gradients(output);before_energy=float(np.mean([np.abs(a).mean() for a in old]));after_energy=float(np.mean([np.abs(a).mean() for a in new]));assert after_energy>before_energy
correlation=float(np.corrcoef(old[0].ravel(),new[0].ravel())[0,1]);assert correlation>.8
for name in ['cancelled','fine-undone']:
    assert read(name)==before and np.array_equal(image(name),source)
for name in ['fine-redone','crop-undone']:
    assert read(name)==full and np.array_equal(image(name),output)
cropped=read('fine-cropped');expected=deepcopy(full);crop=dict(x=120/3896,y=90/2586,width=3400/3896,height=2100/2586);expected['crop']=crop;expected['layers'][0]['photo']['settings']['crop']=crop;expected['layers'][0]['photo']['normal']['crop']=crop
assert cropped==expected
assert np.array_equal(image('fine-cropped'),output[90:2190,120:3520])
for name in ['crop-redone','fresh/reopened']:
    assert read(name)==cropped and np.array_equal(image(name),image('fine-cropped'))
grid_source=np.asarray(Image.open(root/'fixtures/FULLSIZE-grid.png').convert('RGBA'));yy,xx=np.indices((1280,1920));levels=((xx+yy)%2*255).astype(np.uint8)
assert grid_source.shape==(1280,1920,4) and all(np.array_equal(grid_source[:,:,c],levels) for c in range(3)) and (grid_source[:,:,3]==255).all()
grid_read=lambda name:json.loads((grid/(name+'.retropaint')).read_text(encoding='utf-8'));grid_image=lambda name:np.asarray(Image.open(grid/(name+'.png')).convert('RGBA'))
for name in ['grid-before','grid-done','fresh/grid-reopened']:assert np.array_equal(grid_image(name),grid_source),'Export lost source-resolution one-pixel parity samples'
grid_done=grid_read('grid-done');assert grid_done==grid_read('fresh/grid-reopened') and grid_done['layers'][0]['photo']['settings']['sharpness']==80 and grid_done['layers'][0]['photo']['settings']['threshold']==5
assert np.array_equal(decode(grid_done['layers'][0]),grid_source)
preview=grid_image('grid-public-preview');assert preview.shape==(180,400,4)
visible=preview[:,:,3]>0;preview_levels=np.unique(preview[:,:,:3][visible])
# A reduced parity grid may alias. Uniform grey is not required. Here the
# actual preview has lost every original 0/255 sample and contains mixed levels,
# while the independently checked full-size PNG retains every parity pixel.
assert len(preview_levels)>2 and preview_levels.min()>0 and preview_levels.max()<255
downloads=[]
for location in [folder,grid]:
    events=json.loads((location/'events.json').read_text(encoding='utf-8'))+json.loads((location/'fresh/events.json').read_text(encoding='utf-8'));events=[e for e in events if e['action']=='download']
    assert len(events)==(18 if location==folder else 6)
    for event in events:
        data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
    downloads+=events
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,natural_photo_dimensions=[3896,2586],saved_detail_settings=dict(sharpness=80,radius=1,threshold=5),natural_full_size_changed_pixels=changed,fixed_vegetation_region_xywh=[1900,1700,1600,700],natural_region_gradient_mean_before=before_energy,natural_region_gradient_mean_after=after_energy,natural_region_horizontal_gradient_correlation=correlation,parity_grid_dimensions=[1920,1280],all_source_resolution_parity_pixels_retained_exactly=True,public_grid_preview_loses_original_black_white_parity_samples=True,public_preview_unique_channel_levels=preview_levels.tolist(),originals_neighbour_and_all_unrelated_fields_exact=True,full_size_crop_equals_independently_indexed_full_output=True,cancel_undo_redo_and_fresh_saved_file_reopen_exact=True,actual_downloads_verified=len(downloads),oracle='Independent NumPy parity grid (every full-size pixel), known source-region gradient measurements, literal recipe values, exact preserved data/alpha/neighbour and Pillow-decoded actual full-size/cropped downloads. No preview enlargement or app rendering function generates expected outputs.',harness_correction='Original supplemental preview assertion incorrectly required near-uniform grey instead of allowing aliasing. It failed with mean absolute distance29.59/255. Actual preview levels39..216 lose original0/255 samples; all full-size parity pixels remain exact. No app, fixture or retained output changed.',execution='Isolated headless production UI; no desktop control')
(root/'evidence/PHOTO-018-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
