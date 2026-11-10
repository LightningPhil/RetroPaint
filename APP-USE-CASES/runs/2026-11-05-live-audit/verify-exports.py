"""Independent decoding of actual mouse-driven downloads; no app imports."""
import base64
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import shutil
import struct

from PIL import Image, __version__ as pillow_version

root = Path(__file__).resolve().parents[3]
out = root / 'test-results/audit-2026-11-05/mouse'
downloads = Path.home() / 'Downloads'
report = {'pillow': pillow_version, 'images': [], 'projects': []}

for source in downloads.glob('mouse-audit-*'):
    if source.is_file():
        shutil.copyfile(source, out / source.name)

reference = Image.open(out / 'mouse-audit-shapes.png').convert('RGBA')
for extension in ['png', 'jpg', 'webp', 'bmp', 'gif', 'tif']:
    file = out / f'mouse-audit-shapes.{extension}'
    with Image.open(file) as picture:
        picture.load()
        assert picture.size == (960, 640)
        exact = picture.convert('RGBA').tobytes() == reference.tobytes()
        if extension in ['png', 'webp', 'bmp', 'tif']:
            assert exact, f'{extension} changed opaque source pixels'
        report['images'].append({'file': file.name, 'format': picture.format,
                                 'size': picture.size, 'mode': picture.mode,
                                 'exact_rgba': exact,
                                 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})

for name in ['baseline.retropaint', 'brushes.retropaint',
             'mouse-audit-shapes.retropaint', 'mouse-audit-shapes (1).retropaint']:
    file = out / name
    project = json.loads(file.read_text(encoding='utf-8'))
    assert (project['width'], project['height']) == (960, 640)
    for layer in project['layers']:
        with Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))) as source:
            source.load()
            assert source.size == (960, 640)
    solids = [body for layer in project['layers']
              for body in (layer.get('cad') or {}).get('bodies', [])]
    if name.endswith('(1).retropaint'):
        assert len(solids) == 9
        assert {b['solid']['shape'] for b in solids} == {
            'box', 'sphere', 'cylinder', 'cone', 'torus', 'tube', 'pyramid', 'wedge'}
        cube = next(b for b in solids if b['name'] == 'Cube')
        assert cube['position'] == [30, 0, 10] and cube['rotation'] == [0, 0, 45]
        assert cube['scale'] == [2, 1.5, 1] and cube['color'] == '#57bfca'
        copy = next(b for b in solids if b['name'] == 'Live wedge')
        assert copy['position'] == [70, -40, 10] and copy['scale'] == [2, 2, 2]
    report['projects'].append({'file': name, 'version': project['version'],
                               'layers': len(project['layers']), 'solids': len(solids),
                               'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})

file = out / 'mouse-audit-shapes-3d-mm.stl'
data = file.read_bytes()
count = struct.unpack_from('<I', data, 80)[0]
assert len(data) == 84 + 50 * count
edges = Counter()
winding = Counter()
mins, maxs = [float('inf')] * 3, [float('-inf')] * 3
volume = 0.0
for i in range(count):
    values = struct.unpack_from('<12fH', data, 84 + i * 50)
    normal = values[:3]
    a, b, c = (tuple(values[j:j+3]) for j in [3, 6, 9])
    cross = ((b[1]-a[1])*(c[2]-a[2])-(b[2]-a[2])*(c[1]-a[1]),
             (b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]),
             (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
    assert sum(n*v for n, v in zip(normal, cross)) > 0
    volume += (a[0]*(b[1]*c[2]-b[2]*c[1]) +
               a[1]*(b[2]*c[0]-b[0]*c[2]) +
               a[2]*(b[0]*c[1]-b[1]*c[0])) / 6
    for vertex in [a, b, c]:
        for axis in range(3):
            mins[axis] = min(mins[axis], vertex[axis])
            maxs[axis] = max(maxs[axis], vertex[axis])
    for start, end in [(a, b), (b, c), (c, a)]:
        edge = tuple(sorted([start, end]))
        edges[edge] += 1
        winding[edge] += 1 if start < end else -1
assert all(count == 2 for count in edges.values()), 'STL has open/nonmanifold edges'
assert not any(winding.values()), 'STL has inconsistent winding'
size = [b-a for a, b in zip(mins, maxs)]
assert all(abs(a-b) < .001 for a, b in zip(size, [140, 110, 40]))
assert abs(mins[2]) < .001 and volume > 0
assert abs(volume / 1000 - 81.01) < .005, 'Independent volume differs from UI'
report['stl'] = {'file': file.name, 'triangles': count, 'min': mins, 'max': maxs,
                 'size_mm': size, 'volume_mm3': volume, 'closed': True,
                 'consistent_winding': True,
                 'sha256': hashlib.sha256(data).hexdigest()}
(out / 'independent-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
