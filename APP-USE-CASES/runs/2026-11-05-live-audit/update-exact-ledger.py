"""Record independently verified exact-fixture runs without promoting other cases."""
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

folder = Path(__file__).resolve().parent
root = folder.parents[2]
ledger = json.loads((folder/'execution.json').read_text(encoding='utf-8-sig'))
records = {case['id']: case for case in ledger['cases']}
updates = {
    'JOURNEY-001': ('Pass', 'Repeated continuously on the exact clean 960 x 640 PLAY fixture in Basic mode: three Mint background strokes, cakes and cupcake, two Pink hearts, Purple 36px Comic Sans greeting. Saved each transition. A deliberate Black 96px mistake was recovered with one Undo. The final project equals the greeting project in its entirety; independently decoded PNG pixels equal the final saved raster. Live screenshot confirms legible composition.'),
    'FEATURE-018': ('Pass', 'Repeated the exact unscaled 20mm cube and diameter20 height20 cylinder at X15, Z10, then picked the combined cap and applied a 3mm shell. Repeated with the bottom cap and cylinder X40/3 for one-third overlap. Each actual project reopened through the native picker and re-saved with identical whole-project JSON. Independent STL edge, winding, bounds and section-ray checks pass: straight/curved walls and floor or ceiling 3mm, junction approximately 2.9997mm. Invalid 100mm preview was rejected; valid 2.5mm preview then Cancel preserved the entire original project.'),
    'JOURNEY-003': ('Partial', 'Recovered the actual water, conveyor and Spiro scene from the development origin draft after reload. Save project reported completion, but the native Chrome toolbar shows the blocked-download icon and no downloaded project exists. No browser permission setting changed. Exact PLAY 960x640 repeat, native file reopen, and explicit rainbow-baking exception remain outstanding; the existing scene is 640x480.')
}
for key, (status, note) in updates.items():
    case = records[key]
    case['status'] = status
    if note not in case['observations']:
        case['observations'].append(note)
    if key != 'JOURNEY-003':
        for item in ['test-results/audit-2026-11-05/mouse/exact-fixtures-verification.json', 'APP-USE-CASES/runs/2026-11-05-live-audit/verify-exact-fixtures.py']:
            if item not in case['evidence']: case['evidence'].append(item)
ledger['updated'] = datetime.now(timezone.utc).isoformat()
(folder/'execution.json').write_text(json.dumps(ledger, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
env_path = root/'test-results/audit-2026-11-05/environment.json'
env = json.loads(env_path.read_text(encoding='utf-8-sig'))
for entry in env['dirty_source']:
    entry['sha256'] = hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
env['recorded'] = ledger['updated']
env['fix_count'] = 12
env['latest_regression'] = {'report': 'test-results/audit-2026-11-05/all-twelve-fixes/report.json', 'passed':605,'failed':0,'page_errors':0}
env_path.write_text(json.dumps(env, indent=2)+'\n', encoding='utf-8')
print({status: sum(case['status']==status for case in ledger['cases']) for status in sorted({case['status'] for case in ledger['cases']})})
