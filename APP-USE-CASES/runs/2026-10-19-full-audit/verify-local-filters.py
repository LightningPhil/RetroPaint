"""Independent local-area, checker-detail, relief-order and real-file checks."""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image,ImageColor
from paint_oracle import distances
import numpy as np
import json,hashlib,io,base64,argparse
root=Path(__file__).resolve().parent;repo=root.parents[2];parser=argparse.ArgumentParser();parser.add_argument('--case',choices=['PAINT-016','PAINT-017','PAINT-018'],required=True);parser.add_argument('--paper',action='store_true');parser.add_argument('--prefix',action='store_true');parser.add_argument('--observe',action='store_true');parser.add_argument('--continuation-folder');parser.add_argument('--extra-continuation-folder');args=parser.parse_args();case=args.case
read=lambda p:json.loads(p.read_text(encoding='utf-8'));rgba=lambda p:np.asarray(Image.open(p).convert('RGBA'));plan=read(root/f"fixtures/{case}{'-paper' if args.paper else ''}-plan.json");base=root/f"headless/{case}{'-paper' if args.paper else '-native'}";mode=plan['mode'];decode=lambda doc:rgba(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1])))
def ready_in(folder):return (folder/'native-input.json').exists() and (folder/'fresh/events.json').exists() and len([e for e in read(folder/'fresh/events.json') if e['action']=='download'])==2
continuation=root/'headless'/args.continuation_folder if args.continuation_folder else None
extra=root/'headless'/args.extra_continuation_folder if args.extra_continuation_folder else None
def row_folder(row):
    choices=[folder/row['id'] for folder in [base,continuation,extra] if folder is not None and ready_in(folder/row['id'])];assert len(choices)<=1,'Do not silently choose between duplicate complete workflows';return choices[0] if choices else None
def ready(row):return row_folder(row) is not None
rows=[r for r in plan['rows'] if ready(r)];assert rows and (args.prefix or len(rows)==plan['expected_rows']),('Incomplete execution',len(rows))
if not args.prefix:
    ui=read(base/(case+'-ui.json'));assert not ui['errors']
    if continuation:
        following=read(continuation/(case+'-ui.json'));assert ui['status']=='Fail' and 'Predeclared filter source point is covered' in ui['error'] and len(ui['rows'])==10 and not following['errors']
        completed=ui['rows']+following['rows']
        if extra:
            final=read(extra/(case+'-ui.json'));assert following['status']=='Fail' and 'eraserDrawer' in following['error'] and 'intercepts pointer events' in following['error'] and len(following['rows'])==6 and final['status']=='Pass' and not final['errors'] and len(final['rows'])==6;completed+=final['rows']
        else:assert following['status']=='Pass'
        assert [r['id'] for r in completed]==[r['id'] for r in plan['rows']]
    else:assert ui['status']=='Pass' and [r['id'] for r in ui['rows']]==[r['id'] for r in plan['rows']]
records=[];downloads=[];failures=[];natural=[]
def require(ok,name,detail=None):
    if not bool(ok):failures.append(dict(row=current,name=name,detail=detail))
