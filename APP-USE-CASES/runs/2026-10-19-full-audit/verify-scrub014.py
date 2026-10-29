"""Independent opaque-Paper/destination-out, target, source/history oracle."""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image,ImageColor
from paint_oracle import distances
import numpy as np
import json,hashlib,base64,io,argparse
root=Path(__file__).resolve().parent;parser=argparse.ArgumentParser();parser.add_argument('--folder',default='PAINT-014-before');parser.add_argument('--continuation-folder');parser.add_argument('--prefix',action='store_true');parser.add_argument('--observe',action='store_true');args=parser.parse_args();base=root/'headless'/args.folder;following=root/'headless'/args.continuation_folder if args.continuation_folder else None
read=lambda p:json.loads(p.read_text(encoding='utf-8'));rgba=lambda p:np.asarray(Image.open(p).convert('RGBA'));decode=lambda layer:rgba(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1])));plan=read(root/'fixtures/PAINT-014-plan.json');fixture=root/plan['fixture'];assert hashlib.sha256(fixture.read_bytes()).hexdigest()==plan['fixture_sha256'];original=read(fixture);yy,xx=np.mgrid[:640,:960];downloads=[];records=[];failures=[]
chain=read(root/'evidence/SCRUB-native-composite-chain-verification.json');assert chain['status']=='Pass' and chain['invalid_integer_transitions']==0
def ready(folder):return (folder/'native-input.json').exists() and (folder/'fresh/events.json').exists() and len([e for e in read(folder/'fresh/events.json') if e['action']=='download'])==2
def folder_for(row):
    choices=[folder/row['id'] for folder in [base,following] if folder is not None and ready(folder/row['id'])];assert len(choices)<=1;return choices[0] if choices else None
rows=[r for r in plan['rows'] if folder_for(r) is not None];assert rows and (args.prefix or len(rows)==40),('Incomplete execution',len(rows))
if not args.prefix:
    ui=read(base/'PAINT-014-ui.json');assert not ui['errors']
    if following:
        next_ui=read(following/'PAINT-014-ui.json');assert ui['status']=='Fail' and 'Hide Backdrop' in ui['error'] and len(ui['rows'])==3 and next_ui['status']=='Pass' and not next_ui['errors'];executed=ui['rows']+next_ui['rows']
    else:assert ui['status']=='Pass';executed=ui['rows']
    assert [r['id'] for r in executed]==[r['id'] for r in plan['rows']]
def require(ok,name,detail=None):
    if not bool(ok):failures.append(dict(row=current,name=name,detail=detail))
