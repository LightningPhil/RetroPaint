"""PLAY contrasting-backing copy and all twelve visible palette colours."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures';source=Path.home()/'Downloads/mouse-audit-play-960-baseline.retropaint';d=json.loads(source.read_bytes());assert d['width']==960 and d['height']==640 and len(d['layers'])==1
b=io.BytesIO();Image.new('RGBA',(960,640),(80,80,80,255)).save(b,format='PNG');d['layers'][0]['image']='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode();d['layers'][0]['paper']='#505050';d['drawingMode']='raster'
path=folder/'palette45-contrasting-play.retropaint';raw=json.dumps(d,separators=(',',':')).encode();path.write_bytes(raw)
names=['Red','Yellow','Blue','Green','Black','Pink','Mint','Teal','Gold','Purple','Orange','White'];colours=['#E53935','#FDD835','#1E88E5','#43A047','#1A1A1A','#EF476F','#06D6A0','#118AB2','#FFD166','#9D4EDD','#FF9F1C','#FFFFFF']
rows=[{'name':n,'hex':c,'start':[60+(i%6)*150,200+(i//6)*200],'end':[130+(i%6)*150,200+(i//6)*200]} for i,(n,c) in enumerate(zip(names,colours))];rows.append({'name':'Red','hex':colours[0],'start':[60,520],'end':[130,520]})
plan={'recorded_before_execution':True,'fixture':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'original_PLAY_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'backing_variant':'Original white PLAY remains untouched. Separate uniform#505050copy ensures everystandardcolour, includingWhite,isvisible perINK001alternative.','size':22,'strength':1,'applicator':'Squeaky Marker','rows':rows};(folder/'palette45-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8');print('Prepared 12 swatches and return-to-Red stroke on contrasting PLAY copy')
