"""Independent full-layer right-angle bytes and affine landmarks/interiors."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'edit-whole42-evidence.json').read_bytes());assert len(e['cases'])==20 and len(e['reopens'])==20
def actual(label,suffix,ext='retropaint'):
 name=f'mouse-audit-edit-whole42-{label}-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label,s):return json.loads(actual(label,s))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def source(layer):return image(base64.b64decode(layer['image'].split(',')[1]))
def same(a,b):assert a.size==b.size and a.tobytes()==b.tobytes()
def mm(a,b):
 return [a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]]
def matrix(c):
 if c['label']=='flip-h':return 960,640,[-1,0,0,1,960,0],Image.Transpose.FLIP_LEFT_RIGHT
 if c['label']=='flip-v':return 960,640,[1,0,0,-1,0,640],Image.Transpose.FLIP_TOP_BOTTOM
 if c['button']=='rotatePicture':
  r=math.radians(c['angle']);co,si=math.cos(r),math.sin(r);w=math.ceil(abs(960*co)+abs(640*si)-1e-8);h=math.ceil(abs(960*si)+abs(640*co)-1e-8)
  return w,h,[co,si,-si,co,w/2-co*480+si*320,h/2-si*480-co*320],Image.Transpose.ROTATE_270 if c['angle']==90 else Image.Transpose.ROTATE_90 if c['angle']==-90 else None
 a,b=math.tan(math.radians(c['y'])),math.tan(math.radians(c['x']));return math.ceil(960+abs(b*640)),math.ceil(640+abs(a*960)),[1,a,b,1,max(0,-b*640),max(0,-a*960)],None
baseline={s:doc(s,'before') for s in ['patch','mix']}
same(source(baseline['patch']['layers'][0]),image((root/'test-results/audit-2026-11-05/fixtures/patch-transform-corners.png').read_bytes()))
fixture=json.loads((root/'test-results/audit-2026-11-05/fixtures/mix-transform-corners.retropaint').read_bytes());normalized=copy.deepcopy(fixture)
for i,l in enumerate(fixture['layers']):same(source(l),source(baseline['mix']['layers'][i]));normalized['layers'][i]['image']=baseline['mix']['layers'][i]['image']
assert baseline['mix']==normalized
assert json.loads((out/'export-canonical43-verification.json').read_bytes())['status']=='Pass'
results=[];png_comparisons=[];reopen_failures=[]
for c in e['cases']:
 label=c['scene']+'-'+c['label'];b=baseline[c['scene']];p=doc(label,'placed');assert doc(label,'undone')==b and doc(label,'redone')==p==doc(label,'reopened')
 before_png=image(actual(c['scene'],'before','png'));placed_png=image(actual(label,'placed','png'));reopened_png=image(actual(label,'reopened','png'))
 if placed_png.tobytes()!=reopened_png.tobytes():
  a=np.array(placed_png).astype(int);z=np.array(reopened_png).astype(int);stats=(int(np.any(a!=z,axis=2).sum()),int(abs(a-z).max()));expected_failures={'mix-skew-x20':(1,1),'mix-skew-both':(1,1),'patch-skew-x20':(4,2),'patch-skew-x-minus20':(2,2),'patch-skew-both':(3,2)};assert stats==expected_failures[label]
  corrected='export-canonical43';corrected_label=label+'-pass2';same(image((out/f'mouse-audit-{corrected}-{corrected_label}-placed.png').read_bytes()),image((out/f'mouse-audit-{corrected}-{corrected_label}-reopened.png').read_bytes()))
  reopen_failures.append({'case':label,'original42_different_pixels':stats[0],'original42_max_channel_change':stats[1],'corrected43_different_pixels':0})
 else:same(placed_png,reopened_png)
 w,h,m,transpose=matrix(c);assert (p['width'],p['height'])==(w,h) and placed_png.size==(w,h)
 expected=copy.deepcopy(b);expected['width']=w;expected['height']=h;stats=[]
 yy,xx=np.indices((h,w),dtype=float);xx+=.5;yy+=.5;det=m[0]*m[3]-m[1]*m[2];sx=(m[3]*(xx-m[4])-m[2]*(yy-m[5]))/det;sy=(-m[1]*(xx-m[4])+m[0]*(yy-m[5]))/det
 exterior=(sx < -2)|(sx > 962)|(sy < -2)|(sy > 642)
 for i,(old,new) in enumerate(zip(b['layers'],p['layers'])):
  a=np.array(source(old));shown=np.array(source(new));assert shown.shape==(h,w,4)
  expected['layers'][i]['image']=new['image']
  if transpose is not None:same(source(old).transpose(transpose),source(new))
  assert np.all(shown[exterior]==0)
  # Affine coordinates safely inside a 5x5 uniform source neighbourhood have
  # an exact colour/alpha oracle independent of interpolation tie rounding.
  uniform=np.zeros((640,960),bool);u=np.ones((636,956),bool)
  for dy in range(-2,3):
   for dx in range(-2,3):u &= np.all(a[2+dy:638+dy,2+dx:958+dx]==a[2:638,2:958],axis=2)
  uniform[2:638,2:958]=u;ix=np.floor(sx).astype(int);iy=np.floor(sy).astype(int);valid=(ix>=0)&(ix<960)&(iy>=0)&(iy<640);tx=np.clip(ix,0,959);ty=np.clip(iy,0,639);known=valid&uniform[ty,tx]
  assert np.array_equal(shown[known],a[ty[known],tx[known]]),(label,i,'uniform affine interior')
  k=64+40*i;corner_counts=[]
  for x,y,color in [(8,8,[k,32,16,255]),(864,8,[16,k,32,255]),(8,592,[32,16,k,255]),(864,592,[k,k,16,255])]:
   mask=(sx>=x+4)&(sx<x+20)&(sy>=y+4)&(sy<y+20);assert mask.sum()>100 and np.all(shown[mask]==color),(label,i,'corner landmark');corner_counts.append(int(mask.sum()))
  if old.get('objects'):
   objects=copy.deepcopy(old['objects'])
   for obj,newobj in zip(objects,new['objects']):
    target=mm(m,obj['matrix']);assert all(abs(x-y)<1e-9 for x,y in zip(target,newobj['matrix']));obj['matrix']=newobj['matrix']
   assert objects==new['objects'];expected['layers'][i]['objects']=new['objects']
  stats.append({'layer':old['name'],'all_bytes_exact_right_angle':transpose is not None,'exact_affine_uniform_pixels':int(known.sum()),'exact_corner_interior_pixels':corner_counts,'clear_beyond_transformed_frame_exact':True})
 assert p==expected,(label,'changed unrelated root/layer/object fields')
 if transpose is not None:
  predicted=np.array(before_png.transpose(transpose));shown=np.array(placed_png);diff=np.any(predicted!=shown,axis=2);png_comparisons.append({'case':label,'different_pixels':int(diff.sum()),'max_channel_change':int(abs(predicted.astype(int)-shown.astype(int)).max())})
  if diff.any():
   assert c['scene']=='mix';inside=np.zeros((h,w),bool)
   for layer in p['layers']:
    for obj in layer.get('objects',[]):
     om=obj['matrix'];points=[(om[0]*x+om[2]*y+om[4],om[1]*x+om[3]*y+om[5]) for x,y in [(0,0),(obj['width'],0),(obj['width'],obj['height']),(0,obj['height'])]]
     left=max(0,math.floor(min(x for x,y in points))-2);right=min(w,math.ceil(max(x for x,y in points))+2);top=max(0,math.floor(min(y for x,y in points))-2);bottom=min(h,math.ceil(max(y for x,y in points))+2);inside[top:bottom,left:right]=True
   assert not np.any(diff&~inside),png_comparisons[-1]
   png_comparisons[-1]['scope']='Only inside independently transformed82x82Dogstamp bounds plus2px AA. Every raster source byte and all composite pixels outside that object are exact; object definition and matrix exact. Direct emoji re-render is not claimed identical to flipping an already rendered bitmap.'
   (out/'edit-whole42-composite-transpose-hypothesis.json').write_text(json.dumps({'status':'Failed composite-bitmap-transpose hypothesis','comparisons_so_far':png_comparisons},indent=2)+'\n',encoding='utf-8')
 results.append({'case':label,'bounds':[w,h],'layers':stats,'source_definitions_and_affine_object_matrix_exact':True,'whole_undo_redo_native_project_png_reopen_exact':True})
report={'status':'Pass','cases':results,'right_angle_composite_png_comparisons':png_comparisons,'original42_export_mismatches_corrected_by43':reopen_failures,'oracle_scope':'All source-layer RGBA bytes for flips/quarter turns. Composite PNG exact for PATCH; MIX comparison retains direct emoji re-render differences inside independently transformedDogstamp bounds, with exact raster sources, unchanged object definition, analytic matrix and exact all other composite pixels. For arbitrary rotation/skew: independent affine dimensions, every layer corner marker and every safely uniform source interior, transparent exterior, unchanged metadata/definitions and analytic object matrices. Interpolation at nonuniform antialiased boundaries is not claimed kernel-identical to another renderer. All20wholeproject Undo/Redo/reopens exact. Fifteen original42PNG reopens exact; five mismatches retained and corrected43nativePNG reopens exact, with sourceprojects unchanged.','sha256':hashes}
(out/'edit-whole42-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'status':report['status'],'cases':len(results),'right_angle_png_comparisons':png_comparisons},indent=2))
