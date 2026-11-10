"""Independent tiny-corner fix, completion, cancellation, curve, winding and pixel oracle."""
from pathlib import Path
import copy,hashlib,json,math
import numpy as np
from PIL import Image
from shape_oracle import world_points,path_distances,polygon_pixels
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 raw=(downloads/name).read_bytes();(out/name).write_bytes(raw);hashes[name]=hashlib.sha256(raw).hexdigest();return raw
def docs(prefix,count):return [json.loads(retain(prefix+(f' ({i})'if i else '')+'.retropaint'))for i in range(count)]
def objects(d):return d['layers'][0].get('objects',[])
def without_objects(d):
 d=copy.deepcopy(d);d['layers'][0].pop('objects',None);return d
old=docs('mouse-audit-paths222',10);new=docs('mouse-audit-paths223',33)
bad=objects(old[7])[-1]['paths'][0];assert len(bad['points'])==3 and bad['closed'] and old[7]==old[8]==old[9]
assert old[0]==old[3] and old[1]==old[2]==old[4] and old[5]==old[6]
expected_counts=[0,1,0,1,1,2,2,2,3,3,4,5,6,6,6,7,8,9,10,11,12,13,13]
assert [len(objects(d))for d in new[:23]]==expected_counts
assert new[0]==new[2] and new[1]==new[3]==new[4] and new[5]==new[6]==new[7] and new[8]==new[9] and new[12]==new[13]==new[14] and new[21]==new[22]
assert all(without_objects(d)==without_objects(new[0])for d in new)
for row in range(3):
 n=23+row*3;assert len(objects(new[n]))==(row+1)*9 and objects(new[n+1])==objects(new[n])[:-1] and new[n]==new[n+2]
 if row:assert objects(new[n])[:row*9]==objects(new[n-1])
assert new[31]==new[32]
ui=json.loads((out/'paths223-ui.json').read_text(encoding='utf-8'));assert len(ui['gestures'])==40
core=objects(new[21]);style=objects(new[31]);geometry=[]
for group,gestures in [(core,ui['gestures'][:13]),(style,ui['gestures'][13:])]:
 for obj,g in zip(group,gestures):
  p=world_points(obj);knots=np.array(g['points'],dtype=float);closed=g['family']=='polygon'or g['finish']=='start';path=obj['paths'][0]
  assert obj['kind']=='path'and len(obj['paths'])==1 and path['closed']==closed and np.isfinite(p).all() and np.isfinite(obj['matrix']).all() and obj['width']>=1 and obj['height']>=1
  assert max(np.linalg.norm(p-k,axis=1).min()for k in knots)<.001 and np.linalg.norm(p[0]-knots[0])<.001
  assert np.all(p.min(0)>=knots.min(0)-25)and np.all(p.max(0)<=knots.max(0)+25)
  if g['family']!='spline':assert p.shape==(4,2)and np.max(abs(p-knots))<.001
  elif not closed:assert np.linalg.norm(p[-1]-knots[-1])<.001
  if g['variant']=='duplicate-points':assert (np.linalg.norm(p-knots[1],axis=1)<.001).sum()>=3
  if group is style:
   fill=g['fill']if closed else'none';assert(obj['fill']is None)==(fill=='none')and(obj['stroke']is None)==(g['outline']=='none')
   if fill!='none':assert obj['fill']['color'].lower()==('#1e88e5'if fill=='primary'else'#e53935')
   if obj['stroke']:assert obj['stroke']['color'].lower()=='#1e88e5'
  geometry.append(dict(family=g['family'],variant=g['variant'],closed=closed,knots=len(knots),saved_samples=len(p),finite_bounded=True))
assert len(core[0]['paths'][0]['points'])==4 and not core[0]['paths'][0]['closed']
line=world_points(core[6]);curve=world_points(core[7])-[0,170];assert path_distances(curve,line).max()>5
v=np.diff(curve,axis=0);v=v[np.linalg.norm(v,axis=1)>1e-6];turn=np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i',v[:-1],v[1:])/(np.linalg.norm(v[:-1],axis=1)*np.linalg.norm(v[1:],axis=1)),-1,1)));assert turn.max()<20
degenerate=world_points(core[10]);area=abs(np.sum(degenerate[:,0]*np.roll(degenerate[:,1],-1)-degenerate[:,1]*np.roll(degenerate[:,0],-1)))/2;assert area<.001
pixel_results=[]
for group,png0 in [(core,0),(style,2)]:
 expected=np.full((640,960,4),255,dtype=np.uint8);safe=np.ones((640,960),dtype=bool);stroke_cores=0
 for obj in group:
  vertices=world_points(obj);path=obj['paths'][0];radius=obj['lineWidth']/2;margin=math.ceil(radius+3);patch,inside,edge=polygon_pixels(vertices,960,640,margin=margin)
  yy,xx=np.mgrid[patch[0],patch[1]];points=np.column_stack([xx.ravel()+.5,yy.ravel()+.5]);distance=path_distances(points,vertices,path['closed']).reshape(xx.shape)
  def rgba(ink):
   text=ink['color'].lstrip('#');return[int(text[i:i+2],16)for i in [0,2,4]]+[255]
  if obj['fill']:expected[patch][inside]=rgba(obj['fill'])
  if obj['stroke']:
   centre=distance<radius-.8;outside=distance>radius+.8;safe[patch]&=centre|outside;expected[patch][centre]=rgba(obj['stroke']);stroke_cores+=int(centre.sum())
  elif obj['fill']:safe[patch]&=edge>1.5
 images=[]
 for n in [png0,png0+1]:
  name='mouse-audit-paths223'+(f' ({n})'if n else '')+'.png';retain(name);image=np.array(Image.open(out/name).convert('RGBA'));assert image.shape==expected.shape and np.array_equal(image[safe],expected[safe]);images.append(image)
 assert np.array_equal(images[0],images[1]);pixel_results.append(dict(matrix='completion and degenerate cases'if png0==0 else'nine styles per family',checked_pixels=int(safe.sum()),strict_stroke_core_samples=stroke_cores,interior_exterior_and_line_pixels_match=True))
report=dict(status='Pass',cases=['PLAY-008','PLAY-009','PLAY-010'],fix='LIVE-072 adaptive close target preserves nearby fourth corners',old_native_four_point_tiny_polyline_premature_three_point_closed_triangle_confirmed=True,new_native_all3tiny_families_retain4knots_and_tap_first_closes_correctly=True,enter_and_button_completion_undo_before_intervening_save_exact=True,focused_escape_cancels_and_one_point_finish_no_edit=True,save_intentionally_settles_pending_path_not_claimed_as_cancel=True,untargeted_old_escape_attempt_excluded=True,normal_spline_same_knots_visibly_smoother_than_polyline=True,maximum_adjacent_spline_turn_degrees=float(turn.max()),near_and_duplicate_knots_finite_bounded=True,irregular_closure_bowtie_winding_and_collinear_safe_result_verified=True,all3families9styles_and_reversed_order=True,each_family_one_undo_redo_exact=True,original_paint_unchanged_and_both_actual_projects_reopen_exact=True,all4pngs_pixel_exact_per_reopen_pair=True,pixels=pixel_results,geometry=geometry,hashes=hashes)
(out/'paths222-223-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items()if k not in ['geometry','hashes']},indent=2))
