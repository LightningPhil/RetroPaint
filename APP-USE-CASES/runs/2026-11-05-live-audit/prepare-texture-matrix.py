"""Declare seven labelled PLAY paint/fill rows and periodicity checks in advance."""
from pathlib import Path
from PIL import Image,ImageDraw
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures/texture51';folder.mkdir(exist_ok=True);source=Path.home()/'Downloads/mouse-audit-play-960-baseline.retropaint';d=json.loads(source.read_bytes());assert (d['width'],d['height'])==(960,640) and len(d['layers'])==1
image=Image.new('RGBA',(960,640),'white');draw=ImageDraw.Draw(image);rows=[]
for i,name in enumerate(['brick','dots','weave','grass','stone','water','static']):
    y=60+i*85;draw.text((10,y-5),name,fill='black');draw.text((450,y-5),name,fill='black');draw.rectangle((520,y-40,930,y+40),outline='black',width=1)
    rows.append({'name':name,'ink':'tex-'+name,'paint_line':[[90,y],[400,y]],'fill_seed':[700,y],'fill_bounds':[521,y-39,930,y+40],'period':48 if name=='static' else 64,'animated':name in ['water','static']})
b=io.BytesIO();image.save(b,format='PNG');d['layers'][0]['image']='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode();d['layers'][0]['paper']=None;path=folder/'labelled-play.retropaint';path.write_text(json.dumps(d,separators=(',',':')),encoding='utf-8')
plan={'recorded_before_native_execution':True,'fixture':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source_PLAY_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'brush':'Squeaky Marker','size':72,'strength':1,'clock':[12345,23456],'rows':rows,'oracle':'All14nativepaint/fillactions; exactaffected/exteriorRGBA, retainedoldmaterialdefinitions; 64pixelperiod forfivefixedpatternsandWater,48forStatic withinopaqueinteriors, namedsourcecolours/structureverifiedindependently; twofixedtimesonlyWater/Staticregionschange, nativeproject/PNG reopensandUndoRedoexact, zoomviewonly.'};(folder/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8');print('Prepared all7 labelled PLAY rows, eachpaint+boundedfill, fixedclock/periodicity/history/reopen plan')
