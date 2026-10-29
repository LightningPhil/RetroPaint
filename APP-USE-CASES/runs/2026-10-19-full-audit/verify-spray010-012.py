"""Independent spray observations; no application painter or serializer imports."""
from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import distances
import numpy as np
import json,base64,io,hashlib,sys

root=Path(__file__).resolve().parent
read_json=lambda p:json.loads(p.read_text(encoding='utf-8'))
kind=sys.argv[sys.argv.index('--kind')+1] if '--kind' in sys.argv else 'mist'
case={'mist':'PAINT-010','splatter':'PAINT-011','confetti':'PAINT-012'}[kind]
plan=read_json(root/('fixtures/'+case+'-plan.json'))
positive=root/('headless/SPRAY-foreground/mist' if kind=='mist' else 'headless/SPRAY-supported/'+kind)
cancel=root/('headless/SPRAY-supported/'+kind)
ui=read_json(positive/(case+'-ui.json'))
assert not ui['errors'] and len(ui['rows'])==12
if kind=='mist':assert ui['status']=='Fail' and 'Timeout 5000ms' in ui['error'] and '39:105' in ui['error'], 'Retained initial failure is not the known tab-visibility capability failure'
else:assert ui['status']=='Partial' and ui['supported_workflows_completed']
downloads=[];frames_verified=[];rows=[];cancellations=[];geometry_only='--geometry-only' in sys.argv
trace_checks=[]
if not geometry_only:
    probe=read_json(root/'headless/SPRAY-color-probe/report.json');assert probe['ideal_two_channel_tolerance_is_invalid_for_repeated_native_8bit_compositing'] and any(r['maximum_ideal_line_error']>5 for r in probe['rows'])
    global_probe=read_json(root/'headless/SPRAY-color-probe-global-alpha/report.json');assert global_probe['global_alpha'] and any(r['maximum_endpoint_overshoot']>10 for r in global_probe['rows']),'A channel endpoint is not a valid multi-pass native8-bit bound either'
    traces=read_json(root/'headless/SPRAY-pigment-trace/report.json');assert traces['status']=='Pass' and not traces['errors'] and len(traces['rows'])==36
    for row in [r for r in traces['rows'] if r['applicator']==kind]:
        planned=next(r for r in plan['rows'] if r['id']==row['id']);assert all(row[k]==v for k,v in planned.items()) and row['actual_size']==planned['size'] and row['actual_strength']==planned['strength'];deposits=read_json(root/row['trace']);assert len(deposits)==row['native_deposit_count'] and len(deposits)>0
        red=[d for d in deposits if d['phase']=='red'];assert red
        for deposit in red:
            assert 0<deposit['alpha']<=planned['strength']+1e-9 and deposit['composition']=='source-over'
            if isinstance(deposit['style'],str):assert deposit['style']=='#e53935',('Wrong selected Red deposit',deposit)
            else:
                style=deposit['style'];assert style['kind']=='radial' and len(style['stops'])==3 and [[offset,colour.lower()] for offset,colour in style['stops']]==[[0,'#e53935'],[.4,'#e53935'],[1,'rgba(229,57,53,0)']],('Wrong Red gradient pigment',style)
        if kind=='confetti':assert len({d['style'] for d in deposits if d['phase']=='rainbow' and isinstance(d['style'],str)})>=3
        trace_checks.append(dict(id=row['id'],viewport=row['viewport'],size=row['size'],strength=row['strength'],actual_Red_deposits=len(red),every_actual_native_pigment_and_composition_exact=True,trace=row['trace'],trace_sha256=hashlib.sha256((root/row['trace']).read_bytes()).hexdigest()))
    assert len(trace_checks)==12

def rgba(file):return np.asarray(Image.open(file).convert('RGBA'))
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
def unchanged_header(before,doc):
    expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected,'Non-raster source fields changed'
