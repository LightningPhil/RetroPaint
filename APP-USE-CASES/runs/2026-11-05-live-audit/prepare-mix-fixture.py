"""Reproducible four-layer MIX fixture; preserves genuine previously mouse-created stamp."""
import base64,copy,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures';folder.mkdir(exist_ok=True)
downloads=Path.home()/'Downloads'
def read(name):return json.loads((downloads/name).read_text(encoding='utf-8'))
def url(image):
    stream=io.BytesIO();image.save(stream,format='PNG');return 'data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()
base=read('mouse-audit-play-960-baseline.retropaint');stamps=read('mouse-audit-stamps-animals.retropaint')
dog=copy.deepcopy(stamps['layers'][0]['objects'][0]);assert dog['kind']=='stamp'
dog['name']='Caption dog stamp';dog['matrix'][4]+=636;dog['matrix'][5]+=40
paper=Image.new('RGBA',(960,640),'white');backdrop=Image.new('RGBA',(960,640),'#1E88E5')
character=Image.new('RGBA',(960,640));draw=ImageDraw.Draw(character)
draw.rectangle((100,100,199,179),fill='#FF0000');draw.rectangle((100,300,199,379),fill='#00FF00')
caption=Image.new('RGBA',(960,640));draw=ImageDraw.Draw(caption)
draw.text((50,35),'Test caption',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',48),fill='black')
draw.rectangle((640,65,750,180),fill='white')
layers=[]
for index,(name,image,is_paper) in enumerate([('Paper',paper,True),('Backdrop',backdrop,False),('Character',character,False),('Caption',caption,False)],101):
    layer={'id':index,'name':name,'visible':True,'opacity':1,'paper':'#ffffff' if is_paper else None,'image':url(image),'live':{'strokes':[],'fills':[],'sparkles':[]}}
    if name=='Caption':layer['objects']=[dog]
    layers.append(layer)
base.update(width=960,height=640,drawingMode='raster',active=103,layers=layers,crop={'x':0,'y':0,'width':1,'height':1})
reference=Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(paper,backdrop),character),caption)
# Integer translation of an actual independently decoded stamp export, on the
# same white backing, supplies the platform-specific emoji reference.
stamp_image=Image.open(downloads/'mouse-audit-stamps-animals.png').convert('RGBA')
reference.paste(stamp_image.crop((14,39,97,123)),(650,79))
reference.save(folder/'mix-reference.png')
hashes={}
for name,opacity in [('mix-opaque.retropaint',1),('mix-half-character.retropaint',.5)]:
    variant=copy.deepcopy(base);variant['layers'][2]['opacity']=opacity
    data=(json.dumps(variant,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8');(folder/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
report={'fixture':'MIX','dimensions':[960,640],'layer_order_bottom_to_top':['Paper','Backdrop','Character','Caption'],
 'character_patches':{'red':[100,100,100,80],'green':[100,300,100,80]},'backdrop':'#1E88E5',
 'caption':'Pillow Arial48 text plus genuine mouse-created dog stamp with white backing',
 'source_stamp_project':'mouse-audit-stamps-animals.retropaint','source_stamp_png':'mouse-audit-stamps-animals.png',
 'stamp_integer_translation':[636,40],'expected_reference':'mix-reference.png','sha256':hashes}
(folder/'mix-provenance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
