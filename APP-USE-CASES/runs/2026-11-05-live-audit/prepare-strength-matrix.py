"""Prepare an independent white/blue PLAY background and source-over oracle."""
from pathlib import Path
from PIL import Image, ImageDraw
import base64, hashlib, io, json
root = Path(__file__).resolve().parents[3]
out = root / 'test-results/audit-2026-11-05/fixtures/strength53'
out.mkdir(parents=True, exist_ok=True)
d = json.loads((root / 'test-results/audit-2026-11-05/manual-blockers/PLAY.retropaint').read_bytes())
assert (d['width'], d['height']) == (960, 640)
im = Image.new('RGBA', (960, 640), 'white')
ImageDraw.Draw(im).rectangle((500, 80, 899, 549), fill='#1E88E5')
b = io.BytesIO(); im.save(b, format='PNG')
d['layers'][0]['image'] = 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
data = json.dumps(d, separators=(',', ':')).encode()
(out / 'white-blue.retropaint').write_bytes(data)
im.save(out / 'white-blue.png')
plan = {'fixture_sha256': hashlib.sha256(data).hexdigest(), 'brush': 'Squeaky Marker', 'size': 22,
        'ink': '#E53935', 'strengths': [1, .15], 'stroke_rows': [180, 360],
        'white_x': [100, 350], 'blue_x': [580, 830], 'overlap_row': 360,
        'oracle': 'Source-over channel arithmetic; centre RGB within 2/255. Outside stroke radius+2 unchanged. Whole-project Undo/Redo exact.'}
(out / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
print(out)
