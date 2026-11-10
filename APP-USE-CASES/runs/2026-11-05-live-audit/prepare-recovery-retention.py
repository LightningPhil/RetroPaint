"""Predeclare native recovery count, byte budget and independent eligibility inputs."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures/recovery45';folder.mkdir(exist_ok=True);rows=[]
def png(a):
    b=io.BytesIO();Image.fromarray(a).save(b,format='PNG');return 'data:image/png;base64,'+base64.b64encode(b.getvalue()).decode()
def write(label,image,size,layers=1):
    d={'format':'RetroPaint','version':10,'drawingMode':'raster','width':size,'height':size,'crop':{'x':0,'y':0,'width':1,'height':1},'active':1,'layers':[{'id':i+1,'name':label if i==0 else 'Second sheet','visible':True,'opacity':1,'paper':None,'live':{'strokes':[],'fills':[],'sparkles':[]},'image':image} for i in range(layers)]}
    b=json.dumps(d,separators=(',',':')).encode();path=folder/(label+'.retropaint');path.write_bytes(b);rows.append({'label':label,'file':str(path),'source_characters':len(b),'stored_pixels':size*size*layers,'sha256':hashlib.sha256(b).hexdigest()})
for i in range(1,11):
    a=np.full((32,32,4),255,dtype=np.uint8);a[8:24,8:24,:3]=[i*20,40,220-i*15];write(f'Count {i:02}',png(a),32)
rng=np.random.default_rng(450612);a=np.empty((2048,2048,4),dtype=np.uint8);a[:,:,:3]=rng.integers(0,256,(2048,2048,3),dtype=np.uint8);a[:,:,3]=255;noise=png(a)
for i in range(1,5):write(f'Budget {i:02}',noise,2048)
a=np.empty((4096,4096,4),dtype=np.uint8);a[:,:,:3]=rng.integers(0,256,(4096,4096,3),dtype=np.uint8);a[:,:,3]=255;write('Serialized cutoff',png(a),4096)
assert rows[-1]['source_characters']>50_000_000 and rows[-1]['stored_pixels']<24_000_000
a=np.full((4096,4096,4),255,dtype=np.uint8);write('Pixel cutoff',png(a),4096,2)
assert rows[-1]['source_characters']<50_000_000 and rows[-1]['stored_pixels']>24_000_000
plan={'recorded_before_native_execution':True,'origin':'127.0.0.1:65487 isolated audit database','count':'Ten native openings with distinct32square source pixels; wait each Draft saved. Last eight Count03..10 must remain, old count01/02 absent.','budget':'Four native2048square opaque randomRGB documents. RGB entropy alone implies at least33.55MB UTF16 draft each; four exceed128M, three fit. Newest Budget04 protected; verify actual browser-produced saved project lengths before count assertion.','cutoffs':'4096square one opaque noise layer stays below24M pixels but exceeds50M JSON characters. Two white4096square layers exceed24M pixels but stay below50M characters. Neither cutoff may remove latest valid draft; Save project remains available.','files':rows};(folder/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8');print(json.dumps([{k:v for k,v in r.items() if k not in ['sha256','file']} for r in rows],indent=2))
