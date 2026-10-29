"""Independent lifecycle, local erase/alpha, source/history/retry oracle."""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image,ImageColor
from paint_oracle import distances
import numpy as np
import json,hashlib,base64,io,argparse
root=Path(__file__).resolve().parent;parser=argparse.ArgumentParser();parser.add_argument('--folder',default='PAINT-015-before');parser.add_argument('--continuation-folder');parser.add_argument('--prefix',action='store_true');parser.add_argument('--observe',action='store_true');args=parser.parse_args();base=root/'headless'/args.folder;following=root/'headless'/args.continuation_folder if args.continuation_folder else None
read=lambda p:json.loads(p.read_text(encoding='utf-8'));rgba=lambda p:np.asarray(Image.open(p).convert('RGBA'));decode=lambda layer:rgba(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1])));plan=read(root/'fixtures/PAINT-015-plan.json');yy,xx=np.mgrid[:640,:960];downloads=[];records=[];failures=[]
def ready(folder):return (folder/'native-input.json').exists() and (folder/'fresh/events.json').exists() and len([e for e in read(folder/'fresh/events.json') if e['action']=='download'])==2
def folder_for(row):
    choices=[folder/row['id'] for folder in [base,following] if folder is not None and ready(folder/row['id'])];assert len(choices)<=1;return choices[0] if choices else None
rows=[r for r in plan['rows'] if folder_for(r) is not None];assert rows and (args.prefix or len(rows)==40),('Incomplete execution',len(rows))
if not args.prefix:
    ui=read(base/'PAINT-015-ui.json');assert not ui['errors']
    if following:
        next_ui=read(following/'PAINT-015-ui.json');assert ui['status']=='Fail' and 0<len(ui['rows'])<40 and 'early-effect window' in ui['error'] and next_ui['status']=='Pass' and not next_ui['errors'] and ui['origin']==next_ui['origin'];assert [r['id'] for r in ui['rows']]==[r['id'] for r in plan['rows'][:len(ui['rows'])]];assert next_ui['selected_plan_ids']==[r['id'] for r in plan['rows'][len(ui['rows']):]];executed=ui['rows']+next_ui['rows']
    else:assert ui['status']=='Pass';executed=ui['rows']
    assert [r['id'] for r in executed]==[r['id'] for r in plan['rows']]
def require(ok,name,detail=None):
    if not bool(ok):failures.append(dict(row=current,name=name,detail=detail))
def composition(doc):
    output=Image.new('RGBA',(960,640))
    for layer in doc['layers']:
        assert layer['opacity']==1
        if layer['visible']:output=Image.alpha_composite(output,Image.fromarray(decode(layer)))
    return np.asarray(output)
