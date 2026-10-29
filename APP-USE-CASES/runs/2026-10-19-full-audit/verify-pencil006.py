from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import verify_brush_boundary
import json,hashlib,base64,io,sys
import numpy as np
root=Path(__file__).resolve().parent;read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));folder=root/'headless/PAINT-006-core-final';boundary=root/'headless/PAINT-006-boundary-final';ui=read_json(folder/'PAINT-006-ui.json');plan=read_json(root/'fixtures/PAINT-006-plan.json');bp=read_json(root/'fixtures/PAINT-006-boundary-plan.json');assert ui['status']=='Pass' and not ui['errors'] and ui['origin']=='http://127.0.0.1:8101/'
assert [r['viewport'] for r in ui['rows']]==plan['viewports'];fixture=(root/plan['fixture']).read_bytes();assert hashlib.sha256(fixture).hexdigest()==plan['fixture_sha256'];original=np.asarray(Image.open(io.BytesIO(fixture)).convert('RGBA'))
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
rows=[];downloads=[]
for row in ui['rows']:
    location=folder/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');assert (before['width'],before['height'])==(32,32) and len(before['layers'])==1 and np.array_equal(image('before'),original) and np.array_equal(decoded(before),original);expected=original.copy();counts=[]
    for label,points in [('staircase',plan['staircase_points']),('fit-tap',[plan['fit_tap']]),('actual-tap',[plan['actual_pixel_tap']])]:
        for x,y in points:expected[int(y),int(x)]=plan['colour']
        actual=image(label);assert np.array_equal(actual,expected),(row['id'],label,'does not have exact declared source cells/colours');doc=read(label);header=deepcopy(before);header['layers'][0]['image']=doc['layers'][0]['image'];assert doc==header and np.array_equal(decoded(doc),expected);counts.append(dict(stage=label,changed_cells=int((expected!=original).any(axis=2).sum()),exact_palette_black_and_all_neighbours=True))
    assert row['enlarged_rectangle']['width']/32>=6 and abs(row['actual_pixel_rectangle']['width']-32)<.1 and abs(row['actual_pixel_rectangle']['height']-32)<.1
    for label,reference in {'actual-tap-undone':'fit-tap','fit-tap-undone':'staircase','staircase-undone':'before','staircase-redone':'staircase','fit-tap-redone':'fit-tap','actual-tap-redone':'actual-tap','fresh-project/reopened':'actual-tap'}.items():assert read(label)==read(reference),(row['id'],label,'complete source/history mismatch')
    assert np.array_equal(image('fresh-project/reopened'),expected) and np.array_equal(image('fresh-image/reopened'),expected);png_doc=read('fresh-image/reopened');assert (png_doc['width'],png_doc['height'])==(32,32) and len(png_doc['layers'])==1 and np.array_equal(decoded(png_doc),expected)
    inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);draw=[e for e in inputs if not e['movingPaper']];downs=[e for e in draw if e['type']=='pointerdown'];assert len(downs)==len([e for e in draw if e['type']=='pointerup'])==3
    for event,point in zip(downs,[plan['staircase_points'][0],plan['fit_tap'],plan['actual_pixel_tap']]):assert np.abs(np.array(event['source'])-point).max()<.01,'Native Pencil source point changed from the plan'
    pan_count=len([e for e in inputs if e['type']=='pointerdown' and e['movingPaper']]);assert pan_count==len(row['paper_pans']) and all(p['source_geometry_unchanged'] for p in row['paper_pans'])
    for file in [location/'events.json',location/'fresh-project/events.json',location/'fresh-image/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
    rows.append(dict(viewport=row['viewport'],stages=counts,actual_pans_reveal_same_source_cells=pan_count,enlarged_grid_and_true_actual_pixel_scale=True,complete_gesture_project_history_exact=True,actual_fresh_project_and_PNG_exact_cells_RGBA=True))
assert len(downloads)==72
if '--core-only' in sys.argv:
    for event in downloads:
        data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
    report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,core_rows=rows,actual_downloads_verified=len(downloads),all_core_bytes_and_declared_cells_exact=True,scope='Core only; additional14-row boundary matrix is still required for an acceptance Pass.',oracle=plan['oracle'])
    (root/'evidence/PAINT-006-core-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Verified all four strict32x32 core workflows/72 downloads; this does not close PAINT-006.');sys.exit(0)
bu=read_json(boundary/'PAINT-006-boundary-ui.json');assert bu['status']=='Pass' and not bu['errors'] and bu['origin']==ui['origin']
br,bd=verify_brush_boundary(boundary,bu,bp,read_json,decoded)
for row in bu['rows']:
    location=boundary/row['id'];previous=np.asarray(Image.open(location/'before.png').convert('RGBA'));expected=np.rint(255+(np.array([229,57,53])-255)*row['strength']).astype(int)
    for label in ['slow','tap','fast']:
        pixels=np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));mask=(pixels!=previous).any(axis=2);assert np.abs(pixels[mask,:3].astype(int)-expected).max()<=1,(row['id'],label,'Pencil adds unintended AA shades');
        if row['size']==1 and label=='tap':assert mask.sum()==1,'Minimum Pencil tap occupies more than one source cell'
        previous=pixels
downloads+=bd;assert len(downloads)==380
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,core_rows=rows,boundary_rows=br,actual_downloads_verified=len(downloads),all_core_and_boundary_rows_verified=True,oracle=plan['oracle']+' Additional matrix: '+bp['oracle'],execution=ui['execution'],strict_tolerance='Zero tolerance for32x32 cells/colours and full data/history;1/255 only for the matrix15% compositing arithmetic, not AA edges.',original_before_evidence_retained='evidence/PAINT-006-pixel-before.json; headless/PAINT-006-before; headless/PAINT-006-fixed-core')
(root/'evidence/PAINT-006-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-006',core_rows=len(rows),boundary_rows=len(br),downloads=len(downloads))))
