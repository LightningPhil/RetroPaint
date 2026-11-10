"""Preserved alpha/colour fixtures and budgets fixed before format execution."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures';downloads=Path.home()/'Downloads'
def uri(im):
 b=io.BytesIO();im.save(b,format='PNG');return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
source=downloads/'mouse-audit-edit-clipboard38-before.retropaint';d=json.loads(source.read_bytes());patch=copy.deepcopy(d['layers'][0]);patch.update(id=502,name='Known patches');patch['paper']=None
paper=copy.deepcopy(patch);paper.update(id=501,name='Paper',paper='#ffffff',image=uri(Image.new('RGBA',(960,640),'white')));d['layers']=[paper,patch];d['active']=502;d['drawingMode']='raster';path=folder/'patch-alpha-paper.retropaint';path.write_text(json.dumps(d,separators=(',',':'),ensure_ascii=False),encoding='utf-8')
colors=[('red',[255,0,0]),('orange',[255,128,0]),('yellow',[255,255,0]),('green',[0,255,0]),('aqua',[0,255,255]),('blue',[0,0,255]),('purple',[128,0,255]),('magenta',[255,0,255]),('neutral32',[32,32,32]),('neutral128',[128,128,128]),('neutral224',[224,224,224])]
a=np.zeros((640,960,4),dtype=np.uint8);alphas=[0,64,127,128,192,255];tiles=[]
for row,alpha in enumerate(alphas):
 for col,(name,rgb) in enumerate(colors):
  x,y=16+col*84,16+row*72;a[y:y+64,x:x+72]=rgb+[alpha];tiles.append({'name':name,'box':[x,y,72,64],'RGBA':rgb+[alpha]})
for y in range(464,640):
 for x in range(960):a[y,x]=[round(x*255/959),round((y-464)*255/175),(3*x+5*y)%256,255]
colour=folder/'colour-alpha-rich.png';Image.fromarray(a).save(colour)
plan={'recorded_before_execution':True,'source_project_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'patch_project':{'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'layers':['Paper opaque white visible','Known patches alpha source visible'],'main_action':'Hide Paper through Layers before exporting; source stays transparent after every save.'},'colour_source':{'file':str(colour),'sha256':hashlib.sha256(colour.read_bytes()).hexdigest(),'tiles':tiles,'opaque_ramp':[0,464,960,176]},'formats':['png','webp','tiff','jpeg','bmp','gif'],'oracles':{'png_tiff':'Every decoded source RGBA byte exact.','webp':'Alpha exact. Lossy RGB recorded; PATCH opaque/half-alpha interiors inset8: mean absolute RGB error<=3 and max<=8. Do not demand exact lossy RGB at text/patch edges.','jpeg':'Opaque white matte. Whole PATCH RGB mean absolute error<=3 and PSNR>=32dB. Insets8 of patches: mean<=3,max<=8; clear area at600,500 white within2 perchannel. Record edge/chroma loss.','bmp':'Every RGB byte equals independently white-matted source; no alpha payload.','gif':'Genuine still GIF; palette<=256; alpha only0/255, sourcealpha<128 clears and>=128 opaque. No exact truecolour/partialalpha claim. Opaque-source quantisation maxRGBerror bounded by37R,37G,85B for the8x8x4palette; count changed pixels and error.','backgrounds':'Independently composite decoded alpha formats over black and white and inspect contact sheet.'}}
(folder/'format-plan43.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in plan.items() if k not in ('colour_source','oracles')},indent=2))
