"""Prepare preserved MIX copies with a known opaque mark on the target sheet."""
from pathlib import Path
from PIL import Image, ImageDraw
import base64,copy,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures/eraser57';out.mkdir(parents=True,exist_ok=True)
template=json.loads((root/'test-results/audit-2026-11-05/manual-blockers/MIX.retropaint').read_bytes());records=[]
for variant,target in [('paper',101),('transparent',103),('hidden',103)]:
    d=copy.deepcopy(template);d['active']=target
    layer=next(l for l in d['layers'] if l['id']==target)
    im=Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
    ImageDraw.Draw(im).rectangle((100,350,400,450),fill='#E53935')
    b=io.BytesIO();im.save(b,format='PNG');layer['image']='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
    if variant=='paper':
        for l in d['layers']:l['visible']=l['id']==101
    if variant=='hidden':layer['visible']=False
    data=json.dumps(d,separators=(',',':')).encode();(out/(variant+'.retropaint')).write_bytes(data)
    records.append({'variant':variant,'active':target,'sha256':hashlib.sha256(data).hexdigest()})
plan={'fixtures':records,'size':22,'strength':1,'path':[[150,400],[350,400]],'centre_patch':[230,395,250,405],
      'oracle':'Paper centre becomes opaque white; transparent centre alpha0 exposes Blue Backdrop; all non-target layer pixels exact; Undo returns whole native baseline; hidden active layer must not alter visible neighbours.'}
(out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(out)
