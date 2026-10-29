"""Independent per-gesture RGB inversion, area, alpha and real-file oracle."""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import distances
import numpy as np
import json,hashlib,base64,io,sys
root=Path(__file__).resolve().parent;base=root/'headless/PAINT-017-fixed';read_json=lambda p:json.loads(p.read_text(encoding='utf-8'));plan=read_json(root/'fixtures/PAINT-017-after-plan.json');prefix='--completed-prefix' in sys.argv
def ready(row):
    folder=base/row['id'];file=folder/'fresh/events.json'
    return (folder/'native-input.json').exists() and file.exists() and len([e for e in read_json(file) if e['action']=='download'])==2
if prefix:
    complete=[r for r in plan['rows'] if ready(r)];assert complete;ui=dict(rows=complete)
else:
    ui=read_json(base/'PAINT-017-ui.json');assert ui['status']=='Pass' and not ui['errors'] and [r['id'] for r in ui['rows']]==[r['id'] for r in plan['rows']]
fixture=root/plan['fixture'];assert hashlib.sha256(fixture.read_bytes()).hexdigest()==plan['fixture_sha256'];original=np.asarray(Image.open(fixture).convert('RGBA'));yy,xx=np.mgrid[0:640,0:960];downloads=[];rows=[];public_hashes=[]
def rgba(file):
    with Image.open(file) as image:return np.asarray(image.convert('RGBA'))
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
for row in ui['rows']:
    planned=next(r for r in plan['rows'] if r['id']==row['id']);assert all(row[k]==v for k,v in planned.items());folder=base/row['id'];read=lambda label:read_json(folder/(label+'.retropaint'));image=lambda label:rgba(folder/(label+'.png'));before=read('before');pixels=image('before');assert np.array_equal(pixels,original) and np.array_equal(decoded(before),original) and [before['width'],before['height']]==[960,640] and len(before['layers'])==1 and before['active']==before['layers'][0]['id'];previous=pixels;previous_doc=before;labels=[g['label'] for g in row['gestures']];metrics=[];inputs=read_json(folder/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' and e['type']!='pointercancel' for e in inputs);radius=max(20,row['size']*1.3)
    if not prefix:assert row['labels']==labels and str(row['size'])+' px' in row['actual_tool_label'] and str(round(row['strength']*100))+'%' in row['actual_tool_label']
    for index,gesture in enumerate(row['gestures']):
        label=gesture['label'];doc=read(label);expected=deepcopy(previous_doc);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected,'Filter changes a non-image source field or active target';current=image(label);assert np.array_equal(current,decoded(doc)) and np.array_equal(current,rgba(folder/(label+'-settled-public.png'))),'Saved RGBA differs from source or settled public view';assert np.array_equal(current[:,:,3],previous[:,:,3]),'Invert changes source alpha';assert np.array_equal(current[previous[:,:,3]==0],previous[previous[:,:,3]==0]),'Clear pixels acquire colour/opacity'
        native=[e for e in inputs if e['phase']==label];downs=[e for e in native if e['type']=='pointerdown'];ups=[e for e in native if e['type']=='pointerup'];moves=[e for e in native if e['type']=='pointermove' and e['buttons']];assert len(downs)==len(ups)==1 and len(moves)==len(gesture['points'])-1
        assert np.linalg.norm(np.array(downs[0]['source'])-gesture['points'][0])<.001 and np.linalg.norm(np.array(ups[0]['source'])-gesture['points'][-1])<.001
        for event,source in zip(moves,gesture['points'][1:]):assert np.linalg.norm(np.array(event['source'])-source)<.001,'Native movement differs from the unchanged planned path'
        points=gesture['points'];distance=np.hypot(xx+.5-points[0][0],yy+.5-points[0][1]) if len(points)==1 else distances([points[0],points[-1]],xx.ravel(),yy.ravel()).reshape(640,960);core=(distance<radius-1)&(previous[:,:,3]>0);outside=distance>radius+1;band=(~outside)&(~core)&(previous[:,:,3]>0);assert core.any();changed=(current!=previous).any(axis=2);assert changed.any() and not changed[outside].any(),'Invert leaks outside the predeclared footprint or does nothing'
        p=previous[core,:3].astype(int);wanted=np.rint(p+row['strength']*(255-2*p));error=np.abs(current[core,:3].astype(int)-wanted);allowed=np.where(previous[core,3]==255,1,2);assert (error<=allowed[:,None]).all(),(row['id'],label,'Wrong fully covered inversion/Strength contribution',int(error.max()))
        if row['strength']==1:assert np.array_equal(current[core,:3],255-previous[core,:3]),'Full-strength core is not the exact RGB complement'
        mask_metrics={}
        if band.any():
            p=previous[band,:3].astype(float);delta=current[band,:3].astype(float)-p;vector=255-2*p;denom=np.sum(vector*vector,axis=1);weight=np.sum(delta*vector,axis=1)/denom;residual=float(np.abs(delta-weight[:,None]*vector).max());assert residual<=2 and weight.min()>=-2/255 and weight.max()<=row['strength']+2/255,'Boundary values are not a common mask-weighted inversion';mask_metrics=dict(boundary_pixels_checked=int(band.sum()),maximum_mask_weight_residual=residual,minimum_mask_weight=float(weight.min()),maximum_mask_weight=float(weight.max()))
        returns=row['strength']==1 and (label in ['second','sparse'] or label.endswith('-second'))
        if returns:assert np.array_equal(current[core],original[core]),'Two full inversions fail to restore original fully covered RGBA'
        for suffix in ['cursor-public','settled-public']:
            file=folder/(label+'-'+suffix+'.png');public_hashes.append(dict(path=str(file.relative_to(root)),sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
        assert read(label+'-undone')==read('before' if index==0 else labels[index-1]) and np.array_equal(image(label+'-undone'),image('before' if index==0 else labels[index-1])),'Whole-gesture Undo differs'
        assert read(label+'-redone')==doc and np.array_equal(image(label+'-redone'),current),'Whole-gesture Redo differs'
        metrics.append(dict(label=label,source_samples=len(points),covered_visible_core_pixels=int(core.sum()),wrong_core_pixels=0,maximum_core_RGB_error=int(error.max()),changed_pixels=int(changed.sum()),source_alpha_and_clear_pixels_exact=True,unrelated_pixels_and_source_fields_exact=True,two_full_inversions_restore_original_core=returns,**mask_metrics));previous=current;previous_doc=doc
    assert read('fresh/reopened')==previous_doc and np.array_equal(image('fresh/reopened'),previous),'Actual fresh project input changes complete source or RGBA'
    for file in [folder/'events.json',folder/'fresh/events.json']:
        for event in read_json(file):
            if event['action']=='download':
                data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
    rows.append(dict(id=row['id'],kind=row['kind'],viewport=row['viewport'],size=row['size'],strength=row['strength'],gestures=metrics,all_gesture_Undo_Redo_and_fresh_source_RGBA_exact=True))
expected=sum(6*len(r['gestures'])+4 for r in ui['rows']);assert len(downloads)==expected and (prefix or expected==980)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-017',decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),all16_core14_boundary8_patch_workflows_verified=not prefix,groups={kind:sum(r['kind']==kind for r in rows) for kind in ['core','boundary','patches']},public_canvas_hashes=public_hashes,oracle=plan['oracle'],scope='Completed prefix only; no case Pass.' if prefix else 'Complete38 planned actual-control workflows,980 actual downloads, every Strength/size/layout/source-alpha/history/fresh branch. No kernel-generated expected image, no changed source point or relaxed before-failure core tolerance.')
(root/('evidence/PAINT-017-completed-prefix-verification.json' if prefix else 'evidence/PAINT-017-independent-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-017',groups=report['groups'],actual_downloads=len(downloads),acceptance_complete=not prefix)))
