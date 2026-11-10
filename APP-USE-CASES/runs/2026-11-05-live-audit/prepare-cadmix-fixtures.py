"""Prepare CADMIX from actual mouse-created, independently verified shell/label data."""
import base64,copy,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures';downloads=Path.home()/'Downloads'
def read(name):return json.loads((downloads/name).read_text(encoding='utf-8'))
def url(image):
    stream=io.BytesIO();image.save(stream,format='PNG');return 'data:image/png;base64,'+base64.b64encode(stream.getvalue()).decode()
shell=read('mouse-audit-shell20-top (1).retropaint')
desk=read('mouse-audit-journey7-desk-pot.retropaint')
photo=read('mouse-audit-journey4-final.retropaint')
cad=copy.deepcopy(next(layer for layer in shell['layers'] if layer.get('cad')))
view=copy.deepcopy(next(layer['cad']['view'] for layer in desk['layers'] if layer.get('cad')))
label=copy.deepcopy(desk['layers'][-1]);label['id']=204;label['name']='Paint above 3D'
label['objects'][0]['color']='#9D4EDD'
assert label['objects'][0]['kind']=='text' and label['objects'][0]['callout']
arrow=Image.open(io.BytesIO(base64.b64decode(label['image'].split(',')[1]))).convert('RGBA')
draw=ImageDraw.Draw(arrow);draw.line((650,470,550,350),fill='#1E88E5',width=6)
draw.polygon([(550,350),(559,380),(579,363)],fill='#1E88E5');label['image']=url(arrow)
cad.update(id=203,name='Shell model',visible=True,opacity=1)
assert len(cad['cad']['bodies'])==1 and cad['cad']['bodies'][0]['solid']['thickness']==3
paper={'id':201,'name':'Paper','visible':True,'opacity':1,'paper':'#ffffff','image':url(Image.new('RGBA',(960,640),'white')),'live':{'strokes':[],'fills':[],'sparkles':[]}}
green=Image.new('RGBA',(960,640),'#16A34A')
natural=Image.open(root/'test-results/audit-2026-11-05/mouse/photo-natural-original.jpg').convert('RGBA').resize((960,640),Image.Resampling.LANCZOS)
natural.save(folder/'cadmix-natural-guide.png')
trace=green.copy();draw=ImageDraw.Draw(trace);draw.rectangle((416,288,544,352),outline='black',width=2)
draw.line((416,400,544,400),fill='black',width=2);draw.line((416,394,416,406),fill='black',width=2);draw.line((544,394,544,406),fill='black',width=2)
draw.text((420,410),'20 mm reference',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18),fill='black')
hashes={}
for name,projection,guide,crop in [
 ('cadmix-green-perspective','perspective',green,{'x':0,'y':0,'width':1,'height':1}),
 ('cadmix-green-orthographic','orthographic',green,{'x':0,'y':0,'width':1,'height':1}),
 ('cadmix-photo-crop','perspective',natural,{'x':.1,'y':.1,'width':.8,'height':.8}),
 ('cadmix-trace-guide','orthographic',trace,{'x':0,'y':0,'width':1,'height':1})
]:
    guide_layer={'id':202,'name':'Guide photo' if guide is natural else 'Backdrop','visible':True,'opacity':1,'paper':False,'image':url(guide),'live':{'strokes':[],'fills':[],'sparkles':[]}}
    if guide is natural:
        guide_layer['photo']=copy.deepcopy(photo['layers'][0]['photo']);guide_layer['photo']['settings']['crop']=crop.copy()
    body_layer=copy.deepcopy(cad);body_layer['cad']['view']=copy.deepcopy(view);body_layer['cad']['view']['projection']=projection
    if guide is trace:body_layer['cad']['view']={'position':[0,0,200],'target':[0,0,0],'up':[0,1,0],'projection':'orthographic','span':100}
    document={'format':'RetroPaint','version':11,'drawingMode':'raster','width':960,'height':640,'crop':crop,'active':203,'layers':[copy.deepcopy(paper),guide_layer,body_layer,copy.deepcopy(label)]}
    data=(json.dumps(document,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8');(folder/(name+'.retropaint')).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
report={'fixture':'CADMIX','dimensions':[960,640],'source_shell':'mouse-audit-shell20-top (1).retropaint',
 'source_caption_and_camera':'mouse-audit-journey7-desk-pot.retropaint','source_photo_recipe':'mouse-audit-journey4-final.retropaint',
 'guide_source':'photo-natural-original.jpg, public-domain provenance separately retained; resized independently with Pillow LANCZOS',
 'layer_order_bottom_to_top':['Paper','Backdrop or Guide photo','Shell model','Paint above 3D'],
 'coloured_arrow':{'colour':'#1E88E5','line_pixels':[650,470,550,350],'width':6,'head_pixels':[[550,350],[559,380],[579,363]]},
 'shell_recipe':'Exact unscaled20mmcube + diameter20cylinder X15, 3mm top opening; independent prior STL proof',
 'trace_calibration':{'projection':'Top orthographic','vertical_span_mm':100,'pixels_per_mm':6.4,'reference_pixels':128,'reference_mm':20,'rectangle_pixels':[416,288,128,64],'rectangle_mm':[20,10]},
 'sha256':hashes}
(folder/'cadmix-provenance.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