def known_red(previous,pixels):
    mask=(pixels!=previous).any(axis=2);assert mask.any(),'No deposited pigment'
    start=previous[mask,:3].astype(float);end=pixels[mask,:3].astype(float);ink=np.array([229,57,53]);vector=ink-start;change=end-start;denom=np.sum(vector*vector,axis=1);valid=denom>0;alpha=np.zeros(len(start));alpha[valid]=np.sum(change[valid]*vector[valid],axis=1)/denom[valid];error=np.abs(end-(start+alpha[:,None]*vector));maximum=float(error.max())
    # The original ideal-line assertion failed and remains retained. The native
    # calibration disproves that model for repeated quantized composites. Check
    # every actual pigment/gradient stop in a complete observational matrix must
    # match the known palette value. A separate globalAlpha calibration also
    # disproves the attempted one-step endpoint envelope, which stays retained.
    overshoot=float(np.maximum(np.minimum(start,ink)-end,end-np.maximum(start,ink)).max())
    return dict(changed_pixels=int(mask.sum()),ideal_line_error_diagnostic_only=maximum,ideal_endpoint_overshoot_diagnostic_only=overshoot,actual_pigment_trace_verified=not geometry_only)
def component_areas(mask):
    # Run-length union find, independent eight-neighbour raster components.
    parent=[];weight=[];previous=[]
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for line in mask:
        edges=np.diff(np.pad(line.astype(np.int8),1));starts=np.flatnonzero(edges==1);ends=np.flatnonzero(edges==-1);current=[]
        for start,end in zip(starts,ends):
            neighbours={find(label) for left,right,label in previous if start<=right and end>=left}
            if neighbours:
                label=min(neighbours)
                for other in neighbours-{label}:parent[other]=label;weight[label]+=weight[other];weight[other]=0
                weight[label]+=int(end-start)
            else:label=len(parent);parent.append(label);weight.append(int(end-start))
            current.append((start,end,label))
        previous=current
    return [weight[i] for i in range(len(parent)) if parent[i]==i]
def files(location):
    for file in [location/'events.json',location/'fresh/events.json']:
        events=read_json(file);states=[e['visibility'] for e in events if e['action']=='headless-foreground-ready'];assert len(states)==1 and states[0]['visibility']=='visible' and not states[0]['hidden']
        for event in events:
            if event['action']=='download':
                data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256'];downloads.append(event)
