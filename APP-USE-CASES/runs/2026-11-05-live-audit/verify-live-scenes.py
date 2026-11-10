"""Decode actual browser downloads; independent of application render code."""
import base64
import hashlib
import io
import json
from pathlib import Path
import shutil

from PIL import Image, ImageChops

root = Path(__file__).resolve().parents[3]
downloads = Path.home() / 'Downloads'
out = root / 'test-results/audit-2026-11-05/mouse'
report = {'stamp_sheets': [], 'graphics_recovery': [], 'labels': {}}
for source in downloads.glob('mouse-audit-*'):
    if source.is_file():
        shutil.copyfile(source, out / source.name)

def project(name):
    return json.loads((out / (name + '.retropaint')).read_text(encoding='utf-8'))

def rgba(data):
    return Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))).convert('RGBA')

before = project('mouse-audit-wiki-lost-preview-before')
after = project('mouse-audit-wiki-preview-after')
for old, new in zip(before['layers'], after['layers']):
    assert old['name'] == new['name']
    if old.get('cad'):
        assert old['cad']['bodies'] == new['cad']['bodies'], 'Help changed solid recipes'
        old_bounds = rgba(old['image']).getchannel('A').getbbox()
        new_bounds = rgba(new['image']).getchannel('A').getbbox()
        assert old_bounds is None and new_bounds is not None, 'CAD graphics recovery missing'
        report['graphics_recovery'].append({'layer': old['name'], 'bodies': len(new['cad']['bodies']),
                                           'before_alpha_bounds': old_bounds, 'after_alpha_bounds': new_bounds})
    else:
        assert old['image'] == new['image'] and old.get('objects') == new.get('objects'), 'Help altered paint or labels'

labels = project('mouse-audit-labels-after')
annotation = next(layer for layer in labels['layers'] if layer['name'] == 'Annotations')['objects']
assert len(annotation) == 2 and len({o['id'] for o in annotation}) == 2
for obj in annotation:
    assert obj['kind'] == 'text' and obj['callout']['text'] == 'Castle'
    assert obj['size'] == 25 and 'Georgia' in obj['font']
    assert not obj['callout']['border'] and not obj['callout']['rounded']
    assert obj['width'] < obj['callout']['wrapWidth'], 'Short label did not auto-size'
for old, new in zip(after['layers'], labels['layers']):
    if old.get('cad'):
        assert old['cad']['bodies'] == new['cad']['bodies'], 'Labelling changed model geometry'
report['labels'] = {'count': 2, 'text': 'Castle', 'font': '25px Georgia',
                    'unique_ids': True, 'model_recipes_unchanged': True}

for category in ['animals', 'nature', 'rides', 'adventure', 'faces', 'treats', 'play', 'shapes']:
    name = 'mouse-audit-stamps-' + category
    doc = project(name)
    picture = Image.open(out / (name + '.png')).convert('RGBA')
    assert picture.size == (640, 480) and (doc['width'], doc['height']) == picture.size
    objects = doc['layers'][0]['objects']
    count = 5 if category == 'shapes' else 18
    expected_kind = 'path' if category == 'shapes' else 'stamp'
    assert len(objects) == count and all(o['kind'] == expected_kind for o in objects)
    # Independent cells from the mouse grid (six columns, three rows).
    # Composite over white so transparent borders do not masquerade as artwork.
    opaque = Image.new('RGBA', picture.size, 'white')
    opaque.alpha_composite(picture)
    ink = ImageChops.difference(opaque.convert('RGB'), Image.new('RGB', picture.size, 'white'))
    cells = []
    for i in range(count):
        cx, cy = 55 + (i % 6) * 103, 82 + (i // 6) * 134
        bounds = ink.crop((max(0, cx-48), max(0, cy-48), min(640, cx+48), min(480, cy+48))).getbbox()
        assert bounds is not None, f'{category} stamp {i+1} is blank'
        cells.append(bounds)
    report['stamp_sheets'].append({'category': category, 'count': count, 'nonblank_cells': len(cells),
                                   'sha256': hashlib.sha256((out / (name + '.png')).read_bytes()).hexdigest()})

first = Image.open(out / 'mouse-audit-spiro-before-reset.png').convert('RGBA')
second = Image.open(out / 'mouse-audit-spiro-after-reset.png').convert('RGBA')
assert first.size == second.size == (640, 480) and first.tobytes() == second.tobytes(), 'Reset kit changed the drawing'
doc = project('mouse-audit-spiro-after-reset')
report['spiro'] = {'reset_preserves_exact_rgba': True, 'size': first.size,
                   'editable_pieces': len(doc['layers'][0]['objects'])}
report['status'] = 'Pass'
(out / 'live-scenes-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