for row in rows:
    current=row['id'];folder=row_folder(row);image=lambda label:rgba(folder/(label+'.png'));doc=lambda label:read(folder/(label+'.retropaint'));before=doc('before');initial=image('before');fixture=repo/row['fixture'];assert hashlib.sha256(fixture.read_bytes()).hexdigest()==row['fixture_sha256'];original=rgba(fixture);assert list(original.shape[:2][::-1])==row['dimensions'];assert np.array_equal(initial,decode(before)) and len(before['layers'])==1 and before['active']==before['layers'][0]['id']
    if args.paper:assert before['layers'][0]['paper'] is not None and ImageColor.getrgb(before['layers'][0]['paper'])==(255,255,255) and before['layers'][0]['name']=='Paper' and (initial[:,:,3]==255).all(),'Defined opaque Paper scope not established through actual controls'
    else:assert before['layers'][0]['paper'] is None,'Original image-sheet scope differs from declared baseline'
    source_error=np.abs(initial.astype(int)-original.astype(int));allowed=np.full(original.shape[:2],2 if row['kind']=='owned-portrait' else 0);allowed[original[:,:,3]==128]=2;assert (source_error[:,:,:3]<=allowed[:,:,None]).all() and np.array_equal(initial[:,:,3],original[:,:,3]),'Native image input disagrees with independent decoder beyond predeclared allowance'
    w,h=row['dimensions'];yy,xx=np.mgrid[:h,:w];radius=max(22,row['size']*1.4) if mode=='pixelate' else max(20,row['size']*1.3);previous=initial;previous_doc=before;inputs=read(folder/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' and e['type']!='pointercancel' for e in inputs);metrics=[]
    for index,gesture in enumerate(row['gestures']):
        label=gesture['label'];after=doc(label);pixels=image(label);expected=deepcopy(previous_doc);expected['layers'][0]['image']=after['layers'][0]['image'];require(after==expected,'Effect only changes active source image')
        require(np.array_equal(pixels,decode(after)) and np.array_equal(pixels,image(label+'-settled-public')),'Saved PNG/raw source/settled public canvas exact')
        require(np.array_equal(pixels[:,:,3],previous[:,:,3]),'Complete source alpha preserved')
        clear=previous[:,:,3]==0;require(np.array_equal(pixels[clear],previous[clear]),'Transparent border stays clear RGBA without an opaque fringe')
        points=gesture['points']
        # Every planned sweep is straight and monotonic. Establish that first,
        # then use its identical segment union instead of repeatedly scanning
        # the same full-sized distance arrays for every collinear subsegment.
        if len(points)>1:
            p=np.array(points,dtype=float);v=p[-1]-p[0];t=((p-p[0])@v)/(v@v);assert np.allclose(p,p[0]+t[:,None]*v,atol=1e-12) and (np.diff(t)>=0).all() and t[0]==0 and t[-1]==1
        distance=np.hypot(xx+.5-points[0][0],yy+.5-points[0][1]) if len(points)==1 else distances([points[0],points[-1]],xx.ravel(),yy.ravel()).reshape(h,w);outside=distance>radius+1;changed=np.any(pixels!=previous,axis=2);require(changed.any(),'Effect visibly changes the declared local detail');require(not changed[outside].any(),'All pixels outside the declared swept radius plus1 remain exact',int(changed[outside].sum()))
        native=[e for e in inputs if e['phase']==label and not e.get('moving_paper')];downs=[e for e in native if e['type']=='pointerdown'];ups=[e for e in native if e['type']=='pointerup'];moves=[e for e in native if e['type']=='pointermove' and e['buttons']];assert len(downs)==len(ups)==1 and len(moves)==len(points)-1;assert np.linalg.norm(np.array(downs[0]['source'])-points[0])<.001 and np.linalg.norm(np.array(ups[0]['source'])-points[-1])<.001
        for event,p in zip(moves,points[1:]):assert np.linalg.norm(np.array(event['source'])-p)<.001
        require(doc(label+'-undone')==previous_doc and np.array_equal(image(label+'-undone'),previous),'Complete whole-gesture Undo exact');require(doc(label+'-redone')==after and np.array_equal(image(label+'-redone'),pixels),'Complete whole-gesture Redo exact')
        metric=dict(label=label,changed_pixels=int(changed.sum()),changed_outside_predeclared_footprint=int(changed[outside].sum()),native_samples=len(points),all_alpha_and_clear_RGBA_exact=np.array_equal(pixels[:,:,3],previous[:,:,3]) and np.array_equal(pixels[clear],previous[clear]))
        if row['kind']=='known-pattern' and label=='tap':
            core=(distance<radius-(1 if mode=='invert' else 8))&(xx>=72)&(xx<632)&(yy>=72)&(yy<568)&(previous[:,:,3]==255);assert core.sum()>20
            if mode=='pixelate':
                wanted=np.rint(previous[core,:3].astype(float)+(128-previous[core,:3].astype(float))*row['strength']);error=np.abs(pixels[core,:3].astype(int)-wanted);require(error.max()<=1,'Checker core averages independently to128 at chosen Strength',int(error.max()));metric.update(checker_core_pixels=int(core.sum()),maximum_independent_average_error=int(error.max()))
            elif mode=='invert':
                wanted=np.rint(previous[core,:3].astype(float)+row['strength']*(255-2*previous[core,:3].astype(float)));error=np.abs(pixels[core,:3].astype(int)-wanted);require(error.max()<=1,'Defined Paper core inverts once at chosen Strength',int(error.max()))
                if row['strength']==1:require(np.array_equal(pixels[core,:3],255-previous[core,:3]),'Full Paper inversion is the exact RGB complement')
                metric.update(opaque_Paper_core_pixels=int(core.sum()),maximum_independent_inversion_error=int(error.max()))
            else:
                old=previous[:,:,0].astype(int);new=pixels[:,:,0].astype(int);left=np.roll(old,1,axis=1);rising=core&(old==224)&(left==32);high_flat=core&(old==224)&(left==224);falling=core&(old==32)&(left==224);low_flat=core&(old==32)&(left==32);assert all(mask.any() for mask in [rising,high_flat,falling,low_flat]);lift=float(new[rising].mean()-new[high_flat].mean());shade=float(new[low_flat].mean()-new[falling].mean());require(lift>1 and shade>1,'Relief brightens rising edges and darkens falling edges against equal-grey flat equivalents',dict(rising_lift=lift,falling_shade=shade));require(np.array_equal(pixels[core,0],pixels[core,1]) and np.array_equal(pixels[core,1],pixels[core,2]),'Neutral source relief remains neutral');metric.update(checker_core_pixels=int(core.sum()),rising_edge_lift_over_equal_grey_flat=lift,falling_edge_shade_below_equal_grey_flat=shade)
        if row['kind']=='owned-portrait':
            core=(distance<radius-8)&(previous[:,:,3]==255);assert core.sum()>20;delta=np.abs(pixels[:,:,:3].astype(int)-previous[:,:,:3].astype(int));metric['mean_absolute_detail_change']=float(delta[core].mean());require(delta[core].any(),'Actual eye/glasses detail changes visibly inside footprint');natural.append(dict(row=row,original=previous.copy(),after=pixels.copy(),core=core))
            if mode=='pixelate' and row['strength']==1:
                pairs=core[:,1:]&core[:,:-1];old_diff=np.abs(previous[:,1:,:3].astype(int)-previous[:,:-1,:3].astype(int));new_diff=np.abs(pixels[:,1:,:3].astype(int)-pixels[:,:-1,:3].astype(int));old_equal=float(np.all(old_diff==0,axis=2)[pairs].mean());new_equal=float(np.all(new_diff==0,axis=2)[pairs].mean());old_tv=float(old_diff[pairs].mean());new_tv=float(new_diff[pairs].mean());require(new_equal>old_equal and new_tv<old_tv,'Real photograph becomes locally blockier with reduced fine detail',dict(original_equal_neighbour_fraction=old_equal,filtered_equal_neighbour_fraction=new_equal,original_horizontal_variation=old_tv,filtered_horizontal_variation=new_tv));metric.update(original_equal_neighbour_fraction=old_equal,filtered_equal_neighbour_fraction=new_equal,original_horizontal_variation=old_tv,filtered_horizontal_variation=new_tv)
        metrics.append(metric);previous=pixels;previous_doc=after
    require(doc('fresh/reopened')==previous_doc and np.array_equal(image('fresh/reopened'),previous),'Actual fresh project input complete source/RGBA exact')
    for file in [folder/'events.json',folder/'fresh/events.json']:
        for event in read(file):
            if event['action']=='download':data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
    records.append(dict(id=current,folder=str(folder.relative_to(root)),kind=row['kind'],viewport=row['viewport'],size=row['size'],strength=row['strength'],actual_saved_paper_colour=before['layers'][0]['paper'],gestures=metrics))
metamorphic=[]
for weak in natural:
    if weak['row']['strength']!=.15:continue
    full=next((r for r in natural if r['row']['strength']==1 and r['row']['viewport']==weak['row']['viewport']),None)
    if full:
        current=weak['row']['id'];assert np.array_equal(weak['original'],full['original']);core=weak['core'];wanted=np.rint(weak['original'][:,:,:3].astype(float)+.15*(full['after'][:,:,:3].astype(float)-weak['original'][:,:,:3].astype(float)));error=np.abs(weak['after'][:,:,:3].astype(int)-wanted);maximum=int(error[core].max());require(maximum<=1,'Actual portrait15% Strength agrees with observed full contribution',maximum);metamorphic.append(dict(weak=current,full=full['row']['id'],maximum_blend_error=maximum))
assert len(downloads)==sum(4+6*len(r['gestures']) for r in rows)
report=dict(at=datetime.now(timezone.utc).isoformat(),case=case,mode=mode,paper_scope=args.paper,status='Fail' if failures else ('Completed prefix only' if args.prefix else 'Pass'),rows=records,actual_downloads_verified=len(downloads),portrait_strength_metamorphic_checks=metamorphic,failures=failures,oracle=plan['oracle'],scope='Completed prefix only; no case Pass.' if args.prefix else 'All14 defined opaque-Paper native size/Strength/layout workflows,140 actual downloads, saved paper property/alpha verified and all area/effect/history/fresh branches.' if args.paper else 'All22 native workflows/388 actual downloads,14 pattern and8 actual owned portrait rows; all area/alpha/detail-or-relief/Strength/history/fresh branches.')
target=root/('evidence/'+case+('-paper' if args.paper else '')+('-completed-prefix-verification.json' if args.prefix else '-independent-verification.json'));target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case=case,status=report['status'],paper_scope=args.paper,rows=len(rows),actual_downloads=len(downloads),failures=failures)))
if failures and not args.observe:raise SystemExit(1)
