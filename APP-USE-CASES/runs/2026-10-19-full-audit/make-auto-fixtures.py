from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
root=Path(__file__).resolve().parent
source=np.asarray(Image.open(root/'fixtures/TONAL.png').convert('RGBA'))
rows=[]
for name,start in [('dark',10),('bright',145)]:
    pixels=source.copy();pixels[:,:,:3]=np.rint(start+source[:,:,:3].astype(float)*100/255).astype(np.uint8)
    target=root/('fixtures/AUTO-'+name+'.png');assert not target.exists(),'Refusing to replace a retained fixture'
    Image.fromarray(pixels).save(target)
    rows.append(dict(file=target.name,dimensions=[1024,256],source_encoded_range=[start,start+100],sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
(root/'fixtures/AUTO-manifest.json').write_text(json.dumps(dict(generator='Independent Pillow/NumPy bounded luminance ramps',rows=rows),indent=2)+'\n',encoding='utf-8')
print('Created two fixed uneven-exposure ramps.')
