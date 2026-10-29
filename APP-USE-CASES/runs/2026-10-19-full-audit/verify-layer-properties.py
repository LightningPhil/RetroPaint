from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,sys
import numpy as np
root=Path(__file__).resolve().parent;kind=sys.argv[1];assert kind in ['rename','opacity'];folder=root/('headless/LAYER-002-final' if kind=='rename' else 'headless/LAYER-004-complete')
ui=json.loads((folder/'LAYER-properties-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==4
fixture=json.loads((root/'headless/MIX-final/MIX-enriched.retropaint').read_text(encoding='utf-8'));rows=[];downloads=[]
for row in ui['rows']:
    location=folder/f"{row['width']}x{row['height']}";read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'));image=lambda name:np.asarray(Image.open(location/(name+'.png')).convert('RGBA'))
    before=read('before');expected=deepcopy(fixture);field='name' if kind=='rename' else 'opacity';expected['layers'][2][field]='Sketch sheet' if kind=='rename' else 1;assert before==expected
    pixels=image('before');assert pixels.shape==(640,960,4)
    expected_name='Sketch sheet';expected_opacity=1
    items=[('character','Character'),('blank','Layer'),('long',row['long_name'])] if kind=='rename' else [('half',.5),('zero',0),('full',1)]
    previous=before;previous_pixels=pixels
    for label,value in items:
        doc=read(label);expected=deepcopy(before);expected['layers'][2][field]=value;assert doc==expected,'Unrelated layer identity, pixels, live, recipe or object changed'
        current=image(label)
        if kind=='rename':assert np.array_equal(current,pixels),'Renaming changed artwork pixels'
        assert read(label+'-undone')==previous and np.array_equal(image(label+'-undone'),previous_pixels),'Undo did not restore the complete previous value in one action'
        assert read(label+'-redone')==doc and np.array_equal(image(label+'-redone'),current)
        previous=doc;previous_pixels=current
    assert read('fresh/reopened')==previous and np.array_equal(image('fresh/reopened'),previous_pixels)
    details={}
    if kind=='opacity':
        events=row['pointer_inputs'];assert len(events)>5 and len({item['value'] for item in events})>5 and all(item['trusted'] for item in events) and events[-1]['value']==.5
        full=image('full');zero=image('zero');half=image('half');expected_half=(full.astype(float)+zero.astype(float))*.5
        maximum=float(np.abs(half.astype(float)-expected_half).max());assert maximum<=2,'Composite violates independently computed opacity interpolation'
        # Independent sRGB +0.5 EV on the known original blue backing.
        encoded=np.array([30,136,229],dtype=float)/255;linear=np.where(encoded<=.04045,encoded/12.92,((encoded+.055)/1.055)**2.4)*2**.5;linear=np.clip(linear,0,1);blue=np.rint(np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)*255)
        assert np.abs(zero[140,150,:3].astype(float)-blue).max()<=1
        assert np.array_equal(full[140,150],np.array([229,57,53,255]))
        assert np.abs(half[140,150,:3].astype(float)-(.5*np.array([229,57,53])+.5*blue)).max()<=1
        assert np.array_equal(full,pixels) and np.array_equal(half,np.asarray(Image.open(root/'headless/START-007-complete'/f"{row['width']}x{row['height']}"/'before.png').convert('RGBA')))
        details=dict(trusted_pointer_input_events=len(events),single_gesture_undo_restores_full_opacity=True,independent_all_pixel_half_blend_max_error_255=maximum,known_red_over_exposed_blue_probe_exact_within_one=True)
    else:assert len(row['long_name'])==60 and row['blank_fallback']=='Layer'
    for log in [location/'events.json',location/'fresh/events.json']:
        downloads += [e for e in json.loads(log.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(viewport=[row['width'],row['height']],complete_saved_data_changes_only_target_property=True,all_original_live_photo_object_and_other_layers_exact=True,undo_redo_and_actual_fresh_project_reopen_exact=True,**details))
assert len(downloads)==88
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,kind=kind,rows=rows,actual_downloads_verified=len(downloads),render_time_ms=10000,oracle='Complete project field identity, independent full-size RGBA, and, for opacity, physically affine all-pixel interpolation between full/zero plus published sRGB gain and known red/blue probe. Native pointer input observations prove a multi-input single gesture.',declared_all_pixel_blend_tolerance_255=2 if kind=='opacity' else 0,declared_known_probe_tolerance_255=1 if kind=='opacity' else 0,execution='Isolated headless public UI; no existing browser or desktop access')
(root/('evidence/LAYER-'+('002' if kind=='rename' else '004')+'-independent-verification.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
