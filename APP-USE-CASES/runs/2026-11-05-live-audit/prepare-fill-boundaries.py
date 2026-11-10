"""Exact prescribed FILL family and independent four-neighbour RGBA-L1 oracle."""
from pathlib import Path
from PIL import Image,ImageDraw
from collections import deque
import base64,copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];folder=root/'test-results/audit-2026-11-05/fixtures/fill49';folder.mkdir(exist_ok=True)
template=json.loads((Path.home()/'Downloads/mouse-audit-wheel48-before.retropaint').read_bytes());rows=[]
for variant in ['closed','gap','antialiased','transparent','noise']:
    image=Image.new('RGBA',(320,240),'white');draw=ImageDraw.Draw(image);draw.rectangle((20,20,140,140),fill='#E8E8E8',outline='black',width=1);draw.rectangle((220,40,259,79),fill='#E8E8E8')
    if variant=='gap':image.putpixel((80,20),(255,255,255,255))
    if variant=='antialiased':draw.rectangle((21,21,139,139),outline=(100,100,100,255),width=1)
    if variant=='transparent':draw.rectangle((21,21,139,139),fill=(232,232,232,0))
    if variant=='noise':
        for y in range(21,140):
            for x in range(21,140):
                v=232+[-8,0,8][min(2,(x-21)//40)];image.putpixel((x,y),(v,v,v,255))
    d=copy.deepcopy(template);d['width']=320;d['height']=240;d['layers']=d['layers'][:2];d['activeLayer']=d['layers'][1]['id']
    for layer,picture in zip(d['layers'],[Image.new('RGBA',(320,240),(80,80,80,255)),image]):
        b=io.BytesIO();picture.save(b,format='PNG');layer['image']='data:image/png;base64,'+base64.b64encode(b.getvalue()).decode();layer['paper']=None
    path=folder/(variant+'.retropaint');path.write_text(json.dumps(d,separators=(',',':')),encoding='utf-8');image.save(folder/(variant+'.png'))
    composite=np.array(Image.alpha_composite(Image.new('RGBA',(320,240),(80,80,80,255)),image));seed=(80,80)
    for tolerance in ([0,23,24,200] if variant=='noise' else [80]):
        mask=np.zeros((240,320),dtype=bool);queue=deque([seed]);target=composite[seed[1],seed[0]].astype(int)
        while queue:
            x,y=queue.popleft()
            if not (0<=x<320 and 0<=y<240) or mask[y,x]:continue
            pixel=composite[y,x].astype(int)
            if not ((target[3]==0 and pixel[3]==0) or np.abs(pixel-target).sum()<=tolerance):continue
            mask[y,x]=True;queue.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
        label=f'{variant}-{tolerance}';Image.fromarray(mask.astype('uint8')*255).save(folder/(label+'-mask.png'));rows.append({'label':label,'fixture':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'variant':variant,'tolerance':tolerance,'seed':seed,'expected_fill_pixels':int(mask.sum())})
plan={'recorded_before_native_execution':True,'metric':'Four connected neighbours; sum of absolute RGBA differences from fixed seed <= tolerance, except both alpha0 always match. Source src/fill.ts reviewed before selecting23/24 boundary for neutral±8. Oracle independent queue implementation over independently composited fixture pixels.','ink':'#E53935','rows':rows};(folder/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8');print([(r['label'],r['expected_fill_pixels']) for r in rows])
