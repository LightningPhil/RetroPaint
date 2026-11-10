"""Independent saved-recipe and frame comparisons for exact-size live journey."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
    data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(stem):return json.loads(retain('mouse-audit-journey3-960-'+stem+'.retropaint'))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
projects={name:doc(name) for name in ['water','conveyor','rainbow','final','reopened']}
final=projects['final'];assert final==projects['reopened']
assert (final['width'],final['height'],len(final['layers']))==(960,640,1)
live=final['layers'][0]['live'];assert len(live['fills'])==2 and len(live['strokes'])==1 and not live['sparkles']
assert all(fill['spec']['texture']=='water' for fill in live['fills'])
stroke=live['strokes'][0];assert stroke['spec']=={'kind':'conveyor','colors':['#E53935','#FDD835','#1E88E5'],'speed':3,'mode':'ooze','along':True,'texture':None}
assert all(point['w']==22 for point in stroke['points'])
assert all(not item.get('rainbow') for item in live['strokes'])
source=image(base64.b64decode(final['layers'][0]['image'].split(',')[1]))
first=image(retain('mouse-audit-journey3-960-reopened.png'));later=image(retain('mouse-audit-journey3-960-later-frame.png'))
finished=image(retain('mouse-audit-journey3-960-final.png'))
assert first.size==later.size==finished.size==(960,640)
# Static rainbow and Spiro regions must survive exactly, while supported live
# water and conveyor regions must actually change after the native reopen.
static_box=(0,0,960,360)
assert source.crop(static_box).tobytes()==first.crop(static_box).tobytes()==later.crop(static_box).tobytes()==finished.crop(static_box).tobytes()
assert ImageChops.difference(first.crop((40,430,920,610)).convert('RGB'),later.crop((40,430,920,610)).convert('RGB')).getbbox()
assert ImageChops.difference(first.crop((130,365,830,405)).convert('RGB'),later.crop((130,365,830,405)).convert('RGB')).getbbox()
assert projects['conveyor']['layers'][0]['image']!=projects['rainbow']['layers'][0]['image']
assert projects['rainbow']['layers'][0]['live']==projects['conveyor']['layers'][0]['live']
assert projects['rainbow']['layers'][0]['image']!=final['layers'][0]['image']
report={'exact_fixture':[960,640],'whole_project_native_reopen_exact':True,'water_fills':2,'live_conveyor_colours':stroke['spec']['colors'],
 'water_and_conveyor_animate_after_reopen':True,'rainbow_baked_and_static_region_exact':True,'spiro_static_region_exact':True,
 'png_dimensions':[960,640],'sha256':hashes}
(out/'live-journey-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
