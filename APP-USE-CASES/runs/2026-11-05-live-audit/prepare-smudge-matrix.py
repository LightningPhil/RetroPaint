"""Independent SMUDGE source, with a contrasting neighbour to detect sampling leaks."""
from pathlib import Path
from PIL import Image,ImageDraw
import base64,copy,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/fixtures/smudge60';out.mkdir(parents=True,exist_ok=True)
def url(im):
    b=io.BytesIO();im.save(b,format='PNG');return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
d=json.loads((root/'test-results/audit-2026-11-05/manual-blockers/PLAY.retropaint').read_bytes())
im=Image.new('RGBA',(320,240));draw=ImageDraw.Draw(im);draw.rectangle((40,60,139,179),fill='red');draw.rectangle((160,60,259,179),fill='blue')
layer=copy.deepcopy(d['layers'][0]);layer.update(id=602,name='Red and blue',paper=None,image=url(im))
neighbour=copy.deepcopy(layer);neighbour.update(id=601,name='Green neighbour',image=url(Image.new('RGBA',(320,240),'lime')))
d.update(width=320,height=240,active=602,layers=[neighbour,layer])
data=json.dumps(d,separators=(',',':')).encode();(out/'settled.retropaint').write_bytes(data);im.save(out/'settled.png')
wet=copy.deepcopy(d);wet['layers'][1]['image']=url(Image.new('RGBA',(320,240)));fills=[]
for bounds,colours in [((40,60,139,179),['#ff0000','#880000']),((160,60,259,179),['#0000ff','#000088'])]:
    mask=Image.new('RGBA',(320,240));ImageDraw.Draw(mask).rectangle(bounds,fill='white')
    fills.append({'mask':url(mask),'opacity':1,'spec':{'kind':'conveyor','colors':colours,'speed':1,'mode':'snap','along':False,'texture':None},'gradient':None,'sparkles':[]})
wet['layers'][1]['live']['fills']=fills
(out/'wet.retropaint').write_text(json.dumps(wet,separators=(',',':')))
(out/'plan.json').write_text(json.dumps({'sha256':hashlib.sha256(data).hexdigest(),'size':22,'strengths':[1,.15],'gesture':[[120,120],[200,120]],'oracle':'Compare active-layer local displacement and feathering, no green neighbour sampling, exact outside pixels and native Undo/Redo.'},indent=2)+'\n')
print(out)
