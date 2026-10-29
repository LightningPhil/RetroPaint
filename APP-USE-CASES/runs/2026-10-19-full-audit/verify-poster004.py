from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import verify_brush_boundary,components,distances,curve
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PAINT-004-complete';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'PAINT-004-ui.json');plan=read_json(root/'fixtures/PAINT-004-plan.json');assert ui['status']=='Pass' and not ui['errors'] and len(ui['phases'])==4
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
rows,downloads=verify_brush_boundary(folder,ui,plan,read_json,decoded);phases=[];assert {p['row'] for p in ui['phases']}=={r['id'] for r in plan['rows'] if r['size']==22 and r['strength']==1}
for phase in ui['phases']:
    location=folder/phase['row']/'material';read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert (blank==255).all();stage={};mask={};previous=blank;core={};maximum={}
    for label,offset in [('marker',-160),('full',0),('weak',200),('overlap',200)]:
        doc=read(label);expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected;pixels=image(label);assert np.array_equal(pixels,decoded(doc));delta=(pixels!=previous).any(axis=2);assert components(delta)==1,label+' material delta disconnected';ys,xs=np.where(delta);distance=distances(curve(offset),xs,ys);assert distance.max()<=13,'Material outside declared22px nib/AA tube';ys_core=ys[distance<8];xs_core=xs[distance<8];assert len(xs_core)>1000;core[label]=(ys_core,xs_core);maximum[label]=float(distance.max());stage[label]=pixels;mask[label]=delta;previous=pixels
        for t in np.linspace(0,1,101):
            x=150*(1-t)**2+800*(1-t)*t+650*t*t;y=280*(1-t)**2+320*(1-t)*t+280*t*t+offset;xx=int(round(x));yy=int(round(y));assert delta[yy-2:yy+3,xx-2:xx+3].any(),'Material centreline gap'
    ys,xs=core['full'];colours=stage['full'][ys,xs,:3].astype(int);marker=stage['marker'][ys-160,xs,:3].astype(int);assert np.abs(marker-np.array([229,57,53])).max()<=2;unique=len(np.unique(colours,axis=0));spread=int(np.ptp(colours[:,1]));different=float((colours!=marker).any(axis=1).mean());assert unique>=3 and spread>=3 and different>=.1,'Poster Paint is a flat Marker clone'
    ys,xs=core['weak'];first=stage['weak'][ys,xs,:3].astype(float);second=stage['overlap'][ys,xs,:3].astype(float);expected=np.rint(1.85*first-.85*255);error=int(np.abs(second-expected).max());assert error<=2,'Weak Poster overlap violates independent source-over';assert first[:,1].mean()>colours[:,1].mean()+10 and second[:,1].mean()<first[:,1].mean()
    assert read('poster-selected')==read('marker');assert all(read(label)==read('overlap') for label in ['zoom-out','zoom-restored','tool-changed']);assert phase['zoom_out_rectangle']['width']<phase['before_view_rectangle']['width']
    labels=['marker','full','weak','overlap']
    for index,label in enumerate(labels):assert read(label+'-undone')==read('before' if index==0 else labels[index-1]) and read(label+'-redone')==read(label)
    assert read('fresh/reopened')==read('overlap') and np.array_equal(image('fresh/reopened'),stage['overlap']);inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==4
    for file in [location/'events.json',location/'fresh/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
    phases.append(dict(row=phase['row'],viewport=phase['viewport'],core_unique_RGB_values=unique,core_green_range=spread,core_fraction_different_from_flat_Marker=different,weak_overlap_max_channel_error=error,maximum_path_distances=maximum,zoom_tool_history_and_fresh_complete_data_RGBA_exact=True))
assert len(downloads)==404
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,boundary_rows=rows,phases=phases,actual_downloads_verified=len(downloads),all_planned_rows_and_phases_verified=True,oracle=plan['oracle'],execution=ui['execution']);(root/'evidence/PAINT-004-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-004',boundary_rows=len(rows),material_phases=len(phases),downloads=len(downloads))))
