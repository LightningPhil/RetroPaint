"""Independent colour/alpha/direction, layer, history and actual-file oracle.

No application import or replica Smudge kernel. Expected colour follows the
predeclared pure-red/transparent invariant and the actual immutable input frame.
"""
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy
from PIL import Image
import numpy as np
import json, hashlib, base64, io, argparse

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--folder',default='PAINT-013-before');parser.add_argument('--prefix',action='store_true');parser.add_argument('--observe',action='store_true');args=parser.parse_args()
base=root/'headless'/args.folder
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
plan=read(root/'fixtures/PAINT-013-plan.json')
rgba=lambda p:np.asarray(Image.open(p).convert('RGBA'))
decode=lambda layer:rgba(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1])))
source=rgba(root/'fixtures/SMUDGE.png'); yy,xx=np.mgrid[:240,:320]
records=[];downloads=[];failures=[]
def require(ok,name,detail=None):
    if not bool(ok): failures.append(dict(row=current,name=name,detail=detail))
    return bool(ok)
def complete(row):
    folder=base/row['id']
    return (folder/'native-input.json').exists() and (folder/'fresh/events.json').exists() and len([e for e in read(folder/'fresh/events.json') if e['action']=='download'])==2
rows=[r for r in plan['rows'] if complete(r)]
assert rows and (args.prefix or len(rows)==40),('Incomplete execution',len(rows))
if not args.prefix:
    ui=read(base/'PAINT-013-ui.json');assert ui['status']=='Pass' and not ui['errors'] and [r['id'] for r in ui['rows']]==[r['id'] for r in plan['rows']]
