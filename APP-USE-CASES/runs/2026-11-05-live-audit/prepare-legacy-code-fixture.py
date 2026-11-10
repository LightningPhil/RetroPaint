"""Synthetic v12 compatibility fixture, explicitly not a historical download."""
import base64,copy,io,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[3]
d=json.loads((Path.home()/'Downloads/mouse-audit-code-limit-2mb.retropaint').read_bytes())
l=next(l for l in d['layers'] if l.get('cad'));b=copy.deepcopy(l['cad']['bodies'][-1])
b['name']='Legacy v12 source';b['script']={'language':'retrocad-1','source':'// Legacy subset model\ncube([2,3,4]);\n'}
l['cad']['bodies']=[b];buf=io.BytesIO();Image.new('RGBA',(d['width'],d['height'])).save(buf,format='PNG')
l['image']='data:image/png;base64,'+base64.b64encode(buf.getvalue()).decode();d['version']=12
(root/'test-results/audit-2026-11-05/fixtures/legacy-code-v12.retropaint').write_text(json.dumps(d,separators=(',',':')),encoding='utf-8')
