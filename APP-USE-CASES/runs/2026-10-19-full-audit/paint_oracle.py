"""Independent raster measurements; no RetroPaint renderer/serializer imports."""
import numpy as np
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
        dx=b[0]-a[0];dy=b[1]-a[1];denom=dx*dx+dy*dy
        if denom==0:minimum=np.minimum(minimum,np.hypot(x-a[0],y-a[1]));continue
        t=np.clip(((x-a[0])*dx+(y-a[1])*dy)/denom,0,1);minimum=np.minimum(minimum,np.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
    return minimum
def curve(offset):return [[150*(1-t)**2+800*(1-t)*t+650*t*t,280*(1-t)**2+320*(1-t)*t+280*t*t+offset] for t in np.linspace(0,1,41)]

def dilate_one(mask):
    padded=np.pad(mask,1);result=np.zeros_like(mask)
    for dy in range(3):
        for dx in range(3):result|=padded[dy:dy+mask.shape[0],dx:dx+mask.shape[1]]
    return result

def verify_brush_boundary(folder,ui,plan,read_json,decode,soft=False,texture_dilation=False):
    from copy import deepcopy
    from PIL import Image
    rows=[];downloads=[]
    assert len(ui['rows'])==len(plan['rows'])==14
    for row,planned in zip(ui['rows'],plan['rows']):
        assert all(row[key]==value for key,value in planned.items());location=folder/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and (blank==255).all() and len(before['layers'])==1 and before['drawingMode']=='raster'
        previous=blank;deltas={};maximum={};raw_components={};bound=1.2*row['size']+4 if soft else row['size']/2+2
        for count,label in enumerate(['slow','tap','fast'],1):
            doc=read(label);expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected;pixels=image(label);assert np.array_equal(pixels,decode(doc)) and (pixels[:,:,3]==255).all();delta=(pixels!=previous).any(axis=2);raw_components[label]=components(delta);assert (components(dilate_one(delta)) if texture_dilation else raw_components[label])==1,(row['id'],label,'disconnected material mark');previous=pixels;deltas[label]=delta
            # Soft paint can legitimately overlap between the declared curves;
            # the newly affected mask, not total disjoint-island count, is tested.
            if not soft and not texture_dilation:assert components((pixels!=blank).any(axis=2))==count
        for label,offset in [('slow',0),('fast',-160)]:
            mask=deltas[label];ys,xs=np.where(mask);distance=distances(curve(offset),xs,ys);assert distance.max()<=bound,(row['id'],label,'material outside declared tube');maximum[label]=float(distance.max())
            for t in np.linspace(0,1,101):
                x=150*(1-t)**2+800*(1-t)*t+650*t*t;y=280*(1-t)**2+320*(1-t)*t+280*t*t+offset;xx=int(round(x));yy=int(round(y));assert mask[max(0,yy-2):yy+3,max(0,xx-2):xx+3].any(),(row['id'],label,'missing material centreline')
        ys,xs=np.where(deltas['tap']);assert np.hypot(xs+.5-800,ys+.5-200).max()<=bound
        for label,reference in {'fast-undone':'tap','tap-undone':'slow','slow-undone':'before','slow-redone':'slow','tap-redone':'tap','fast-redone':'fast','fresh/reopened':'fast'}.items():assert read(label)==read(reference) and np.array_equal(image(label),image(reference)),(row['id'],label,'complete material history/fresh mismatch')
        inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==3 and row['fast_elapsed_ms']<row['slow_elapsed_ms']
        for file in [location/'events.json',location/'fresh/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
        rows.append(dict(id=row['id'],viewport=row['viewport'],size=row['size'],strength=row['strength'],maximum_curve_distance=maximum,tap_pixels=int(deltas['tap'].sum()),new_gesture_masks_connected_and_contained=True,all_gesture_history_and_fresh_source_RGBA_exact=True))
        if texture_dilation:
            rows[-1].pop('new_gesture_masks_connected_and_contained')
            rows[-1].update(new_gesture_masks_contained=True,connected_after_declared_one_cell_grain_dilation=True,raw_components=raw_components,declared_one_cell_texture_dilation=True)
    return rows,downloads
