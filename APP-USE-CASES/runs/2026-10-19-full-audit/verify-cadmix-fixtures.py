from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io,math
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/CADMIX-fixtures';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'CADMIX-fixture-ui.json');assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==8
source=read_json(root/'backups/artwork-before-acceptance-audit.retropaint');plan=read_json(root/'fixtures/CADMIX-pairwise-plan.json');assert [r['fixture'] for r in ui['rows']]==[r['fixture'] for r in plan['rows']]
decode=lambda value:Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA');rows=[];downloads=[];views={};cad_images={};pixels={}
zero_keys='exposure brightness contrast highlights shadows whites blacks temperature tint saturation vibrance hue sharpness radius threshold texture clarity pop dehaze noise colourNoise vignette midpoint feather roundness grain grainSize grainRoughness distortion aberration vertical horizontal angle zoom flipX flipY'.split()
defaults={key:0 for key in zero_keys};defaults.update(radius=1,midpoint=50,feather=75,grainSize=1.2,grainRoughness=50,zoom=100,flipX=False,flipY=False,balance=[1,1,1],mixer=[dict(hue=0,saturation=0,luminance=0)]*8,curves={key:[dict(x=0,y=0),dict(x=1,y=1)] for key in ['rgb','red','green','blue']},crop=dict(x=0,y=0,width=1,height=1))
for row in ui['rows']:
    location=folder/row['fixture'];doc=read_json(location/'fixture.retropaint');assert read_json(location/'fresh/fixture.retropaint')==doc
    image=np.asarray(Image.open(location/'fixture.png').convert('RGBA'));fresh=np.asarray(Image.open(location/'fresh/fixture.png').convert('RGBA'));assert np.array_equal(image,fresh);pixels[row['fixture']]=image
    expected=deepcopy(source);expected['active']=4;expected['layers'][2]['image']=doc['layers'][2]['image'];expected['layers'][2]['cad']['view']=doc['layers'][2]['cad']['view']
    view=doc['layers'][2]['cad']['view'];assert view['projection']==row['projection'] and view['target']==[7.5,0,10] and view['up']==[0,0,1] and view['span']>0 and all(math.isfinite(v) for key in ['position','target','up'] for v in view[key])
    if row['projection'] in views:assert view==views[row['projection']] and doc['layers'][2]['image']==cad_images[row['projection']]
    views[row['projection']]=view;cad_images[row['projection']]=doc['layers'][2]['image']
    crop=dict(x=100/960,y=80/640,width=760/960,height=480/640) if row['crop'] else deepcopy(defaults['crop']);expected['crop']=crop
    if row['photo'] or row['crop']:
        settings=deepcopy(defaults);settings.update(crop=crop,exposure=.5 if row['photo'] else 0,brightness=5 if row['photo'] else 0);expected['layers'][1]['photo']=dict(settings=settings,normal=settings,look='custom',lookActive=False)
    assert doc==expected,'Fixture changed data outside its declared view/guide/frame scope'
    assert image.shape==((480,760,4) if row['crop'] else (640,960,4))
    if not row['photo']:
        composite=Image.new('RGBA',(960,640))
        for layer in doc['layers']:assert layer['visible'] and layer['opacity']==1;composite=Image.alpha_composite(composite,decode(layer['image']))
        reference=np.asarray(composite);reference=reference[80:560,100:860] if row['crop'] else reference;assert int(np.abs(reference.astype(int)-image.astype(int)).max())<=1
    for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in read_json(file) if e['action']=='download']
    rows.append(dict(fixture=row['fixture'],sha256=hashlib.sha256((location/'fresh/fixture.retropaint').read_bytes()).hexdigest(),projection=row['projection'],photo=row['photo'],crop=row['crop'],source_resolution=[960,640],output_resolution=[image.shape[1],image.shape[0]],original_body_recipes_and_all_other_source_pixels_exact=True,declared_recipe_and_frame_only=True,actual_fresh_file_data_and_rgba_exact=True))
for projection in ['perspective','orthographic']:
    for photo in [False,True]:
        label=projection+('-photo' if photo else '-plain');assert np.array_equal(pixels[label+'-crop'],pixels[label+'-full'][80:560,100:860]),'Shared crop does not equal the retained full-picture region'
assert len(downloads)==32
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=32,known_isometric_views=views,independent_plain_layer_composite_max_tolerance=1,all_four_crop_variants_exact_slices_of_their_full_picture=True,scope='Fixture preparation only. Original body recipes, IDs, order and raw guide/annotation pixels are exact. View and guide recipe/frame changes are explicit. Photo settings are verified as independently specified inputs; this does not replace the separate Photo lab effect tests. No acceptance case Pass is inferred from fixture creation.')
(root/'fixtures/CADMIX-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Verified8 CADMIX variants,32 actual downloads, both projections and exact full-picture crop correspondence.')
