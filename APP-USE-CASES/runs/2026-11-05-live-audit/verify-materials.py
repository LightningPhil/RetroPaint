"""Decode actual neon/glitter exports and check pigment, alpha and preservation."""
import base64
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageChops

root=Path(__file__).resolve().parents[3]
out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(retain('mouse-audit-'+stem+'.retropaint'))
def pixels(data):return Image.open(io.BytesIO(data)).convert('RGBA')
def layer(doc,index):return pixels(base64.b64decode(doc['layers'][index]['image'].split(',')[1]))
blue=doc('neon-blue');both=doc('neon-blue-pink')
a,b=layer(blue,1),layer(both,1)
assert a.crop((100,150,850,300)).tobytes()==b.crop((100,150,850,300)).tobytes()
transparent=doc('neon-transparent');assert transparent==doc('neon-after-exports')
png=pixels(retain('mouse-audit-neon-transparent.png'))
assert png.tobytes()==layer(transparent,1).tobytes()
assert png.getpixel((20,20))[3]==0
assert png.getpixel((480,220))[2]>png.getpixel((480,220))[0]+100
assert png.getpixel((480,420))[0]>png.getpixel((480,420))[2]+100
assert png.getpixel((480,220))[3]==255 and 0<png.getpixel((480,200))[3]<255
assert png.getpixel((100,200))[3]==0  # no rectangular halo backdrop
jpeg=pixels(retain('mouse-audit-neon-transparent.jpg'))
assert jpeg.crop((0,0,100,100)).getextrema()==((255,255),(255,255),(255,255),(255,255))
retain('mouse-audit-neon-blue-pink.png')
glitter=doc('glitter-gold');first=pixels(retain('mouse-audit-glitter-gold.png'));later=pixels(retain('mouse-audit-glitter-after-wait-zoom.png'))
assert first.tobytes()==later.tobytes(), 'Committed glitter changed after waiting/zooming'
assert glitter['layers'][2]['live']=={'strokes':[],'fills':[],'sparkles':[]}
saved=layer(glitter,2)
assert first.getchannel('A').tobytes()==saved.getchannel('A').tobytes()
opaque_colours=set();max_premult_error=0
for source,exported in zip(saved.getdata(),first.getdata()):
    alpha=source[3]
    if alpha==255:
        assert source==exported
        opaque_colours.add(source)
    # Canvas compositing can round unpremultiplied low-alpha RGB. Compare visible
    # premultiplied contribution rather than silently relaxing opaque pigment.
    max_premult_error=max(max_premult_error,*(abs(round(source[c]*alpha/255)-round(exported[c]*alpha/255)) for c in range(3)))
assert max_premult_error<=1 and len(opaque_colours)>100
assert first.getpixel((480,320))[0]>first.getpixel((480,320))[2]
assert first.getpixel((20,20))[3]==0
report={'neon_blue_unchanged':True,'neon_png_exact_to_visible_layer':True,'neon_two_tints_and_translucent_halo':True,
 'jpeg_white_background':True,'exports_preserve_entire_project':True,'glitter_wait_zoom_pixels_exact':True,
 'glitter_opaque_pixels_exact':True,'glitter_opaque_colours':len(opaque_colours),'glitter_max_premultiplied_error':max_premult_error,'sha256':hashes}
(out/'material-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
