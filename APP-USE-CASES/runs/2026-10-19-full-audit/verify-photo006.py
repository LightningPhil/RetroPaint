from pathlib import Path
from datetime import datetime,timezone
from copy import deepcopy
import json,base64,io
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parent
folder=root/'evidence'
read=lambda label:json.loads((folder/('PHOTO-006-'+label+'.retropaint')).read_text(encoding='utf-8'))
image=lambda label:np.asarray(Image.open(folder/('PHOTO-006-'+label+'.png')).convert('RGBA'))
decode=lambda layer:np.asarray(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA'))
before=read('before');photo=read('photo-step');paint=read('paint-step')
assert before==json.loads((folder/'PHOTO-004-saved-before.retropaint').read_text(encoding='utf-8'))
assert (before['width'],before['height'])==(3896,2586)
assert photo['layers'][0]['photo']['settings']['brightness']==25 and before['layers'][0]['photo']['settings']['brightness']==7
copy=deepcopy(photo);copy['layers'][0]['photo']=before['layers'][0]['photo']
assert copy==before,'Photo commit changed unrelated data'
copy=deepcopy(paint);copy['active']=photo['active'];copy['layers'][1]['image']=photo['layers'][1]['image']
assert copy==photo,'Paint changed photo data or another layer'
old,new=decode(photo['layers'][1]),decode(paint['layers'][1])
mask=np.any(old!=new,axis=2);y,x=np.where(mask)
assert len(x)>2000 and x.min()>=1980 and x.max()<=2520 and y.min()>=1780 and y.max()<=2020
assert np.all(new[mask,0]>new[mask,1]) and np.all(new[mask,0]>new[mask,2]),'Paint is not the chosen red'
def expect(label,reference,pixel_reference):
    doc=read(label);expected=deepcopy(reference)
    # Layer selection is a deliberate UI action, recorded separately. No source,
    # recipe, image, identity, order, visibility or other field is normalised.
    assert doc['active'] in [2,3]
    expected['active']=doc['active']
    assert doc==expected,label+' did not restore its complete expected document'
    assert np.array_equal(image(label),image(pixel_reference)),label+' did not restore exact full-size RGBA'
    return dict(stage=label,active_layer=doc['active'],complete_expected_document=True,full_size_rgba_exact=True)
rows=[expect('undo-paint',photo,'photo-step'),expect('undo-photo',before,'before'),expect('redo-photo',photo,'photo-step'),expect('redo-paint',paint,'paint-step'),expect('draft-undo-cancelled',paint,'paint-step'),expect('undo-after-draft',photo,'photo-step'),expect('redo-after-draft',paint,'paint-step')]
assert read('undo-photo')==before
assert read('redo-photo')==read('undo-paint') and read('redo-paint')==paint
assert np.any(image('photo-step')!=image('before')) and np.any(image('paint-step')!=image('photo-step'))
result=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,source_dimensions=[3896,2586],native_red_mark_changed_layer_pixels=int(len(x)),native_mark_bounds=[int(x.min()),int(y.min()),int(x.max()),int(y.max())],photo_and_paint_are_distinct_history_steps=True,unsaved_draft_undo_cancels_without_consuming_document_undo=True,all_original_photo_pixels_preserved=True,rows=rows,active_layer_handling='Actual layer selection varies between IDs 2 and 3. Each full document comparison permits only that independently recorded selection; no content fields are ignored.')
(folder/'PHOTO-006-independent-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
