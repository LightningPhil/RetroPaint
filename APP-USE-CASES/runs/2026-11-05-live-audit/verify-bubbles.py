"""Native bubble matrices: independent boundaries, concave fills and saved history."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from shape_oracle import world_points,bubble_vertices,assert_boundary,polygon_pixels
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-bubbles228';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(17)]
def objects(d):return d['layers'][0].get('objects',[])
def without_objects(d):
 d=copy.deepcopy(d);d['layers'][0].pop('objects',None);return d
assert all(without_objects(d)==without_objects(docs[0])for d in docs)
assert [len(objects(d))for d in docs[:7]]==[0,3,6,9,8,9,9]and docs[3]==docs[5]==docs[6]
assert objects(docs[4])==objects(docs[3])[:-1]
for row in range(3):
 n=7+row*3;assert len(objects(docs[n]))==(row+1)*9 and objects(docs[n+1])==objects(docs[n])[:-1]and docs[n]==docs[n+2]
 if row:assert objects(docs[n])[:row*9]==objects(docs[n-1])
assert docs[15]==docs[16]
ui=json.loads((out/'bubbles228-ui.json').read_text(encoding='utf-8'));assert len(ui['gestures'])==36;results=[]
for sample,gestures,png0 in [(docs[3],ui['gestures'][:9],0),(docs[15],ui['gestures'][9:],2)]:
 expected=np.full((640,960,4),255,dtype=np.uint8);safe=np.ones((640,960),dtype=bool)
 for obj,g in zip(objects(sample),gestures):
  assert obj['kind']=='path'and len(obj['paths'])==1 and obj['paths'][0]['closed']and obj['lineWidth']==3 and obj['opacity']==1
  assert (obj['fill']is None)==(g['fill']=='none')and(obj['stroke']is None)==(g['outline']=='none')
  if g['fill']!='none':assert obj['fill']['color'].lower()==('#1e88e5'if g['fill']=='primary'else'#e53935')
  if g['outline']!='none':assert obj['stroke']['color'].lower()=='#1e88e5'
  vertices=bubble_vertices(g['family'],g['from'],g['to']);assert_boundary(world_points(obj),vertices);patch,inside,distance=polygon_pixels(vertices,960,640,margin=4)
  if g['fill']!='none':expected[patch][inside]=[30,136,229,255]if g['fill']=='primary'else[229,57,53,255]
  safe[patch]&=distance>3.5
 images=[]
 for n in [png0,png0+1]:
  name=prefix+(f' ({n})'if n else '')+'.png';retain(name);image=np.array(Image.open(out/name).convert('RGBA'));assert image.shape==expected.shape and np.array_equal(image[safe],expected[safe]);images.append(image)
 assert np.array_equal(*images);results.append(dict(matrix='normal/reverse/tiny'if png0==0 else'nine styles per family',pieces=len(gestures),safe_pixels=int(safe.sum())))
report=dict(status='Partial',case='PLAY-007',all3families_normal_reverse_tiny_and9styles_pass=True,all36boundaries_and_concave_fills_pass=True,actual_projects_reopen_exact=True,all4pngs_match_independent_oracle=True,undo_redo_and_earlier_pieces_exact=True,remaining='Character/caption workflow and held-mouse preview-switch branch',matrices=results,hashes=hashes)
(out/'bubbles228-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
