"""Independent nearest-distance and quantized bilinear checks, not Pillow identity."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-sampling39-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
def pixels(d):return np.array(image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1])))
def nearest_candidates(v,limit):
 low=math.floor(v);fraction=v-low
 candidates=[low,low+1] if abs(fraction-.5)<1e-12 else [math.floor(v+.5)]
 return {max(0,min(limit-1,n)) for n in candidates}
def check_nearest(src,dest):
 h,w=dest.shape[:2];sh,sw=src.shape[:2];ties=0
 for y in range(h):
  ys=nearest_candidates((y+.5)*sh/h-.5,sh)
  for x in range(w):
   xs=nearest_candidates((x+.5)*sw/w-.5,sw);ties+=len(xs)*len(ys)>1
   assert any(np.array_equal(dest[y,x],src[sy,sx]) for sy in ys for sx in xs),(x,y,'not an equally nearest source colour')
 return ties
def fixed_bilinear(src,w,h):
 a=src.astype(float);xs=(np.arange(w)+.5)*a.shape[1]/w-.5;ys=(np.arange(h)+.5)*a.shape[0]/h-.5;ix=np.floor(xs).astype(int);iy=np.floor(ys).astype(int);fx=np.floor((xs-ix)*256+.5)/256;fy=np.floor((ys-iy)*256+.5)/256
 x0=np.clip(ix,0,a.shape[1]-1);x1=np.clip(ix+1,0,a.shape[1]-1);y0=np.clip(iy,0,a.shape[0]-1);y1=np.clip(iy+1,0,a.shape[0]-1)
 top=a[y0[:,None],x0[None,:]]*(1-fx[None,:,None])+a[y0[:,None],x1[None,:]]*fx[None,:,None];bottom=a[y1[:,None],x0[None,:]]*(1-fx[None,:,None])+a[y1[:,None],x1[None,:]]*fx[None,:,None]
 return top*(1-fy[:,None,None])+bottom*fy[:,None,None]
raw=(out.parent/'fixtures/pixel-32.png').read_bytes();provenance=json.loads((out.parent/'fixtures/pixel-32-provenance.json').read_bytes());assert hashlib.sha256(raw).hexdigest()==provenance['sha256'];src=np.array(image(raw));before=doc('before');assert np.array_equal(pixels(before),src) and image(actual('before','png')).tobytes()==image(raw).tobytes() and not before['layers'][0].get('objects')
e=json.loads((out/'edit-sampling39-evidence.json').read_bytes());assert len(e['cases'])==6;results=[]
for case in e['cases']:
 scope=case['scope'];smooth=case['smooth'];target=case.get('target',48 if scope=='whole' else 6);suffix=scope+'-'+('smooth' if smooth else 'crisp')+(str(target) if case.get('crossValidation') else '');after=doc(suffix);png=np.array(image(actual(suffix,'png')));assert np.array_equal(pixels(after),png)
 complete=json.loads(json.dumps(before));complete['layers'][0]['image']=after['layers'][0]['image']
 if scope=='whole':
  assert png.shape==(target,target,4) and (after['width'],after['height'])==(target,target);complete['width']=complete['height']=target;source=src;piece=png
 else:
  assert png.shape==(32,32,4) and (after['width'],after['height'])==(32,32);unchanged=np.ones((32,32),bool);unchanged[22:22+target,2:2+target]=False;assert np.array_equal(png[unchanged],src[unchanged]);source=src[22:26,2:6];piece=png[22:22+target,2:2+target]
 assert complete==after and np.all(png[:,:,3]==255) and doc(suffix+'-undone')==before and doc(suffix+'-redone')==after
 palette={tuple(p) for p in source.reshape(-1,4)};introduced=sum(tuple(p) not in palette for p in piece.reshape(-1,4));ties=None
 if smooth:
  q=fixed_bilinear(source,target,target);assert np.all(piece>=np.floor(q)) and np.all(piece<=np.ceil(q)),suffix+' outside previously fixed interpolation envelope';assert introduced>0
 else:ties=check_nearest(source,piece);assert introduced==0
 nominal=np.array(Image.fromarray(source).resize((target,target),Image.Resampling.BILINEAR if smooth else Image.Resampling.NEAREST));differences=np.abs(piece.astype(int)-nominal.astype(int));results.append({'label':suffix,'scope':scope,'smooth':smooth,'dimensions':[after['width'],after['height']],'introduced_colour_pixels':introduced,'nearest_tie_pixels':ties,'nearest_distance_or_predeclared_fixed_point_bilinear_model_pass':True,'pillow_nominal_different_pixels':int(np.any(differences,2).sum()),'pillow_nominal_max_channel_difference':int(differences.max()),'exact_document_scope_alpha_history':True})
assert doc('reopened')==doc('selection-smooth7-redone') and image(actual('reopened','png')).tobytes()==image(actual('selection-smooth7','png')).tobytes()
report={'status':'Pass','cases':results,'rounding_model_is_inference_cross_validated_at_new_factors':True,'native_project_png_reopen_exact':True,'oracle_plan':'resampling-oracle-plan39.json','sha256':hashes};(out/'edit-sampling39-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
