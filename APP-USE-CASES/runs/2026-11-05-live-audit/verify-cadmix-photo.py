"""Check actual native CADMIX save/reopen/edit/Undo outputs independently."""
import copy, hashlib, io, json, struct
from collections import Counter
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[3]
out = root/'test-results/audit-2026-11-05/mouse'
downloads = Path.home()/'Downloads'
hashes = {}
def retain(name):
    data = (downloads/name).read_bytes()
    (out/name).write_bytes(data)
    hashes[name] = hashlib.sha256(data).hexdigest()
    return data
def doc(name): return json.loads(retain('mouse-audit-cadmix-'+name+'.retropaint'))
baseline = doc('photo-baseline')
edited = doc('photo-edited25')
restored = doc('photo-reopened-undo')
compact = doc('after-compact')
assert baseline == restored
for i in [0,1,3]: assert baseline['layers'][i] == edited['layers'][i]
before_cad = baseline['layers'][2]['cad']
after_cad = edited['layers'][2]['cad']
assert before_cad['view'] == after_cad['view']
assert before_cad['view']['projection'] == 'perspective'
assert before_cad['bodies'][0]['solid']['thickness'] == 3
assert after_cad['bodies'][0]['solid']['thickness'] == 2.5
expected = copy.deepcopy(baseline)
expected['layers'][2]['cad']['bodies'][0]['solid']['thickness'] = 2.5
# The CAD preview raster is regenerated after a real geometry edit.
expected['layers'][2]['image'] = edited['layers'][2]['image']
assert expected == edited
compact_expected = copy.deepcopy(baseline['layers'])
compact_expected[2]['image'] = compact['layers'][2]['image']
assert compact_expected == compact['layers']
assert baseline['crop'] == compact['crop']
a = Image.open(io.BytesIO(retain('mouse-audit-cadmix-photo-baseline.png'))).convert('RGBA')
b = Image.open(io.BytesIO(retain('mouse-audit-cadmix-photo-reopened-undo.png'))).convert('RGBA')
assert a.size == (768,512) and a.tobytes() == b.tobytes()
data = retain('mouse-audit-cadmix-photo-edited25-3d-mm.stl')
count = struct.unpack_from('<I',data,80)[0]
assert len(data) == 84+50*count
edges, directions, points, volume = Counter(), Counter(), [], 0
for i in range(count):
    v = struct.unpack_from('<12f',data,84+50*i)
    a,b,c = [tuple(v[j:j+3]) for j in [3,6,9]]
    points += [a,b,c]
    volume += sum(a[j]*(b[(j+1)%3]*c[(j+2)%3]-b[(j+2)%3]*c[(j+1)%3]) for j in range(3))/6
    for start,end in [(a,b),(b,c),(c,a)]:
        edge=tuple(sorted([start,end])); edges[edge]+=1
        directions[edge]+=1 if start<end else -1
assert all(n==2 for n in edges.values()) and not any(directions.values()) and volume>0
bounds = [[min(p[j] for p in points),max(p[j] for p in points)] for j in range(3)]
assert bounds == [[-10,25],[-10,10],[0,20]]
report = {'project_reopen_and_undo_exact':True,'non_cad_layers_preserved_during_edit':True,
          'camera_preserved_during_edit':True,'only_recipe_change_wall_mm':[3,2.5],
          'compact_cancel_recipes_non_cad_pixels_and_crop_exact':True,
          'compact_cad_preview_raster_regenerated':True,'repeated_png_pixel_exact':[768,512],
          'edited_stl':{'triangles':count,'closed_outward':True,'bounds_mm':bounds,'volume_mm3':volume},
          'sha256':hashes}
ortho=doc('photo-orthographic');ortho_edit=doc('ortho-edited25');ortho_undo=doc('ortho-undone')
assert ortho==ortho_undo and ortho['layers'][2]['cad']['view']['projection']=='orthographic'
ortho_expected=copy.deepcopy(ortho)
ortho_expected['layers'][2]['cad']['bodies'][0]['solid']['thickness']=2.5
ortho_expected['layers'][2]['image']=ortho_edit['layers'][2]['image']
assert ortho_expected==ortho_edit
first=Image.open(io.BytesIO(retain('mouse-audit-cadmix-photo-orthographic.png'))).convert('RGBA')
last=Image.open(io.BytesIO(retain('mouse-audit-cadmix-ortho-undone.png'))).convert('RGBA')
assert first.size==(768,512) and first.tobytes()==last.tobytes()
report['orthographic_native_reopen_edit_apply_and_whole_document_undo_exact']=True
report['orthographic_camera_photo_recipe_text_preserved_during_edit']=True
report['orthographic_repeated_png_pixel_exact']=[768,512]
(out/'cadmix-photo-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
