"""Independent exact paper-frame growth/crop with pixels and vector retention."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def actual(mode,suffix,ext='retropaint'):
 name=f'mouse-audit-edit-paper39-{mode}-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(mode,suffix):return json.loads(actual(mode,suffix))
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))
def expected_document(before,after,width,height):
 expected=json.loads(json.dumps(before));expected['width']=width;expected['height']=height;expected['layers'][0]['image']=after['layers'][0]['image'];assert after==expected
def retained_stroke_coverage(before,expected,actual):
 # Changing canvas dimensions rerasterizes vectors. Source geometry is the
 # primary vector oracle; require exact PNG pixels outside its AA footprint.
 a=np.array(actual);b=np.array(expected);ys,xs=np.where(np.any(a!=b,axis=2));proof=[]
 for x,y in zip(xs,ys):
  matched=None
  for o in before['layers'][0].get('objects',[]):
   if o['kind']!='path' or not o.get('stroke') or o.get('fill') or o['opacity']!=1:continue
   ink=o['stroke'];spec=ink.get('spec');
   if spec and spec['kind']!='solid':continue
   colour=tuple(int(ink['color'][i:i+2],16) for i in (1,3,5));palette={tuple(math.floor(c*alpha/255+255-alpha+.5) for c in colour)+(255,) for alpha in range(256)}
   if tuple(a[y,x]) not in palette or tuple(b[y,x]) not in palette:continue
   m=o['matrix'];linear=np.array([[m[0],m[2]],[m[1],m[3]]]);radius=o['lineWidth']*np.linalg.svd(linear,compute_uv=False)[0]/2;distance=math.inf
   for lane in o['paths']:
    if lane.get('svg'):continue
    points=[(m[0]*p['x']+m[2]*p['y']+m[4],m[1]*p['x']+m[3]*p['y']+m[5]) for p in lane['points']]
    for u,v in zip(points,points[1:]):
     dx,dy=v[0]-u[0],v[1]-u[1];length=dx*dx+dy*dy;t=max(0,min(1,((x+.5-u[0])*dx+(y+.5-u[1])*dy)/length)) if length else 0;distance=min(distance,math.hypot(x+.5-u[0]-t*dx,y+.5-u[1]-t*dy))
   if distance<=radius+math.sqrt(.5):matched={'x':int(x),'y':int(y),'path':o['id'],'distance':distance,'stroke_half_width':radius,'before_RGBA':b[y,x].tolist(),'after_RGBA':a[y,x].tolist()};break
  assert matched,(int(x),int(y),'changed outside an identical retained stroke coverage footprint');proof.append(matched)
 return proof
e=json.loads((out/'edit-paper39-evidence.json').read_bytes());assert len(e['cases'])==2;results=[]
for c in e['cases']:
 mode=c['mode'];before=doc(mode,'before');base=pixels(before);base_png=image(actual(mode,'before','png'));assert base.size==base_png.size==(960,640)
 if mode=='raster':
  source=(out.parent/'fixtures/patch-paper-square.png').read_bytes();provenance=json.loads((out.parent/'fixtures/patch-paper-square-provenance.json').read_bytes());assert hashlib.sha256(source).hexdigest()==provenance['sha256'] and base.tobytes()==image(source).tobytes();assert base.crop((650,300,750,400)).tobytes()==Image.new('RGBA',(100,100),(124,58,237,255)).tobytes();background=(0,0,0,0)
 else:assert len(before['layers'][0]['objects'])==9;background=(255,255,255,255)
 enlarged=doc(mode,'enlarged');reduced=doc(mode,'reduced');expected_document(before,enlarged,1200,800);expected_document(before,reduced,450,350)
 expected=Image.new('RGBA',(1200,800),background);expected.paste(base,(0,0));assert pixels(enlarged).tobytes()==expected.tobytes() and pixels(reduced).tobytes()==base.crop((0,0,450,350)).tobytes()
 expected_png=Image.new('RGBA',(1200,800),background);expected_png.paste(base_png,(0,0));enlarged_png=image(actual(mode,'enlarged','png'));coverage=[]
 if mode=='raster':assert enlarged_png.tobytes()==expected_png.tobytes()
 else:coverage=retained_stroke_coverage(before,expected_png,enlarged_png)
 assert image(actual(mode,'reduced','png')).tobytes()==base_png.crop((0,0,450,350)).tobytes()
 assert doc(mode,'reduction-undone')==enlarged and doc(mode,'enlargement-undone')==before and doc(mode,'enlargement-redone')==enlarged and doc(mode,'reduction-redone')==reduced
 assert doc(mode,'reopened')==reduced and image(actual(mode,'reopened','png')).tobytes()==image(actual(mode,'reduced','png')).tobytes()
 if mode=='raster':assert pixels(enlarged).crop((650,300,750,400)).tobytes()==base.crop((650,300,750,400)).tobytes()
 assert c['enlargedDimensions']=='1200 × 800 pixels · 1 layer' and c['reducedDimensions']=='450 × 350 pixels · 1 layer'
 results.append({'mode':mode,'source_pixel_dimensions_and_coordinates_exact':True,'new_area_RGBA':list(background),'clipped_content_recovered_by_undo':True,'all_nine_piece_definitions_and_matrices_unchanged':mode=='vector','vector_AA_coverage_variation_with_identical_geometry':coverage,'whole_history_native_project_png_reopen_exact':True})
report={'status':'Pass','cases':results,'fixture_gap_recorded':'Separate PATCH copy adds the100pxsquare absent from the shared fixture; four original patches preserved.','sha256':hashes};(out/'edit-paper39-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
