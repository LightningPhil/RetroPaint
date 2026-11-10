"""Actual project bytes prove all palette/custom colours remain on one body ID."""
from pathlib import Path
import base64,copy,hashlib,io,json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def load(suffix):
    name=f'mouse-audit-solid161-palette-baseline{suffix}.retropaint';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
base=load('');index=next(i for i,l in enumerate(base['layers']) if 'cad' in l);bodies=base['layers'][index]['cad']['bodies'];assert len(bodies)==2 and bodies[0]['name']=='Colour tube' and bodies[1]['name']=='Unchanged cube';ui=json.loads((out/'solid161-ui.json').read_text());colours=[r['expected'] for r in ui['palette']]+[ui['custom']];assert all(r['expected']==r['shown'] for r in ui['palette']);documents=[]
for n,colour in enumerate(colours,1):
    d=load(f' ({n})');expected=copy.deepcopy(base);expected['active']=d['active'];assert expected['active']==base['layers'][index]['id'];expected['layers'][index]['cad']['bodies'][0]['color']=colour;expected['layers'][index]['image']=d['layers'][index]['image'];assert d==expected;documents.append(d)
data=(downloads/'mouse-audit-solid161-reopened.retropaint').read_bytes();(out/'mouse-audit-solid161-reopened.retropaint').write_bytes(data);reopened=json.loads(data);expected=copy.deepcopy(documents[-1]);expected['layers'][index]['image']=reopened['layers'][index]['image'];assert reopened==expected;assert ui['switching']['other']==dict(name='Unchanged cube',colour='#57bfca') and ui['switching']['returned']==dict(name='Colour tube',colour='#2468ac')
decode=lambda d:np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][index]['image'].split(',')[1]))).convert('RGBA')).astype(int)
a,b=decode(documents[-1]),decode(reopened);error=abs(a-b);assert np.array_equal(a[:,:,3],b[:,:,3]) and np.all(error[a[:,:,3]==255]==0) and error.max()<=2;changed=int(np.count_nonzero(np.any(error,axis=2)));assert changed<=2
report=dict(status='Pass',palette_and_custom=colours,identity_and_other_body_exact=True,recipes_transforms_and_paint_exact=True,reopened_source_fields_exact=True,cached_preview_edge_pixels_requantized=changed,cached_preview_max_RGB_change=int(error.max()),hashes=hashes);(out/'solid161-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