for row in rows:
    current=row['id'];folder=folder_for(row);doc=lambda label:read(folder/(label+'.retropaint'));image=lambda label:rgba(folder/(label+'.png'));fixture=root/row['fixture'];assert hashlib.sha256(fixture.read_bytes()).hexdigest()==row['fixture_sha256'];original=read(fixture);before=doc('before');hole=doc('hole');retry=doc('retry');target=next(i for i,l in enumerate(original['layers']) if l['id']==row['target_layer_id']);expected=deepcopy(original)
    if row['hidden_target']:expected['layers'][target]['visible']=False
    assert before==expected,'Recorded before source differs from declared fixture/hidden preparation';source=decode(before['layers'][target]);pixels=decode(hole['layers'][target]);expected=deepcopy(before);expected['layers'][target]['image']=hole['layers'][target]['image'];expected['layers'][target]['visible']=True;require(hole==expected,'Only target source and explicit target reveal may change');expected=deepcopy(hole);expected['layers'][target]['image']=retry['layers'][target]['image'];require(retry==expected,'Independent next mark changes only its active source')
    points=row['points'];distance=np.hypot(xx+.5-points[0][0],yy+.5-points[0][1]) if len(points)==1 else distances([points[0],points[-1]],xx.ravel(),yy.ravel()).reshape(640,960);changed=np.any(pixels!=source,axis=2);outside=distance>plan['footprint_radius']+plan['footprint_padding'];require(changed.any(),'Black Hole actually changes painted material');require(not changed[outside].any(),'No raw source change outside declared path/tool footprint',int(changed[outside].sum()))
    final=points[-1];end_distance=np.hypot(xx+.5-final[0],yy+.5-final[1]);end_changed=int(changed[end_distance<10].sum())
    if row['kind']!='transparent-border':require(end_changed>0,'Held effect follows the final pointer footprint',end_changed)
    stop_labels=['stop-first-public','stop-stable-1-public','stop-stable-2-public','cleanup-public'];stopped=[image(label) for label in stop_labels];deltas=[int(np.any(stopped[i]!=stopped[0],axis=2).sum()) for i in range(1,4)];saved_delta=int(np.any(image('hole')!=stopped[0],axis=2).sum());require(all(delta==0 for delta in deltas) and saved_delta==0,'Release/cancel acknowledgement freezes effect through recovery/save',dict(post_ack_changed_pixels=deltas,saved_vs_ack_changed_pixels=saved_delta))
    held_progress=int(np.any(image('effect-first-held-public')!=image('effect-late-held-public'),axis=2).sum())
    if row['kind']!='transparent-border':require(held_progress>0,'Real held frames show visible local effect progress',held_progress)
    if row['scope']=='paper':require(ImageColor.getrgb(hole['layers'][target]['paper'])==(255,255,255) and (pixels[:,:,3]==255).all(),'Defined Paper remains White and opaque');cleared=(pixels[:,:,:3]==255).all(axis=2)&np.any(source[:,:,:3]!=255,axis=2)
    else:
        assert before['layers'][target]['paper'] is None and not source[:,:,1].any();opaque_black=(pixels[:,:,3]==255)&(pixels[:,:,:3]==0).all(axis=2);green_channel=int((pixels[:,:,1]>0).sum());require(not opaque_black.any(),'Clear-sheet erasing never injects opaque Black',int(opaque_black.sum()));require(green_channel==0,'Clear-sheet erasing creates no non-source Green/White pigment',green_channel);centre=(int(final[1]),int(final[0]));require(pixels[centre][3]==0,'Clear-sheet hole centre removes alpha rather than painting a matte',pixels[centre].tolist());require(np.array_equal(image('hole')[centre],[67,160,71,255]),'Clear hole centre reveals unchanged original Green guide',image('hole')[centre].tolist());cleared=(pixels[:,:,3]==0)&(source[:,:,3]>0)
    if row['kind']!='transparent-border':require((cleared&(end_distance<10)).any(),'Last footprint contains actual clearing, not only a stale first-centre action')
    for label in ['before','hole','retry']:
        error=int(np.abs(composition(doc(label)).astype(int)-image(label).astype(int)).max());require(error<=1,'Independent complete layer composition '+label,error)
    require(doc('hole-undone')==before and np.array_equal(image('hole-undone'),image('before')),'Whole-effect Undo restores complete source/RGBA including original visibility');require(doc('hole-redone')==hole and np.array_equal(image('hole-redone'),image('hole')),'Whole-effect Redo complete source/RGBA exact');require(doc('retry-undone')==hole and np.array_equal(image('retry-undone'),image('hole')),'Next gesture is an independent Undo action');require(doc('retry-redone')==retry and np.array_equal(image('retry-redone'),image('retry')),'Next gesture Redo exact');require(doc('fresh/reopened')==retry and np.array_equal(image('fresh/reopened'),image('retry')),'Actual fresh project input complete source/RGBA exact')
    mark=decode(retry['layers'][target]);mark_changed=np.any(mark!=pixels,axis=2);retry_distance=distances([plan['retry_points'][0],plan['retry_points'][-1]],xx.ravel(),yy.ravel()).reshape(640,960);require(mark_changed.any() and not mark_changed[retry_distance>13].any(),'Next mark starts locally without a false line from the effect');require(np.array_equal(mark[420,750],[229,57,53,255]),'Next actual Marker gesture remains usable and paints selected Red',mark[420,750].tolist())
    events=read(folder/'native-input.json');life=read(folder/'native-lifecycle.json');assert all(e['trusted'] for e in events) and all(e['trusted'] for e in life);effect=[e for e in events if e['phase']=='effect'];downs=[e for e in effect if e['type']=='pointerdown'];moves=[e for e in effect if e['type']=='pointermove' and e['buttons']];assert len(downs)==1 and len(moves)==len(points)-1 and np.linalg.norm(np.array(downs[0]['source'])-points[0])<.001
    for e,p in zip(moves,points[1:]):assert np.linalg.norm(np.array(e['source'])-p)<.001
    if row['mode']=='touch-cancel':assert downs[0]['pointerType']=='touch' and len([e for e in effect if e['type']=='pointercancel' and e['pointerType']=='touch'])==1
    else:assert downs[0]['pointerType']=='mouse' and len([e for e in effect if e['type']=='pointerup'])==1
    if row['mode']=='blur-cancel':assert any(e['type']=='blur' and e['trusted'] and e['timeStamp']>downs[0]['timeStamp'] for e in life)
    retry_inputs=[e for e in events if e['phase']=='retry'];retry_down=[e for e in retry_inputs if e['type']=='pointerdown'];retry_moves=[e for e in retry_inputs if e['type']=='pointermove' and e['buttons']];assert len(retry_down)==1 and len(retry_moves)==16 and np.linalg.norm(np.array(retry_down[0]['source'])-plan['retry_points'][0])<.001
    for e,p in zip(retry_moves,plan['retry_points'][1:]):assert np.linalg.norm(np.array(e['source'])-p)<.001
    stop_event=next(e for e in read(folder/'events.json') if e['action']=='native-Black-Hole-stop');assert stop_event['mode']==row['mode'] and stop_event['original_points']==points
    if row['mode']!='moving-release':assert stop_event['actual_pre_stop_elapsed_ms']<500
    for file in [folder/'events.json',folder/'fresh/events.json']:
        for event in read(file):
            if event['action']=='download':data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
    records.append(dict(id=current,folder=str(folder.relative_to(root)),scope=row['scope'],mode=row['mode'],kind=row['kind'],viewport=row['viewport'],actual_pre_stop_elapsed_ms=stop_event['actual_pre_stop_elapsed_ms'],changed_target_pixels=int(changed.sum()),changed_outside_footprint=int(changed[outside].sum()),changed_at_last_footprint=end_changed,post_ack_changed_pixels=deltas,saved_vs_ack_changed_pixels=saved_delta,held_progress_pixels=held_progress,actual_new_mark_pixels=int(mark_changed.sum())))
assert len(downloads)==16*len(rows)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-015',status='Fail' if failures else 'Completed prefix only' if args.prefix else 'Pass',rows=records,actual_downloads_verified=len(downloads),failures=failures,oracle=plan['oracle'],scope='Completed prefix only; no case Pass.' if args.prefix else 'All40 native workflows/640 actual downloads: opaque Paper/clear-sheet main release/movement/touchCancel/native-blur, transparent borders and hidden targets, complete separate effect/next-mark history and actual fresh input. Original setup interruption retained.')
(root/('evidence/PAINT-015-'+args.folder+('-prefix' if args.prefix else '-independent')+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-015',status=report['status'],rows=len(rows),actual_downloads=len(downloads),failed_requirements=len(failures),failure_names=sorted(set(f['name'] for f in failures)))))
if failures and not args.observe:raise SystemExit(1)
