"""Independent arrow direction, narrow bounds, rounded resize and style oracle."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from shape_oracle import world_points,arrow_rounded_vertices,assert_boundary,polygon_pixels
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-arrows221';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(29)]
def objects(d):return d['layers'][0].get('objects',[])
def without_objects(d):
 d=copy.deepcopy(d);d['layers'][0].pop('objects',None);return d
assert all(without_objects(d)==without_objects(docs[0])for d in docs)
assert [len(objects(d))for d in docs[:5]]==[0,5,10,15,20]
for i in range(1,4):assert objects(docs[i+1])[:i*5]==objects(docs[i])
for i in range(5):
 before,after=objects(docs[4+i]),objects(docs[5+i]);assert len(after)==20 and before[:i]+before[i+1:]==after[:i]+after[i+1:]
 a,b=copy.deepcopy(before[i]),copy.deepcopy(after[i]);a.pop('matrix');b.pop('matrix');assert a==b
 bounds=world_points(after[i]);assert np.max(abs(bounds.max(0)-bounds.min(0)-[150,80]))<.001 and np.max(abs(bounds.min(0)-world_points(before[i]).min(0)))<.001
assert docs[10]==docs[8] and docs[9]==docs[11]==docs[12]
for row in range(5):
 n=13+row*3;assert len(objects(docs[n]))==(row+1)*9 and objects(docs[n+1])==objects(docs[n])[:-1] and docs[n]==docs[n+2]
 if row:assert objects(docs[n])[:row*9]==objects(docs[n-1])
assert docs[27]==docs[28]
ui=json.loads((out/'arrows221-ui.json').read_text(encoding='utf-8'));assert len(ui['gestures'])==65
matrices=[]
for sample,gestures,pngs,resized in [(docs[4],ui['gestures'][:20],[0],False),(docs[9],ui['gestures'][:20],[1,2],True),(docs[27],ui['gestures'][20:],[3,4],False)]:
 expected=np.full((640,960,4),255,dtype=np.uint8);safe=np.ones((640,960),dtype=bool)
 for i,(obj,g)in enumerate(zip(objects(sample),gestures)):
  assert obj['kind']=='path' and len(obj['paths'])==1 and obj['paths'][0]['closed'] and obj['lineWidth']==3 and obj['opacity']==1
  assert (obj['fill']is None)==(g['fill']=='none') and (obj['stroke']is None)==(g['outline']=='none')
  if g['fill']!='none':assert obj['fill']['color'].lower()==('#1e88e5'if g['fill']=='primary'else'#e53935')
  if g['outline']!='none':assert obj['stroke']['color'].lower()=='#1e88e5'
  vertices=arrow_rounded_vertices(g['family'],g['from'],g['to'])
  if resized and i<5:vertices=(vertices-g['from'])*[1.25,.8]+g['from']
  assert_boundary(world_points(obj),vertices);patch,inside,distance=polygon_pixels(vertices,960,640,margin=4)
  if g['fill']!='none':expected[patch][inside]=[30,136,229,255]if g['fill']=='primary'else[229,57,53,255]
  safe[patch]&=distance>(3.5 if len(gestures)==45 else 1.5)
 images=[]
 for n in pngs:
  name=prefix+(f' ({n})'if n else '')+'.png';retain(name);image=np.array(Image.open(out/name).convert('RGBA'));assert image.shape==expected.shape and np.array_equal(image[safe],expected[safe]);images.append(image)
 if len(images)==2:assert np.array_equal(images[0],images[1])
 matrices.append(dict(pieces=len(gestures),resized=resized,checked_pixels=int(safe.sum())))
report=dict(status='Pass',case='PLAY-006',all4arrow_directions_and_rounded_rectangle_normal_reverse_tiny8by6_narrow4by80=True,all5normal_pieces_resized150by80_with_local_path_unchanged=True,each_resize_changes_only_target_matrix_and_keeps_top_left=True,rounded_arcs_survive_nonuniform_resize=True,all5families9outline_fill_combinations=True,all65boundaries_match_expected_direction_and_curves=True,each_family_undo_redo_exact_and_last_resize_undo_redo_exact=True,original_paint_and_neighbours_unchanged=True,actual_resized_and_style_projects_reopen_exact=True,all5pngs_match_independent_pixels_and_reopen_pairs_exact=True,matrices=matrices,hashes=hashes)
(out/'arrows221-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
