"""All actual native portrait/landscape ratios, resize, clamping and Cancel."""
from pathlib import Path
import base64,copy,hashlib,io,json,sys
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={};ui=json.loads((out/'ratio132-ui.json').read_text());complete=[r for r in ui if 'outside' in r];partial='--partial' in sys.argv
defaults=json.loads((downloads/'mouse-audit-photo98-full-reset.retropaint').read_text())['layers'][0]['photo']['settings'];details=[]
def load(orientation,index,ext='retropaint',cancel=False):
    name=f'mouse-audit-ratio132-{orientation}-{index}'+('-cancelled' if cancel else '')+'.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return json.loads(data) if ext=='retropaint' else np.array(Image.open(out/name).convert('RGBA'))
for row in complete:
    orientation,index=row['orientation'],row['index'];base=json.loads((downloads/f'mouse-audit-ratio130-{orientation}-baseline.retropaint').read_text());d=load(orientation,index);assert load(orientation,index,cancel=True)==d;c=d['crop'];w,h=row['source']['w'],row['source']['h'];x=round(c['x']*w);y=round(c['y']*h);cw=round(c['width']*w);ch=round(c['height']*h)
    if 'outside_rechecked_project' in row:
        name=row['outside_rechecked_project'];data=(downloads/name).read_bytes();assert json.loads(data)==d;(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
    assert row['shrunk']==dict(x=x,y=y,width=cw,height=ch);assert cw<row['initial']['width']*.8 and ch<row['initial']['height']*.8
    assert 0<=x<x+cw<=w and 0<=y<y+ch<=h
    outside=row['outside'];assert outside['width']>cw+5 and outside['height']>ch+5;assert outside['x']+outside['width']<=w and outside['y']+outside['height']<=h;assert outside['x']+outside['width']==w or outside['y']+outside['height']==h
    if index:
        ratio=float(row['option']['value']);assert abs(c['width']*w/(c['height']*h)-ratio)<1e-6
        assert abs(cw-ratio*ch)<(1+ratio)/2+.02;assert abs(outside['width']-ratio*outside['height'])<(1+ratio)/2+.02
        if index==1:assert abs(ratio-w/h)<1e-9
    else:assert abs(c['width']-.6)<1e-6 and abs(c['height']-.4)<1e-6
    s=copy.deepcopy(defaults);s['crop']=c;expected=copy.deepcopy(base);expected['crop']=c;expected['layers'][0]['photo']=dict(settings=s,normal=s,look='custom',lookActive=False);assert d==expected
    source=np.array(Image.open(io.BytesIO(base64.b64decode(base['layers'][0]['image'].split(',')[1]))).convert('RGBA'));a=load(orientation,index,'png');assert np.array_equal(a,source[y:y+ch,x:x+cw])
    details.append(dict(orientation=orientation,ratio=row['option']['label'],crop_pixels=[x,y,cw,ch],RGBA_exact=True,cancel_document_exact=True))
if not partial:assert len(complete)==16 and {(r['orientation'],r['index']) for r in complete}=={(o,i) for o in ['landscape','portrait'] for i in range(8)}
report=dict(status='Partial' if partial else 'Pass',native_cases_completed=len(complete),all_offered_ratios_resize_clamp_cancel_and_exact_export=True,whole_source_recipe_document_preserved=True,excluded_attempts='ratio130 boundary and ratio1313pxinset attempts did not resize. Rounded paper corner hit stage. ratio132 starts8pxinsidevisiblecorner and asserts resize before saving.',details=details,sha256=hashes)
(out/'ratio132-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(f'{report["status"]}: {len(complete)} native ratio variants, exact source PNG/document Cancel, resize/bounds/aspect')
