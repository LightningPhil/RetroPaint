from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import components
import json,hashlib,base64,io,math
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PAINT-008-complete';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'PAINT-008-ui.json');plan=read_json(root/'fixtures/PAINT-008-plan.json');assert ui['status']=='Pass' and not ui['errors'] and [r['viewport'] for r in ui['rows']]==plan['viewports']
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
rows=[];downloads=[]
for row in ui['rows']:
    location=folder/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and (blank==255).all() and before['drawingMode']=='raster' and len(before['layers'])==1;previous=blank;areas=[];cursor_measurements=[]
    for index,tap in enumerate(plan['taps']):
        label='size-'+str(tap['size']);doc=read(label);expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected;pixels=image(label);assert np.array_equal(pixels,decoded(doc));mask=(pixels!=previous).any(axis=2);assert components(mask)==1 and components((pixels!=blank).any(axis=2))==index+1;ys,xs=np.where(mask);x,y=tap['point'];radius=tap['size']/2;assert np.hypot(xs+.5-x,ys+.5-y).max()<=radius+2
        area=float((previous[:,:,1].astype(int)-pixels[:,:,1].astype(int)).sum()/198)
        if tap['size']==1:assert .5<=area<=1.1
        else:assert math.pi*(radius-2)**2<=area<=math.pi*(radius+2)**2
        areas.append(dict(size=tap['size'],changed_pixels=int(mask.sum()),independent_coverage_area=area));previous=pixels
    assert areas[0]['independent_coverage_area']<areas[1]['independent_coverage_area']<areas[2]['independent_coverage_area']
    assert read('view-controls')==read('size-96') and read('rapid-controls')==read('size-96'),'View or rapid controls rescale/change previous artwork'
    assert {(c['size'],c['zoom']) for c in row['cursors']}=={(s,z) for s in [1,22,96] for z in [0,1]}
    for c in row['cursors']:
        assert c['value']==c['size'] and str(c['size'])+' px' in c['public_size_label'];overlay=image(c['label']);assert overlay.shape==(640,960,4);ys,xs=np.where(overlay[:,:,3]>2);assert len(xs)>0;scale=960/c['view_rectangle']['width'];outer=float(np.hypot(xs+.5-800,ys+.5-200).max());literal_outer=c['size']/2+1.5*scale
        if c['size']>=22:assert abs(outer-literal_outer)<=2,'Cursor does not match the source footprint at this zoom'
        cursor_measurements.append(dict(size=c['size'],zoom=c['zoom'],source_pixels_per_CSS_pixel=scale,measured_outer_radius=outer,literal_nib_plus_outline_radius=literal_outer,literal_footprint_verified=c['size']>=22,minimum_visible_cue_separately_reported=c['size']==1))
    widths=[c['view_rectangle']['width'] for c in row['cursors'] if c['size']==22];assert widths[1]<widths[0] and abs(widths[1]/widths[0]-2/3)<.02
    for label,reference in {'size-96-undone':'size-22','size-22-undone':'size-1','size-1-undone':'before','size-1-redone':'size-1','size-22-redone':'size-22','size-96-redone':'size-96','fresh/reopened':'size-96'}.items():assert read(label)==read(reference),label+' does not restore complete source data'
    assert np.array_equal(image('fresh/reopened'),previous);inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==3
    events=read_json(location/'events.json');rapid=[e for e in events if e['action']=='rapid-size-controls'];assert len(rapid)==1 and rapid[0]['keys']==20 and not rapid[0]['pointer_down']
    for file in [location/'events.json',location/'fresh/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
    rows.append(dict(viewport=row['viewport'],tap_coverage=areas,cursors=cursor_measurements,source_size_and_earlier_marks_unchanged=True,rapid_and_zoom_create_no_extra_gesture_history=True,all_undo_redo_and_fresh_source_RGBA_exact=True))
assert len(downloads)==72
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),all_planned_rows_verified=True,oracle=plan['oracle'],execution=ui['execution'],minimum_cursor_cue_note='The1px tool has a larger minimum visible cursor cue. Its literal paint area is independently verified and the exact observed cue radii are reported, rather than claiming the cue paints a larger source area.22/96 literal footprint correspondence is checked at both zooms.')
(root/'evidence/PAINT-008-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-008',rows=len(rows),downloads=len(downloads))))