for row in rows:
    current=row['id'];folder=folder_for(row);doc=lambda name:read(folder/(name+'.retropaint'));image=lambda name:rgba(folder/(name+'.png'));before=doc('before');after=doc('after');target=0 if row['target']=='Paper' else 2;expected=deepcopy(original);expected['active']=expected['layers'][target]['id']
    if row['isolate_Paper']:
        for layer in expected['layers'][1:]:layer['visible']=False
    if row['hidden_target']:expected['layers'][target]['visible']=False
    assert before==expected,'Before state differs from declared fixture and actual layer/eye preparation';require(ImageColor.getrgb(before['layers'][0]['paper'])==(255,255,255),'Original Paper remains defined White')
    source=decode(before['layers'][target]);pixels=decode(after['layers'][target]);public=image('after');expected=deepcopy(before);expected['layers'][target]['image']=after['layers'][target]['image'];expected['layers'][target]['visible']=True;require(after==expected,'Only working source and explicit hidden-target reveal may change')
    inputs=read(folder/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' and e['type']!='pointercancel' for e in inputs);downs=[e for e in inputs if e['type']=='pointerdown'];ups=[e for e in inputs if e['type']=='pointerup'];moves=[e for e in inputs if e['type']=='pointermove' and e['buttons']];assert len(downs)==len(ups)==1 and len(moves)==len(row['points'])-1;assert np.linalg.norm(np.array(downs[0]['source'])-row['points'][0])<.001 and np.linalg.norm(np.array(ups[0]['source'])-row['points'][-1])<.001
    for e,p in zip(moves,row['points'][1:]):assert np.linalg.norm(np.array(e['source'])-p)<.001
    radius=plan['radius_by_size'][str(row['size'])];points=row['points'];distance=np.hypot(xx+.5-points[0][0],yy+.5-points[0][1]) if len(points)==1 else distances([points[0],points[-1]],xx.ravel(),yy.ravel()).reshape(640,960);outside=distance>radius+2;changed=np.any(pixels!=source,axis=2);require(changed.any(),'Actual Scrub changes the target paint');require(not changed[outside].any(),'All raw source pixels beyond calibrated cursor radius plus2 remain exact',int(changed[outside].sum()));require(np.array_equal(public,image('released-public')),'Actual saved PNG and released public canvas exact')
    core=(distance<radius-1)&(source[:,:,3]>0);maximum_error=0;colour_error=0
    if target==0:
        require((pixels[:,:,3]==255).all(),'Paper alpha remains fully opaque');require(np.all(pixels[:,:,:3]>=source[:,:,:3]),'White erasing never darkens source pigment');require(np.array_equal(public,pixels),'Isolated Paper PNG/public view equals its actual raw RGBA')
        delta=(pixels[:,:,:3].astype(float)-source[:,:,:3]);vector=255-source[:,:,:3].astype(float);denom=np.sum(vector*vector,axis=2);affected=changed&(denom>0);weights=np.sum(delta*vector,axis=2)[affected]/denom[affected]
        if row['kind']=='tap-boundary':require(weights.max()<=row['strength']+2/255 and weights.min()>0,'One-tap opaque Paper contribution is coverage weighted and bounded by chosen Strength',dict(minimum=float(weights.min()),maximum=float(weights.max())))
        if core.any():
            wanted=np.rint(source[core,:3].astype(float)+row['strength']*(255-source[core,:3].astype(float)));error=np.abs(pixels[core,:3].astype(int)-wanted);maximum_error=int(error.max());require(maximum_error<=1,'Paper core independently erases towards its defined colour at chosen Strength',maximum_error)
            if row['strength']==1:require((pixels[core,:3]==255).all(),'Full Paper core is exact defined White')
    else:
        require(np.all(pixels[:,:,3]<=source[:,:,3]),'Transparent-sheet erasing never adds opacity');clear=source[:,:,3]==0;require(np.array_equal(pixels[clear],source[clear]),'Original clear RGBA remains exact');require((pixels[pixels[:,:,3]==0]==0).all(),'Fully cleared source contains no visible/hidden colour residue')
        remaining=pixels[:,:,3]>0;associated=np.abs((pixels[:,:,:3].astype(float)-source[:,:,:3].astype(float))*pixels[:,:,3,None]/255);colour_error=float(associated[remaining].max())
        if row['kind']=='main-scrub':
            proof=next(r for r in chain['rows'] if r['id']==current);require(proof['all_shared_factor_integer_transitions_valid'] and proof['no_unobserved_source_change_between_operations'] and proof['final_full_document_and_raw_RGBA_and_actual_PNG_exact_to_original_uninstrumented'] and hashlib.sha256(pixels.tobytes()).hexdigest()==proof['untraced_after_source_RGBA_sha256'],'Every repeated native pigment contribution satisfies exact integer-chain law and matches uninstrumented source')
        else:require(colour_error<=1,'Remaining one-tap pigment preserves associated colour within calibrated native1 byte',colour_error)
        opaque_enough=pixels[:,:,3]>=128;straight_error=int(np.abs(pixels[opaque_enough,:3].astype(int)-source[opaque_enough,:3].astype(int)).max()) if opaque_enough.any() else 0;require(straight_error<=2,'Remaining alpha>=128 pigment retains straight RGB within2 native bytes',straight_error)
        if row['kind']!='main-scrub':
            nonzero=source[:,:,3]>0;weight=1-pixels[nonzero,3].astype(float)/source[nonzero,3];require(weight.max()<=row['strength']+2/255,'One-tap destination-out contribution is bounded by selected Strength',float(weight.max()))
        if core.any():
            wanted=np.rint(source[core,3].astype(float)*(1-row['strength']));error=np.abs(pixels[core,3].astype(int)-wanted);maximum_error=int(error.max());require(maximum_error<=1,'Transparent core independently erases alpha at chosen Strength',maximum_error)
            if row['strength']==1:require((pixels[core]==0).all(),'Full transparent core is exact zero RGBA')
        roi=(slice(95,186),slice(95,206));blue=np.array([30,136,229],float);composition_errors=[]
        for name,layer_pixels,visible in [('before',source,before['layers'][2]['visible']),('after',pixels,True)]:
            a=layer_pixels[roi][:,:,3:4].astype(float)/255*.5*visible;wanted=np.rint(layer_pixels[roi][:,:,:3]*a+blue*(1-a));error=int(np.abs(image(name)[roi][:,:,:3].astype(int)-wanted).max());require(error<=1,'Independent Character0.5/Blue composition '+name,error);composition_errors.append(error)
        if row['strength']==1 and row['size']>4:require(np.array_equal(public[140,150],[30,136,229,255]),'Cleared Character centre exposes exact original Blue neighbour')
    undone=doc('undone');undo_image=image('undone');diagnostic=None
    if row['hidden_target']:
        without_visibility=deepcopy(undone);without_visibility['layers'][target]['visible']=before['layers'][target]['visible'];diagnostic=dict(expected_original_visible=before['layers'][target]['visible'],actual_undone_visible=undone['layers'][target]['visible'],all_other_undone_source_data_exact=without_visibility==before)
    require(undone==before and np.array_equal(undo_image,image('before')),'Whole-gesture Undo restores exact original source/RGBA including visibility',diagnostic);require(doc('redone')==after and np.array_equal(image('redone'),public),'Whole-gesture Redo complete source/RGBA exact');require(doc('fresh/reopened')==after and np.array_equal(image('fresh/reopened'),public),'Actual fresh project input complete source/RGBA exact')
    for file in [folder/'events.json',folder/'fresh/events.json']:
        for event in read(file):
            if event['action']=='download':data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
    records.append(dict(id=current,folder=str(folder.relative_to(root)),target=row['target'],kind=row['kind'],viewport=row['viewport'],size=row['size'],strength=row['strength'],calibrated_radius=radius,changed_source_pixels=int(changed.sum()),changed_outside_radius_plus2=int(changed[outside].sum()),core_pixels=int(core.sum()),maximum_independent_core_error=maximum_error,maximum_associated_pigment_error=colour_error,hidden_Undo_diagnostic=diagnostic))
assert len(downloads)==10*len(rows)
report=dict(at=datetime.now(timezone.utc).isoformat(),case='PAINT-014',status='Fail' if failures else 'Completed prefix only' if args.prefix else 'Pass',rows=records,actual_downloads_verified=len(downloads),failures=failures,oracle=plan['oracle'],calibration='evidence/ERASER-independent-calibration.json',scope='Completed prefix only; no case Pass.' if args.prefix else 'All40 native workflows/400 actual downloads,28 opaque-Paper/clear-sheet boundary taps,8 main sweeps and4 hidden-target/source/history negatives. Initial plan and native interruptions retained.')
target=root/('evidence/PAINT-014-'+args.folder+('-prefix' if args.prefix else '-independent')+'.json');target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-014',status=report['status'],rows=len(rows),actual_downloads=len(downloads),failed_requirements=len(failures),failure_names=sorted(set(f['name'] for f in failures)))))
if failures and not args.observe:raise SystemExit(1)
