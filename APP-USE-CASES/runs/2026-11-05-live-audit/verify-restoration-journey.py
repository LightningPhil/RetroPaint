"""Check separate native enhancement output and exact original/restoration recovery."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data)
    hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(name):return json.loads(retain('mouse-audit-restoration-'+name+'.retropaint'))
def png(name):return Image.open(io.BytesIO(retain('mouse-audit-restoration-'+name+'.png'))).convert('RGBA')
original=doc('original');edited=doc('edited');after=doc('after-enhance')
assert edited==after==doc('reset-undone')
assert original['layers'][0]['image']==edited['layers'][0]['image']
settings=edited['layers'][0]['photo']['settings']
assert settings['noise']==18 and settings['colourNoise']==12 and settings['balance']!=[1,1,1]
assert settings['curves']['rgb']==[{'x':0,'y':0},{'x':.25,'y':.18},{'x':.75,'y':.82},{'x':1,'y':1}]
source=Image.open(root/'test-results/audit-2026-11-05/fixtures/restoration-240.png').convert('RGBA')
assert png('reset').tobytes()==source.tobytes()
restoration=png('edited');enhanced=png('edited-2x-enhanced')
assert restoration.size==(240,160) and enhanced.size==(480,320)
assert enhanced.getchannel('A').getextrema()==(255,255)
assert enhanced.tobytes()!=restoration.resize((480,320),Image.Resampling.LANCZOS).tobytes()
assert any(lo<hi for lo,hi in enhanced.getextrema()[:3])
doc('reset')
report={'editable_restoration_unchanged_by_enhancement':True,'captured_original_unchanged':True,
        'photo_reset_recovers_original_pixels_exactly':True,'reset_undo_restores_whole_project_exactly':True,
        'enhanced_png_size':[480,320],'editable_source_size':[240,160],
        'enhanced_not_a_plain_lanczos_resize':True,'synthetic_restoration_fixture':True,'sha256':hashes}
(out/'restoration-journey-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
