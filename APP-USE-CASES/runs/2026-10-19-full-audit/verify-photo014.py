from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io,re
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/PHOTO-014-complete'
read=lambda name:json.loads((folder/(name+'.retropaint')).read_text(encoding='utf-8'))
image=lambda name:np.asarray(Image.open(folder/(name+'.png')).convert('RGBA'))
decode=lambda layer:np.asarray(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
ui=json.loads((folder/'PHOTO-014-headless-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and ui['fresh_reopen_complete'] and len(ui['rows'])==5
defaults={key:0 for key in ['exposure','brightness','contrast','highlights','shadows','whites','blacks','temperature','tint','saturation','vibrance','hue','sharpness','threshold','texture','clarity','pop','dehaze','noise','colourNoise','vignette','roundness','grain','distortion','aberration','vertical','horizontal','angle']}
defaults.update(balance=[1,1,1],radius=1,midpoint=50,feather=75,grainSize=1.2,grainRoughness=50,zoom=100,flipX=False,flipY=False,crop=dict(x=0,y=0,width=1,height=1),mixer=[dict(hue=0,saturation=0,luminance=0)]*8,curves={key:[dict(x=0,y=0),dict(x=1,y=1)] for key in ['rgb','red','green','blue']})
rows=[]
for row in ui['rows']:
    name=row['name'];before=read(name+'-before');done=read(name+'-done');source=image(name+'-before');output=image(name+'-done');assert len(before['layers'])==1
    settings=done['layers'][0]['photo']['settings'];expected_settings=deepcopy(defaults)
    for key in ['exposure','contrast','shadows','highlights','vibrance']:
        value=settings[key];assert isinstance(value,(float,int)) and np.isfinite(value)
        assert (-1.5<=value<=1.5) if key=='exposure' else (-100<=value<=100)
        expected_settings[key]=value
        # The range thumb snaps to its .05 EV step. The adjacent visible value
        # has two decimals. Both must represent the actual stored settings.
        tolerance=.0250001 if key=='exposure' else 0
        assert abs(row['first'][key]-value)<=tolerance
    assert settings==expected_settings
    recipe=dict(settings=settings,normal=settings,look='custom',lookActive=False);assert done['layers'][0]['photo']==recipe
    expected=deepcopy(before);expected['layers'][0]['photo']=recipe;assert done==expected
    assert row['first']==row['repeated']
    assert np.array_equal(image(name+'-auto-preview'),image(name+'-repeated-preview')) and np.array_equal(image(name+'-auto-preview'),image(name+'-after-comparison'))
    text=(folder/(name+'-auto.txt')).read_text(encoding='utf-8')
    # Exposure/contrast remain visible in the captured light-basic UI.
    exposed=float(re.search(r'Exposure\s*(-?[\d.]+)\s*EV',text).group(1));assert abs(exposed-settings['exposure'])<=.0050001
    assert np.array_equal(decode(before['layers'][0]),decode(done['layers'][0])) and np.array_equal(source,decode(before['layers'][0]))
    assert source.shape==output.shape and np.array_equal(output[:,:,3],source[:,:,3])
    for suffix in ['cancelled','undone']:
        assert read(name+'-'+suffix)==before and np.array_equal(image(name+'-'+suffix),source)
    assert read(name+'-redone')==done and np.array_equal(image(name+'-redone'),output)
    details={}
    if name in ['dark','bright']:
        before_mean=float(source[:,:,:3].mean());after_mean=float(output[:,:,:3].mean())
        assert abs(after_mean-128)<abs(before_mean-128),'Auto moves a deliberately uneven ramp away from an encoded neutral midpoint'
        assert settings['exposure']>0 if name=='dark' else settings['exposure']<0
        assert np.array_equal(output[:,:,0],output[:,:,1]) and np.array_equal(output[:,:,1],output[:,:,2])
        details=dict(before_mean_255=before_mean,after_mean_255=after_mean,closer_to_independent_encoded_midpoint_128=True)
    if name in ['empty','constant']:
        assert settings==defaults and np.array_equal(output,source),'Degenerate input did not produce a defined unchanged result'
        details=dict(defined_noop=True)
    if name=='natural':assert source.shape==(2586,3896,4) and np.any(output!=source)
    rows.append(dict(name=name,exact_reset_repeat_preview_and_settings=True,visible_settings_match_recipe=True,original_and_all_unrelated_fields_exact=True,cancel_undo_redo_exact=True,**details))
assert read('fresh/reopened')==read('natural-done') and np.array_equal(image('fresh/reopened'),image('natural-done'))
events=json.loads((folder/'events.json').read_text(encoding='utf-8'))+json.loads((folder/'fresh/events.json').read_text(encoding='utf-8'));downloads=[e for e in events if e['action']=='download'];assert len(downloads)==52
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,all_input_variants_executed=['dark ramp','bright ramp','empty transparent','constant RGB colour','supplied natural sunset photograph'],actual_fresh_downloaded_file_reopen_exact=True,actual_downloads_verified=len(downloads),declared_visible_exposure_thumb_tolerance_EV=.0250001,declared_visible_exposure_label_rounding_EV=.0050001,oracle='Independent pixel statistics against encoded midpoint128 for deliberately dark/bright ramps; exact repeated preview/data, literal allowed setting fields and ranges, original data, degenerate no-op outputs, actual Undo/Redo/reopen. Does not copy or call the Auto light algorithm.',execution='Isolated headless production UI; no desktop control')
(root/'evidence/PHOTO-014-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
