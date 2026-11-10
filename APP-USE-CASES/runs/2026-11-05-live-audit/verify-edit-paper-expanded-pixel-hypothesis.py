"""Independent exact paper-frame growth/crop with pixels and vector retention."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def actual(mode,suffix,ext='retropaint'):
 name=f'mouse-audit-edit-paper39-{mode}-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(mode,suffix):return json.loads(actual(mode,suffix))
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))
def expected_document(before,after,width,height):
 expected=json.loads(json.dumps(before));expected['width']=width;expected['height']=height;expected['layers'][0]['image']=after['layers'][0]['image'];assert after==expected
e=json.loads((out/'edit-paper39-evidence.json').read_bytes());assert len(e['cases'])==2;results=[]
for c in e['cases']:
 mode=c['mode'];before=doc(mode,'before');base=pixels(before);base_png=image(actual(mode,'before','png'));assert base.size==base_png.size==(960,640)
 if mode=='raster':
  source=(out.parent/'fixtures/patch-paper-square.png').read_bytes();provenance=json.loads((out.parent/'fixtures/patch-paper-square-provenance.json').read_bytes());assert hashlib.sha256(source).hexdigest()==provenance['sha256'] and base.tobytes()==image(source).tobytes();assert base.crop((650,300,750,400)).tobytes()==Image.new('RGBA',(100,100),(124,58,237,255)).tobytes();background=(0,0,0,0)
 else:assert len(before['layers'][0]['objects'])==9;background=(255,255,255,255)
 enlarged=doc(mode,'enlarged');reduced=doc(mode,'reduced');expected_document(before,enlarged,1200,800);expected_document(before,reduced,450,350)
 expected=Image.new('RGBA',(1200,800),background);expected.paste(base,(0,0));assert pixels(enlarged).tobytes()==expected.tobytes() and pixels(reduced).tobytes()==base.crop((0,0,450,350)).tobytes()
 expected_png=Image.new('RGBA',(1200,800),background);expected_png.paste(base_png,(0,0));assert image(actual(mode,'enlarged','png')).tobytes()==expected_png.tobytes() and image(actual(mode,'reduced','png')).tobytes()==base_png.crop((0,0,450,350)).tobytes()
 assert doc(mode,'reduction-undone')==enlarged and doc(mode,'enlargement-undone')==before and doc(mode,'enlargement-redone')==enlarged and doc(mode,'reduction-redone')==reduced
 assert doc(mode,'reopened')==reduced and image(actual(mode,'reopened','png')).tobytes()==image(actual(mode,'reduced','png')).tobytes()
 if mode=='raster':assert pixels(enlarged).crop((650,300,750,400)).tobytes()==base.crop((650,300,750,400)).tobytes()
 assert c['enlargedDimensions']=='1200 × 800 pixels · 1 layer' and c['reducedDimensions']=='450 × 350 pixels · 1 layer'
 results.append({'mode':mode,'source_pixel_dimensions_and_coordinates_exact':True,'new_area_RGBA':list(background),'clipped_content_recovered_by_undo':True,'all_nine_piece_definitions_and_matrices_unchanged':mode=='vector','whole_history_native_project_png_reopen_exact':True})
report={'status':'Pass','cases':results,'fixture_gap_recorded':'Separate PATCH copy adds the100pxsquare absent from the shared fixture; four original patches preserved.','sha256':hashes};(out/'edit-paper39-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
