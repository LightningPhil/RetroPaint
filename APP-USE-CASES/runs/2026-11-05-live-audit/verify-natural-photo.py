"""Independent decoding and preservation checks for the live natural-photo journey."""
import base64
import hashlib
import io
import json
from pathlib import Path
from PIL import Image, ImageChops
from pypdf import PdfReader

root = Path(__file__).resolve().parents[3]
out = root/'test-results/audit-2026-11-05/mouse'
downloads = Path.home()/'Downloads'
hashes = {}
def retain(name):
    data = (downloads/name).read_bytes()
    (out/name).write_bytes(data)
    hashes[name] = hashlib.sha256(data).hexdigest()
    return data
def doc(stem): return json.loads(retain('mouse-audit-journey4-'+stem+'.retropaint'))
def pixels(url): return Image.open(io.BytesIO(base64.b64decode(url.split(',')[1]))).convert('RGBA')

final = doc('final')
assert final == doc('reopened') == doc('cancelled') == doc('print-cancelled'), 'Whole-project roundtrip/cancellation changed data'
assert (final['width'], final['height']) == (2100,1398)
assert len(final['layers']) == 2
source, caption = final['layers']
assert caption['name'] == 'Landscape caption' and caption['visible'] and source['visible']
assert source.get('photo') and not caption.get('photo')
original = Image.open(out/'photo-natural-original.jpg').convert('RGBA')
saved_source = pixels(source['image'])
assert saved_source.size == original.size
extrema = ImageChops.difference(original,saved_source).getextrema()
assert all(high <= 1 for low,high in extrema), extrema  # independent JPEG decoder rounding
crop = final['crop']
crop_px = [round(crop[k]*size) for k,size in [('x',2100),('y',1398),('width',2100),('height',1398)]]
assert crop_px == [150,100,1800,1200]
cap = pixels(caption['image'])
assert cap.size == original.size
cap_bounds = cap.getchannel('A').getbbox()
assert cap_bounds and cap_bounds[0]>=150 and cap_bounds[1]>=100 and cap_bounds[2]<=1950 and cap_bounds[3]<=1300
png = Image.open(io.BytesIO(retain('mouse-audit-journey4-final.png'))).convert('RGBA')
reopened = Image.open(io.BytesIO(retain('mouse-audit-journey4-reopened.png'))).convert('RGBA')
assert png.size == (1800,1200)
assert png.tobytes() == reopened.tobytes(), 'Reopened PNG changed'
assert png.getchannel('A').getextrema() == (255,255)
pdf = PdfReader(out/'journey4-print.pdf')
assert len(pdf.pages) == 1 and len(pdf.pages[0].images) == 1
assert pdf.pages[0].images[0].image.convert('RGB').tobytes() == png.convert('RGB').tobytes()
settings = source['photo']['settings']
assert settings['exposure'] == .05 and settings['contrast'] == 11 and settings['vibrance'] == 12
assert settings['balance'] == [1,1,1]
report = {'natural_source':[2100,1398], 'crop_pixels':crop_px, 'caption_bounds_on_source':cap_bounds,
          'original_retained_max_decoder_error':max(high for low,high in extrema),
          'whole_project_roundtrip_and_cancel_exact':True, 'reopened_png_pixel_exact':True,
          'export_size':png.size, 'source_photo_recipe_retained':True,
          'print_pdf_one_page_image_pixel_exact':True, 'print_cancel_project_exact':True, 'sha256':hashes}
(out/'natural-photo-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
