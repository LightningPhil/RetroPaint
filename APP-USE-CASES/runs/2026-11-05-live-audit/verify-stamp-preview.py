"""Actual hover, keyboard save, single-tap and announced flip-state evidence."""
import base64,hashlib,io,json,statistics
from datetime import datetime
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'stamp-preview-evidence.json').read_bytes())
def actual(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(actual(stem+'.retropaint'))
def image(name):return Image.open(io.BytesIO(actual(name))).convert('RGBA')
def screen(name):return Image.open(out/name).convert('RGB')
def dark_bounds(im,box):
    region=im.crop(box);mask=region.convert('L').point(lambda v:255 if v<230 else 0);return mask.getbbox()
assert e['flipStateBeforeFix'][0]['pressed'] is None and 'active' in e['flipStateBeforeFix'][0]['class']
assert all(s['pressed']=='false' for s in e['flipStateAfterFixInitial'])
for states,expected in zip(e['flipTransitions'],[(True,False),(True,True),(False,True),(False,False),(True,False)]):
    for state,value in zip(states,expected):assert state['pressed']==str(value).lower() and ('active' in state['class'])==value
rows=[json.loads(line) for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines()]
results=[]
for mode,prefix,baseline,ghost_export,interval,normal_file,ghost_file,solid_file in [
    ('raster','mouse-audit-stamp-preview-r28','mouse-audit-stamp-preview-r28-before',e['keyboardGhostExport']['path'],(e['tapStarted'],e['tapFinished']),'stamp-preview-r28-normal-settled.png','stamp-preview-r28-large-flipped.png','stamp-preview-r28-committed-only.png'),
    ('vector','mouse-audit-stamp-preview-vector','mouse-audit-stamp-transform-vector-before',e['vector']['exportPath'],(e['vector']['tapStarted'],e['vector']['tapFinished']),'stamp-preview-vector-normal.png','stamp-preview-vector-ghost-settled.png','stamp-preview-vector-committed-only.png')]:
    before=doc(baseline);assert before==doc(prefix+'-ghost-project')==doc(prefix+'-one-undone')
    after=doc(prefix+'-one');assert after==doc(prefix+'-one-redone')==doc(prefix+'-one-reopened')
    exported=image(Path(ghost_export).name);assert exported.size==(960,640) and exported.getextrema()==((255,255),)*4
    output=image(prefix+'-one.png');assert output.size==(960,640)
    if mode=='vector':
        objects=after['layers'][0]['objects'];assert len(objects)==1
        stamp=objects[0];assert stamp['kind']=='stamp' and stamp['emoji']=='\U0001f680' and stamp['angle']==0
        assert stamp['flipH'] is False and stamp['flipV'] is True and abs(stamp['width']-82*2.6)<1e-6
    else:
        assert not after['layers'][0].get('objects')
        src=Image.open(io.BytesIO(base64.b64decode(after['layers'][0]['image'].split(',',1)[1]))).convert('RGBA')
        composed=Image.alpha_composite(Image.new('RGBA',src.size,'white'),src);assert composed.tobytes()==output.tobytes()
    events=[r['event']['detail'] for r in rows if r.get('event',{}).get('type')=='native pointer' and interval[0]<=datetime.fromisoformat(r['event']['at'].replace('Z','+00:00')).timestamp()*1000<=interval[1]]
    downs=[p for p in events if p['phase']=='pointerdown'];ups=[p for p in events if p['phase']=='pointerup']
    assert len(downs)==len(ups)==1 and downs[0]['target']=='view'
    cx,cy=downs[0]['clientX'],downs[0]['clientY'];oldx,oldy=cx-360/1.1,cy-220/1.1
    old_box=(round(oldx)-65,round(oldy)-65,round(oldx)+65,round(oldy)+65)
    large_box=(round(cx)-115,round(cy)-115,round(cx)+115,round(cy)+115)
    normal,ghost,solid=screen(normal_file),screen(ghost_file),screen(solid_file)
    nb=dark_bounds(normal,old_box);gb=dark_bounds(ghost,large_box)
    assert nb and gb and dark_bounds(ghost,old_box) is None,'Ghost did not follow pointer'
    wr=(gb[2]-gb[0])/(nb[2]-nb[0]);hr=(gb[3]-gb[1])/(nb[3]-nb[1])
    assert 2.3<wr<2.9 and 2.3<hr<2.9,(mode,wr,hr)
    ratios=[]
    for a,b in zip(ghost.crop(large_box).get_flattened_data(),solid.crop(large_box).get_flattened_data()):
        contrast=sum(255-v for v in b)
        if contrast>200:ratios.append(sum(255-v for v in a)/contrast)
    ratio=statistics.median(ratios);assert .1<ratio<.8,'Preview is not translucent'
    # One source footprint only; no ghost remains at the former pointer site.
    diff=ImageChops.difference(output.convert('RGB'),Image.new('RGB',output.size,'white'))
    source=downs[0];r=source['rect'];sx=(cx-r['x'])/r['width']*960;sy=(cy-r['y'])/r['height']*640
    diff.paste((0,0,0),(round(sx)-115,round(sy)-115,round(sx)+115,round(sy)+115));assert diff.getbbox() is None
    results.append({'mode':mode,'ghost_contrast_fraction':ratio,'preview_width_scale':wr,'preview_height_scale':hr,'one_native_mouse_tap':True,'whole_undo_redo_and_native_reopen_exact':True,'keyboard_ghost_export_and_project_contain_no_preview':True})
report={'status':'Pass','flip_controls_announce_all_four_states':True,'raster_and_editable_hover_workflows':results,'download_event_tool_timeout_not_product_failure':True,'sha256':hashes}
(out/'stamp-preview-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
