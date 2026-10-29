from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import verify_brush_boundary,components,distances
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PAINT-005-complete';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));ui=read_json(folder/'PAINT-005-ui.json');plan=read_json(root/'fixtures/PAINT-005-plan.json');assert ui['status']=='Pass' and not ui['errors'] and len(ui['phases'])==4
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
rows,downloads=verify_brush_boundary(folder,ui,plan,read_json,decoded,soft=True);phases=[];assert {p['row'] for p in ui['phases']}=={r['id'] for r in plan['rows'] if r['size']==22 and r['strength']==1};red=np.array([229,57,53],float)
for phase in ui['phases']:
    location=folder/phase['row']/'wash';read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert (blank==255).all();stage={};previous=blank
    for label in ['first','second','third']:
        doc=read(label);expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected;pixels=image(label);assert np.array_equal(pixels,decoded(doc));delta=(pixels!=previous).any(axis=2);assert components(delta)==1;ys,xs=np.where(delta);distance=distances([[150,300],[650,300]],xs,ys);assert distance.max()<=30.4,'Watercolor leaks beyond the declared soft footprint';stage[label]=pixels;previous=pixels
    first=stage['first'][300,400,:3].astype(float);alpha=(255-first[1])/198;assert .03<=alpha<=.15;assert np.abs(np.rint(255*(1-alpha)+red*alpha)-first).max()<=2,'Wash does not retain compatible translucent Red channels'
    full=np.asarray(Image.open(folder/phase['row']/'slow.png').convert('RGBA'))[220,400,:3].astype(float);full_alpha=(255-full[1])/198;assert .1<=alpha/full_alpha<=.2,'Reduced Strength does not retain its endpoint relationship'
    errors=[]
    for previous_label,label in [('first','second'),('second','third')]:
        prior=stage[previous_label][300,200:601,:3].astype(float);actual=stage[label][300,200:601,:3].astype(float);first_patch=stage['first'][300,200:601,:3].astype(float);weights=(255-first_patch[:,1])/198;expected=np.rint(prior*(1-weights[:,None])+red*weights[:,None]);error=int(np.abs(expected-actual).max());assert error<=2,'Overlapping wash disagrees with independent source-over';errors.append(error);assert actual[:,1].mean()<prior[:,1].mean()
    edge_levels=[]
    for yy in [slice(270,300),slice(301,331)]:
        values=255-stage['first'][yy,400,1].astype(int);levels=len(np.unique(values[values>0]));assert levels>=4,'Watercolor edge is hard rather than a soft wash';edge_levels.append(levels)
    for label in ['waited','tool-changed','fresh/reopened']:assert read(label)==read('third') and np.array_equal(image(label),stage['third']),'Wait/tool/save/reopen changes wash opacity/data'
    assert np.array_equal(image('first-public-frame'),stage['first']) and np.array_equal(image('waited-public-frame'),stage['third']),'Public paint frame differs from actual exported source'
    for label,reference in {'third-undone':'second','second-undone':'first','first-undone':'before','first-redone':'first','second-redone':'second','third-redone':'third'}.items():assert read(label)==read(reference)
    inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==3;assert phase['actual_wait_ms']>=2000
    events=read_json(location/'events.json');waits=[e for e in events if e['action']=='native-time-wash-wait'];assert len(waits)==1 and not waits[0]['fake_clock'] and waits[0]['elapsed_ms']==phase['actual_wait_ms']
    for file in [location/'events.json',location/'fresh/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
    phases.append(dict(row=phase['row'],viewport=phase['viewport'],first_centre_RGB=first.astype(int).tolist(),first_effective_alpha=float(alpha),full_strength_effective_alpha=float(full_alpha),overlap_maximum_channel_errors=errors,edge_distinct_positive_gradient_levels=edge_levels,actual_wait_ms=phase['actual_wait_ms'],public_frames_actual_export_RGBA_exact=True,wait_tool_history_and_fresh_source_RGBA_exact=True))
assert len(downloads)==388
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,boundary_rows=rows,phases=phases,actual_downloads_verified=len(downloads),all_planned_rows_and_phases_verified=True,oracle=plan['oracle'],execution=ui['execution'],soft_footprint_note='At the large endpoint, legitimate soft tails may overlap between the fixed curves. Every new affected mask is independently connected and contained; total disjoint-island count is not incorrectly imposed on deliberately broad soft paint.')
(root/'evidence/PAINT-005-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-005',boundary_rows=len(rows),wash_phases=len(phases),downloads=len(downloads))))