for row in rows:
    current=row['id'];folder=base/current;start_failures=len(failures)
    doc=lambda label:read(folder/(label+'.retropaint'))
    image=lambda label:rgba(folder/(label+'.png'))
    before=doc('before');after=doc('after');pixels=decode(after['layers'][1]);before_pixels=decode(before['layers'][1]);view=image('after');initial=image('pointer-down-source-public')
    fixture=root/row['fixture'];assert hashlib.sha256(fixture.read_bytes()).hexdigest()==row['fixture_sha256']
    expected_before=read(fixture)
    if row['flow']=='clear-only':expected_before['layers'][1]['name']='Smudge history target'
    require(before==expected_before,'Before document equals declared native fixture and optional rename')
    require(after['layers'][0]==before['layers'][0],'Every guide field and RGBA unchanged')
    expected=deepcopy(before);expected['layers'][1]['image']=after['layers'][1]['image'];expected['layers'][1]['live']=after['layers'][1]['live']
    require(after==expected,'Only active source image/live representation may change')
    require(np.array_equal(image('before'),initial),'Pointer-down preserves same-phase rendered pixels')
    require(np.array_equal(view,image('released-public')),'Export equals actual released public canvas')
    composite_source=pixels;remaining_live=any(after['layers'][1]['live'].get(kind) for kind in ['strokes','fills','sparkles'])
    if remaining_live:
        # Empty-space edits preserve Water as an overlay over its white raw
        # backing. Its independently captured, same-phase opaque input RGB is
        # the rendered source; the white backing alone is not the picture.
        require(row['flow']=='clear-only' and after==before,'Unchanged live source remains exactly the original document')
        composite_source=np.zeros_like(source);opaque=source[:,:,3]==255;composite_source[opaque]=initial[opaque]
    a=composite_source[:,:,3:4].astype(float)/255;guide=decode(before['layers'][0]);composed=np.empty_like(pixels);composed[:,:,:3]=np.rint(composite_source[:,:,:3]*a+guide[:,:,:3]*(1-a));composed[:,:,3]=255
    composition_error=int(np.abs(composed.astype(int)-view.astype(int)).max())
    require(composition_error<=1,'Independent active-source/Green-guide composition',composition_error)
    events=read(folder/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in events)
    down=[e for e in events if e['type']=='pointerdown'];up=[e for e in events if e['type']=='pointerup'];moves=[e for e in events if e['type']=='pointermove' and e['buttons']]
    assert len(down)==len(up)==1 and len(moves)==len(row['points'])-1
    assert np.linalg.norm(np.array(down[0]['source'])-row['points'][0])<.001 and np.linalg.norm(np.array(up[0]['source'])-row['points'][-1])<.001
    for e,p in zip(moves,row['points'][1:]):assert np.linalg.norm(np.array(e['source'])-p)<.001
    require(doc('redone')==after and np.array_equal(image('redone'),view),'Complete source/RGBA Redo exact')
    require(doc('fresh/reopened')==after and np.array_equal(image('fresh/reopened'),view),'Actual fresh project input complete source/RGBA exact')
    held_changes=None;released_changes=None
    if row['source_kind']=='live':
        held_changes=int(np.any(image('held-live-phase-10371-public')!=image('pointer-down-public'),axis=2).sum())
        require(held_changes>0,'Water remains animated while held before any movement',held_changes)
    metrics=dict(id=current,flow=row['flow'],source_kind=row['source_kind'],viewport=row['viewport'],size=row['size'],strength=row['strength'],maximum_independent_composition_error=composition_error,held_Water_phase_changed_pixels=held_changes)
    if row['flow']=='clear-only':
        require(after==before and np.array_equal(view,image('before')),'Empty-space gesture preserves complete source/live/RGBA')
        require(doc('undone')==doc('unprimed') and np.array_equal(image('undone'),image('unprimed')),'Empty-space gesture adds no Undo entry over primed rename')
        if row['source_kind']=='live':
            released_changes=int(np.any(image('released-live-phase-10371-public')!=image('released-public'),axis=2).sum())
            require(released_changes>0,'Water remains animated after empty-space release',released_changes)
            require(np.array_equal(image('released-restored-phase-public'),view),'Returning to declared reference render phase is exact')
        metrics['released_Water_phase_changed_pixels']=released_changes
    else:
        # Original foreground alpha is binary. In opaque cells the captured view
        # contains source RGB directly; clear cells must remain transparent.
        starting=np.zeros_like(source);opaque=source[:,:,3]==255;starting[opaque]=initial[opaque]
        radius=max(12,row['size']);p0,p1=np.array(row['points'][0]),np.array(row['points'][-1]);nearest_x=np.clip(xx+.5,p0[0],p1[0]);distance=np.hypot(xx+.5-nearest_x,yy+.5-p0[1]);outside=distance>radius+1
        changed=np.any(pixels!=starting,axis=2)
        require(changed.any(),'Meaningful Smudge actually changes active source')
        require(not changed[outside].any(),'Pixels outside predeclared path radius plus1 remain exact',int(changed[outside].sum()))
        pure=(xx<154)&(pixels[:,:,3]>0);errors=np.max(np.abs(pixels[pure,:3].astype(int)-np.array([255,0,0])),axis=1);wrong=int((errors>1).sum())
        require(wrong==0,'Transparent Red resampling retains pure Red and never imports black/Green',dict(wrong_pixels=wrong,maximum_RGB_error=int(errors.max())))
        feather=(source[:,:,3]==0)&(pixels[:,:,3]>0)&(pixels[:,:,3]<255);levels=np.unique(pixels[feather,3]);require(len(levels)>=3,'Clear gap develops at least3 partial-alpha feathering levels',len(levels))
        region=xx<154;alpha=pixels[:,:,3].astype(float)*region;alpha0=source[:,:,3].astype(float)*region
        shift=float(((xx+.5)*alpha).sum()/alpha.sum()-((xx+.5)*alpha0).sum()/alpha0.sum());require(shift>0,'Alpha-weighted Red-region centroid moves in drag direction',shift)
        require(doc('undone')==before and np.array_equal(image('undone'),image('before')),'Whole-gesture Undo restores exact complete source/live/RGBA')
        metrics.update(changed_active_pixels=int(changed.sum()),pure_Red_wrong_pixels=wrong,maximum_pure_Red_RGB_error=int(errors.max()),partial_alpha_levels=len(levels),Red_centroid_shift_right_pixels=shift)
    for file in [folder/'events.json',folder/'fresh/events.json']:
        for event in read(file):
            if event['action']=='download':
                data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
    metrics['failed_requirements']=len(failures)-start_failures;records.append(metrics)
for record in records:
    if record['flow']=='smudge' and record['strength']==1:
        weak=next((r for r in records if r['flow']=='smudge' and r['source_kind']==record['source_kind'] and r['size']==record['size'] and r['viewport']==record['viewport'] and r['strength']==.15),None)
        if weak:
            current=record['id'];require(record['Red_centroid_shift_right_pixels']>weak['Red_centroid_shift_right_pixels'],'Full Strength moves Red farther than15%',dict(full=record['Red_centroid_shift_right_pixels'],weak=weak['Red_centroid_shift_right_pixels']))
assert len(downloads)==sum(12 if r['flow']=='clear-only' else 10 for r in rows)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-013',status='Fail' if failures else ('Completed prefix only' if args.prefix else 'Pass'),folder=str(base.relative_to(root)),executed_rows=len(rows),planned_rows=40,actual_downloads_verified=len(downloads),rows=records,failures=failures,oracle=plan['oracle'],scope='Independent observed actual outputs; failures retained. Prefix never certifies case.' if args.observe or args.prefix else 'All40 actual-control workflows,416 actual downloads, colour/alpha/direction/Strength/active-layer/live/history/fresh checks.')
target=root/'evidence'/('PAINT-013-'+args.folder+'-'+('prefix' if args.prefix else 'independent')+'.json');target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=report['status'],rows=len(rows),actual_downloads=len(downloads),failed_requirements=len(failures),failure_names=sorted(set(f['name'] for f in failures)))))
if failures and not args.observe:raise SystemExit(1)
