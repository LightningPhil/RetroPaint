"""Prepare named VECTOR inputs from actual native objects and an independent PNG.

Heart, plain text and two separate brush gestures are added live after loading.
"""
import base64,copy,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[3];downloads=Path.home()/'Downloads'
out=root/'test-results/audit-2026-11-05/fixtures';sources={}
def read(name):
    data=(downloads/name).read_bytes();sources[name]=hashlib.sha256(data).hexdigest();return json.loads(data)
def url(image):
    stream=io.BytesIO();image.save(stream,format='PNG');return 'data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()
source=read('mouse-audit-vectors-clipboard.retropaint')
paths=source['layers'][0]['objects']
rectangle=copy.deepcopy(paths[2]);rectangle.update(id='fixture-rectangle',name='Rectangle',matrix=[1,0,0,1,80,80])
line=copy.deepcopy(paths[0]);line.update(id='fixture-line',name='Line',matrix=[1,0,0,1,180,110])
animal=read('mouse-audit-stamps-animals.retropaint')
stamp=copy.deepcopy(next(l['objects'][0] for l in animal['layers'] if l.get('objects')))
stamp.update(id='fixture-stamp',name='Dog stamp',matrix=[1,0,0,1,600,80])
spiros=read('mouse-audit-spiro-after-reset.retropaint')
spiro=copy.deepcopy(next(l['objects'][0] for l in spiros['layers'] if l.get('objects')))
spiro.update(id='fixture-spiro',name='Spiro path',matrix=[.35,0,0,.35,420,350])
image=Image.new('RGBA',(96,64),(0,0,0,0));draw=ImageDraw.Draw(image)
draw.rectangle((8,8,47,55),fill=(229,57,53,255));draw.rectangle((48,8,87,55),fill=(30,136,229,128))
draw.rectangle((8,8,23,23),fill=(22,163,74,255));image.save(out/'vector-import.png')
raster={'id':'fixture-import','name':'Transparent PNG','kind':'raster','width':96,'height':64,
        'matrix':[1.5,0,0,1.5,-20,500],'opacity':1,'image':url(image)}
doc=copy.deepcopy(source);doc.update(width=960,height=640,active=1,drawingMode='vector');doc.pop('crop',None)
paper=doc['layers'][0];paper.update(id=1,name='Paper',paper='#ffffff',visible=True,opacity=1,
                                  image=url(Image.new('RGBA',(960,640),'white')),
                                  live={'strokes':[],'fills':[],'sparkles':[]},
                                  objects=[rectangle,line,stamp,spiro,raster])
paper.pop('photo',None);doc['layers']=[paper]
(out/'vector-seed.retropaint').write_text(json.dumps(doc,ensure_ascii=False),encoding='utf-8')
(out/'vector-provenance.json').write_text(json.dumps({'sources':sources,
    'native_additions_pending':['Concave heart','Editable plain text','Raster gesture 1','Raster gesture 2'],
    'import_png_original_dimensions':[96,64],'import_starts_partly_outside_paper':True},indent=2)+'\n')
print('Prepared five named source objects; four native additions remain.')
