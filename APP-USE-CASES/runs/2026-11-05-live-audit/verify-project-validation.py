"""Independently compare native downloaded project data and controlled frames."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';fixtures=root/'test-results/audit-2026-11-05/fixtures';hashes={}
plan=json.loads((fixtures/'project-validation44/manifest.json').read_bytes());e=json.loads((out/'project44-fixed-evidence.json').read_bytes())
def actual(s,extension='retropaint'):
    name='mouse-audit-project44-'+s+'.'+extension;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(s):return json.loads(actual(s))
def rgba(url):return Image.open(io.BytesIO(base64.b64decode(url.split(',',1)[1]))).convert('RGBA').tobytes()
before=doc('fixed-before');mixed=doc('mixed-before');assert before['drawingMode']=='raster' and mixed['drawingMode']=='vector'
assert len(e['rejections'])==len(e['retries'])==len(plan['invalid'])==28
results=[]
for row,rejection,retry in zip(plan['invalid'],e['rejections'],e['retries']):
    label=row['label'];assert label==rejection['label']==retry['label'];assert rejection['message'].strip();assert retry['mode']=='raster' and not retry['vectorClass']
    assert hashlib.sha256(Path(row['file']).read_bytes()).hexdigest()==row['sha256']
    assert doc('fixed-rejected-'+label)==before==doc('fixed-returned-'+label)
    assert doc('fixed-retry-'+label)==mixed
    results.append({'label':label,'message':rejection['message'],'whole_document_unchanged_and_valid_retry_and_Undo_exact':True})
assert doc('mixed-reopened')==mixed==doc('mixed-time-changed')
raw=Path(plan['valid']['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==plan['valid']['sha256'];source=json.loads(raw)
# PNG compression may differ when a genuine image is decoded and saved. Compare
# decoded source RGBA and every other field, without dropping editing definitions.
source_meta=copy.deepcopy(source);mixed_meta=copy.deepcopy(mixed)
for a,b in zip(source_meta['layers'],mixed_meta['layers']):
    assert rgba(a['image'])==rgba(b['image']);a['image']=b['image']
# The source producer omitted an optional stroke clip. Current save explicitly
# writes null, representing the same unbounded stroke; assert that sole default.
assert 'clip' not in source_meta['layers'][1]['live']['strokes'][0]
assert mixed_meta['layers'][1]['live']['strokes'][0]['clip'] is None
source_meta['layers'][1]['live']['strokes'][0]['clip']=None
assert source_meta==mixed_meta
photo=json.loads((downloads/'mouse-audit-save43-photo-before.retropaint').read_bytes());vector=json.loads((downloads/'mouse-audit-edit-vector-overhang38-before.retropaint').read_bytes());live=json.loads((fixtures/'mix-live-clear.retropaint').read_bytes())
live_source=copy.deepcopy(live['layers'][1]['live']);assert 'clip' not in live_source['strokes'][0];live_source['strokes'][0]['clip']=None
assert mixed['layers'][1]['photo']==photo['layers'][1]['photo'] and mixed['layers'][1]['live']==live_source
assert mixed['layers'][2]['objects']==vector['layers'][0]['objects'];assert len(mixed['layers'])==4 and mixed['active']==103 and mixed['layers'][2]['opacity']==.5
frames=[np.array(Image.open(io.BytesIO(actual(s,'png'))).convert('RGBA')) for s in ['mixed-time12345','mixed-reopened-time12345','mixed-time23456']]
assert np.array_equal(frames[0],frames[1]);changed=int(np.any(frames[0]!=frames[2],axis=2).sum());assert changed>0
report={'status':'Pass','invalid_cases':results,'mixed_project':{'whole_native_saved_data_exact_after_fresh_reopen':True,'all_fixture_source_RGBA_and_editing_fields_preserved':True,'sole_source_default':'Absent optional Backdrop live stroke clip becomes explicit null; no clipping before or after. All other non-image fields exact; every decoded source Raster RGBA byte exact.','genuine_photo_live_and_nine_vector_definitions_preserved':True,'controlled_12345ms_frame_RGBA_exact':True,'alternate_23456ms_changed_pixels':changed,'no_flattening':True},'sha256':hashes}
(out/'project44-validation-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','invalid_cases']},indent=2));print('28 exact rejection/retry/Undo cycles')
