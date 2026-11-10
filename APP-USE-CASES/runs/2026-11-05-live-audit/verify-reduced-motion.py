"""Independent exported pixels and motor outcomes for ACCESS-010."""
import base64,hashlib,io,json,math
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def data(stage,ext='retropaint'):
    name='mouse-audit-motion-'+stage+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(stage):return json.loads(data(stage))
before=doc('before');assert before==doc('motor-before')==doc('motor-undone')
after=doc('motor-after');assert after==doc('motor-redone')==doc('motor-reopened')
assert len(before['layers'])==len(after['layers'])==4 and before['active']==after['active']==103
for a,b in zip(before['layers'],after['layers']):
    if a['id']!=103:assert a==b
    else:
        for k in a:
            if k!='image':assert a[k]==b[k],k
        old=Image.open(io.BytesIO(base64.b64decode(a['image'].split(',',1)[1]))).convert('RGBA')
        new=Image.open(io.BytesIO(base64.b64decode(b['image'].split(',',1)[1]))).convert('RGBA')
        black=sum(p==(26,26,26,255) for p in new.get_flattened_data());assert black>1000
        changed=0
        for y in range(640):
            for x in range(960):
                if old.getpixel((x,y))!=new.getpixel((x,y)):
                    assert math.hypot(x+.5-480,y+.5-320)<214,'Motor changed paint outside its 200px ring and22px nib'
                    changed+=1
        assert changed>1000
normal=Image.open(io.BytesIO(data('normal','png'))).convert('RGBA');reduced=Image.open(io.BytesIO(data('reduced','png'))).convert('RGBA')
assert normal.size==reduced.size==(960,640) and normal.tobytes()==reduced.tobytes()
e=json.loads((out/'motion-evidence.json').read_bytes());assert 'reduced-motion' in e['reduced']['class'] and e['styles']['transition']=='0s'
assert 'reduced-motion' in e['motorObserved']['bodyClass'] and e['motorObserved']['auto']=='true'
assert e['motorObserved']['at']>e['motorStarted']+1000
assert 'reduced-motion' not in e['restored']['bodyClass'] and e['restored']['styles']['transition']=='0.16s'
frames={}
for kind,box in [('live',(900,465,1055,486)),('motor',(730,200,1040,470))]:
    a=Image.open(out/f'motion-{kind}-t0.png').convert('RGB').crop(box);b=Image.open(out/f'motion-{kind}-t1.png').convert('RGB').crop(box)
    count=sum(any(p) for p in ImageChops.difference(a,b).get_flattened_data());assert count>100,(kind,count);frames[kind]=count
report={'status':'Pass','decorative_transition_zero_and_restored_016_seconds':True,'frozen_clock_actual_exports_pixel_identical':True,'live_ink_and_motor_remain_active_under_reduced_motion':True,'changed_screenshot_pixels':frames,'new_motor_black_pixels':black,'motor_source_changed_pixels':changed,'all_neighbouring_layers_and_existing_live_recipe_exact':True,'whole_undo_redo_and_native_reopen_exact':True,'sha256':hashes}
(out/'reduced-motion-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
