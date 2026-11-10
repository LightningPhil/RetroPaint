from pathlib import Path
import json, hashlib
from PIL import Image
root=Path(__file__).resolve().parent/'legacy-recovered'
manifest=json.loads((root/'manifest.json').read_text(encoding='utf8'))
reference=Image.open(root/'legacy-tree-v3.png').convert('RGBA')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
for row in manifest['results']:
 v=row['version'];source=root/f'legacy-tree-v{v}.retropaint';migrated=root/f'migrated-tree-v{v}.retropaint';reopened=root/f'reopened-tree-v{v}.retropaint'
 a=json.loads(source.read_text(encoding='utf8'));b=json.loads(migrated.read_text(encoding='utf8'));c=json.loads(reopened.read_text(encoding='utf8'))
 assert a['version']==v and sha(source)==row['fixture_sha256'] and sha(migrated)==row['migrated_sha256']
 a['version']=b['version'];assert a==b==c, f'Project mismatch for v{v}'
 for name in [f'legacy-tree-v{v}.png',f'reopened-tree-v{v}.png']:
  image=Image.open(root/name).convert('RGBA');assert image.size==reference.size and image.tobytes()==reference.tobytes(),f'Pixel mismatch: {name}'
 print(f'PASS v{v}: producer hash, all project data and both RGBA references')
a=json.loads((root/'legacy-v11-original.retropaint').read_text(encoding='utf8'));b=json.loads((root/'legacy-v11-verified.retropaint').read_text(encoding='utf8'))
assert a['version']==b['version']==11
assert 'liveSize' not in a['layers'][3]['objects'][1]
a['layers'][3]['objects'][1]['liveSize']={'width':a['width'],'height':a['height']};assert a==b
print('PASS v11: only missing raster liveSize was defaulted to the picture size')
