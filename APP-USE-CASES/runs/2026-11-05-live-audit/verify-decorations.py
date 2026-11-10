"""Independent star/heart/bolt geometry, concave pixels, style and history checks."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from shape_oracle import world_points,decoration_vertices,assert_boundary,polygon_pixels
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-decor220';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(21)]
def objects(d):return d['layers'][0].get('objects',[])
def without_objects(d):
 d=copy.deepcopy(d);d['layers'][0].pop('objects',None);return d
assert all(without_objects(d)==without_objects(docs[0])for d in docs)
assert [len(objects(d))for d in docs[:5]]==[0,5,10,15,15] and docs[3]==docs[4] and objects(docs[2])[:5]==objects(docs[1]) and objects(docs[3])[:10]==objects(docs[2])
for row in range(5):
 n=5+row*3;assert len(objects(docs[n]))==(row+1)*9 and objects(docs[n+1])==objects(docs[n])[:-1] and docs[n]==docs[n+2]
 if row:assert objects(docs[n])[:row*9]==objects(docs[n-1])
assert docs[19]==docs[20]
ui=json.loads((out/'decor220-ui.json').read_text(encoding='utf-8'));assert len(ui['gestures'])==60
results=[]
for sample,gestures,png0 in [(docs[3],ui['gestures'][:15],0),(docs[19],ui['gestures'][15:],2)]:
 expected=np.full((640,960,4),255,dtype=np.uint8);safe=np.ones((640,960),dtype=bool)
 for obj,g in zip(objects(sample),gestures):
  assert obj['kind']=='path' and len(obj['paths'])==1 and obj['paths'][0]['closed'] and obj['lineWidth']==3 and obj['opacity']==1
  assert (obj['fill']is None)==(g['fill']=='none') and (obj['stroke']is None)==(g['outline']=='none')
  if g['fill']!='none':assert obj['fill']['color'].lower()==('#1e88e5'if g['fill']=='primary'else'#e53935')
  if g['outline']!='none':assert obj['stroke']['color'].lower()=='#1e88e5'
  vertices=decoration_vertices(g['family'],g['from'],g['to']);assert_boundary(world_points(obj),vertices);patch,inside,distance=polygon_pixels(vertices,960,640,margin=4)
  if g['fill']!='none':expected[patch][inside]=[30,136,229,255]if g['fill']=='primary'else[229,57,53,255]
  safe[patch]&=distance>(1.5 if png0==0 else 3.5)
 images=[]
 for n in [png0,png0+1]:
  name=prefix+(f' ({n})'if n else '')+'.png';retain(name);image=np.array(Image.open(out/name).convert('RGBA'));assert image.shape==expected.shape and np.array_equal(image[safe],expected[safe]);images.append(image)
 assert np.array_equal(images[0],images[1]);results.append(dict(submatrix='normal/reversed/tiny'if png0==0 else 'nine styles per family',pieces=len(gestures),checked_pixels=int(safe.sum()),independent_concave_fill_and_notch_exterior_pixels_verified=True))
report=dict(status='Pass',case='PLAY-005',all5decoration_families_normal_reversed_tiny_and9styles=True,all60saved_paths_match_star_heart_bolt_boundaries=True,sharp_notches_and_concave_interiors_match_independent_pixel_oracle=True,correct_blue_red_absent_fills_and_outlines=True,each_family_undo_one_and_redo_exact=True,earlier_pieces_and_original_paint_unchanged=True,both_actual_projects_reopened_exact=True,all4downloaded_pngs_match_and_each_reopen_pair_pixel_exact=True,matrices=results,hashes=hashes)
(out/'decor220-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