def public(location,label,held=True):
    released=rgba(location/(label+'-released-public.png'));stopped=rgba(location/(label+'-stopped-public.png'));assert np.array_equal(released,stopped),(kind,location.name,label,'Paint continues after release/cancellation acknowledgement')
    held_changed=None
    if held:
        first=rgba(location/(label+'-first-held-public.png'));late=rgba(location/(label+'-late-held-public.png'));held_changed=int((first!=late).any(axis=2).sum());assert held_changed>0,(kind,location.name,label,'Stationary hold did not deposit further pigment')
    for suffix in (['first-held-public','late-held-public'] if held else [])+['released-public','stopped-public']:
        file=location/(label+'-'+suffix+'.png');frames_verified.append(dict(path=str(file.relative_to(root)),sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    return dict(stopped_after_acknowledgement_and_250ms_exact=True,additional_held_pixels=held_changed)
def hue_bins(pixels):
    rgb=pixels[:,:,:3].astype(float);mx=rgb.max(axis=2);mn=rgb.min(axis=2);d=mx-mn;chromatic=d>25;h=np.zeros(mx.shape)
    for ch,offset in [(0,0),(1,2),(2,4)]:
        mask=(rgb[:,:,ch]==mx)&chromatic
        h[mask]=((rgb[:,:,(ch+1)%3]-rgb[:,:,(ch+2)%3])[mask]/d[mask]+offset)%6
    return sorted(set(np.floor(h[chromatic]).astype(int).tolist()))

for row,planned in zip(ui['rows'],plan['rows']):
    assert all(row[k]==v for k,v in planned.items());location=positive/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:rgba(location/(label+'.png'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and (blank==255).all() and len(before['layers'])==1 and before['drawingMode']=='raster'
    labels=['stationary']+(['long'] if row['long_hold'] else [])+['moving','edge']+(['solid'] if kind=='confetti' else []);assert row['labels']==labels;previous=blank;metrics={};radius=plan['footprint']['radius_factor']*row['size']+plan['footprint']['radius_padding'];inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs)
    for index,label in enumerate(labels):
        doc=read(label);unchanged_header(before,doc);pixels=image(label);assert np.array_equal(pixels,decoded(doc)) and (pixels[:,:,3]==255).all();mask=(pixels!=previous).any(axis=2);ys,xs=np.where(mask);assert len(xs)>0
        source=row['edge'] if label=='edge' else [480,320];distance=distances([[320,320],[640,320]],xs,ys) if label=='moving' else np.hypot(xs+.5-source[0],ys+.5-source[1]);assert distance.max()<=radius,(kind,row['id'],label,'Outside declared spray footprint',float(distance.max()),radius)
        state=public(location,label,label!='moving');assert np.array_equal(pixels,rgba(location/(label+'-released-public.png'))),'Actual exported picture disagrees with the settled public paint canvas'
        downs=[e for e in inputs if e['phase']==label and e['type']=='pointerdown'];ups=[e for e in inputs if e['phase']==label and e['type']=='pointerup'];assert len(downs)==len(ups)==1
        if label!='moving':
            assert np.linalg.norm(np.array(downs[0]['source'])-source)<.001
            assert not [e for e in inputs if e['phase']==label and e['type']=='pointermove' and e['buttons']],'Stationary gesture actually moved while held'
        else:
            moves=[e for e in inputs if e['phase']==label and e['type']=='pointermove' and e['buttons']];assert len(moves)==40 and np.linalg.norm(np.array(downs[0]['source'])-[320,320])<.001
            assert max(np.linalg.norm(np.array(e['source'])-[328+8*i,320]) for i,e in enumerate(moves))<.001
        if label=='edge':
            if source[0]<1:edge=mask[:,0];opposite=mask[:,-2:]
            elif source[0]>959:edge=mask[:,-1];opposite=mask[:,:2]
            elif source[1]<1:edge=mask[0,:];opposite=mask[-2:,:]
            else:edge=mask[-1,:];opposite=mask[:2,:]
            assert edge.any() and not opposite.any(),(kind,row['id'],'No actual clipped boundary pixels, or opposite-edge wrapping')
        if kind!='confetti' or label=='solid':state['known_selected_Red']=known_red(previous,pixels)
        if kind=='confetti' and row['long_hold'] and label=='stationary':state['chromatic_hue_bins']=hue_bins(pixels);assert len(state['chromatic_hue_bins'])>=3,'Rainbow burst lacks several colours'
        if label=='stationary':state['radius90']=float(np.quantile(distance,.9));state['largest_drop_component']=max(component_areas(mask))
        if kind=='splatter' and row['long_hold'] and label=='stationary':assert state['largest_drop_component']>=30,'Splatter lacks a measurable drop character'
        assert read(label+'-undone')==read('before' if index==0 else labels[index-1]) and read(label+'-redone')==doc,'Complete random gesture history is not exact'
        metrics[label]=dict(**state,changed_pixels=len(xs),maximum_path_distance=float(distance.max()),boundary_clip_verified=label=='edge');previous=pixels
    if kind=='confetti':assert read('red-selected')==read('edge'),'Selecting solid Red changed existing Rainbow pixels/data'
    assert read('fresh/reopened')==read(labels[-1]) and np.array_equal(image('fresh/reopened'),previous),'Actual fresh project reopen changed the committed random arrangement'
    events=read_json(location/'events.json');held_events=[e for e in events if e['action']=='native-stationary-spray'];assert len(held_events)==len(labels)-1 and all(e['actual_hold_ms']>=e['minimum_hold_ms'] for e in held_events)
    files(location);rows.append(dict(id=row['id'],viewport=row['viewport'],size=row['size'],strength=row['strength'],gestures=metrics,source_dimensions_and_non_image_data_exact=True,all_history_and_fresh_source_RGBA_exact=True))

size_comparisons=[]
for viewport in [[1280,720],[320,568],[390,844],[844,390]]:
    small=next(r for r in rows if r['viewport']==viewport and r['size']==1);large=next(r for r in rows if r['viewport']==viewport and r['size']==96);ratio=large['gestures']['stationary']['radius90']/small['gestures']['stationary']['radius90'];assert ratio>8;size_comparisons.append(dict(viewport=viewport,large_to_small_radius90_ratio=ratio,dimensions_unchanged=True))

prefix='--positive-only' in sys.argv or geometry_only
if not prefix:
    cancel_ui=read_json(cancel/(case+'-ui.json'));assert cancel_ui['status']=='Partial' and cancel_ui['supported_workflows_completed'] and not cancel_ui['errors'];assert len(cancel_ui['cancellations'])==4 and len(cancel_ui['unsupported_rows'])==4
    for row,planned in zip(cancel_ui['cancellations'],[r for r in plan['cancellation_rows'] if r['mode']=='touch-cancel']):
        assert all(row[k]==v for k,v in planned.items());location=cancel/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));before=read('before');doc=read('cancelled');unchanged_header(before,doc);pixels=rgba(location/'cancelled.png');assert np.array_equal(pixels,decoded(doc)) and not (pixels==255).all();state=public(location,'cancel');assert np.array_equal(pixels,rgba(location/'cancel-released-public.png'));assert read('cancelled-undone')==before and read('cancelled-redone')==doc and read('fresh/reopened')==doc and np.array_equal(pixels,rgba(location/'fresh/reopened.png'))
        events=read_json(location/'native-input.json');requested=row['cancel_requested_performance_ms'];assert all(e['trusted'] for e in events);actual=[e for e in events if e['type']=='pointercancel' and e['pointerType']=='touch' and e['timeStamp']>=requested-1];assert len(actual)==1 and row['actual_hold_ms']>=row['hold_ms'];files(location);cancellations.append(dict(id=row['id'],viewport=row['viewport'],**state,trusted_pointercancel_after_actual_request=True,complete_history_fresh_RGBA_exact=True,physical_device=False))
    assert len(downloads)==({'mist':272,'splatter':272,'confetti':332}[kind]-32),'Unexpected actual retained download count'

report=dict(at=datetime.now(timezone.utc).isoformat(),case=case,applicator=kind,decoder='Pillow '+Image.__version__,positive_rows=rows,size_comparisons=size_comparisons,cancellations=cancellations,pigment_trace_checks=trace_checks,actual_downloads_verified=len(downloads),public_frame_hashes=frames_verified,original_preplanned_oracle=plan['oracle'],oracle_correction='Original ideal Red source-over line within2 is invalid for repeated native8-bit composites. The attempted one-step channel endpoint envelope is invalid too. Retained failed assertions and two independent native Canvas calibrations demonstrate both. Neither pixel threshold is widened or used as a Pass oracle: every actual native pigment/gradient stop, alpha and composition is checked exactly for each size/Strength/layout in a separate actual-control observational matrix. Original line/endpoint errors remain numerical diagnostics. All original affected-area/history/fresh checks remain strict.',supported_scope_complete=not prefix,acceptance_status='Prefix only' if prefix else 'Partial',unavailable=[] if prefix else cancel_ui['unsupported_rows'],limitation='Genuine headless tab/new-window activation produces no blur/visibility event. Four planned blur-cancellation rows are explicitly unavailable, not passed. Browser-native touch cancellation is software emulation, not a physical-device certificate.')
target=root/('evidence/'+case+('-geometry-prefix-verification.json' if geometry_only else '-positive-verification.json' if prefix else '-independent-verification.json'));target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case=case,positive_rows=len(rows),touch_cancellations=len(cancellations),actual_downloads=len(downloads),acceptance_status=report['acceptance_status'])))
