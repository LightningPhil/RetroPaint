"""Check retained genuine v2 photo migration evidence without modifying it."""
import hashlib
import json
import copy
from pathlib import Path

root = Path(__file__).resolve().parents[1] / '2026-10-19-full-audit'
paths = [root / 'fixtures/legacy-v2-5ae1169.retropaint',
         root / 'evidence/LEGACY-v2-migrated-current.retropaint',
         root / 'evidence/LEGACY-v2-migrated-reopened.retropaint']
documents = [json.loads(path.read_text(encoding='utf-8')) for path in paths]
assert [doc['version'] for doc in documents] == [2, 10, 10]
original, migrated, reopened = [doc['layers'][0]['photo'] for doc in documents]
assert migrated == reopened
for section in ('settings', 'normal'):
    old, new = original[section], migrated[section]
    assert 'grainSize' not in old and 'grainRoughness' not in old
    assert new['grainSize'] == 1.2 and new['grainRoughness'] == 50
    assert all(new[key] == value for key, value in old.items())
print(json.dumps({'result': 'pass', 'sections': ['settings', 'normal'],
                  'added_defaults': {'grainSize': 1.2, 'grainRoughness': 50},
                  'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}, indent=2))

# The later live edit must preserve the entire original project, including the
# embedded original image and crop, except for migration and the intended edit.
edited_path = Path(__file__).resolve().parent / 'legacy-recovered/legacy-v2-grain-edited.retropaint'
edited = json.loads(edited_path.read_text(encoding='utf-8'))
expected = copy.deepcopy(documents[0])
expected['version'] = 10
expected['drawingMode'] = 'raster'
for section in ('settings', 'normal'):
    settings = expected['layers'][0]['photo'][section]
    settings.update(grain=1, grainSize=1.3, grainRoughness=51)
assert edited == expected
print(json.dumps({'edited_project_exact_except_expected_changes': True,
                  'sha256': hashlib.sha256(edited_path.read_bytes()).hexdigest()}))
