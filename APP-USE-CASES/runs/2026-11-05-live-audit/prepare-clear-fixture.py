"""Compose the declared MIX variant from independently retained native assets."""
import copy,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures'
mix=out/'mix-half-character.retropaint';native=Path.home()/'Downloads/mouse-audit-journey3-960-conveyor.retropaint'
d=json.loads(mix.read_bytes());live=json.loads(native.read_bytes())['layers'][0]['live']
d['layers'][1]['live']=copy.deepcopy(live)
data=json.dumps(d,ensure_ascii=False,separators=(',',':')).encode('utf-8')
(out/'mix-live-clear.retropaint').write_bytes(data)
provenance={'fixture':'Synthetic MIX variant; actual native live definitions retained exactly. Brightness12 was subsequently applied through live Photo lab.',
 'sources':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [mix,native]},'sha256':hashlib.sha256(data).hexdigest()}
(out/'mix-live-clear-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
