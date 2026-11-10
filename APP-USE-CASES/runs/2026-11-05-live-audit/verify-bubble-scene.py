"""Verify real stamps/captions survive bubble placement and actual file reopening."""
from pathlib import Path
import copy,hashlib,json
import numpy as np
from PIL import Image
from shape_oracle import world_points,bubble_vertices,assert_boundary
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';prefix='mouse-audit-bubble-scene229';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
ds=[json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(11)]
images=[]
for i in range(5):
 name=prefix+(f' ({i})'if i else '')+'.png';retain(name);images.append(np.array(Image.open(out/name).convert('RGBA')))
base=copy.deepcopy(ds[0]);base['layers'][0].pop('objects',None)
for i,d in enumerate(ds):
 c=copy.deepcopy(d);c['layers'][0].pop('objects',None);assert c==base
 if 0<i<10:
  objects=d['layers'][0]['objects'];assert len(objects)==i and objects[:-1]==ds[i-1]['layers'][0].get('objects',[])
assert ds[9]==ds[10]and np.array_equal(images[3],images[4]);final=ds[9]['layers'][0]['objects'];checked=[]
for row,(family,y,text)in enumerate([('callout',70,'Hello!'),('ovalCallout',250,'Woof!'),('cloud',430,'Thinking')]):
 stamp,bubble,caption=final[3*row:3*row+3];assert stamp['kind']=='stamp'and bubble['kind']=='path'and caption['kind']=='text';assert_boundary(world_points(bubble),bubble_vertices(family,[220,y],[440,y+110]))
 assert caption['lines'][0]['text']==text and caption['size']==24 and caption['paper']is None
 assert abs(caption['matrix'][4]-250)<.001 and abs(caption['matrix'][5]-(100 if row==0 else y+25))<.001
 x0,y0=np.floor(stamp['matrix'][4:6]).astype(int);x1,y1=np.ceil(np.array(stamp['matrix'][4:6])+[stamp['width'],stamp['height']]).astype(int)
 before=images[0 if row==0 else row+1][y0:y1,x0:x1];after=images[3][y0:y1,x0:x1];mask=np.any(before[:,:,:3]!=255,axis=2);assert mask.sum()>100 and np.array_equal(before[mask],after[mask])
 xx,yy=np.round(caption['matrix'][4:6]).astype(int);region=images[3][yy:yy+40,xx:xx+170];assert np.sum(np.all(region==[30,136,229,255],axis=2))>50
 checked.append(dict(family=family,caption=text,character_ink_pixels_unchanged=int(mask.sum()),original_stamp_and_bubble_source_preserved=True))
report=dict(status='Partial',case='PLAY-007',caption_scene_complete=True,all3families_beside_actual_stamp=True,all_prior_objects_and_paint_exact=True,all_character_ink_pixels_preserved=True,all3caption_strings_positions_and_visible_blue_ink_verified=True,actual_project_and_png_reopen_exact=True,remaining='Changing family while a mouse drag is held: native API does not support pausing a held drag to operate another control.',rows=checked,hashes=hashes)
(out/'bubble-scene229-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k!='hashes'},indent=2))
