"""Independent editable raster source resolution, transform and clipping oracle."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def decode(data):return image(base64.b64decode(data.split(',',1)[1]))
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-trim38-editable-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
def near(a,b):assert len(a)==len(b) and max(abs(x-y) for x,y in zip(a,b))<1e-9
src=image((out.parent/'fixtures/patch-labelled.png').read_bytes());card=image((out.parent/'fixtures/trim-labelled-card.png').read_bytes());rotated=card.transpose(Image.Transpose.ROTATE_270);before=doc('before');layer=before['layers'][0];assert before['drawingMode']=='vector' and len(layer['objects'])==2;bg,original=layer['objects'];assert bg['kind']==original['kind']=='raster' and bg['matrix']==[1,0,0,1,0,0] and decode(bg['image']).tobytes()==src.tobytes();assert decode(original['image']).tobytes()==card.tobytes() and (original['width'],original['height'])==(120,100);near(original['matrix'],[0,1,-1,0,530,260]);expected=src.copy();expected.alpha_composite(rotated,(430,260));assert image(actual('before','png')).tobytes()==expected.tobytes()
e=json.loads((out/'edit-trim38-editable-evidence.json').read_bytes());assert len(e['cases'])==5 and e['piece']['value']==original['id']
spec={'left':((0,0,120,60),[0,1,-1,0,60,260]),'right':((0,40,120,100),[0,1,-1,0,960,260]),'top':((40,0,120,100),[0,1,-1,0,530,0]),'bottom':((0,0,60,100),[0,1,-1,0,530,580])};results=[]
for c in e['cases']:
 edge=c['edge'];after=doc(edge+'-placed');objects=after['layers'][0]['objects'];complete=json.loads(json.dumps(before));assert objects[0]==bg
 if edge=='outside':
  assert len(objects)==1;complete['layers'][0]['objects']=[bg]
 else:
  assert len(objects)==2;obj=objects[1];crop,matrix=spec[edge];expected_source=card.crop(crop);assert decode(obj['image']).tobytes()==expected_source.tobytes() and (obj['width'],obj['height'])==expected_source.size;near(obj['matrix'],matrix)
  w,h=expected_source.size;clip=obj['clip'];assert len(clip)==4
  assert all(min(abs(p['x']-x)+abs(p['y']-y) for x,y in [(0,0),(w,0),(w,h),(0,h)])<1e-9 for p in clip)
  area=abs(sum(p['x']*clip[(i+1)%4]['y']-clip[(i+1)%4]['x']*p['y'] for i,p in enumerate(clip)))/2;assert abs(area-w*h)<1e-7
  expected_obj=json.loads(json.dumps(original))
  for key in ['image','width','height','matrix','clip']:expected_obj[key]=obj[key]
  assert obj==expected_obj;complete['layers'][0]['objects'][1]=obj
 assert after==complete and doc(edge+'-undone')==before
 if edge!='left':assert doc(edge+'-redone')==after
 expected_png=src.copy();expected_png.alpha_composite(rotated,tuple(c['position']));assert image(actual(edge+'-placed','png')).tobytes()==expected_png.tobytes()
 assert c['beforePlaceSize']=='100 × 120 px · trims on Place' and not c['selectionVisible'] and c['placementStatus']=='Placed. Off-paper raster pixels were trimmed. Undo brings them back.'
 if edge=='left':
  returned=doc('left-returned');returned_obj=returned['layers'][0]['objects'][1];near(returned_obj['matrix'],[0,1,-1,0,360,400]);expected_return=json.loads(json.dumps(after));expected_return['layers'][0]['objects'][1]['matrix']=returned_obj['matrix'];assert returned==expected_return and c['returnedSize']=='60 × 120 px'
  moved=src.copy();moved.alpha_composite(rotated.crop((40,0,100,120)),(300,400));assert image(actual('left-returned','png')).tobytes()==moved.tobytes() and doc('left-return-undone')==after and doc('left-return-redone')==returned
 results.append({'edge':edge,'retained_source_size':None if edge=='outside' else list(expected_source.size),'source_RGBA_and_matrix_exact':True,'export_and_whole_history_exact':True})
assert doc('reopened')==doc('outside-redone') and image(actual('reopened','png')).tobytes()==src.tobytes()
assert json.loads((out/'edit-trim38-raster-verification.json').read_bytes())['ordinary_raster_matrix_status']=='Pass'
report={'status':'Pass','ordinary_and_editable_raster_matrices_complete':True,'editable_source_resolution_and_transform_retained':results,'moved_back_fragment_keeps_clipped_source_without_resampling':True,'background_object_and_all_other_document_fields_unchanged':True,'native_project_png_reopen_exact':True,'sha256':hashes};(out/'edit-trim38-editable-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
