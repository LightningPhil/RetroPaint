from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import numpy as np,json,hashlib,base64,io
root=Path(__file__).resolve().parent;repo=root.parents[2];folder=root/'headless/SMUDGE-producer';read_json=lambda p:json.loads(p.read_text(encoding='utf-8'));ui=read_json(folder/'SMUDGE-producer-ui.json');assert ui['status']=='Producer controls completed; independent fixture verification required' and not ui['errors'];manifest=read_json(root/'fixtures/SMUDGE-source-manifest.json');source=np.asarray(Image.open(root/'fixtures/SMUDGE.png').convert('RGBA'));assert hashlib.sha256((root/'fixtures/SMUDGE.png').read_bytes()).hexdigest()==manifest['sha256'];decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'));records=[];downloads=[];blue=np.zeros((240,320),bool);blue[60:180,160:260]=True
for kind in ['settled','live']:
    file=folder/('SMUDGE-'+kind+'.retropaint');doc=read_json(file);assert doc['drawingMode']=='raster' and [doc['width'],doc['height']]==[320,240] and doc['crop']==dict(x=0,y=0,width=1,height=1) and len(doc['layers'])==2;guide,paint=doc['layers'];assert guide['name']=='Green guide' and paint['name']=='Smudge source' and doc['active']==paint['id'] and guide['id']!=paint['id'] and all(l['visible'] and l['opacity']==1 and l['paper'] is None for l in doc['layers']);guide_pixels=decode(guide['image']);assert np.array_equal(guide_pixels,np.full((240,320,4),[67,160,71,255],np.uint8));raw=decode(paint['image']);expected=source.copy()
    if kind=='live':
        # Actual Bucket stores white under its procedural fill; this is fixture
        # representation, not an invented expected Smudge result.
        expected[blue]=[255,255,255,255];assert len(paint['live']['fills'])==1 and not paint['live']['strokes'] and not paint['live']['sparkles'];fill=paint['live']['fills'][0];assert fill['opacity']==1 and fill['spec']==dict(kind='texture',colors=[],speed=1,mode='snap',along=False,texture='water') and fill['gradient'] is None and not fill['sparkles'];mask=decode(fill['mask']);assert np.array_equal(mask[:,:,3]>0,blue) and (mask[blue,3]==255).all()
    else:assert paint['live']==dict(strokes=[],fills=[],sparkles=[])
    assert np.array_equal(raw,expected) and guide['live']==dict(strokes=[],fills=[],sparkles=[]);pixels=np.asarray(Image.open(folder/('SMUDGE-'+kind+'.png')).convert('RGBA'));reopened=read_json(folder/('fresh-'+kind)/'reopened.retropaint');assert reopened==doc and np.array_equal(pixels,np.asarray(Image.open(folder/('fresh-'+kind)/'reopened.png').convert('RGBA'))),'Genuine fixture fresh input changes source/phase pixels'
    composite=np.asarray(Image.alpha_composite(Image.fromarray(guide_pixels),Image.fromarray(source)))
    if kind=='settled':assert np.array_equal(composite,pixels)
    else:
        first=np.asarray(Image.open(folder/'SMUDGE-water-time-10000.png').convert('RGBA'));assert np.array_equal(first,pixels) and np.array_equal(first[~blue],composite[~blue]);motion=[]
        for time in [10371,11113]:
            other=np.asarray(Image.open(folder/('SMUDGE-water-time-'+str(time)+'.png')).convert('RGBA'));changed=(other!=first).any(axis=2);assert changed.any() and not changed[~blue].any();motion.append(dict(render_time_ms=time,changed_water_pixels=int(changed.sum())))
        assert pixels[blue,2].mean()>pixels[blue,0].mean(),'Live source is not visibly Blue water';records.append(dict(kind='moving-water-evidence',reference_time_ms=10000,changes=motion))
    records.append(dict(kind=kind,path=str(file.relative_to(root)),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),source_layer_id=paint['id'],guide_layer_id=guide['id'],raw_image_alpha_exact=True,working_target_valid=True,complete_fresh_source_and_fixed_frame_RGBA_exact=True))
for location in [folder,folder/'fresh-settled',folder/'fresh-live']:
    for event in read_json(location/'events.json'):
        if event['action']=='download':assert hashlib.sha256(Path(event['path']).read_bytes()).hexdigest()==event['sha256'];downloads.append(event)
assert len(downloads)==8;report=dict(at=datetime.now(timezone.utc).isoformat(),status='Verified native layered/live fixture only; not a PAINT-013 result',producer='headless/SMUDGE-producer/SMUDGE-producer-ui.json',records=records,actual_downloads_verified=8,source_png_sha256=manifest['sha256'],controlled_time_note='Render timestamps and performance.now reads fixed at10000ms only for deterministic live-frame comparisons; real RAF scheduling, timers, Date and native input remain. No age/latency/performance claim. Actual Water animation separately changes at10371/11113ms. Smudge is distance based.',clock_helper_sha256=hashlib.sha256((repo/'tests/controlled-render-time.mjs').read_bytes()).hexdigest());(root/'fixtures/SMUDGE-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Verified two actual layered fixtures, real moving Water definitions/frames and eight exact fresh source/PNG downloads. No PAINT-013 Pass.')
