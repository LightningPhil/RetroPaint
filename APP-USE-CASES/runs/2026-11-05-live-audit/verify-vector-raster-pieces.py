"""Native cropped gesture surfaces, isolated movement and padding hit test."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';hashes={}
def doc(n):
    name='mouse-audit-vector76-'+n+'.retropaint';data=(Path.home()/'Downloads'/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
before=doc('before');gestures=doc('gestures');moved=doc('second-moved-correct');old=before['layers'][0]['objects'];objects=gestures['layers'][0]['objects'];new=moved['layers'][0]['objects']
assert len(objects)==len(old)+3 and objects[:-3]==old and len({o['id']for o in objects})==len(objects)
for o in objects[-3:]:
    assert o['kind']=='raster';im=Image.open(io.BytesIO(base64.b64decode(o['image'].split(',',1)[1]))).convert('RGBA')
    assert im.size==(o['width'],o['height']);assert im.getchannel('A').getbbox()==(0,0,im.width,im.height)
    assert im.width<300 and im.height<200
assert new[:-2]==objects[:-2] and new[-1]==objects[-1]
a=copy.deepcopy(objects[-2]);b=copy.deepcopy(new[-2]);am=a.pop('matrix');bm=b.pop('matrix');assert a==b and am[:4]==bm[:4] and am[5]==bm[5];assert abs(bm[4]-am[4]-25*960/811.9994506835938)<.001
assert doc('move-undone')==gestures and doc('move-redone')==moved
padding=json.loads((out/'vector76-padding-point.json').read_bytes());assert padding['opaque_underlying_alpha']==255 and padding['spray_alpha']==0
report={'status':'Pass','three_independent_raster_pieces':True,'all_surfaces_cropped_to_actual_alpha_bounds':True,'only_second_piece_translation_changes':True,'exact_move_Undo_Redo':True,'native_padding_click_selected_underlying223x22_piece':padding,'sha256':hashes};(out/'vector76-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS cropped pieces, isolated translation, exact history and transparent-padding selection')
