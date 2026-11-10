"""Compare native screenshot Before crops with independently selected source pixels."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';ui=json.loads((out/'enhance151-ui.json').read_text());source=Image.open(root/'test-results/audit-2026-11-05/fixtures/photo130-landscape.png').convert('RGB');metrics={}
assert ui['size64']=='493,1017,64,64' and ui['right8']=='501,1017,64,64' and ui['down32']=='501,1049,64,64' and ui['invalidated']
assert ui['dragEdge']==ui['repeatEdge']=='1844,1142,256,256'
box=ui['previewBox'];side=round(min(box['w'],box['h']));left=round(box['x']+(box['w']-side)/2);top=round(box['y']+(box['h']-side)/2)
for size in [64,128,256]:
    x,y,w,h=map(int,ui[f'size{size}'].split(','));before=np.array(Image.open(out/f'enhance151-{size}-before.png').convert('RGB'))[top+3:top+side-3,left+3:left+side-3].astype(float);enhanced=np.array(Image.open(out/f'enhance151-{size}-enhanced.png').convert('RGB'))[top+3:top+side-3,left+3:left+side-3].astype(float)
    expected=np.array(source.crop((x,y,x+w,y+h)).resize((side,side),Image.Resampling.BICUBIC))[3:-3,3:-3].astype(float);error=float(abs(before-expected).mean());correlation=float(np.corrcoef(before.ravel(),expected.ravel())[0,1]);difference=float(abs(enhanced-before).mean());assert error<7 and correlation>.97,(size,error,correlation);assert difference>.1,(size,difference)
    metrics[str(size)]=dict(before_mean_RGB_error=error,source_correlation=correlation,neural_vs_before_mean_RGB_difference=difference)
report=dict(status='Pass',metrics=metrics,exact_keyboard_steps=[8,32],invalidates_detail=True,edge_repeats_do_not_wrap=True);(out/'enhance151-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
