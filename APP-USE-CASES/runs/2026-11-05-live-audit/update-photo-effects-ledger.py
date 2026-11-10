"""Record complete photographic Pixelate and Emboss cases."""
from pathlib import Path
from datetime import datetime,timezone
import json
folder=Path(__file__).resolve().parent;root=folder.parents[2]
for name in ['photo62','face63']:assert json.loads((root/f'test-results/audit-2026-11-05/mouse/{name}-verification.json').read_bytes())['status']=='Pass'
notes={
'PAINT-016':'Native Pixelate22px/100% on2100x1398 landscape and2615x3269 NASA portrait facial detail. Independent decoded files show24547 and16834 changed pixels respectively, exact alpha and every pixel outside the declared33px-radius gesture tube, and exact whole-project Undo/Redo. Adjacent equal-colour pairs increased2328→9941 in the landscape and182→4173 across the facial core. Smallest1px setting changed only14213 landscape pixels within24px of the same local path, fewer than22px setting. Native56% zoom/pan confirmed visible facial blocks. New public-domain NASA portrait retained with source, licence, dimensions and hash because the existing landscape could not exercise the specified face-detail step.',
'PAINT-018':'Native Emboss22px/100% across a high-contrast river detail in the2100x1398 natural photograph:32013 changed pixels, exact alpha and all pixels outside31px-radius tube, local neutral relief (mean chroma66.53→19.96), and exact whole-project Undo/Redo. Additional fixture clears only left20px; native edge-crossing stroke preserves every alpha value, clear border and all outside pixels exactly, with exact whole-project Undo/Redo.'}
p=folder/'execution.json';ledger=json.loads(p.read_text(encoding='utf-8-sig'))
for c in ledger['cases']:
    if c['id'] in notes:
        c['status']='Pass';note=notes[c['id']]
        if note not in c['observations']:c['observations'].append(note)
        names=['photo62-verification.json','photo62-evidence.json']+(['face63-verification.json','face63-evidence.json','face63-pixelated.jpg'] if c['id']=='PAINT-016' else [])
        for n in names:
            path='test-results/audit-2026-11-05/mouse/'+n
            if path not in c['evidence']:c['evidence'].append(path)
ledger['updated']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
p=folder/'README.md';s=p.read_text(encoding='utf-8').replace('**117 Pass, 229 Partial','**119 Pass, 227 Partial')
if '## Photographic effects completed' not in s:s+='\n## Photographic effects completed\n\n'+ '\n\n'.join(notes.values())+'\n'
p.write_text(s,encoding='utf-8');print('119Pass227Partial3Blocked')
