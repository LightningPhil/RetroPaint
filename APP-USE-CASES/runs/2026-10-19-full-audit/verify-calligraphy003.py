from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import components,distances,curve
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PAINT-003-complete';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'PAINT-003-ui.json');plan=read_json(root/'fixtures/PAINT-003-plan.json');assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==len(plan['rows'])==14 and len(ui['phases'])==8
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
downloads=[];rows=[];phases=[]
def events(location):
    for file in [location/'events.json',location/'fresh/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
def only_image(before,doc):
    expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected
for row,planned in zip(ui['rows'],plan['rows']):
    assert all(row[key]==value for key,value in planned.items());location=folder/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and (blank==255).all() and len(before['layers'])==1 and before['drawingMode']=='raster'
    previous=blank;stage={};deltas={};bound=max(4,.6*row['size'])+4;maximum={}
    for count,label in enumerate(['slow','tap','fast'],1):
        doc=read(label);only_image(before,doc);pixels=image(label);assert np.array_equal(pixels,decoded(doc)) and (pixels[:,:,3]==255).all();assert components((pixels!=blank).any(axis=2))==count,label+' lost a joined calligraphy mark';delta=(pixels!=previous).any(axis=2);assert components(delta)==1;previous=pixels;stage[label]=pixels;deltas[label]=delta
    for label,offset in [('slow',0),('fast',-160)]:
        mask=deltas[label];ys,xs=np.where(mask);distance=distances(curve(offset),xs,ys);assert distance.max()<=bound,'Calligraphy spikes outside its declared tube';maximum[label]=float(distance.max())
        for t in np.linspace(0,1,101):
            x=150*(1-t)**2+800*(1-t)*t+650*t*t;y=280*(1-t)**2+320*(1-t)*t+280*t*t+offset;xx=int(round(x));yy=int(round(y));assert mask[max(0,yy-4):yy+5,max(0,xx-4):xx+5].any(),'Calligraphy loses the hand curve'
    ys,xs=np.where(deltas['tap']);assert np.hypot(xs+.5-800,ys+.5-200).max()<=bound
    for label,reference in {'fast-undone':'tap','tap-undone':'slow','slow-undone':'before','slow-redone':'slow','tap-redone':'tap','fast-redone':'fast','fresh/reopened':'fast'}.items():assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),label+' loses complete calligraphy history'
    inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==3 and row['fast_elapsed_ms']<row['slow_elapsed_ms'];events(location);rows.append(dict(id=row['id'],viewport=row['viewport'],size=row['size'],strength=row['strength'],maximum_curve_distance=maximum,tap_pixels=int(deltas['tap'].sum()),all_gestures_connected_and_contained=True,all_gesture_history_and_fresh_source_RGBA_exact=True))
expected_phases={(r['id'],phase) for r in plan['rows'] if r['size']==22 and r['strength']==1 for phase in ['directions','short-sharp']};assert {(p['row'],p['phase']) for p in ui['phases']}==expected_phases
for phase in ui['phases']:
    location=folder/phase['row']/phase['phase'];read=lambda label:read_json(location/(label+'.retropaint'));before=read('before');blank=decoded(before);assert (blank==255).all();previous=blank;labels=[];widths={};changed=[]
    if phase['phase']=='directions':
        expected_paths=[dict(label=colour.lower()+'-'+name,points=[[x,y+(290 if colour=='Blue' else 0)] for x,y in points],colour=colour) for colour in ['Red','Blue'] for name,points in plan['direction_paths'].items()]
    else:expected_paths=[dict(label='short',points=[[800,200],[801,200]],colour='Red'),dict(label='sharp',points=[[100,420],[200,520],[300,420],[400,520]],colour='Red')]
    assert phase['paths']==expected_paths
    for path in expected_paths:
        label=path['label'];doc=read(label);only_image(before,doc);pixels=decoded(doc);mask=(pixels!=previous).any(axis=2);assert components(mask)==1,label+' has disconnected nib joins';ys,xs=np.where(mask);distance=distances(path['points'],xs,ys);bound=22 if phase['phase']=='short-sharp' else 22*.6+4;assert distance.max()<=bound,label+' has an oversized spike';colour=pixels[ys,xs,:3].astype(int)
        assert ((colour[:,0]>colour[:,2]) if path['colour']=='Red' else (colour[:,2]>colour[:,0])).all(),'Colour change did not apply only to the requested mark'
        if phase['phase']=='directions':
            a,b=np.array(path['points'],float);v=b-a;length=np.linalg.norm(v);t=((xs+.5-a[0])*v[0]+(ys+.5-a[1])*v[1])/(length*length);widths[label]=float(((t>.2)&(t<.8)).sum()/(length*.6))
        else:
            for a,b in zip(path['points'],path['points'][1:]):
                for t in np.linspace(0,1,41):
                    x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1]);xx=int(round(x));yy=int(round(y));assert mask[yy-8:yy+9,xx-8:xx+9].any(),'Short/sharp stroke loses its smoothed centreline'
        previous=pixels;labels.append(label);changed.append(int(mask.sum()))
    if phase['phase']=='directions':
        assert read('colour-selected')==read('red-ascending')
        for colour in ['red','blue']:assert widths[colour+'-descending']>=2*widths[colour+'-ascending'],'Nib direction does not produce a distinct thick/thin character'
    for index,label in enumerate(labels):
        reference='before' if index==0 else labels[index-1];assert read(label+'-undone')==read(reference);assert read(label+'-redone')==read(label)
    assert read('fresh/reopened')==read(labels[-1]);assert np.array_equal(previous,np.asarray(Image.open(location/'completed.png').convert('RGBA'))) and np.array_equal(previous,np.asarray(Image.open(location/'fresh/reopened.png').convert('RGBA')))
    inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==len(labels);events(location);phases.append(dict(row=phase['row'],viewport=phase['viewport'],phase=phase['phase'],paths=phase['paths'],changed_pixels=changed,direction_middle_widths=widths,all_connected_and_contained=True,colour_selection_preserves_previous_data=True,all_gesture_history_and_fresh_source_RGBA_exact=True))
assert len(downloads)==472
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,boundary_rows=rows,phases=phases,actual_downloads_verified=len(downloads),all_planned_rows_and_phases_verified=True,oracle=plan['oracles'],execution=ui['execution']);(root/'evidence/PAINT-003-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-003',boundary_rows=len(rows),additional_phases=len(phases),downloads=len(downloads))))
