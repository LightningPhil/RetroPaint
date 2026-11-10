"""Independent native normal/reversed/tiny geometric outlines and exported pixels."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from shape_oracle import world_points,geometric_vertices,assert_boundary,polygon_pixels
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-shapes218';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
docs=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(7)]
def objects(d):return d['layers'][0].get('objects',[])
def without_objects(d):
 d=copy.deepcopy(d);d['layers'][0].pop('objects',None);return d
assert all(without_objects(d)==without_objects(docs[0])for d in docs)
assert [len(objects(d))for d in docs]==[0,5,10,15,14,15,15]
assert objects(docs[2])[:5]==objects(docs[1]) and objects(docs[3])[:10]==objects(docs[2]) and objects(docs[4])==objects(docs[3])[:-1] and docs[3]==docs[5]==docs[6]
assert len({o['id']for o in objects(docs[3])})==15
ui=json.loads((out/'shapes218-ui.json').read_text(encoding='utf-8'));assert len(ui['gestures'])==15
expected=np.full((640,960,4),255,dtype=np.uint8);safe=np.ones((640,960),dtype=bool);specimens=[]
for obj,g in zip(objects(docs[3]),ui['gestures']):
 assert obj['kind']=='path' and len(obj['paths'])==1 and obj['paths'][0]['closed'] and obj['fill']['color'].lower()=='#1e88e5' and obj['stroke']is None and obj['opacity']==1
 vertices=geometric_vertices(g['family'],g['from'],g['to']);points=world_points(obj);assert_boundary(points,vertices)
 patch,inside,distance=polygon_pixels(vertices,960,640);expected[patch][inside]=[30,136,229,255];safe[patch]&=distance>1.5
 specimens.append(dict(family=g['family'],variant=g['variant'],expected_vertices=len(vertices),boundary_verified=True,actual_bounds=[points.min(0).tolist(),points.max(0).tolist()]))
images=[]
for n in range(2):
 name=prefix+(f' ({n})'if n else '')+'.png';retain(name);image=np.array(Image.open(out/name).convert('RGBA'));assert image.shape==expected.shape and np.array_equal(image[safe],expected[safe]);images.append(image)
assert np.array_equal(images[0],images[1])
report=dict(status='Pass',case='PLAY-004',all_five_families_normal_reversed_tiny8by6_have_exact_expected_boundary_vertices=True,first_shapes_and_white_paint_unchanged=True,one_undo_removes_last_piece_redo_exact=True,all15_unique_editable_shapes=True,actual_project_reopen_exact=True,downloaded_png_interior_and_exterior_pixels_match_independent_polygons=True,antialias_edge_exclusion_px=1.5,checked_pixels=int(safe.sum()),both_pngs_pixel_exact_after_reopen=True,specimens=specimens,hashes=hashes)
(out/'shapes218-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k not in ['specimens','hashes']},indent=2))
