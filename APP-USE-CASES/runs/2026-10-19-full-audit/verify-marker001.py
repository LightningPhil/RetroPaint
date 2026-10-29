from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,math,sys
import numpy as np
root=Path(__file__).resolve().parent;prefix='--prefix' in sys.argv;folder=root/('headless/PAINT-001-complete' if prefix else 'headless/PAINT-001-fixed');read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'PAINT-001-ui.json');plan=read_json(root/'fixtures/PAINT-001-plan.json')
if prefix:
    assert ui['status']=='Fail' and not ui['errors'] and len(ui['rows'])==7 and 'workspaceToolDetail' in ui['error']
else:
    assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==len(plan['rows'])==14
    assert [r['id'] for r in ui['rows']]==[r['id'] for r in plan['rows']]
completed=[(folder,row) for row in ui['rows']]
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
def curve(offset):
    return [[150*(1-t)**2+800*(1-t)*t+650*t*t,280*(1-t)**2+320*(1-t)*t+280*t*t+offset] for t in np.linspace(0,1,41)]
rows=[];downloads=[]
for (evidence,row),planned in zip(completed,plan['rows']):
    assert all(row[key]==value for key,value in planned.items());location=evidence/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and (blank==255).all() and len(before['layers'])==1 and before['drawingMode']=='raster'
    size=row['size'];radius=size/2;strength=row['strength'];expected_rgb=np.rint(255+(np.array([229,57,53])-255)*strength).astype(int);stages={label:image(label) for label in ['slow','tap','fast']}
    for label,pixels in stages.items():
        doc=read(label);expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected and (pixels[:,:,3]==255).all();mask=(pixels!=blank).any(axis=2);assert components(mask)=={'slow':1,'tap':2,'fast':3}[label],label+' has a gap or bridge between gestures'
    delta={label:(stages[label]!=(blank if label=='slow' else stages['slow' if label=='tap' else 'tap'])).any(axis=2) for label in ['slow','tap','fast']}
    maximum_distances={}
    for label,offset in [('slow',0),('fast',-160)]:
        mask=delta[label];assert components(mask)==1;ys,xs=np.where(mask);distance=distances(curve(offset),xs,ys);maximum_distances[label]=float(distance.max());assert distance.max()<=radius+2,'Spike or cross-stroke connector beyond the independently specified curve'
        for t in np.linspace(0,1,101):
            x=150*(1-t)**2+800*(1-t)*t+650*t*t;y=280*(1-t)**2+320*(1-t)*t+280*t*t+offset;xx=int(round(x));yy=int(round(y));assert mask[max(0,yy-1):yy+2,max(0,xx-1):xx+2].any(),'Curve loses a centreline sample'
        if size>=22:
            core=distance<radius-2;assert core.any();colours=stages[label][ys[core],xs[core],:3].astype(int);assert int(np.abs(colours-expected_rgb).max())<=2,'Marker core disagrees with one known Strength contribution'
            for centre,tangent in [(np.array([150,280+offset]),np.array([-250,120])),(np.array([650,280+offset]),np.array([250,120]))]:
                p=centre+tangent/np.linalg.norm(tangent)*radius*.65;xx,yy=np.rint(p).astype(int);assert mask[yy-1:yy+2,xx-1:xx+2].any(),'End cap does not extend roundly behind its tangent'
    tap=delta['tap'];assert components(tap)==1;ys,xs=np.where(tap);r=np.hypot(xs+.5-800,ys+.5-200);assert r.max()<=radius+2
    if size>=22:
        assert math.pi*max(0,radius-2)**2<=tap.sum()<=math.pi*(radius+2)**2;assert int(np.abs(stages['tap'][200,800,:3].astype(int)-expected_rgb).max())<=2
    else:
        assert int((stages['slow'][:,:,1].astype(int)-stages['tap'][:,:,1].astype(int)).sum())>=10,'Minimum-size tap is effectively invisible'
    for label,reference in {'fast-undone':'tap','tap-undone':'slow','slow-undone':'before','slow-redone':'slow','tap-redone':'tap','fast-redone':'fast','fresh/reopened':'fast'}.items():assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),label+' did not restore its exact complete gesture state'
    overlay=image('cursor-before-tap');assert overlay.shape==(640,960,4);oy,ox=np.where(overlay[:,:,3]>2);assert len(ox)>0;scale=960/row['view_rectangle']['width'];outer=np.hypot(ox+.5-800,oy+.5-200).max();cursor_checked=size==22
    if cursor_checked:assert abs(float(outer)-(radius+1.5*scale))<=2,'Visible cursor ring does not match22px footprint plus its3 CSS-pixel outline'
    inputs=read_json(location/'native-input.json');assert len([e for e in inputs if e['type']=='pointerdown'])==3 and len([e for e in inputs if e['type']=='pointerup'])==3 and all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert row['fast_elapsed_ms']<row['slow_elapsed_ms']
    for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in read_json(file) if e['action']=='download']
    rows.append(dict(id=row['id'],viewport=row['viewport'],size=size,strength=strength,three_separate_connected_gestures=True,no_independent_centreline_gaps_or_tube_spikes=True,maximum_curve_distance=maximum_distances,round_tap_pixels=int(tap.sum()),known_marker_alpha_core_verified=size>=22,standard22_cursor_checked=cursor_checked,actual_fast_ms=row['fast_elapsed_ms'],actual_slow_ms=row['slow_elapsed_ms'],all_three_undo_redo_and_fresh_complete_data_RGBA_exact=True))
assert len(downloads)==22*len(completed)
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=308,all_pre_recorded_pairwise_rows_and_four_exact_main_flows_executed=True,oracle='Independent run-length8-connectivity, elementary point-to-segment distances to the declared quadratic samples, dense centreline coverage and round cap/tap geometry with predeclared2px AA allowance; elementary red-over-white alpha blend within2/255; public cursor ring radius plus independently scaled3 CSS-pixel outline at standard22. Complete expected source/header mutations, each gesture Undo/Redo and actual fresh-file exact RGBA. Native input/timing is recorded; no physical pen claim.',execution='Isolated headless production controls and actual bytes; no internal painter/serializer supplies expected data')
report['actual_downloads_verified']=len(downloads);report['all_pre_recorded_pairwise_rows_and_four_exact_main_flows_executed']=not prefix;report['coverage_chunks']=[dict(folder=str(folder.relative_to(root)),completed_rows=[r['id'] for r in ui['rows']],unfinished_label_readiness_failure_excluded=prefix)];report['scope']='Prefix checks only, not an acceptance Pass' if prefix else 'All fourteen planned rows independently verified'
(root/('evidence/PAINT-001-'+('prefix-verification' if prefix else 'independent-verification')+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-001',rows=len(completed),downloads=len(downloads),prefix_only=prefix),indent=2))
