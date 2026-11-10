"""Independent PNG/source checks for the actual live neural jobs."""
import hashlib
import json
from pathlib import Path
import shutil

from PIL import Image, ImageChops

root = Path(__file__).resolve().parents[3]
downloads = Path.home() / 'Downloads'
out = root / 'test-results/audit-2026-11-05/mouse'
names = ['mouse-audit-enhance-source.png', 'mouse-audit-enhance-source-after.png',
         'mouse-audit-enhance-source.retropaint', 'mouse-audit-enhance-source-after.retropaint',
         'mouse-audit-spiro-after-reset-2x-enhanced.png', 'mouse-audit-enhance-source-4x-enhanced.png']
for name in names:
    shutil.copyfile(downloads / name, out / name)
source = Image.open(out / names[0]).convert('RGBA')
after = Image.open(out / names[1]).convert('RGBA')
assert source.size == after.size == (640, 480)
assert source.tobytes() == after.tobytes(), 'Enhancement changed source pixels'
before_project = json.loads((out / names[2]).read_text(encoding='utf-8'))
after_project = json.loads((out / names[3]).read_text(encoding='utf-8'))
assert before_project == after_project, 'Enhancement changed editable project data'
report = {'source_rgba_unchanged': True, 'project_unchanged': True, 'outputs': [],
          'limits': 'Opaque artwork fixture only. Transparent margins, independent tile-boundary stress, CPU fallback and large sources remain untested.'}
for scale, name in [(2, names[4]), (4, names[5])]:
    picture = Image.open(out / name)
    assert picture.format == 'PNG'
    picture = picture.convert('RGBA')
    assert picture.size == (640*scale, 480*scale)
    nearest = source.resize(picture.size, Image.Resampling.NEAREST)
    assert ImageChops.difference(picture, nearest).convert('RGB').getbbox(), 'Output is just nearest-neighbour scaling'
    assert picture.getchannel('A').getextrema() == source.getchannel('A').getextrema() == (255, 255)
    report['outputs'].append({'file': name, 'scale': scale, 'size': picture.size,
                               'alpha_range': picture.getchannel('A').getextrema(),
                               'differs_from_nearest_neighbour': True,
                               'sha256': hashlib.sha256((out / name).read_bytes()).hexdigest()})
report['status'] = 'Pass'
(out / 'enhancement-verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
shutil.copyfile(downloads / 'main.scad', out / 'castle-gatehouse.scad')
code = (out / 'castle-gatehouse.scad').read_text(encoding='utf-8')
assert code.startswith('// Four hollow towers') and 'tower_height=33;' in code and 'module tower()' in code
print(json.dumps(report, indent=2))
