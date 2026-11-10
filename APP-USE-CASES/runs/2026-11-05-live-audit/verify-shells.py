"""Measure signed STL volume and edge closure without using RetroPaint."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import shutil
import struct

out = Path(__file__).resolve().parents[3] / 'test-results/audit-2026-11-05/mouse'
report = []
for suffix, expected, surfaces in [(' (1)', 9024, 2), (' (2)', 7152, 1)]:
    name = f'mouse-audit-shapes-3d-mm{suffix}.stl'
    shutil.copyfile(Path.home() / 'Downloads' / name, out / name)
    data = (out / name).read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + count * 50
    edges, signs, graph = Counter(), Counter(), defaultdict(set)
    triangle_volumes = []
    owners = defaultdict(list)
    for index in range(count):
        a, b, c = [struct.unpack_from('<3f', data, 84+index*50+12+j*12) for j in range(3)]
        triangle_volumes.append((a[0]*(b[1]*c[2]-b[2]*c[1])+
                                 a[1]*(b[2]*c[0]-b[0]*c[2])+
                                 a[2]*(b[0]*c[1]-b[1]*c[0]))/6)
        for start, end in [(a,b), (b,c), (c,a)]:
            edge = tuple(sorted([start,end]))
            edges[edge] += 1
            signs[edge] += 1 if start < end else -1
            owners[edge].append(index)
    assert all(n == 2 for n in edges.values()) and not any(signs.values())
    for first, second in owners.values():
        graph[first].add(second)
        graph[second].add(first)
    remaining = set(range(count))
    components = []
    while remaining:
        pending = [remaining.pop()]
        connected = []
        while pending:
            triangle = pending.pop()
            connected.append(triangle)
            for neighbour in graph[triangle] & remaining:
                remaining.remove(neighbour)
                pending.append(neighbour)
        components.append(sum(triangle_volumes[i] for i in connected))
    volume = sum(components)
    assert len(components) == surfaces
    assert abs(volume-expected) < .02, (volume, expected)
    if surfaces == 2:
        assert min(components) < 0 < max(components), 'Cavity winding was filled in'
    report.append({'file':name,'triangles':count,'volume_mm3':volume,
                   'analytic_volume_mm3':expected,'signed_surface_volumes_mm3':components,
                   'closed':True,'consistent_winding':True})
(out/'shell-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
