"""Opaque gradient and irregular grid spanning 64px neural tile boundaries."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures';y,x=np.mgrid[:160,:192];a=np.stack([40+x*.8,45+y,70+x*.25+y*.35],axis=2);lines=(x%23==7)|(y%29==9);a[lines]=[230,240,245];diagonal=abs(y-(.53*x+17))<1;a[diagonal]=[30,40,60];a=np.rint(np.clip(a,0,255)).astype('uint8');p=folder/'enhance154-grid.png';Image.fromarray(a).save(p);(folder/'enhance154-manifest.json').write_text(json.dumps(dict(dimensions=[192,160],sha256=hashlib.sha256(p.read_bytes()).hexdigest(),description=__doc__),indent=2)+'\n')
