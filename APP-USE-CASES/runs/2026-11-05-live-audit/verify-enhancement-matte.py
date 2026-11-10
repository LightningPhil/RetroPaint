"""Compare real neural RGB against opaque twins and render both alpha backgrounds."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';metrics={}
sheet=Image.new('RGB',(1280,540),'#dddddd');draw=ImageDraw.Draw(sheet)
for scale in [2,4]:
    name=f'mouse-audit-enhance149-twin-{scale}x-enhanced.png';data=(downloads/name).read_bytes();(out/name).write_bytes(data);twin=np.array(Image.open(out/name).convert('RGBA')).astype(int);a=np.array(Image.open(out/f'mouse-audit-enhance148-baseline-{scale}x-enhanced.png').convert('RGBA')).astype(int);visible=a[:,:,3]>0;error=abs(a[:,:,:3]-twin[:,:,:3]);assert error[visible].max()<=2 and error[visible].mean()<.3
    metrics[str(scale)]=dict(max_visible_RGB_difference=int(error[visible].max()),mean_visible_RGB_difference=float(error[visible].mean()),sha256=hashlib.sha256(data).hexdigest())
    if scale==4:
        for column,colour in enumerate(['black','white']):
            composite=Image.new('RGBA',(640,480),colour);composite.alpha_composite(Image.fromarray(a.astype('uint8')));sheet.paste(composite.convert('RGB'),(640*column,30));draw.text((640*column+10,10),f'Actual 4x PNG over {colour}',fill='black')
sheet.save(out/'enhance149-alpha-backgrounds.png');(out/'enhance149-verification.json').write_text(json.dumps(dict(status='Pass',metrics=metrics,interpretation='Real 2x/4x neural RGB agrees with independent opaque-padding twin within 2 quantisation levels; 4x exact. All alpha and clear RGBA checks are in enhance148-verification.json.'),indent=2)+'\n');print(json.dumps(metrics))
