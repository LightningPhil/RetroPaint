from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,math,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PAINT-002-selected-control-final';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'PAINT-002-ui.json');plan=read_json(root/'fixtures/PAINT-002-plan.json')
assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==len(plan['rows'])==14;assert [r['id'] for r in ui['rows']]==[r['id'] for r in plan['rows']]
def components(mask):
    parent=[];labels=[];previous=[]
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for row in mask:
        edges=np.diff(np.pad(row.astype(np.int8),1));starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1);current=[]
        for start,end in zip(starts,ends):
            neighbours=[label for left,right,label in previous if start<=right and end>=left]
            if neighbours:
                label=find(neighbours[0])
                for other in neighbours[1:]:parent[find(other)]=label
            else:label=len(parent);parent.append(label)
            current.append((start,end,label));labels.append(label)
        previous=current
    return len({find(label) for label in labels})
def distances(points,xs,ys):
    x=xs.astype(float)+.5;y=ys.astype(float)+.5;minimum=np.full(x.shape,np.inf)
    for a,b in zip(points,points[1:]):
        dx=b[0]-a[0];dy=b[1]-a[1];t=np.clip(((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy),0,1);minimum=np.minimum(minimum,np.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
    return minimum
def curve(offset):return [[150*(1-t)**2+800*(1-t)*t+650*t*t,280*(1-t)**2+320*(1-t)*t+280*t*t+offset] for t in np.linspace(0,1,41)]
rows=[];downloads=[]
for row,planned in zip(ui['rows'],plan['rows']):
    assert all(row[key]==value for key,value in planned.items());location=folder/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and (blank==255).all() and len(before['layers'])==1 and before['drawingMode']=='raster'
    labels=['marker','slow','tap','fast','returned'];stages={label:image(label) for label in labels};deltas={};previous=blank;size=row['size'];strength=row['strength'];bound=max(1.5,size*.15)+2
    expected_core=round(255+(26-255)*strength)
    for index,label in enumerate(labels):
        pixels=stages[label];doc=read(label);expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected;decoded=np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'));assert np.array_equal(pixels,decoded) and (pixels[:,:,3]==255).all()
        mask=(pixels!=blank).any(axis=2);assert components(mask)==index+1,label+' has a gap or bridge';delta=(pixels!=previous).any(axis=2);assert components(delta)==1;deltas[label]=delta;previous=pixels
    assert read('biro-selected')==read('marker');assert read('spray-selected')==read('fast') and read('biro-restored')==read('fast'),'Changing applicators altered existing data'
    curve_bounds={}
    for label,offset in [('slow',-160),('fast',200)]:
        mask=deltas[label];ys,xs=np.where(mask);distance=distances(curve(offset),xs,ys);assert distance.max()<=bound,'Biro leaves the independently declared fine tube';curve_bounds[label]=float(distance.max())
        for t in np.linspace(0,1,101):
            x=150*(1-t)**2+800*(1-t)*t+650*t*t;y=280*(1-t)**2+320*(1-t)*t+280*t*t+offset;xx=int(round(x));yy=int(round(y));assert mask[max(0,yy-1):yy+2,max(0,xx-1):xx+2].any(),'Biro misses the declared hand curve'
        if size>=22:
            assert mask.sum()<.4*deltas['marker'].sum(),'Biro does not have a visibly finer character'
            centre=stages[label][220+offset,400,:3].astype(int);assert np.abs(centre-expected_core).max()<=2,'Biro core does not retain requested dark ink/Strength'
    for label,centre in [('tap',[800,200]),('returned',[800,480])]:
        mask=deltas[label];ys,xs=np.where(mask);assert np.hypot(xs+.5-centre[0],ys+.5-centre[1]).max()<=bound,'Returned Biro sprays beyond its fine tap';assert int((255-stages[label][ys,xs,1].astype(int)).sum())>=10,'Biro tap effectively invisible'
    history={'returned-undone':'fast','fast-undone':'tap','tap-undone':'slow','slow-undone':'marker','marker-undone':'before','marker-redone':'marker','slow-redone':'slow','tap-redone':'tap','fast-redone':'fast','returned-redone':'returned','fresh/reopened':'returned'}
    for label,reference in history.items():assert read(label)==read(reference),label+' did not restore the exact complete gesture'
    assert np.array_equal(image('fresh/reopened'),stages['returned'])
    inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==5;assert row['fast_elapsed_ms']<row['slow_elapsed_ms']
    for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in read_json(file) if e['action']=='download']
    rows.append(dict(id=row['id'],viewport=row['viewport'],size=size,strength=strength,maximum_biro_distance=curve_bounds,marker_pixels=int(deltas['marker'].sum()),slow_biro_pixels=int(deltas['slow'].sum()),fast_biro_pixels=int(deltas['fast'].sum()),tap_pixels=int(deltas['tap'].sum()),returned_from_spray_tap_pixels=int(deltas['returned'].sum()),existing_marks_exact_on_all_three_applicator_switches=True,five_gestures_connected_and_separate=True,all_gesture_history_and_fresh_source_RGBA_exact=True,actual_slow_ms=row['slow_elapsed_ms'],actual_fast_ms=row['fast_elapsed_ms']))
assert len(downloads)==27*14
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),all_fourteen_pre_recorded_rows_verified=True,oracle=plan['oracle'],execution=ui['execution'],coverage_chunks=[dict(folder=str(folder.relative_to(root)),completed_rows=[r['id'] for r in ui['rows']])])
(root/'evidence/PAINT-002-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-002',rows=len(rows),downloads=len(downloads))))
