"""Independent MIX composition, alpha, external clipboard and Undo verification."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';fixtures=root/'test-results/audit-2026-11-05/fixtures';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(retain('mouse-audit-'+stem+'.retropaint'))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
def layer(doc,index):return image(base64.b64decode(doc['layers'][index]['image'].split(',')[1]))
baseline=image(retain('mouse-audit-mix-baseline.png'))
assert baseline.tobytes()==Image.open(fixtures/'mix-reference.png').convert('RGBA').tobytes()
full=doc('mix-transparent');half=doc('mix-transparent-half')
assert full==doc('mix-after-exports') and half==doc('mix-half-after-exports')
assert [x['name'] for x in full['layers']]==['Paper','Backdrop','Character','Caption']
assert [x['visible'] for x in full['layers']]==[False,False,True,True]
stamp=Image.open(downloads/'mouse-audit-stamps-animals.png').convert('RGBA').crop((14,39,97,123))
for stem,document,alpha in [('mix-transparent',full,255),('mix-transparent-half',half,128)]:
    character=layer(document,2)
    character.putalpha(character.getchannel('A').point(lambda value:round(value*alpha/255)))
    expected=Image.alpha_composite(character,layer(document,3));expected.paste(stamp,(650,79))
    png=image(retain('mouse-audit-'+stem+'.png'))
    assert png.tobytes()==expected.tobytes(), stem+' did not preserve exact alpha/composition'
    assert png.getpixel((20,20))==(0,0,0,0) and png.getpixel((150,140))==(255,0,0,alpha)
    jpeg=image(retain('mouse-audit-'+stem+'.jpg'))
    assert jpeg.crop((0,0,40,40)).getextrema()==((255,255),(255,255),(255,255),(255,255))
    white=Image.alpha_composite(Image.new('RGBA',png.size,'white'),expected)
    # JPEG is lossy: use an interior flat patch, away from edges and font/emoji detail.
    assert max(abs(a-b) for a,b in zip(jpeg.getpixel((150,140)),white.getpixel((150,140))))<=2
pasted=doc('mix-external-paste')
assert all(pasted['layers'][i]==half['layers'][i] for i in [0,1,3])
expected=layer(half,2);source=Image.open(fixtures/'fill-tolerance.png').convert('RGBA')
expected.alpha_composite(source,(280,120))
assert expected.tobytes()==layer(pasted,2).tobytes(), 'External Paint pixels moved or changed'
assert pasted['layers'][2]['opacity']==.5
for stem in ['mix-external-paste-undone','mix-text-only-before-fix','mix-text-only-after-fix','mix-paste-button-fallback']:
    assert doc(stem)==half, stem+' changed the source document'
report={'mix_baseline_independent_reference_exact':True,'transparent_and_half_alpha_png_exact':True,
 'jpeg_white_backing':True,'export_source_stacks_exact':True,'external_paint_clipboard_source_size':source.size,
 'pasted_at_pixels':[280,120],'pasted_pixels_exact':True,'other_layers_exact':True,'paste_undo_project_exact':True,
 'text_only_and_paste_fallback_project_exact':True,'sha256':hashes}
(out/'mix-and-paste-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
