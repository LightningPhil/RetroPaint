"""Software fast-curve evidence is never physical pen certification."""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import distances,components
import json,hashlib,base64,io,argparse,numpy as np
root=Path(__file__).resolve().parent;parser=argparse.ArgumentParser();parser.add_argument('--folder',default='PAINT-020-software');parser.add_argument('--prefix',action='store_true');parser.add_argument('--observe',action='store_true');args=parser.parse_args();base=root/'headless'/args.folder;read=lambda p:json.loads(p.read_text(encoding='utf-8'));plan=read(root/'fixtures/PAINT-020-plan.json');rgba=lambda p:np.asarray(Image.open(p).convert('RGBA'));decode=lambda l:rgba(io.BytesIO(base64.b64decode(l['image'].split(',',1)[1])));records=[];downloads=[];failures=[]
rows=[r for r in plan['rows'] if (base/r['id']/'native-input.json').exists() and (base/r['id']/'fresh/events.json').exists() and len([e for e in read(base/r['id']/'fresh/events.json') if e['action']=='download'])==2];assert rows and (args.prefix or len(rows)==32)
if not args.prefix:
    ui=read(base/'PAINT-020-ui.json');assert ui['status']=='Software UI complete; physical pen unavailable' and not ui['errors'] and [r['id'] for r in ui['rows']]==[r['id'] for r in plan['rows']];assert hashlib.sha256((base/'executed-harness.mjs').read_bytes()).hexdigest()==ui['harness_sha256']
def require(ok,name,detail=None):
    if not bool(ok):failures.append(dict(row=current,name=name,detail=detail))
for row in rows:
    current=row['id'];folder=base/current;doc=lambda label:read(folder/(label+'.retropaint'));image=lambda label:rgba(folder/(label+'.png'));before=doc('before');after=doc('loop');assert before['width']==960 and before['height']==640 and before['drawingMode']=='raster' and len(before['layers'])==1;source=decode(before['layers'][0]);assert (source==255).all();pixels=decode(after['layers'][0]);expected=deepcopy(before);expected['layers'][0]['image']=after['layers'][0]['image'];require(after==expected,'Scale/layer/document fields unchanged by pointer/pressure/load/API capability');require((pixels[:,:,3]==255).all(),'Opaque Paper alpha unchanged');mask=np.any(pixels!=source,axis=2);ys,xs=np.where(mask);assert len(xs)>0;distance=distances(plan['points'],xs,ys);require(distance.max()<=24,'Saved loop is local to the declared source path',float(distance.max()));require(components(mask)==1,'Saved loop is one continuous connected mark',components(mask));missing=[]
    for x,y in plan['points']:
        x=int(round(x));y=int(round(y))
        if not mask[y-2:y+3,x-2:x+3].any():missing.append([x,y])
    require(not missing,'No missing centreline sample in saved fast loop',missing);require(np.array_equal(pixels[350,590],[229,57,53,255]),'Full-strength Red Marker core retains exact chosen pigment',pixels[350,590].tolist())
    for label in ['before','loop','undone','redone','fresh/reopened']:require(np.array_equal(image(label),decode(doc(label)['layers'][0])),'Actual PNG equals independently decoded raw source '+label)
    require(np.array_equal(rgba(folder/'loop-public.png'),image('loop')),'Committed PNG matches public post-gesture frame')
    for label,wanted,ref in [('undone',before,'before'),('redone',after,'loop'),('fresh/reopened',after,'loop')]:require(doc(label)==wanted and np.array_equal(image(label),image(ref)),'Whole-gesture complete history/fresh source '+label)
    events=read(folder/'native-input.json');assert all(e['trusted'] for e in events);down=[e for e in events if e['type']=='pointerdown'];up=[e for e in events if e['type']=='pointerup'];moves=[e for e in events if e['type']=='pointermove' and e['buttons']];assert len(down)==len(up)==1 and len(moves)==96 and all(e['pointerType']==('mouse' if row['device']=='mouse' else 'pen') for e in down+moves+up)
    for e,p in zip(down+moves,plan['points']):assert np.linalg.norm(np.array(e['source'])-p)<.01
    samples=[s for e in moves for s in (e['coalesced'] or [])];intermediate=[s for e in moves for s in (e['coalesced'] or []) if np.linalg.norm(np.array(s['source'])-e['source'])>.01]
    if row['api']=='absent-fallback':assert all(e['coalesced'] is None for e in events)
    else:assert all(isinstance(e['coalesced'],list) for e in events)
    for s in samples:
        assert s['trusted'];x,y=[int(round(n)) for n in s['source']];require(mask[max(0,y-2):y+3,max(0,x-2):x+3].any(),'Observed coalesced sample footprint appears in saved loop',s)
    pressure=[e['pressure'] for e in down+moves]
    if row['device']=='browser-emulated-pen':require(min(pressure)<.11 and max(pressure)>.89,'Chrome delivered the declared varied emulated pen pressures',[min(pressure),max(pressure)])
    load=read(folder/'native-load.json')
    if row['load']=='busy':require(len(load)>0 and all(e['end']-e['start']>=12 for e in load),'Real main-thread busy intervals occurred during gesture',len(load))
    else:assert not load
    for file in [folder/'events.json',folder/'fresh/events.json']:
        for e in read(file):
            if e['action']=='download':data=Path(e['path']).read_bytes();assert len(data)==e['bytes'] and hashlib.sha256(data).hexdigest()==e['sha256'];downloads.append(e)
    records.append(dict(id=current,viewport=row['viewport'],device=row['device'],api=row['api'],load=row['load'],changed_pixels=int(mask.sum()),components=components(mask),maximum_path_distance=float(distance.max()),coalesced_samples=len(samples),distinct_intermediate_samples=len(intermediate),pressure_range=[min(pressure),max(pressure)],actual_busy_intervals=len(load),actual_downloads=10,physical_pen_tested=False))
assert len(downloads)==10*len(rows)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-020',status='Fail' if failures else 'Completed software prefix only' if args.prefix else 'Partial',software_scope_passed=not failures and len(rows)==32,rows=records,actual_downloads_verified=len(downloads),failures=failures,oracle=plan['oracle'],blocker='No physical pen is available, per user. Browser-emulated pressure/source scale is software evidence only. Native sample footprints and supplementary coalesced component tests cannot certify physical sampling; no unobserved intermediate native sample is counted as executed.',scope='Completed software prefix; no case Pass.' if args.prefix else '32 software workflows/320 actual downloads. Physical mouse/pen hardware and physical pressure/coalescing remain unverified; case Partial.')
(root/('evidence/PAINT-020-'+args.folder+('-prefix' if args.prefix else '-independent')+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-020',status=report['status'],rows=len(rows),actual_downloads=len(downloads),failures=failures[:10])))
if failures and not args.observe:raise SystemExit(1)
