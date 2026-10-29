from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
import hashlib,json
root=Path(__file__).resolve().parent;folder=root/'fixtures/layer-limits';folder.mkdir(exist_ok=True)
limit=64_000_000;nearest=None
for count in range(2,17):
    for width in range(1,4097):
        height=limit//(count*width)+1
        if height<=4096:
            candidate=(count*width*height,count,width,height)
            if nearest is None or candidate<nearest:nearest=candidate
assert nearest==(64_000_006,7,2518,3631)
rows=[]
for label,width,height,count,reason in [('count',64,64,16,'16 sheets'),('exact-budget',4000,4000,4,'exactly64 million stored pixels'),('nearest-over-budget',2518,3631,6,'seventh sheet exceeds the budget by6 pixels')]:
    file=folder/(label+'.png');assert not file.exists(),'Retain original fixture bytes'
    image=Image.new('RGBA',(width,height),(30,136,229,255));draw=ImageDraw.Draw(image);draw.rectangle((0,0,15,15),fill=(229,57,53,255));draw.rectangle((width-16,height-16,width-1,height-1),fill=(67,160,71,128));image.save(file)
    rows.append(dict(label=label,width=width,height=height,max_layers=count,reason=reason,file=str(file),bytes=file.stat().st_size,sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
report=dict(at=datetime.now(timezone.utc).isoformat(),generator='Independent Pillow '+Image.__version__+' known RGBA with two corner patches',nearest_invalid_combination=dict(stored_pixels=nearest[0],layers=nearest[1],width=nearest[2],height=nearest[3]),nearest_search='All layer counts2..16 and widths1..4096; first integer height above budget, retained if<=4096. Minimum invalid total is64,000,006. Exact valid64,000,000 is4000x4000x4.',fixtures=rows)
(folder/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
