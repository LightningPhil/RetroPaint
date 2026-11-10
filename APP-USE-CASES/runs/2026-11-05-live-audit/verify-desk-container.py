"""Independent checks of the actual custom desk-container delivery files.

This is the 40 x 30 x 30 mm block variant, not the catalogue's 20 mm fixture.
No RetroPaint serializer, modeller or repair function is imported.
"""
import base64
from collections import Counter
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import struct

from PIL import Image, ImageChops

root = Path(__file__).resolve().parents[3]
downloads = Path.home() / 'Downloads'
out = root / 'test-results/audit-2026-11-05/mouse'
stem = 'mouse-audit-journey7-desk-pot'
names = [stem + suffix for suffix in ['.retropaint', '.png', '-3d-mm.stl', '-reopened.retropaint', '-reopened.png']]
for name in names:
    shutil.copyfile(downloads / name, out / name)
doc = json.loads((out / (stem + '.retropaint')).read_text())
assert doc == json.loads((out / (stem + '-reopened.retropaint')).read_text())
picture = Image.open(out / (stem + '.png')).convert('RGBA')
assert picture.size == (960, 640)
assert picture.tobytes() == Image.open(out / (stem + '-reopened.png')).convert('RGBA').tobytes()
cad = next(layer for layer in doc['layers'] if layer['name'] == 'Desk container')
assert cad['visible'] and len(cad['cad']['bodies']) == 1
solid = cad['cad']['bodies'][0]['solid']
assert solid['kind'] == 'shell' and solid['thickness'] == 3 and len(solid['faces']) == 1
assert solid['source']['solid']['operation'] == 'union'
assert cad['cad']['view']['projection'] == 'perspective'
caption = doc['layers'][-1]
assert caption['name'] == 'Paint above 3D' and caption['visible']
label, = caption['objects']
assert label['kind'] == 'text' and label['callout']['text'] == 'Desk pot\n3 mm walls'
assert label['size'] == 26 and label['matrix'][:4] == [1, 0, 0, 1]
base = Image.new('RGBA', picture.size)
for layer in doc['layers']:
    if layer['visible']:
        assert layer['opacity'] == 1
        base.alpha_composite(Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',')[1]))).convert('RGBA'))
label_difference = ImageChops.difference(picture, base).convert('RGB').getbbox()
assert label_difference == (85, 367, 404, 519)

data = (out / (stem + '-3d-mm.stl')).read_bytes()
count = struct.unpack_from('<I', data, 80)[0]
assert len(data) == 84 + 50 * count
triangles, points, edges, directions = [], [], Counter(), Counter()
volume = 0
def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
for i in range(count):
    normal = struct.unpack_from('<3f', data, 84 + 50*i)
    a, b, c = [struct.unpack_from('<3f', data, 96 + 50*i + 12*j) for j in range(3)]
    assert dot(cross(sub(b, a), sub(c, a)), normal) > 0
    triangles.append((a, b, c)); points.extend((a, b, c))
    volume += dot(a, cross(b, c)) / 6
    for start, end in [(a, b), (b, c), (c, a)]:
        edge = tuple(sorted([start, end])); edges[edge] += 1
        directions[edge] += 1 if start < end else -1
assert all(n == 2 for n in edges.values()) and not any(directions.values())
bounds = [(min(p[j] for p in points), max(p[j] for p in points)) for j in range(3)]
assert bounds == [(-20, 25), (-15, 15), (0, 30)]
assert {p[2] for p in points} == {0, 3, 30}

def ray(origin, direction):
    hits = []
    for a, b, c in triangles:
        e1, e2 = sub(b, a), sub(c, a); h = cross(direction, e2); determinant = dot(e1, h)
        if abs(determinant) < 1e-8: continue
        f = 1 / determinant; s = sub(origin, a); u = f * dot(s, h)
        if u < -1e-7 or u > 1+1e-7: continue
        q = cross(s, e1); v = f * dot(direction, q)
        if v < -1e-7 or u+v > 1+1e-7: continue
        t = f * dot(e2, q)
        if t > 1e-7 and not any(abs(t-x) < 1e-5 for x in hits): hits.append(t)
    return sorted(hits)

straight_curved = ray((-30, 0, 15), (1, 0, 0))
assert straight_curved == [10, 13, 52, 55]
floor = ray((0, .123, -5), (0, 0, 1))
assert len(floor) == 2 and abs(floor[1]-floor[0]-3) < 1e-6
direction = (-math.sqrt(3)/2, -.5, 0)
origin = (20-direction[0]*.1, 5*math.sqrt(3)-direction[1]*.1, 15)
junction = ray(origin, direction)
assert abs(junction[1]-junction[0]-3) < .005

# Integrate the analytic offset cross-section, including concave junction arcs.
def integral(radius, y):
    return .5 * (y*math.sqrt(max(0, radius*radius-y*y)) + radius*radius*math.asin(y/radius))
a, b = 7*math.sqrt(3)/2, 5*math.sqrt(3)
outer_area = 1200 + 100*math.pi/3 - 25*math.sqrt(3)
inner_area = 2*(32*a + integral(7, a) + 37*(b-a) + integral(3, a-b) + 34*(12-b))
analytic_volume = outer_area*30 - inner_area*27
assert abs(volume-analytic_volume) < 1  # tessellated curved surfaces, mm³
report = {'fixture': '40x30x30 block + diameter20 height30 cylinder at X15; top shell3',
          'project_roundtrip_exact': True, 'png_roundtrip_exact': True,
          'caption_only_pixel_difference_bounds': label_difference,
          'triangles': count, 'closed': True, 'consistent_outward_winding': True,
          'bounds_mm': bounds, 'volume_mm3': volume, 'analytic_volume_mm3': analytic_volume,
          'straight_and_curved_ray_distances_mm': straight_curved,
          'floor_mm': floor[1]-floor[0], 'junction_wall_mm': junction[1]-junction[0],
          'files': {name: hashlib.sha256((out/name).read_bytes()).hexdigest() for name in names}}
(out / 'desk-container-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
