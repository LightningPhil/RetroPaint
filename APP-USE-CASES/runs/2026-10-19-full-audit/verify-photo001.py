from pathlib import Path
from datetime import datetime,timezone
import base64,hashlib,io,json
from PIL import Image,ImageChops,ImageOps

root=Path(__file__).resolve().parent
repo=root.parents[2]
e=root/'evidence'
read=lambda name:json.loads((e/name).read_text(encoding='utf-8'))
png=lambda name:Image.open(e/name).convert('RGBA')
hidden=read('PHOTO-001-hidden-before.retropaint')
assert hidden==read('PHOTO-001-hidden-after.retropaint')
assert len(hidden['layers'])==1 and not hidden['layers'][0]['visible']
assert hidden['layers'][0]['image']==read('PHOTO-002-before-navigation.retropaint')['layers'][0]['image']
assert png('PHOTO-001-hidden-before.png').tobytes()==png('PHOTO-001-hidden-after.png').tobytes()
assert png('PHOTO-001-hidden-after.png').getchannel('A').getextrema()==(0,0)
assert 'Show this layer and raise its opacity before opening Photo lab.' in (e/'PHOTO-001-hidden-rejected.txt').read_text(encoding='utf-8')
before=read('PHOTO-001-import-context-before.json')
failure=read('PHOTO-001-import-context-before-fix.json')
fixed=read('PHOTO-001-import-context-after-fix.json')
assert before['expected_after_import']=='detail-noise' and not failure['passed'] and failure['actual']['group']=='light-basic'
assert fixed['group']==fixed['reopenedGroup']=='detail-noise'
assert {v['name']:v['value'] for v in fixed['noise']}=={'Luminance noise':'0','Colour noise':'0'}
assert {v['name']:v['value'] for v in fixed['light']}=={'Exposure':'0','Brightness':'0','Contrast':'0'}
assert 'FAIL Photo import retains' in (e/'PHOTO-001-context-regression-before.txt').read_text(encoding='utf-8')
assert 'PASS Photo import retains' in (e/'PHOTO-001-context-regression-after.txt').read_text(encoding='utf-8')
source=read('PHOTO-001-new-source-after-fix.retropaint')
assert (source['width'],source['height'])==(4031,2267) and len(source['layers'])==1
layer=source['layers'][0]
assert source['active']==layer['id'] and source['active']!=hidden['active'] and layer['visible'] and layer['opacity']==1
assert source['crop']==dict(x=0,y=0,width=1,height=1) and not layer.get('photo') and not layer.get('cad') and not layer.get('objects')
embedded=Image.open(io.BytesIO(base64.b64decode(layer['image'].split(',',1)[1]))).convert('RGBA')
saved=png('PHOTO-001-new-source-after-fix.png')
assert embedded.tobytes()==saved.tobytes()
original=ImageOps.exif_transpose(Image.open(repo/'Example_Images/Sunset.jpg')).convert('RGBA')
assert original.size==saved.size
maximum=max(hi for lo,hi in ImageChops.difference(original,saved).getextrema())
assert maximum<=2,maximum
assert source==read('PHOTO-001-new-source-reopened-production.retropaint')
assert saved.tobytes()==png('PHOTO-001-new-source-reopened-production.png').tobytes()
production=read('PHOTO-001-production-context.json')
assert production['group']=='detail-noise' and production['dimensions'].startswith('3896 × 2586')
assert all(v['value']=='0' for v in production['noise'])
fresh=read('PHOTO-001-production-fresh-source.retropaint')
assert (fresh['width'],fresh['height'])==(3896,2586) and len(fresh['layers'])==1 and fresh['layers'][0]['visible'] and not fresh['layers'][0].get('photo')
assert png('PHOTO-001-production-fresh-source.png').tobytes()==png('PHOTO-source-Laukka.png').tobytes()
assert read('NATIVE-cancel-independent-verification.json')['photo_draft_group_and_all_experiment_values_restored']
report=dict(at=datetime.now(timezone.utc).isoformat(),decoder='Pillow '+Image.__version__,hidden_target_rejection_preserves_complete_project_and_pixels=True,ordinary_reopen_remembers_group=True,new_photo_import_remembers_group=True,new_photo_receives_fresh_values=True,new_target_visible_and_distinct=True,source_dimensions=[4031,2267],source_jpeg_sha256=hashlib.sha256((repo/'Example_Images/Sunset.jpg').read_bytes()).hexdigest(),jpeg_cross_decoder_maximum_channel_difference=maximum,embedded_source_and_export_exact=True,actual_project_fresh_production_reopen_exact=True,production_reverse_photo_import_verified=True,native_picker_cancel_restores_complete_draft=True,original_failure_preserved=True)
(e/'PHOTO-001-independent-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
