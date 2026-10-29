from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,base64,io
root=Path(__file__).resolve().parent
data=(root/'backups/artwork-before-acceptance-audit.retropaint').read_bytes()
checksum=hashlib.sha256(data).hexdigest()
assert checksum=='612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28'
doc=json.loads(data)
assert len(doc['layers'])==4 and (doc['width'],doc['height'])==(960,640)
layers=[]
for layer in doc['layers']:
    image=Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
    assert image.size==(960,640)
    layers.append(dict(id=layer['id'],name=layer['name'],rgba_sha256=hashlib.sha256(image.tobytes()).hexdigest()))
result=dict(at=datetime.now(timezone.utc).isoformat(),backup_sha256=checksum,bytes=len(data),layers=layers,scope='Immutable original backup reverified without accessing or modifying the current artwork browser session. Earlier actual save/reopen verification remains retained.')
(root/'evidence/BACKUP-no-desktop-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('Original backup checksum and all four independently decoded layers verified.')
