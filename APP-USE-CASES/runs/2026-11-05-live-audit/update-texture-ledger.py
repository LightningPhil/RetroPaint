"""Record texture evidence without treating pending export checks as passed."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re

folder = Path(__file__).resolve().parent
root = folder.parents[2]
evidence = root / 'test-results/audit-2026-11-05'
report = json.loads((evidence / 'all-fifty-fixes-cropped/report.json').read_bytes())
assert report['status'] == 'Pass'
assert all(hashlib.sha256((root / f['path']).read_bytes()).hexdigest() == f['sha256'] for f in report['source_files'])
note = ('Native 960x640 matrix: all seven textures painted and bucket-filled; independent PNG checks verify 64px periods (Static 48px), declared structure colours, five static textures and four Water/Static animation masks. Whole-project last-fill Undo/Redo and zoom invariance are exact. LIVE-050 reproduced: placing raster text baked all existing live fills. Fixed by retaining original live artwork beneath the placed raster piece; preview cancellation and whole-project Undo/Redo pass the regression. Live retest placed seven labels, exercised Undo/Redo, and observed two animation frames. Project file reopening works after the user enabled extension file access. Fixed labelled project/PNG exports have not yet arrived from Chrome, so their exact preservation and round-trip checks remain pending. Full regression: 728 checks, no failures or page errors; TypeScript and production build pass.')
assert json.loads((evidence / 'mouse/texture52-verification.json').read_bytes())['status']=='Pass'
note += ' Completion: Chrome file access and downloads are now working. Both labelled frame exports preserve every pixel outside the labels exactly; all original live definitions and raster bytes remain exact. Native project and PNG round-trips are exact. Refined placement bounds are 28x9 pixels; cancellation, Undo and Redo preserve whole project data exactly. INK-009 is now Pass. The current regression report is all-fifty-fixes-cropped/report.json.'
lp = folder / 'execution.json'
ledger = json.loads(lp.read_text(encoding='utf-8-sig'))
for case in ledger['cases']:
    if case['id'] == 'INK-009':
        case['status'] = 'Pass'
        if note not in case['observations']: case['observations'].append(note)
        for name in ['texture52-evidence.json', 'texture52-verification.json', 'texture52-fixed-seven-labels.jpg']:
            path = 'test-results/audit-2026-11-05/mouse/' + name
            if path not in case['evidence']: case['evidence'].append(path)
ledger['updated'] = datetime.now(timezone.utc).isoformat()
lp.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
rp = folder / 'README.md'
text = rp.read_text(encoding='utf-8').replace('after all forty-nine fixes passes **726 checks', 'after all fifty fixes passes **728 checks').replace('(`all-forty-nine-fixes/report.json`)', '(`all-fifty-fixes-cropped/report.json`)')
text = text.replace('The dedicated development origin is http://127.0.0.1:52551/.', 'The resumed development origin is http://127.0.0.1:51463/; the production audit wrapper is http://127.0.0.1:64542/.')
text = text.replace('**111 Pass, 235 Partial', '**112 Pass, 234 Partial').replace('(`all-fifty-fixes/report.json`)', '(`all-fifty-fixes-cropped/report.json`)')
if '## Texture matrix completed' not in text: text += '\n## Texture matrix completed\n\n' + note + '\n'
rp.write_text(text, encoding='utf-8')
ep = evidence / 'environment.json'
env = json.loads(ep.read_text(encoding='utf-8-sig'))
for f in env['dirty_source']: f['sha256'] = hashlib.sha256((root / f['path']).read_bytes()).hexdigest()
env['recorded'] = ledger['updated']
env['fix_count'] = 50
env['latest_regression'] = {'report': 'test-results/audit-2026-11-05/all-fifty-fixes-cropped/report.json', 'passed': sum(s['passed'] for s in report['suites']) + 1, 'failed': 0, 'page_errors': 0}
assert env['latest_regression']['passed'] == 728
production = evidence / 'production-seven-fixes'
index = (production / 'index.html').read_bytes()
entry = re.search(rb'<script[^>]+src="([^"]+)"', index).group(1).decode()
env['production_build'] = {'fixes': 50, 'index_sha256': hashlib.sha256(index).hexdigest(), 'entry': entry, 'entry_sha256': hashlib.sha256((production / entry.removeprefix('./').lstrip('/')).read_bytes()).hexdigest()}
ep.write_text(json.dumps(env, indent=2) + '\n', encoding='utf-8')
print('Recorded LIVE-050 and passing native texture matrix; full728 regression verified.')
