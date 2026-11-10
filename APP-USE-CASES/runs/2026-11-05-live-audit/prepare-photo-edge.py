"""Retain the natural photo while adding a transparent border for effect checks."""
from pathlib import Path
from PIL import Image,ImageDraw
import base64,io,json,hashlib
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures/photo62';out.mkdir(parents=True,exist_ok=True)
source=(Path.home()/'Downloads/mouse-audit-photo62-before.retropaint').read_bytes();d=json.loads(source)
im=Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA');draw=ImageDraw.Draw(im)
draw.rectangle((0,0,19,1397),fill=(0,0,0,0));b=io.BytesIO();im.save(b,format='PNG');d['layers'][0].update(paper=None,image='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode())
data=json.dumps(d,separators=(',',':')).encode();(out/'transparent-edge.retropaint').write_bytes(data)
(out/'manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source).hexdigest(),'fixture_sha256':hashlib.sha256(data).hexdigest(),'change':'Only left20px cleared to transparent; all other natural-photo pixels exact.'},indent=2)+'\n')
print(out)
