"""Cancelled native multipoint natural-photo draft and genuine late reply."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
base=json.loads((downloads/'mouse-audit-photo105-expanded.retropaint').read_text())
for name in ['cancelled','reopened','late-reply']:
    p=downloads/f'mouse-audit-curve116-{name}.retropaint';data=p.read_bytes();(out/p.name).write_bytes(data);hashes[p.name]=hashlib.sha256(data).hexdigest();assert json.loads(data)==base
raw=np.array(Image.open(downloads/'mouse-audit-photo105-expanded.png').convert('RGBA'))
for name in ['cancelled','late-reply']:
    p=downloads/f'mouse-audit-curve116-{name}.png';shutil.copyfile(p,out/p.name);hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest();assert np.array_equal(np.array(Image.open(p).convert('RGBA')),raw)
before=np.array(Image.open(out/'curve116-before-release.jpg'));after=np.array(Image.open(out/'curve116-after-release.jpg'));assert before.shape==after.shape
# Entire unobstructed paper including its saved Photo rendering, excluding UI.
assert np.array_equal(before[123:663,424:1236],after[123:663,424:1236])
log=(out/'curve116-late-log.txt').read_text();assert 'photo reply held' in log and 'photo replies released: {"count":1}' in log
report=dict(status='Pass',native_multiple_RGB_and_red_draft_edits_Cancel_reopen=True,entire_saved_project_exact_including_other_groups=True,full2100x1398_PNG_every_RGBA_exact=True,genuine_Worker_reply_deferred_until_after_Cancel_and_new_session=True,visible_restored_paper_pixels_exact_after_release=True,sha256=hashes)
(out/'curve116-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS native Cancel/reopen, genuine stale reply, exact display/document/full PNG')
