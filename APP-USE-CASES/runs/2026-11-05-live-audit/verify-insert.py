"""Independent inserted-source pixels, placement, scope, trimming, and limits."""
from pathlib import Path
from PIL import Image
from datetime import datetime
import base64,copy,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'insert43-evidence.json').read_bytes());assert len(e['cases'])==7 and len(e['reopens'])==6 and len(e['rejections'])==2
def actual(s,ext='retropaint'):
 name=f'mouse-audit-insert43-{s}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(s):return json.loads(actual(s))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def source(value):return image(base64.b64decode(value.split(',')[1]))
def same(a,b):assert a.size==b.size and a.tobytes()==b.tobytes()
small=image((root/'test-results/audit-2026-11-05/fixtures/import-formats/source.png').read_bytes());purple=(124,58,237,255);events=[]
for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text().splitlines():
 event=json.loads(line).get('event',{})
 if event.get('type')=='native pointer':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,event['detail']))
def pointer_delta(c):
 p=[d for at,d in events if c['start']<=at<=c['end'] and d.get('target')=='view'];down=next(d for d in p if d['phase']=='pointerdown');up=next(d for d in reversed(p) if d['phase']=='pointerup')
 def xy(d):
  r=d.get('paperRect',d['rect']);return [(d['clientX']-r['x'])*960/r['width'],(d['clientY']-r['y'])*640/r['height']]
 a,b=xy(down),xy(up);return [b[i]-a[i] for i in range(2)]
def expected_inserted(b,p,c,anchor):
 expected=copy.deepcopy(b)
 if c['mode']=='raster':
  im=source(b['layers'][2]['image'])
  if c['move']:im.alpha_composite(small,tuple(round(v) for v in anchor))
  elif c['label']=='raster-maximum':im.paste(purple,(0,0,960,640))
  elif c['label']=='raster-max-width':im.paste(purple,(0,320,960,321))
  elif c['label']=='raster-max-height':im.paste(purple,(480,0,481,640))
  else:raise AssertionError(c['label'])
  same(im,source(p['layers'][2]['image']));expected['layers'][2]['image']=p['layers'][2]['image']
 else:
  old=b['layers'][2].get('objects',[]);objects=p['layers'][2]['objects'];assert len(objects)==len(old)+1 and objects[:-1]==old;obj=objects[-1];assert obj['kind']=='raster' and obj['opacity']==1 and obj['matrix'][:4]==[1,0,0,1]
  if c['move']:
   assert (obj['width'],obj['height'])==(320,240) and 'clip' not in obj;same(source(obj['image']),small)
   for a,z in zip(obj['matrix'][4:],anchor):assert abs(a-z)<1e-9
  else:
   assert (obj['width'],obj['height'])==(960,640) and obj['matrix'][4:]==[0,0];assert np.all(np.array(source(obj['image']))==purple);assert sorted((v['x'],v['y']) for v in obj['clip'])==[(0,0),(0,640),(960,0),(960,640)]
  expected['layers'][2]['objects']=objects
 assert expected==p,(c['label'],'unrelated sheet/source/object changed')
def composite(d):
 im=Image.new('RGBA',(960,640));stamp=None
 for layer in d['layers']:
  part=source(layer['image'])
  for obj in layer.get('objects',[]):
   if obj['kind']=='stamp':stamp=obj;continue
   assert obj['kind']=='raster' and obj['matrix'][:4]==[1,0,0,1] and obj['opacity']==1;part.alpha_composite(source(obj['image']),tuple(round(v) for v in obj['matrix'][4:]))
  if layer['opacity']!=1:part.putalpha(part.getchannel('A').point(lambda a:math.floor(a*layer['opacity']+.5)))
  if layer['visible']:im.alpha_composite(part)
 assert stamp and stamp['emoji']=='🐶';m=stamp['matrix'];mask=np.ones((640,960),bool);mask[math.floor(m[5])-2:math.ceil(m[5]+stamp['height'])+2,math.floor(m[4])-2:math.ceil(m[4]+stamp['width'])+2]=False
 return np.array(im),mask
results=[];normalizations=[]
for c in e['cases']:
 label=c['label'];b=doc(label+'-before');p=doc(label+'-placed');assert len(b['layers'])==4 and b['active']==103 and b['drawingMode']==c['mode']
 anchor=[470,300]
 if c['move']:
  delta=pointer_delta(c);assert all(abs(x-y)<.001 for x,y in zip(delta,[150,100]));anchor=[320+delta[0],200+delta[1]]
 expected_inserted(b,p,c,anchor)
 if label=='vector-small':
  # The initial probe captures only Undo move. The completed v2 below also
  # verifies Undo insertion and both Redos, preserving the original evidence.
  expected_inserted(b,doc(label+'-undone'),c,[320,200]);assert doc(label+'-redone')==p;continue
 assert doc(label+'-undone')==b and doc(label+'-redone')==p
 reopened=doc(label+'-reopened');expected_reopen=copy.deepcopy(p)
 if c['mode']=='vector':
  obj=expected_reopen['layers'][2]['objects'][-1];assert not obj.get('live') and 'liveSize' not in obj;obj['liveSize']={'width':960,'height':640};normalizations.append({'case':label,'inserted_raster_optional_liveSize_default':[960,640],'live_data_absent':True})
 assert expected_reopen==reopened
 if c.get('separateMoveHistory'):
  unmoved=doc(label+'-move-undone');expected_inserted(b,unmoved,c,[320,200]);assert doc(label+'-insert-redone')==unmoved
 png=image(actual(label+'-placed','png'));same(png,image(actual(label+'-reopened','png')));expected,mask=composite(p);shown=np.array(png);assert np.array_equal(expected[mask],shown[mask]);assert np.any(expected[~mask]!=shown[~mask])
 results.append({'case':label,'source_RGBA_and_geometry_exact':True,'all_original_other_layers_objects_metadata_exact':True,'composite_exact_outside_unchanged_Dogstamp_bounds':True,'complete_undo_redo_exact':True,'native_project_reopen_exact_except_documented_optional_default':True,'native_PNG_reopen_exact':True})
for label in ['raster-small','vector-small']:same(image((out/f'insert43-{label}-copy.png').read_bytes()),small)
reject=doc('reject-before');assert reject==doc('rejected-over-width')==doc('rejected-over-height')==doc('vector-small-v2-before');assert all('1 and 4096' in c['message'] for c in e['rejections'])
report={'status':'Pass','cases':results,'project_import_normalizations':normalizations,'two_4097pixel_axis_rejections_preserve_whole_project':True,'valid_insert_move_place_after_rejection_works':True,'history_contract':'Ordinary floating Rasterinsert/move/Place Undo removes insertion asonechange. EditableVectorinsertionandmousemovementareseparategestures: Undo move restoresanchor320,200; Undo insertion removesonlyaddedpiece; bothRedos exact. Initialsingle-Undo probe preserved, not mislabelled as insertion Undo.','trim_contract':'4096squareRaster/Vector insertion isaccepted; Place discardsoff-paperRasterpixelswithshownwarning. OpaquePurplecoversactiveCharacteronly; everyotherMIXsheet/objectunchanged. Width4096x1andheight1x4096cliptoexpectedpaperrow/column.','sha256':hashes};(out/'insert43-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
