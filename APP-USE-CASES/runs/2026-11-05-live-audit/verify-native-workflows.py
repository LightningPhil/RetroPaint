"""Independently decode actual files opened/saved through the Windows picker."""
import base64
import io
import json
from pathlib import Path
import shutil

from PIL import Image, ImageChops

root = Path(__file__).resolve().parents[3]
downloads = Path.home() / 'Downloads'
out = root / 'test-results/audit-2026-11-05/mouse'
report = {'imports': [], 'gradients': [], 'tolerance': []}

def project(name):
    source = downloads / (name + '.retropaint')
    shutil.copyfile(source, out / source.name)
    return json.loads(source.read_text(encoding='utf-8'))

def pixels(doc):
    return Image.open(io.BytesIO(base64.b64decode(doc['layers'][0]['image'].split(',')[1]))).convert('RGBA')

mixed = project('mouse-audit-labels-after')
assert mixed == project('mouse-audit-native-reopened-labels')
assert mixed == project('mouse-audit-after-rejected-projects')
report['mixed_reopen_exact'] = True
report['damaged_imports_atomic'] = True
assert project('mouse-audit-photo-reopen-before') == project('mouse-audit-photo-reopen-after')
report['photo_reopen_exact'] = True

for name, extension in [('jpeg', 'jpg'), ('webp', 'webp'), ('bmp', 'bmp'), ('gif', 'gif'), ('tiff', 'tif')]:
    doc = project('mouse-audit-import-' + name)
    actual = pixels(doc)
    source = Image.open(downloads / ('mouse-audit-shapes.' + extension)).convert('RGBA')
    error = max(high for low, high in ImageChops.difference(actual, source).getextrema())
    assert actual.size == (960, 640) and len(doc['layers']) == 1
    assert error <= (1 if name == 'jpeg' else 0)
    report['imports'].append({'format': name, 'dimensions': actual.size, 'maximum_channel_error': error})

baseline = project('mouse-audit-fill-baseline')
assert baseline == project('mouse-audit-gradient-cancelled')
assert baseline == project('mouse-audit-gradient-after-undo')
report['gradient_cancel_and_undo_exact'] = True
for name in ['sunset', 'rainbow', 'ocean', 'candy']:
    doc = project('mouse-audit-gradient-' + name)
    actual = pixels(doc)
    bounds = ImageChops.difference(pixels(baseline), actual).convert('RGB').getbbox()
    # Independently retained black outline and isolated blue region are unchanged.
    assert bounds == (319, 56, 570, 250)
    source = downloads / ('mouse-audit-gradient-' + name + '.png')
    assert Image.open(source).convert('RGBA').tobytes() == actual.tobytes()
    shutil.copyfile(source, out / source.name)
    report['gradients'].append({'preset': name, 'changed_bounds': bounds, 'png_matches_project': True})

for tolerance, expected in [(0, 7000), (40, 21000)]:
    name = 'mouse-audit-fill-tolerance-' + str(tolerance)
    doc = project(name)
    source = downloads / (name + '.png')
    actual = Image.open(source).convert('RGBA')
    assert actual.tobytes() == pixels(doc).tobytes()
    count = sum(1 for colour in actual.get_flattened_data() if colour == (229, 57, 53, 255))
    assert count == expected
    assert actual.getpixel((375, 150)) == (128, 128, 128, 255)
    shutil.copyfile(source, out / source.name)
    report['tolerance'].append({'value': tolerance, 'filled_pixels': count, 'disconnected_island_unchanged': True})

(out / 'native-workflows-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
