"""Check coloured-paper exploration and a deliberate second-ink dot."""
import base64,hashlib,io,json
from pathlib import Path
from PIL import Image,ImageChops
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def actual(suffix,ext='retropaint'):
 name='mouse-audit-spiro-explore36-'+suffix+'.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(suffix):return json.loads(actual(suffix))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
before=doc('before');assert before==doc('after')==doc('cancelled')==doc('secondary-undone')
png=image(actual('before','png'));assert png.size==(960,640) and png.tobytes()==image(actual('after','png')).tobytes()==image(actual('cancelled','png')).tobytes()
source=image(base64.b64decode(before['layers'][0]['image'].split(',',1)[1]));assert png.tobytes()==source.tobytes()
assert source.getpixel((0,0))==(253,216,53,255) and sum(p==(30,136,229,255) for p in source.get_flattened_data())>100
e=json.loads((out/'spiro-explore36-evidence.json').read_bytes());assert e['before']['blue']==e['afterCancel']['blue']=='true' and e['before']['secondary']==e['afterCancel']['secondary']=='#9d4edd' and e['afterCancel']['selectedGear']=='red' and e['afterCancel']['ghostHidden']
secondary=doc('secondary');expected=json.loads(json.dumps(before));expected['layers'][0]['image']=secondary['layers'][0]['image'];assert expected==secondary
marked=image(actual('secondary','png'));assert marked.tobytes()==image(base64.b64decode(secondary['layers'][0]['image'].split(',',1)[1])).tobytes()
assert marked.getpixel((300,100))==(157,78,221,255)
difference=ImageChops.difference(marked.convert('RGB'),png.convert('RGB'));bounds=difference.getbbox();assert bounds and bounds[0]>=297 and bounds[1]>=97 and bounds[2]<=304 and bounds[3]<=104
report={'status':'Pass','whole_project_and_png_unchanged_by_open_close_and_rejected_drag':True,'yellow_paper_and_blue_primary_unchanged':True,'purple_secondary_visible_and_actual_right_click_colour':True,'deliberate_secondary_dot_bounds':bounds,'one_undo_removes_only_deliberate_dot':True,'sha256':hashes}
(out/'spiro-explore36-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
