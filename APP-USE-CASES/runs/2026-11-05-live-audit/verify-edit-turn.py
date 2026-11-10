"""Independent native flip/turn, centred placement, alpha, and history checks."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(s,ext='retropaint',version=42):
 name=f'mouse-audit-edit-turn{version}-{s}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(s,version=42):return json.loads(actual(s,version=version))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',')[1]))
def same(a,b):assert a.size==b.size and a.tobytes()==b.tobytes()
def cp(s):return image((out/f'edit-turn42-{s}-copy.png').read_bytes())
before=doc('before');assert before==doc('before',41);original=pixels(before);source=image((out/'edit-turn41-source.png').read_bytes());same(source,original.crop((90,90,210,190)))
clear=original.copy();clear.paste((0,0,0,0),(90,90,210,190));quarter=source.transpose(Image.Transpose.ROTATE_270)
bad=clear.copy();bad.alpha_composite(quarter,(90,90));same(bad,pixels(doc('after90',41)))
expected=clear.copy();expected.alpha_composite(quarter,(100,80));same(expected,pixels(doc('quarter-only')));same(expected,image(actual('quarter-only','png')))
same(cp('quarter-only'),quarter);same(cp('flip-h'),source.transpose(Image.Transpose.FLIP_LEFT_RIGHT));same(cp('flip-hv'),source.transpose(Image.Transpose.FLIP_LEFT_RIGHT).transpose(Image.Transpose.FLIP_TOP_BOTTOM));same(cp('turn90'),cp('flip-hv').transpose(Image.Transpose.ROTATE_270))
assert cp('turn45').size==(156,156)
expected=clear.copy();expected.alpha_composite(cp('turn45'),(72,62));placed=doc('placed');shown=pixels(placed)
ea=np.array(expected);sa=np.array(shown);assert np.array_equal(ea[:,:,3],sa[:,:,3]);same(shown,image(actual('placed','png')))
outside_glyph=ea[:,:,3]==0;assert np.array_equal(ea[outside_glyph],sa[outside_glyph]);assert np.array_equal(ea[ea[:,:,3]==255],sa[ea[:,:,3]==255])
assert np.all(sa[62:218,72:228,1:3]==0)
straight=np.array(expected).astype(int)-np.array(shown).astype(int);assert int(np.any(straight!=0,axis=2).sum())==5 and int(abs(straight).max())==2
(out/'edit-turn42-straight-rgba-hypothesis.json').write_text(json.dumps({'status':'Failed hypothesis','different_straight_RGBA_pixels':5,'max_channel_difference':2,'limitation':'The OS clipboard PNG and placed export differ in straight red at five mixed red/black translucent pixels. Alpha geometry and opaque pixels match exactly; presumed conversion/rounding path not independently established. Not counted as exact arbitrary-angle RGB proof. Separate pure-red translucent matrix below verifies the no-fringe acceptance condition exactly.'},indent=2)+'\n',encoding='utf-8')
for suffix in ['placed','quarter-only','alpha-placed']:
 d=doc(suffix);scope=copy.deepcopy(before);scope['layers'][0]['image']=d['layers'][0]['image'];assert scope==d
assert doc('undone')==before and doc('redone')==placed==doc('reopened');same(image(actual('reopened','png')),shown)
alpha_source=image((out/'edit-turn42-alpha-source.png').read_bytes());same(alpha_source,original.crop((400,300,500,380)));assert set(map(tuple,np.array(alpha_source).reshape(-1,4)))=={(255,0,0,128)}
alpha=[]
for i,size in enumerate([128,182,258,365],1):
 a=np.array(cp(f'alpha-{i}'));assert a.shape==(size,size,4);mask=a[:,:,3]>0;assert np.all(a[:,:,:3][mask]==[255,0,0]) and int(a[:,:,3].max())==128 and len(np.unique(a[:,:,3]))>2;alpha.append({'turn':i,'size':size,'nonzero_alpha_pixels':int(mask.sum()),'alpha_levels':len(np.unique(a[:,:,3])),'all_visible_rgb_exact_red':True})
alpha_doc=doc('alpha-placed');assert doc('alpha-undone')==before and doc('alpha-redone')==alpha_doc==doc('alpha-reopened');same(pixels(alpha_doc),image(actual('alpha-placed','png')));same(image(actual('alpha-reopened','png')),pixels(alpha_doc))
# The final 365px square has centred mathematical origin267.5,157.5.
# Ordinary raster placement rounds its position to whole paper pixels.
alpha_expected=original.copy();alpha_expected.paste((0,0,0,0),(400,300,500,380));alpha_expected.alpha_composite(cp('alpha-4'),(268,158));same(alpha_expected,pixels(alpha_doc))
report={'status':'Pass','before_fix_quarter_turn_exactly_kept_top_left_and_shifted_centre_by_10_each_axis':True,'after_fix_quarter_turn_exact_at_100_80_same_centre150_140':True,'flip_h_v_quarter_source_rgba_exact':True,'45degree_final156square_at72_62_same_centre_alpha_geometry_opaque_pixels_exact':True,'arbitrary_mixed_colour_clipboard_RGB_limitation':'Five translucent red/black pixels differ up to2 straight red levels from clipboard PNG; no exact RGB claim for this mixed-colour arbitrary turn. Native whole export/project round trips exact.','unrelated_layers_fields_and_neighbours_exact':True,'complete_undo_redo_two_native_project_png_reopens_exact':True,'repeated_translucent_rotations':alpha,'final365square_at_rounded268_158_full_RGBA_exact':True,'sha256':hashes}
(out/'edit-turn42-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
