from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
root=Path(__file__).resolve().parent;file=root/'fixtures/FULLSIZE-grid.png';assert not file.exists()
y,x=np.indices((1280,1920));levels=((x+y)%2*255).astype(np.uint8);pixels=np.empty((1280,1920,4),dtype=np.uint8);pixels[:,:,:3]=levels[:,:,None];pixels[:,:,3]=255
Image.fromarray(pixels).save(file)
(root/'fixtures/FULLSIZE-grid-manifest.json').write_text(json.dumps(dict(generator='Independent NumPy parity: RGB=255*((x+y)%2), alpha=255',dimensions=[1920,1280],file=file.name,sha256=hashlib.sha256(file.read_bytes()).hexdigest(),oracle='Every one-pixel black/white sample must remain distinct in the full-size output. A 720px preview cannot retain the source Nyquist pattern.'),indent=2)+'\n',encoding='utf-8');print('Created fixed 1920x1280 one-pixel parity grid.')
