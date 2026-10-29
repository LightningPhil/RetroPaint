from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io,argparse,numpy as np
root=Path(__file__).resolve().parent;parser=argparse.ArgumentParser();parser.add_argument('--folder',default='INK-002-history');parser.add_argument('--continuation-folder');parser.add_argument('--prefix',action='store_true');parser.add_argument('--observe',action='store_true');args=parser.parse_args();base=root/'headless'/args.folder;following=root/'headless'/args.continuation_folder if args.continuation_folder else None;read=lambda p:json.loads(p.read_text(encoding='utf-8'));plan=read(root/'fixtures/INK-002-history-plan.json');assert hashlib.sha256((root/plan['parent_plan']).read_bytes()).hexdigest()==plan['parent_plan_sha256'];assert hashlib.sha256((root/plan['fixture']).read_bytes()).hexdigest()==plan['fixture_sha256'];rgba=lambda p:np.asarray(Image.open(p).convert('RGBA'));decode=lambda l:rgba(io.BytesIO(base64.b64decode(l['image'].split(',',1)[1])));yy,xx=np.mgrid[:640,:960];failures=[];records=[];downloads=[]
def folder_for(row):
    choices=[folder/row['id'] for folder in [base,following] if folder is not None and (folder/row['id']/'history-observations.json').exists() and (folder/row['id']/'fresh/events.json').exists() and len([e for e in read(folder/row['id']/'fresh/events.json') if e['action']=='download'])==2];assert len(choices)<=1;return choices[0] if choices else None
rows=[r for r in plan['rows'] if folder_for(r) is not None];assert rows and (args.prefix or len(rows)==4)
if not args.prefix:
    ui=read(base/'INK-002-ui.json');assert ui['history_probe'] and not ui['errors'];assert hashlib.sha256((base/'executed-harness.mjs').read_bytes()).hexdigest()==ui['harness_sha256'];executed=ui['rows']
    if following:
        next_ui=read(following/'INK-002-ui.json');assert ui['status']=='Fail' and len(ui['rows'])==3 and "'' !== 'view'" in ui['error'] and next_ui['status']=='Pass' and next_ui['history_probe'] and not next_ui['errors'] and len(next_ui['rows'])==1 and next_ui['origin']==ui['origin'];assert hashlib.sha256((following/'executed-harness.mjs').read_bytes()).hexdigest()==next_ui['harness_sha256'];executed+=next_ui['rows']
    else:assert ui['status']=='Pass'
    assert [r['id'] for r in executed]==[r['id'] for r in plan['rows']]
def require(ok,name,detail=None):
    if not bool(ok):failures.append(dict(row=current,name=name,detail=detail))
for row in rows:
    current=row['id'];folder=folder_for(row);doc=lambda label:read(folder/(label+'.retropaint'));image=lambda label:rgba(folder/(label+'.png'));previous=doc('prepared');target=next(i for i,l in enumerate(previous['layers']) if l['id']==previous['active']);assert len(previous['layers'])==5 and previous['layers'][target]['name']=='Borrowed swatches' and not decode(previous['layers'][target])[:,:,3].any();assert read(folder/'history-observations.json')==plan['scenarios'];native=read(folder/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in native);checks=[]
    for scenario in plan['scenarios']:
        current=row['id']+'/'+scenario['id'];label=scenario['id'];before=doc(label+'-before-control');control=doc(label+'-control');expected=deepcopy(previous)
        if scenario['hide_character']:next(l for l in expected['layers'] if l['name']=='Character')['visible']=False
        require(before==expected,'Only declared hidden state/previous control marks before next probe');source=decode(before['layers'][target]);paint=decode(control['layers'][target]);expected=deepcopy(before);expected['layers'][target]['image']=control['layers'][target]['image'];require(control==expected,'Known control mark changes only clear target source');changed=np.any(source!=paint,axis=2);x,y=scenario['control_point'];distance=np.hypot(xx+.5-x,yy+.5-y);require(changed.any() and not changed[distance>13].any(),'Known control mark exists locally before sampling',int(changed.sum()));require(np.array_equal(paint[int(y),int(x)],[229,57,53,255]),'Known control core is actual selected Red');require(np.array_equal(rgba(folder/(label+'-sampled-public.png')),image(label+'-control')),'Sampling does not change known control frame');undone=doc(label+'-control-undone');redone=doc(label+'-control-redone');require(undone==before and np.array_equal(image(label+'-control-undone'),image(label+'-before-control')),'Single Undo after sampling removes the preceding real mark,not an empty sampling step');require(redone==control and np.array_equal(image(label+'-control-redone'),image(label+'-control')),'Redo after sampling restores exact control source/RGBA');
        for phase,point in [('control',scenario['control_point']),('sample',scenario['sample'])]:
            inputs=[e for e in native if e['phase']==label+'-'+phase];down=[e for e in inputs if e['type']=='pointerdown'];up=[e for e in inputs if e['type']=='pointerup'];assert len(down)==len(up)==1 and np.linalg.norm(np.array(down[0]['source'])-point)<.01
        checks.append(dict(id=label,control_changed_pixels=int(changed.sum()),sample_adds_no_history_entry=undone==before,control_redo_exact=redone==control));previous=control
    reopened=doc('fresh/reopened');expected=deepcopy(previous);assert 'clip' not in expected['layers'][2]['live']['strokes'][0] and reopened['layers'][2]['live']['strokes'][0]['clip'] is None;expected['layers'][2]['live']['strokes'][0]['clip']=None;require(reopened==expected and np.array_equal(image('fresh/reopened'),image('hidden-character-control')),'Actual fresh control file complete source/RGBA exact with documented no-clip default only')
    for file in [folder/'events.json',folder/'fresh/events.json']:
        for e in read(file):
            if e['action']=='download':data=Path(e['path']).read_bytes();assert len(data)==e['bytes'] and hashlib.sha256(data).hexdigest()==e['sha256'];downloads.append(e)
    records.append(dict(id=row['id'],viewport=row['viewport'],probes=checks,actual_downloads=28,representation_change=dict(path='$.layers[2].live.strokes[0].clip',before_present=False,after_present=True,after=None)))
assert len(downloads)==28*len(rows)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='INK-002',status='Fail' if failures else 'Completed prefix only' if args.prefix else 'Pass',rows=records,actual_downloads_verified=len(downloads),actual_history_probes=3*len(rows),failures=failures,oracle=plan['oracle'],scope='Separate explicit no-op-history proof; main visible RGB/magnifier scope remains in its own report. No case Pass inferred from this alone.')
(root/('evidence/INK-002-'+args.folder+('-prefix' if args.prefix else '-independent')+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='INK-002-history',status=report['status'],rows=len(rows),actual_downloads=len(downloads),failures=failures[:10])))
if failures and not args.observe:raise SystemExit(1)
