"""Independent native photo comparison, cancellation and mixed history."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(prefix,n):
    name=f'mouse-audit-photo{prefix}-{n}.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
original=doc(93,'original');assert doc(93,'compared-cancelled')==original
saved=doc(93,'saved-recipe');assert saved['layers'][0]['image']==original['layers'][0]['image'];assert saved['layers'][0]['photo']['settings']['brightness']==20
assert saved['layers'][0]['photo']['settings']['curves']['rgb']==[{'x':0,'y':0},{'x':.25,'y':.18},{'x':.75,'y':.82},{'x':1,'y':1}]
for n in ['cancel','close','escape']:assert doc(94,n)==saved
source=Image.open(io.BytesIO(base64.b64decode(original['layers'][0]['image'].split(',')[1]))).convert('RGB').resize((897,597),Image.Resampling.BICUBIC)
region=(slice(150,690),slice(410,1245));before=np.array(Image.open(out/'photo93-before.jpg')).astype(int)[region];after=np.array(Image.open(out/'photo93-after-b.jpg')).astype(int)[region];early=np.array(Image.open(out/'photo93-after-a.jpg')).astype(int)[region]
reference=np.array(source).astype(int)[28:568,29:864];correlation=float(np.corrcoef(reference.flatten(),before.flatten())[0,1]);assert correlation>.99
assert np.mean(np.max(before,axis=2)-np.min(before,axis=2))>40 and np.max(np.max(after,axis=2)-np.min(after,axis=2))==0
assert np.array_equal(early,after)
foundation=doc(95,'before');photo=doc(95,'photo-edit');painted=doc(95,'painted');expected=copy.deepcopy(foundation);expected['layers'][0]['photo']=photo['layers'][0]['photo'];assert expected==photo
assert photo['layers'][0]['photo']['settings']['brightness']==21 and photo['layers'][0]['image']==original['layers'][0]['image']
assert painted['layers'][0]==photo['layers'][0];assert painted['layers'][1]['image']!=photo['layers'][1]['image']
expected=copy.deepcopy(photo);expected['active']=painted['active'];assert doc(95,'paint-undone')==expected and doc(95,'photo-redone')==expected
assert doc(95,'photo-undone')==foundation and doc(95,'paint-redone')==painted and doc(95,'draft-undo')==painted and doc(95,'next-undo')==expected
expected=copy.deepcopy(painted);expected['active']=photo['active'];assert doc(95,'multilayer-cancel')==expected
png=[]
for n in ['painted','redone']:
    name=f'mouse-audit-photo95-{n}.png';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();png.append(np.array(Image.open(out/name).convert('RGBA')))
assert np.array_equal(*png)
report=dict(status='Pass',comparison_source_correlation=correlation,before_shows_original_colour=True,after_current_monochrome_draft_exact_across_pending_toggle=True,comparison_cancel_whole_document_exact=True,cancel_close_escape_preserve_saved_recipe_exactly=True,underlying_original_image_bytes_exact=True,other_sheet_preserved_on_cancel=True,photo_and_paint_history_separate_and_exact=True,unsaved_draft_ctrl_z_cancels_without_consuming_document_history=True,redo_full_size_png_pixels_exact=True,sha256=hashes)
(out/'photo93-95-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native photo Before/After, all cancellation routes, exact separate history and rendered Redo')
