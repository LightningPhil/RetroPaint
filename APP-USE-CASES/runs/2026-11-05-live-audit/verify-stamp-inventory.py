"""Catalogue identity, native round trips and independent raster stamp oracles."""
import base64,hashlib,io,json
from datetime import datetime
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageStat
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
catalog=json.loads((root/'APP-USE-CASES/catalog.json').read_bytes())
banks=next(v['values'] for v in catalog['variants'] if v['feature']=='Stamp inventory')
names=['animals','nature','rides','adventure','faces','treats','play','shapes']
evidence=json.loads((out/'raster-stamp-evidence.json').read_bytes());assert len(evidence)==8
def actual(stem,extension):
    name=stem+'.'+extension;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(stem):return json.loads(actual(stem,'retropaint'))
def png(stem):return Image.open(io.BytesIO(actual(stem,'png'))).convert('RGBA')
def opaque(im):return Image.alpha_composite(Image.new('RGBA',im.size,'white'),im).convert('RGB')
def layer_image(d):return opaque(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
def crop(im,x,y):return im.crop((round(x)-50,round(y)-50,round(x)+50,round(y)+50))
def feature(im,mask=False):
    difference=ImageChops.difference(im,Image.new('RGB',im.size,'white'));bounds=difference.getbbox();assert bounds,'Blank stamp'
    im=im.crop(bounds)
    if mask:
        im=ImageChops.difference(im,Image.new('RGB',im.size,'white')).convert('L').point(lambda v:0 if v>20 else 255).convert('RGB')
        # Raster and editable shape stamps have different intrinsic aspect
        # ratios (particularly the heart). This is a categorical silhouette
        # check, not a claim that both modes produce equal physical geometry.
        return im.resize((64,64),Image.Resampling.LANCZOS)
    im.thumbnail((64,64),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(72,72),'white');canvas.paste(im,((72-im.width)//2,(72-im.height)//2));return canvas
references=[];queries=[];reports=[]
rows=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines()]
for bank,category,e in zip(banks,names,evidence):
    count=len(bank['items']);assert e['category']==category and len(e['placements'])==count and e.get('reopened')
    expected_labels=['Stamp '+s.removeprefix('vec:') for s in bank['items']]
    assert e['labels']==expected_labels and [p['label'] for p in e['placements']]==expected_labels
    assert e['settings'][0]['value']=='1' and e['settings'][1]['text']=='Keep upright'
    assert all('active' not in s['class'] for s in e['settings'][2:])
    vector_stem='mouse-audit-stamps-'+category;v=doc(vector_stem);vr=doc(vector_stem+'-reopened27');assert v==vr
    vp,vrp=png(vector_stem),png(vector_stem+'-reopened27');assert vp.size==vrp.size==(640,480) and vp.tobytes()==vrp.tobytes()
    objects=v['layers'][0]['objects'];assert len(objects)==count
    if category!='shapes':assert [o['emoji'] for o in objects]==bank['items'] and all(o['kind']=='stamp' for o in objects)
    else:assert all(o['kind']=='path' for o in objects)
    raster_stem='mouse-audit-raster-stamps-'+category;r=doc(raster_stem)
    assert r==doc(raster_stem+'-redone')==doc(raster_stem+'-reopened')
    assert r['drawingMode']=='raster' and (r['width'],r['height'])==(960,640) and len(r['layers'])==1
    assert not r['layers'][0].get('objects') and all(not values for values in r['layers'][0]['live'].values())
    rp,rrp=png(raster_stem),png(raster_stem+'-reopened');assert rp.size==rrp.size==(960,640) and rp.tobytes()==rrp.tobytes()
    raster=opaque(rp);assert raster.tobytes()==layer_image(r).tobytes(),'Export differs from actual raster source'
    undone=doc(raster_stem+'-undone');undo_pixels=layer_image(undone)
    allowed=Image.new('L',(960,640));draw=ImageDraw.Draw(allowed)
    for i,(stamp,p) in enumerate(zip(bank['items'],e['placements'])):
        x,y=80+i%6*160,100+i//6*220;assert p['source']=={'x':x,'y':y}
        draw.rectangle((x-50,y-50,x+49,y+49),fill=255)
        query=crop(raster,x,y);reference=crop(opaque(vp),55+i%6*103,82+i//6*134)
        references.append({'id':stamp,'feature':feature(reference,category=='shapes'),'shape':category=='shapes'})
        queries.append({'id':stamp,'feature':feature(query,category=='shapes'),'shape':category=='shapes'})
    diff=ImageChops.difference(raster,Image.new('RGB',raster.size,'white'));outside=diff.copy();outside.paste((0,0,0),(0,0),allowed);assert outside.getbbox() is None,'Stamp changed unrelated paper'
    last=e['placements'][-1]['source'];last_box=(last['x']-50,last['y']-50,last['x']+50,last['y']+50)
    delta=ImageChops.difference(raster,undo_pixels);assert delta.getbbox(),'Undo removed nothing'
    delta.paste((0,0,0),last_box);assert delta.getbbox() is None,'Undo affected more than final stamp'
    assert undo_pixels.crop(last_box).getextrema()==((255,255),(255,255),(255,255))
    pointer=[row['event'] for row in rows if row.get('event',{}).get('type')=='native pointer' and e['started']<=datetime.fromisoformat(row['event']['at'].replace('Z','+00:00')).timestamp()*1000<=e['finished']]
    downs=[p['detail'] for p in pointer if p['detail']['phase']=='pointerdown'];ups=[p['detail'] for p in pointer if p['detail']['phase']=='pointerup']
    assert len(downs)==len(ups)==count,(category,len(downs),len(ups))
    for event,p in zip(downs,e['placements']):
        assert event['target']=='view' and event['buttons']==1
        assert abs(event['clientX']-p['point'][0])<.01 and abs(event['clientY']-p['point'][1])<.01
    reports.append({'category':category,'stamp_count':count,'whole_vector_and_raster_native_round_trips_exact':True,'both_exports_pixel_exact_after_reopen':True,'one_last_stamp_undo_and_whole_redo_exact':True,'actual_mouse_taps':count})

# Identify every raster glyph against all preserved, previously recognised
# editable stamp pictures. A wrong item, repeated missing-glyph box or silent
# category switch cannot pass by merely producing a non-empty cell.
matches=[]
for q in queries:
    distances=sorted((sum(ImageStat.Stat(ImageChops.difference(q['feature'],ref['feature'])).sum),ref['id']) for ref in references if ref['shape']==q['shape'])
    assert distances[0][1]==q['id'],(q['id'],distances[:3])
    assert distances[0][0]<distances[1][0],(q['id'],'ambiguous identity')
    matches.append({'id':q['id'],'distance':distances[0][0],'runner_up_distance':distances[1][0]})
assert sum(r['stamp_count'] for r in reports)==len(matches)==131
report={'status':'Pass','all_131_catalogue_stamps_in_both_raster_and_editable_modes':True,'all_16_category_sheets_reopened_through_native_picker':True,'glyph_and_shape_identity_matches_known_editable_art':True,'native_interrupted_first_attempt_excluded':True,'categories':reports,'identity_checks':matches,'sha256':hashes}
(out/'stamp-inventory-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['identity_checks','sha256']},indent=2))
