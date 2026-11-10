"""Check native text transforms, retained detail and explicit off-paper trimming."""
import base64,copy,hashlib,io,json,math
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(retain('mouse-audit-vector-'+name+'.retropaint'))
def png(name):return Image.open(io.BytesIO(retain('mouse-audit-vector-'+name+'.png'))).convert('RGBA')
def image(o):return Image.open(io.BytesIO(base64.b64decode(o['image'].split(',')[1]))).convert('RGBA')
def canonical(doc):
    d=copy.deepcopy(doc)
    for l in d['layers']:
        for o in l.get('objects',[]):
            if o.get('wet') is False:o.pop('wet')
    return d
baseline=doc('mixed-baseline');transformed=doc('text-transformed');reopened=doc('text-reopened')
original=baseline['layers'][0]['objects'];changed=transformed['layers'][0]['objects']
assert len(original)==len(changed)==9
for i in range(9):
    a,b=copy.deepcopy(original[i]),copy.deepcopy(changed[i])
    if i==6:
        assert a['kind']==b['kind']=='text' and a['id']==b['id']
        angle=math.radians(-12);ca,sa=1.5*math.cos(angle),1.5*math.sin(angle)
        expected=[ca,sa,-sa,ca,345-ca*150+sa*41.5,462.25-sa*150-ca*41.5]
        assert all(abs(x-y)<1e-8 for x,y in zip(b['matrix'],expected))
        a.pop('matrix');b.pop('matrix')
    assert a==b
assert canonical(transformed)==canonical(reopened)
assert png('text-transformed').tobytes()==png('text-reopened').tobytes()
placed=doc('offpaper-placed');undone=doc('offpaper-undone')
assert undone==reopened
before=reopened['layers'][0]['objects'][4];after=placed['layers'][0]['objects'][4]
assert before['width']==96 and after['width']==83 and after['matrix']==[1.5,0,0,1.5,-.5,500]
trimmed=image(after);crop=image(before).crop((13,0,96,64))
assert trimmed.crop((1,0,83,64)).tobytes()==crop.crop((1,0,83,64)).tobytes()
# The cut is at source x13⅓. Its first retained bitmap column is ⅔ covered;
# all complete columns stay exact and boundary RGB has at most one level of
# canvas premultiply/unpremultiply rounding.
for y in range(64):
    a,b=trimmed.getpixel((0,y)),crop.getpixel((0,y))
    assert a[3]==round(b[3]*2/3)
    assert all(abs(x-z)<=1 for x,z in zip(a[:3],b[:3]))
for i in range(9):
    if i!=4:assert placed['layers'][0]['objects'][i]==reopened['layers'][0]['objects'][i]
detail=doc('detail-transformed');objects=detail['layers'][0]['objects']
assert objects[:9]==reopened['layers'][0]['objects'] and len(objects)==10
new=objects[-1];assert new['kind']=='raster' and (new['width'],new['height'])==(96,64)
source=Image.open(root/'test-results/audit-2026-11-05/fixtures/vector-detail-checker.png').convert('RGBA')
assert image(new).tobytes()==source.tobytes()
assert all(abs(a-b)<1e-8 for a,b in zip(new['matrix'],[0,1,-1,0,730,384]))
expected=png('text-reopened');expected.alpha_composite(source.transpose(Image.Transpose.ROTATE_270),(666,384))
assert expected.tobytes()==png('detail-transformed').tobytes()
report={'text_identity_styling_and_neighbours_preserved':True,'text_transform_independent_matrix_exact':True,
        'native_text_reopen_render_pixel_exact':True,'native_text_reopen_semantically_exact':True,
        'reopen_normalizes_optional_wet_false_to_absent_on_two_dry_brushes':True,
        'offpaper_trim_source_crop':[13,0,96,64],'fractional_first_column_coverage':2/3,
        'complete_trimmed_columns_pixel_exact':True,'offpaper_undo_whole_project_exact':True,
        'detail_shrink_96_to24_then_restore96_before_place_source_pixel_exact':True,
        'detail_original_dimensions':[96,64],'detail_90degree_reference_whole_png_exact':True,'sha256':hashes}
(out/'vector-transform-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
