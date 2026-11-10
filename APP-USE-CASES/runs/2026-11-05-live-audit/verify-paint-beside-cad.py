"""Native adjacent paint insertion, isolated raster strokes, per-action Undo and full-stack rejection."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};metrics={}
def retain(stage):
 name='mouse-audit-paintlayers190-'+stage+'.retropaint';raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return json.loads(raw)
base=retain('baseline');ids={l['id'] for l in base['layers']};cad_index=next(i for i,l in enumerate(base['layers']) if 'cad'in l)
def canonical(d):
 d=copy.deepcopy(d);d.pop('active')
 for l in d['layers']:
  if 'cad'in l:l.pop('image');l['cad'].pop('view',None)
 return d
def camera_matches(d):
 a=next(l for l in d['layers'] if 'cad'in l)['cad']['view'];b=base['layers'][cad_index]['cad']['view'];assert a['projection']==b['projection'] and abs(a['span']-b['span'])<1e-8
 for key in ['position','target','up']:assert np.allclose(a[key],b[key],atol=1e-8)
def pixels(layer):return np.array(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))).convert('RGBA'))
for side,name,offset in [('above','Paint above 3D',1),('below','Backdrop',0)]:
 blank=retain(side+'-blank');painted=retain(side+'-painted');stroke_undo=retain(side+'-stroke-undone');layer_undo=retain(side+'-layer-undone');new=next(l for l in blank['layers'] if l['id'] not in ids);assert len(blank['layers'])==5 and blank['active']==new['id'] and blank['layers'].index(new)==cad_index+offset
 assert new['name']==name and new['paper'] is None and new['visible'] and new['opacity']==1 and 'cad'not in new and 'photo'not in new and new['live']==dict(strokes=[],fills=[],sparkles=[]);assert not pixels(new)[:,:,3].any()
 for d in [blank,painted,stroke_undo]:
  expected=copy.deepcopy(d);expected['layers']=[l for l in d['layers'] if l['id'] in ids];assert canonical(expected)==canonical(base);camera_matches(d)
 actual=next(l for l in painted['layers'] if l['id']==new['id']);expected=copy.deepcopy(new);expected['image']=actual['image'];assert actual==expected;rgba=pixels(actual);alpha=rgba[:,:,3];opaque=rgba[alpha==255];assert len(opaque)>1000 and np.all(opaque[:,:3]==[30,136,229]);ys,xs=np.nonzero(alpha);assert len(xs)>1000 and xs.max()-xs.min()>60 and ys.max()-ys.min()<40
 assert next(l for l in stroke_undo['layers'] if l['id']==new['id'])==new and canonical(layer_undo)==canonical(base);camera_matches(layer_undo);assert layer_undo['active']==base['layers'][cad_index]['id']
 metrics[side]=dict(new_layer_id=new['id'],adjacent_index=cad_index+offset,nonzero_alpha_pixels=len(xs),stroke_bounds_pixels=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],normal_transparent_sheet=True,stroke_undo_exact=True,one_layer_undo_restores_original_stack=True)
capacity_before=retain('capacity-before');capacity_after=retain('capacity-after');assert len(capacity_before['layers'])==16 and len({l['id'] for l in capacity_before['layers']})==16 and canonical(capacity_after)==canonical(capacity_before);camera_matches(capacity_before);camera_matches(capacity_after)
ui=json.loads((out/'paintlayers190-ui.json').read_text(encoding='utf-8'));assert all(ui['capacity'][side]['workshopStillOpen'] and 'stack is full' in ui['capacity'][side]['status'] for side in ['above','below'])
report=dict(status='Pass',above_and_below=metrics,painting_opens_on_new_sheet_with_layers=True,old_photo_annotation_crop_camera_and_model_retained=True,full16_layer_rejection_atomic_both_directions=True,no_half_transition_or_flattening=True,source_stack_restored=True,completion_timing_note=ui['saveTiming'],hashes=hashes)
(out/'paintlayers190-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
