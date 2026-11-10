"""Full nine-style expansion and each-family Undo for the geometric shape case."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from shape_oracle import world_points,geometric_vertices,assert_boundary,polygon_pixels
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-shapes219';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(17)]
def objects(d):return d['layers'][0].get('objects',[])
def without_objects(d):
 d=copy.deepcopy(d);d['layers'][0].pop('objects',None);return d
assert all(without_objects(d)==without_objects(docs[0])for d in docs)
for row in range(5):
 n=1+row*3;assert len(objects(docs[n]))==(row+1)*9 and objects(docs[n+1])==objects(docs[n])[:-1] and docs[n]==docs[n+2]
 if row:assert objects(docs[n])[:row*9]==objects(docs[n-1])
assert docs[15]==docs[16]
ui=json.loads((out/'shapes219-ui.json').read_text(encoding='utf-8'));assert len(ui['gestures'])==45
expected=np.full((640,960,4),255,dtype=np.uint8);safe=np.ones((640,960),dtype=bool)
for obj,g in zip(objects(docs[15]),ui['gestures']):
 assert obj['kind']=='path' and len(obj['paths'])==1 and obj['paths'][0]['closed'] and obj['lineWidth']==3 and obj['opacity']==1
 assert (obj['fill']is None)==(g['fill']=='none') and (obj['stroke']is None)==(g['outline']=='none')
 if g['fill']!='none':assert obj['fill']['color'].lower()==('#1e88e5'if g['fill']=='primary'else'#e53935')
 if g['outline']!='none':assert obj['stroke']['color'].lower()=='#1e88e5'
 vertices=geometric_vertices(g['family'],g['from'],g['to']);assert_boundary(world_points(obj),vertices);patch,inside,distance=polygon_pixels(vertices,960,640,margin=4)
 if g['fill']!='none':expected[patch][inside]=[30,136,229,255]if g['fill']=='primary'else[229,57,53,255]
 safe[patch]&=distance>3.5
images=[]
for n in range(2):
 name=prefix+(f' ({n})'if n else '')+'.png';retain(name);image=np.array(Image.open(out/name).convert('RGBA'));assert image.shape==expected.shape and np.array_equal(image[safe],expected[safe]);images.append(image)
assert np.array_equal(images[0],images[1]);boundary=json.loads((out/'shapes218-verification.json').read_text());assert boundary['all_five_families_normal_reversed_tiny8by6_have_exact_expected_boundary_vertices']
report=dict(status='Pass',case='PLAY-004',boundary_matrix='shapes218-verification.json',all5families_each9outline_fill_combinations=True,all45paths_match_independent_family_boundaries=True,primary_blue_secondary_red_absent_fill_and_outline_correct=True,each_family_one_undo_removes_last_shape_and_redo_exact=True,earlier_shapes_and_paint_unchanged=True,actual_saved_project_reopened_exact=True,both_pngs_pixel_exact_after_reopen=True,independent_png_fill_and_exterior_pixel_checks=True,edge_exclusion_for3px_stroke_px=3.5,checked_pixels=int(safe.sum()),hashes=hashes)
(out/'shapes219-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
