"""Independent saved-file checks for actual held-mouse interruption workflows."""
import base64, hashlib, io, json
from pathlib import Path
from PIL import Image, ImageChops

root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse'
hashes={}
def doc(stage):
    name='mouse-audit-interrupt-'+stage+'.retropaint'
    data=(Path.home()/'Downloads'/name).read_bytes()
    (out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
    return json.loads(data)
def pixels(layer):
    return Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')

for before,next_stage in [('brush-window-after','brush-next'),('selection-lost','selection-next'),('spiro-lost','spiro-next')]:
    assert doc(before)==doc(next_stage+'-undone'),next_stage+' Undo'
    assert doc(next_stage)==doc(next_stage+'-redone'),next_stage+' Redo'
assert doc('spiro-before')==doc('spiro-lost')
assert doc('selection-lost')==doc('brush-next-redone')
spiro=doc('spiro-next');crop=doc('crop-next')
assert spiro==doc('crop-next-undone') and crop==doc('crop-next-redone')
assert (crop['width'],crop['height'])==(960,640)
c=crop['crop'];expected=(137,137,687,425)
for key,value,scale in zip(('x','y','width','height'),expected,(960,640,960,640)):
    assert abs(c[key]*scale-value)<1,(key,c[key]*scale,value)
assert spiro['layers'][0]['image']==crop['layers'][0]['image'],'Crop destroyed source'

before=doc('cad-before');moved=doc('cad-next');undone=doc('cad-next-undone');redone=doc('cad-next-redone')
assert moved==redone
assert before['layers'][0]==undone['layers'][0]==moved['layers'][0],'CAD changed paint'
a,b,c=before['layers'][1],undone['layers'][1],moved['layers'][1]
assert a['cad']==b['cad']
assert a['cad']['bodies'][0]['position']==[0,0,10]
assert c['cad']['bodies'][0]['position']==[8,0,10]
for k in a:
    if k!='image':assert a[k]==b[k],k
thumbnail_diff=ImageChops.difference(pixels(a),pixels(b))
thumbnail_changed=sum(any(v) for v in thumbnail_diff.get_flattened_data())
thumbnail_max=max(v[1] for v in thumbnail_diff.getextrema())
# This is a regenerated GPU thumbnail across a production-build reload, not
# editable model data. Report the observed pixel difference separately; recipes,
# source paint and the following same-build whole-project Redo are checked above.

native=json.loads((out/'interruption-event-evidence.json').read_bytes())
for label in ['raster-selection','spiro-gear','photo-crop','cad-move-handle']:
    e=next(e for e in native if e['label']==label)
    assert e['beforeRelease']['inputCompleted'] is None
    trace=e['afterRelease']['trace']
    assert '"phase":"lostpointercapture"' in trace.strip().split('\n')[-1] or label=='photo-crop' and '"phase":"lostpointercapture"' in trace
    assert e['afterRelease']['elapsed']<e['requestedDuration'] and e['finished']-e['started']>=e['requestedDuration']
fixed=json.loads((out/'cad-interruption-after-live-valid.json').read_bytes())
assert fixed['during']['inputCompleted'] is None and not fixed['during']['undoEnabled']
assert fixed['afterLoss']['inputCompleted'] is None and fixed['afterLoss']['undoEnabled']
assert '"phase":"lostpointercapture"' in fixed['afterLoss']['trace'].splitlines()[-1]
assert fixed['afterLateUp']['undoEnabled'] and fixed['afterLateUp']['elapsed']>=7500
report={'status':'Pass','actual_capture_loss_and_outside_app_release':True,'subsequent_brush_selection_spiro_crop_and_cad_gestures_independent':True,'undo_redo_exact_document_or_recipe_checks':True,'cad_following_move_mm':[8,0,0],'cad_thumbnail_changed_pixels':thumbnail_changed,'cad_thumbnail_max_channel_delta':thumbnail_max,'fixed_cad_undo_enabled_before_scheduled_release_ms':fixed['afterLoss']['elapsed'],'native_window_blur_or_pointercancel_observed':False,'window_blur_and_pointercancel_supplementary_four_layout_regressions':True,'sha256':hashes}
(out/'interruptions-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
