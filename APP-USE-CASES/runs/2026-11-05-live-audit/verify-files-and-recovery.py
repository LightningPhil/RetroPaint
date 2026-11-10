"""Verify real filename, keyboard-placement and draft-recovery downloads."""
import hashlib
import io
import json
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[3]
out = root/'test-results/audit-2026-11-05/mouse'
downloads = Path.home()/'Downloads'
hashes = {}
def retain(name):
    data = (downloads/name).read_bytes()
    (out/name).write_bytes(data)
    hashes[name] = hashlib.sha256(data).hexdigest()
    return data
def doc(stem): return json.loads(retain(stem+'.retropaint'))

baseline = doc('mouse-audit-play-960-baseline')
assert baseline == doc('mouse-audit-keyboard-text-undone')
assert baseline != doc('mouse-audit-keyboard-text-placed')
formats = {}
for name, expected in [('mouse-audit-filename.jpg','JPEG'),('mouse-audit----------.png','PNG'),('retropaint.webp','WEBP')]:
    image = Image.open(io.BytesIO(retain(name)))
    assert image.format == expected and image.size == (960,640)
    image.load()
    formats[name] = {'format':image.format, 'size':image.size}
assert not (downloads/'mouse-audit-filename.png.jpg').exists()
current = doc('mouse-audit-draft-current')
assert current == doc('mouse-audit-draft-undo')
restored = doc('mouse-audit-draft-restored')
assert restored == doc('mouse-audit-draft-redo') == doc('mouse-audit-journey4-reopened')
assert current != restored
report = {'keyboard_caption_changed_art':True,'keyboard_one_undo_project_exact':True,
          'filename_decodes':formats,'no_doubled_extension':True,
          'chosen_draft_exact':True,'draft_undo_exact':True,'draft_redo_exact':True,'sha256':hashes}
(out/'files-and-recovery-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
