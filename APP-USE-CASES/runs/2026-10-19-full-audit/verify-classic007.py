from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
from paint_oracle import verify_brush_boundary,components,dilate_one,distances
import json,hashlib,base64,io,sys,math
import numpy as np
root=Path(__file__).resolve().parent;base=root/'headless/PAINT-007-foreground';read_json=lambda file:json.loads(file.read_text(encoding='utf-8'));plan=read_json(root/'fixtures/PAINT-007-plan.json');kinds=plan['applicators'];downloads=[];boundaries={}
def decoded(doc):return np.asarray(Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
def verify_files(events):
    for event in events:
        data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
def foreground(location):
    for file in [location/'events.json',location/'fresh/events.json']:
        states=[e['state'] for e in read_json(file) if e['action']=='isolated-headless-foreground-ready'];assert len(states)==1 and states[0]['visibility']=='visible' and not states[0]['hidden'],'No recorded real foreground precondition'
only=sys.argv[sys.argv.index('--kind')+1] if '--kind' in sys.argv else None
for kind in ([only] if only else kinds):
    assert kind in kinds;folder=base/kind;ui=read_json(folder/('PAINT-007-'+kind+'-ui.json'));bp=read_json(root/('fixtures/PAINT-007-'+kind+'-plan.json'));assert ui['status']=='Pass' and not ui['errors'] and ui['applicator']==kind
    rows,events=verify_brush_boundary(folder,ui,bp,read_json,decoded,texture_dilation=kind in ['crayon','natural']);assert len(events)==308
    for row in ui['rows']:foreground(folder/row['id'])
    endpoint=[]
    for size in [1,22,96]:
        reference=next(r for r in ui['rows'] if r['size']==size and r['strength']==1);full=np.asarray(Image.open(folder/reference['id']/'tap.png').convert('RGBA'));yy,xx=np.mgrid[0:640,0:960];core=np.hypot(xx+.5-800,yy+.5-200)<max(.75,size/2-3)
        for row in [r for r in ui['rows'] if r['size']==size and r['strength']==.15]:
            weak=np.asarray(Image.open(folder/row['id']/'tap.png').convert('RGBA'));expected=np.rint(255+.15*(full[core,:3].astype(float)-255));error=int(np.abs(weak[core,:3].astype(int)-expected).max());assert error<=2,(kind,row['id'],'Strength endpoint does not scale the known material contribution');endpoint.append(dict(row=row['id'],reference=reference['id'],size=size,maximum_channel_error=error))
    boundaries[kind]=dict(rows=rows,strength_endpoint_checks=endpoint,actual_downloads=308);downloads+=events
if only:
    verify_files(downloads);report=dict(at=datetime.now(timezone.utc).isoformat(),applicator=only,scope='One completed applicator boundary matrix only; not a PAINT-007 Pass.',boundary=boundaries[only],actual_downloads_verified=len(downloads),oracle=plan['oracle']);(root/('evidence/PAINT-007-'+only+'-boundary-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(applicator=only,rows=14,downloads=len(downloads),acceptance_complete=False)));sys.exit(0)
sequence=read_json(base/'sequence.json');assert sequence['status']=='Pass' and len(sequence['steps'])==5;folder=base/'main';ui=read_json(folder/'PAINT-007-main-ui.json');assert ui['status']=='Pass' and not ui['errors'] and [r['viewport'] for r in ui['rows']]==plan['main_viewports'];main=[]
def core_colours(pixels,points,radius):
    left=max(0,math.floor(min(p[0] for p in points)-radius));right=min(pixels.shape[1],math.ceil(max(p[0] for p in points)+radius));top=max(0,math.floor(min(p[1] for p in points)-radius));bottom=min(pixels.shape[0],math.ceil(max(p[1] for p in points)+radius));ys,xs=np.mgrid[top:bottom,left:right];inside=distances(points,xs.ravel(),ys.ravel())<radius;return pixels[ys.ravel()[inside],xs.ravel()[inside],:3].astype(int)
def material(colours,kind):
    assert len(colours)>100 and (colours[:,0]>colours[:,1]).all() and (colours[:,0]>colours[:,2]).all(),'Core does not have selected Red character';alpha=(255-colours[:,1])/198;unique=len(np.unique(colours,axis=0));spread=int(np.ptp(colours[:,1]));low=float((alpha<.25).mean());strong=float((alpha>.9).mean());high=float((alpha>.75).mean())
    if kind=='brush':assert np.abs(colours-np.array([229,57,53])).max()<=1,'Classic Brush preview/paint is not its flat ink family'
    elif kind=='oil':assert unique>=3 and spread>=3,'Oil preview/paint loses bristle variation'
    elif kind=='crayon':assert unique>=10 and low>=.05 and strong>=.05,'Crayon preview/paint loses grain gaps/strong pigment'
    else:assert unique>=10 and low<.01 and high>=.05 and alpha.max()<=.95,'Natural Pencil preview/paint loses its soft grain family'
    return dict(core_pixels=len(colours),unique_RGB_values=unique,green_range=spread,low_pigment_fraction=low,strong_pigment_fraction=strong,high_pigment_fraction=high,median_inferred_alpha=float(np.median(alpha)),maximum_inferred_alpha=float(alpha.max()))
for row in ui['rows']:
    location=folder/row['id'];read=lambda label:read_json(location/(label+'.retropaint'));image=lambda label:np.asarray(Image.open(location/(label+'.png')).convert('RGBA'));before=read('before');blank=image('before');assert blank.shape==(640,960,4) and (blank==255).all();previous=blank;previous_label='before';metrics={};labels=[];foreground(location)
    for kind in kinds:
        assert read(kind+'-selected')==read(previous_label),'Classic selection recolours an old mark';shape=plan['main_paths'][kind];preview=Image.open(location/(kind+'-public-sample.png')).convert('RGBA');assert preview.size==(160,60);preview=np.asarray(Image.alpha_composite(Image.new('RGBA',(160,60),'white'),preview));points=[[15+1.85*i,30+9*math.sin(2*math.pi*i/69)] for i in range(70)];sample_stats=material(core_colours(preview,points,3),kind)
        for suffix in ['bent','tap']:
            label=kind+'-'+suffix;doc=read(label);expected=deepcopy(before);expected['layers'][0]['image']=doc['layers'][0]['image'];assert doc==expected;pixels=image(label);assert np.array_equal(pixels,decoded(doc));mask=(pixels!=previous).any(axis=2);raw=components(mask);assert (components(dilate_one(mask)) if kind in ['crayon','natural'] else raw)==1;ys,xs=np.where(mask)
            distance=distances(shape['points'],xs,ys) if suffix=='bent' else np.hypot(xs+.5-shape['tap'][0],ys+.5-shape['tap'][1]);assert distance.max()<=13,'Classic mark spills beyond its declared footprint'
            if suffix=='bent':actual_stats=material(core_colours(pixels,shape['points'],6),kind)
            metrics[label]=dict(changed_pixels=int(mask.sum()),raw_components=raw,one_cell_grain_dilation_used=kind in ['crayon','natural'],maximum_path_distance=float(distance.max()));previous=pixels;previous_label=label;labels.append(label)
        metrics[kind]=dict(public_preview=sample_stats,actual_bent=actual_stats,selected_public_sample_agrees_with_actual_family=True)
    assert row['labels']==labels and [p['kind'] for p in row['previews']]==kinds and all(p['selected_aria_pressed'] for p in row['previews'])
    for index,label in enumerate(labels):assert read(label+'-undone')==read('before' if index==0 else labels[index-1]) and read(label+'-redone')==read(label),'Classic complete gesture history mismatch'
    assert read('fresh/reopened')==read(labels[-1]) and np.array_equal(image('fresh/reopened'),previous);inputs=read_json(location/'native-input.json');assert all(e['trusted'] and e['pointerType']=='mouse' for e in inputs);assert len([e for e in inputs if e['type']=='pointerdown'])==len([e for e in inputs if e['type']=='pointerup'])==8
    for file in [location/'events.json',location/'fresh/events.json']:downloads.extend(e for e in read_json(file) if e['action']=='download')
    main.append(dict(viewport=row['viewport'],material_metrics=metrics,all_four_choices_preserve_previous_data=True,all_eight_complete_gesture_history_and_fresh_RGBA_exact=True))
assert len(downloads)==1392;verify_files(downloads);report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,boundaries=boundaries,main_rows=main,actual_downloads_verified=len(downloads),all_four_actual_applicators_and_every_planned_row_verified=True,oracle=plan['oracle'],execution='All56 boundary rows and four material-main workflows rerun sequentially with real foreground visibility recorded. Earlier concurrent timing/readiness attempts are retained and excluded.')
(root/'evidence/PAINT-007-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(case='PAINT-007',boundary_rows=56,main_rows=4,downloads=len(downloads))))
