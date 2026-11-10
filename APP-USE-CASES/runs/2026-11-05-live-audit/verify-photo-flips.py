"""Exact chart reflections/history and genuinely local flips in a rich MIX."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(n,ext='retropaint'):
    name=f'mouse-audit-flip140-{n}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA')).astype(int)
base=json.loads((downloads/'mouse-audit-align139-reset.retropaint').read_text(encoding='utf-8'));obj=base['layers'][0]['objects'][0];assert obj['matrix']==[1,0,0,1,0,0] and obj['opacity']==1;raw=np.array(Image.open(io.BytesIO(base64.b64decode(obj['image'].split(',')[1]))).convert('RGBA')).astype(int);docs={}
for name,key,reference in [('horizontal','flipX',raw[:,::-1]),('vertical','flipY',raw[::-1])]:
    d=load(name);docs[name]=d;expected=copy.deepcopy(base)
    for kind in ['settings','normal']:expected['layers'][0]['photo'][kind][key]=True
    assert d==expected;assert np.array_equal(load(name,'png'),reference)
assert load('undone')==docs['horizontal'] and load('redone')==docs['vertical'];assert np.array_equal(load('redone','png'),load('vertical','png'))
mix=json.loads((downloads/'mouse-audit-mix135-baseline.retropaint').read_text(encoding='utf-8'));composition=np.array(Image.open(downloads/'mouse-audit-mix135-baseline.png').convert('RGBA')).astype(int);stamp=(slice(449,531),slice(689,771));assert np.count_nonzero(np.any(composition[stamp][:,:,:3]!=[37,159,255],axis=2))>100
for name,key in [('mix-horizontal','flipX'),('mix-vertical','flipY')]:
    d=load(name);a=load(name,'png');expected=copy.deepcopy(mix)
    for kind in ['settings','normal']:expected['layers'][2]['photo'][kind][key]=True
    assert d==expected and a.shape==composition.shape;assert np.array_equal(a[stamp],composition[stamp]);assert np.count_nonzero(a!=composition)>1000
report=dict(status='Pass',native_horizontal_vertical_chart_every_RGBA_exact_numpy_reflections=True,whole_document_single_flip_Undo_Redo_exact=True,redone_PNG_exact=True,selected_Character_only_recipe_changes_in_four_sheet_MIX=True,other_sheets_source_objects_shared_frame_every_field_exact=True,visible_caption_stamp_same_original_pixels_position_both_flips=True,sha256=hashes)
(out/'flip140-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native photo flip directions, exact reflections/history and stationary other-sheet caption/stamp')
