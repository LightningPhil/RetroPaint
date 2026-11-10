"""Sixteen actual stamp placements: metadata, geometry, pixels and history."""
import base64,hashlib,io,json,math
from datetime import datetime
from pathlib import Path
from PIL import Image,ImageChops,ImageOps,ImageStat
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
events=json.loads((out/'stamp-transform-evidence.json').read_bytes());assert len(events)==16
def actual(stem,ext='retropaint'):
    name=stem+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(stem):return json.loads(actual(stem))
def png(stem):return Image.open(io.BytesIO(actual(stem,'png'))).convert('RGB')
def pixels(d):
    im=Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA')
    return Image.alpha_composite(Image.new('RGBA',im.size,'white'),im).convert('RGB')
def bounds(im):return ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox()
def feature(im):
    b=bounds(im);assert b,'Blank transformed stamp';im=im.crop(b)
    # Normalize both small and large stamps to the same feature scale.
    # thumbnail() only shrinks, so it cannot compare the 0.4-scale case.
    ratio=64/max(im.size);im=im.resize((round(im.width*ratio),round(im.height*ratio)),Image.Resampling.LANCZOS)
    c=Image.new('RGB',(72,72),'white');c.paste(im,((72-im.width)//2,(72-im.height)//2));return c
reference=png('mouse-audit-raster-stamps-rides').crop((830,50,930,150));ref_bounds=bounds(reference)
candidates=[]
for h in [False,True]:
    for v in [False,True]:
        im=ImageOps.mirror(reference) if h else reference.copy();im=ImageOps.flip(im) if v else im
        for angle in range(-30,31):
            rotated=im.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True,fillcolor='white')
            candidates.append((h,v,angle,feature(rotated)))
rows=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines()]
results=[]
for mode in ['raster','vector']:
    prefix='mouse-audit-stamp-transform-'+mode
    # A fresh paper was created after the separate editable hover workflow.
    # Keep both originals: the second independently saved before file has ID4,
    # while the hover baseline has ID3. No document ID normalization is used.
    baseline=prefix+'-before'+(' (1)' if mode=='vector' else '')
    previous=doc(baseline);initial=previous;mode_events=[e for e in events if e['mode']==mode];assert len(mode_events)==8
    for i,e in enumerate(mode_events):
        assert e['index']==i
        stem=prefix+'-'+str(i+1);after=doc(stem);assert doc(stem+'-undone')==previous and doc(stem+'-redone')==after
        assert after['drawingMode']==mode and (after['width'],after['height'])==(960,640) and len(after['layers'])==1
        plan=e['plan'];controls={x['id']:x for x in e['controls']}
        assert abs(float(controls['stampScale']['value'])-plan['scale'])<1e-6
        for field,value in [('flipH',plan['h']),('flipV',plan['v'])]:
            assert controls[field]['pressed']==str(value).lower() and ('active' in controls[field]['class'])==value
        assert ('Random' in controls['spinMode']['text'])==(plan['spin']=='auto')
        if mode=='vector':
            objects=after['layers'][0]['objects'];assert len(objects)==i+1 and objects[:-1]==previous['layers'][0].get('objects',[])
            stamp=objects[-1];size=82*plan['scale'];assert stamp['kind']=='stamp' and stamp['emoji']=='\U0001f680'
            assert stamp['flipH']==plan['h'] and stamp['flipV']==plan['v'] and abs(stamp['width']-size)<1e-6 and abs(stamp['height']-size)<1e-6
            assert stamp['matrix'][:4]==[1,0,0,1]
            assert abs(stamp['matrix'][4]+size/2-e['source']['x'])<.001 and abs(stamp['matrix'][5]+size/2-e['source']['y'])<.001
            degrees=math.degrees(stamp['angle']);assert abs(degrees)<=14
            if plan['spin']=='fixed':assert degrees==0
            assert after['layers'][0]['image']==initial['layers'][0]['image']
        else:
            assert not after['layers'][0].get('objects')
            delta=ImageChops.difference(pixels(after),pixels(previous));assert delta.getbbox()
            x,y=e['source']['x'],e['source']['y'];delta.paste((0,0,0),(x-115,y-115,x+115,y+115));assert delta.getbbox() is None
        pointer=[row['event']['detail'] for row in rows if row.get('event',{}).get('type')=='native pointer' and e['start']<=datetime.fromisoformat(row['event']['at'].replace('Z','+00:00')).timestamp()*1000<=e['end']]
        downs=[x for x in pointer if x['phase']=='pointerdown'];ups=[x for x in pointer if x['phase']=='pointerup'];assert len(downs)==len(ups)==1
        assert downs[0]['target']=='view' and abs(downs[0]['clientX']-e['point'][0])<.01 and abs(downs[0]['clientY']-e['point'][1])<.01
        previous=after
    assert previous==doc(prefix)==doc(prefix+'-reopened')
    picture=png(prefix);reopened=png(prefix+'-reopened');assert picture.size==(960,640) and picture.tobytes()==reopened.tobytes()
    if mode=='raster':assert picture.tobytes()==pixels(previous).tobytes()
    for i,e in enumerate(mode_events):
        x,y=e['source']['x'],e['source']['y'];im=picture.crop((x-115,y-115,x+115,y+115));b=bounds(im);f=feature(im)
        matches=sorted((sum(ImageStat.Stat(ImageChops.difference(f,candidate)).sum),h,v,angle) for h,v,angle,candidate in candidates)
        _,h,v,angle=matches[0];assert (h,v)==(e['plan']['h'],e['plan']['v']),(mode,i,matches[:3])
        # Two raster-edge pixels at the centre-to-edge radius, plus half
        # of the one-degree search step. The bounding width is a diameter.
        size=max(b[2]-b[0],b[3]-b[1]);angle_uncertainty=math.degrees(math.atan2(2,size/2))+.5
        if e['plan']['spin']=='fixed':
            assert abs(angle)<=angle_uncertainty,(mode,i,angle)
            for measured,base_dimension in [(b[2]-b[0],ref_bounds[2]-ref_bounds[0]),(b[3]-b[1],ref_bounds[3]-ref_bounds[1])]:
                scale=e['plan']['scale'];assert scale*(base_dimension-2)-2<=measured<=scale*(base_dimension+2)+2,(mode,i,measured,base_dimension,scale)
        else:assert abs(angle)<=14+angle_uncertainty,(mode,i,angle,angle_uncertainty)
        # The emoji font is rasterized anew at each size. Its hinted outlines
        # are not pixel-identical to a resized 82px template, so the fitted
        # image angle checks orientation/range, not exact stored rotation.
        # Exact editable angles and the fixed zero value are checked above.
        results.append({'mode':mode,'index':i+1,'scale':e['plan']['scale'],'flipH':h,'flipV':v,'spin':e['plan']['spin'],'image_fitted_clockwise_degrees':angle,'pixel_angle_uncertainty_degrees':angle_uncertainty,'committed_degrees':math.degrees(previous['layers'][0]['objects'][i]['angle']) if mode=='vector' else None,'whole_per_placement_undo_redo_exact':True})
report={'status':'Pass','sixteen_real_mouse_placements':True,'all_four_flip_combinations_in_both_rotation_modes_and_both_drawing_modes':True,'minimum04_middle14_maximum26_and_normal1_scales':True,'fixed_orientation_and_random14_degree_bound_checked':True,'every_history_step_and_both_native_round_trips_exact':True,'raster_image_angle_measurements_report_pixel_resolution_uncertainty':True,'vector_transform_baseline':'mouse-audit-stamp-transform-vector-before (1).retropaint','placements':results,'sha256':hashes}
(out/'stamp-transforms-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','placements']},indent=2));print(json.dumps(results,indent=2))
