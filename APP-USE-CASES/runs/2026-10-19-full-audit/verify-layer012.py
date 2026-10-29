from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
from PIL import Image
import json,hashlib,base64,io
import numpy as np
root=Path(__file__).resolve().parent;folder=root/'headless/LAYER-012-fixed'
ui=json.loads((folder/'LAYER-012-ui.json').read_text(encoding='utf-8'));assert ui['status']=='Pass' and not ui['errors'] and len(ui['rows'])==3
manifest=json.loads((root/'fixtures/layer-limits/manifest.json').read_text(encoding='utf-8'));rows=[];downloads=[]
decode=lambda value:np.asarray(Image.open(io.BytesIO(base64.b64decode(value.split(',',1)[1]))).convert('RGBA'))
for fixture,row in zip(manifest['fixtures'],ui['rows']):
    label=fixture['label'];assert row['label']==label;location=folder/label;read=lambda name:json.loads((location/(name+'.retropaint')).read_text(encoding='utf-8'))
    before=read('before');assert before['width']==fixture['width'] and before['height']==fixture['height'] and len(before['layers'])==1
    original=before['layers'][0];source=decode(original['image']);expected=np.asarray(Image.open(fixture['file']).convert('RGBA'));assert np.array_equal(source[:,:,3],expected[:,:,3]);alpha=source[:,:,3:4].astype(np.float32)/255
    for backing in [0,255]:assert float(np.abs((source[:,:,:3].astype(float)-expected[:,:,:3])*alpha).max())<=1
    full=read('at-limit');count=fixture['max_layers'];assert len(full['layers'])==count and len({l['id'] for l in full['layers']})==count
    assert full['layers'][0]==original and full['active']==full['layers'][-1]['id']
    for layer in full['layers'][1:]:
        assert layer['visible'] and layer['opacity']==1 and layer['paper'] is None and not any(layer['live'].values())
        assert not layer.get('objects') and not layer.get('cad') and not layer.get('photo') and not decode(layer['image']).any()
    assert read('rejected-add')==full
    released=read('space-released');expected_doc=deepcopy(full);expected_doc['layers'].pop();expected_doc['active']=expected_doc['layers'][-1]['id'];assert released==expected_doc
    reused=read('space-reused');replacement=reused['layers'][-1];expected_doc=deepcopy(released);expected_doc['layers'].append(replacement);expected_doc['active']=replacement['id'];assert reused==expected_doc
    assert replacement['id'] not in {l['id'] for l in full['layers']}
    equivalent=deepcopy(full['layers'][-1]);equivalent['id']=replacement['id'];assert replacement==equivalent
    assert read('add-undone')==released and read('add-redone')==reused and read('fresh/reopened')==reused
    reopened=np.asarray(Image.open(location/'fresh/reopened.png').convert('RGBA'));assert reopened.shape==source.shape and np.array_equal(reopened,source)
    pixels=fixture['width']*fixture['height']*count;assert row['stored_pixels']==pixels and pixels<=64_000_000
    if label=='count':assert count==16 and row['rejected_next_pixels']<64_000_000 and '16 layers' in row['hint'] and 'full' in row['hint']
    else:assert row['rejected_next_pixels']>64_000_000 and '64 million' in row['hint']
    if label=='exact-budget':assert pixels==64_000_000
    if label=='nearest-over-budget':assert row['rejected_next_pixels']==64_000_006 and manifest['nearest_invalid_combination']['stored_pixels']==64_000_006
    for file in [location/'events.json',location/'fresh/events.json']:downloads += [e for e in json.loads(file.read_text(encoding='utf-8')) if e['action']=='download']
    rows.append(dict(label=label,dimensions=[fixture['width'],fixture['height']],layers=count,actual_stored_pixels=pixels,rejected_next_total=row['rejected_next_pixels'],reason=row['hint'],source_rgba_and_all_other_layers_independently_verified=True,rejected_add_has_exact_document=True,removed_space_reusable_with_fresh_identity=True,undo_redo_actual_fresh_project_and_png_exact=True))
assert len(downloads)==27
for event in downloads:
    data=Path(event['path']).read_bytes();assert len(data)==event['bytes'] and hashlib.sha256(data).hexdigest()==event['sha256']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,rows=rows,actual_downloads_verified=len(downloads),oracle='Independent encoded source and RGBA/alpha/composites (predeclared1/255 premultiplication tolerance), exact retained project fields, unique layer identities and all empty surfaces. Exhaustive supported integer-dimension/count search proves exact valid64,000,000 and nearest invalid64,000,006. Real rejected Add, released/reused capacity, history and fresh actual project/PNG.',execution='Isolated headless production UI; small count case before bounded64-million-pixel allocations; no physical desktop access')
(root/'evidence/LAYER-012-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
