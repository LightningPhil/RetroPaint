"""Verify EDIT-017's sampling behavior without requiring an unspecified kernel.

The separately retained fixed-point hypothesis fails on selection-smooth7.
Do not widen it or present it as a passing coefficient/rounding comparison.
HTML Canvas deliberately leaves the smoothing algorithm unspecified:
https://html.spec.whatwg.org/multipage/canvas.html#image-smoothing
"""
from pathlib import Path
from itertools import combinations
from PIL import Image
import base64,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-sampling39-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
def pixels(d):return np.array(image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1])))
def candidates(v,limit):
 low=math.floor(v);fraction=v-low;values=[low,low+1] if abs(fraction-.5)<1e-12 else [math.floor(v+.5)]
 return {max(0,min(limit-1,n)) for n in values}
def convex_mix(rgb,colours):
 # Elementary convex combinations of up to four source colours. This checks
 # edge hue and support, without asserting a particular browser's weights.
 target=np.array([*rgb,1.],float)
 for n in range(1,len(colours)+1):
  for subset in combinations(colours,n):
   matrix=np.array([[*p,1.] for p in subset],float).T;weights=np.linalg.lstsq(matrix,target,rcond=None)[0]
   if np.all(weights>=-1e-9) and np.max(np.abs(matrix@weights-target))<1e-9:return True
 return False
def sampling_checks(src,dest,smooth):
 h,w=dest.shape[:2];sh,sw=src.shape[:2];ties=blended=uniform=strict_edges=0
 for y in range(h):
  v=(y+.5)*sh/h-.5;iy=math.floor(v);fy=v-iy
  for x in range(w):
   u=(x+.5)*sw/w-.5;ix=math.floor(u);fx=u-ix;pixel=dest[y,x]
   if not smooth:
    xs=candidates(u,sw);ys=candidates(v,sh);ties+=len(xs)*len(ys)>1
    assert any(np.array_equal(pixel,src[sy,sx]) for sy in ys for sx in xs),(x,y,'not nearest');continue
   p=np.array([[src[max(0,min(sh-1,iy+dy)),max(0,min(sw-1,ix+dx))] for dx in (0,1)] for dy in (0,1)])
   colours=sorted({tuple(c[:3]) for c in p.reshape(-1,4)});rgb=tuple(pixel[:3]);assert pixel[3]==255
   if len(colours)==1:assert rgb==colours[0];uniform+=1;continue
   assert convex_mix(rgb,colours),(x,y,'colour outside the source edge mixture')
   ideal=(p[0,0].astype(float)*(1-fx)+p[0,1].astype(float)*fx)*(1-fy)+(p[1,0].astype(float)*(1-fx)+p[1,1].astype(float)*fx)*fy
   # A blend separated from every endpoint by more than a final 8-bit
   # quantization cell must actually produce an intermediate edge colour.
   if min(max(abs(float(a)-float(b)) for a,b in zip(ideal[:3],c)) for c in colours)>1:
    assert rgb not in colours,(x,y,'smoothing remained a nearest source sample');strict_edges+=1
   blended+=rgb not in colours
 if smooth:assert blended>0 and strict_edges>0
 return {'nearest_tie_pixels':ties,'exact_uniform_pixels':uniform,'intermediate_edge_pixels':blended,'strict_edges_producing_interpolation':strict_edges}
raw=(out.parent/'fixtures/pixel-32.png').read_bytes();provenance=json.loads((out.parent/'fixtures/pixel-32-provenance.json').read_bytes());assert hashlib.sha256(raw).hexdigest()==provenance['sha256'];src=np.array(image(raw));before=doc('before');assert np.array_equal(pixels(before),src) and image(actual('before','png')).tobytes()==image(raw).tobytes() and not before['layers'][0].get('objects')
e=json.loads((out/'edit-sampling39-evidence.json').read_bytes());assert len(e['cases'])==6;results=[]
for case in e['cases']:
 scope=case['scope'];smooth=case['smooth'];target=case.get('target',48 if scope=='whole' else 6);suffix=scope+'-'+('smooth' if smooth else 'crisp')+(str(target) if case.get('crossValidation') else '');after=doc(suffix);png=np.array(image(actual(suffix,'png')));assert np.array_equal(pixels(after),png);complete=json.loads(json.dumps(before));complete['layers'][0]['image']=after['layers'][0]['image']
 if scope=='whole':
  assert png.shape==(target,target,4) and (after['width'],after['height'])==(target,target);complete['width']=complete['height']=target;source=src;piece=png
 else:
  assert png.shape==(32,32,4) and (after['width'],after['height'])==(32,32);unchanged=np.ones((32,32),bool);unchanged[22:22+target,2:2+target]=False;assert np.array_equal(png[unchanged],src[unchanged]);source=src[22:26,2:6];piece=png[22:22+target,2:2+target]
 assert complete==after and np.all(png[:,:,3]==255) and doc(suffix+'-undone')==before and doc(suffix+'-redone')==after
 checks=sampling_checks(source,piece,smooth);palette={tuple(p) for p in source.reshape(-1,4)};introduced=sum(tuple(p) not in palette for p in piece.reshape(-1,4));assert (introduced>0)==smooth
 results.append({'label':suffix,'scope':scope,'smooth':smooth,'dimensions':[after['width'],after['height']],'introduced_colour_pixels':introduced,**checks,'exact_document_scope_alpha_history':True})
assert doc('reopened')==doc('selection-smooth7-redone') and image(actual('reopened','png')).tobytes()==image(actual('selection-smooth7','png')).tobytes()
report={'status':'Pass','cases':results,'precise_kernel_identity_not_a_product_requirement':'HTML Canvas leaves smoothing algorithm to browser; EDIT-017 requires interpolated edges, actual scope/output and source-colour structure.','strict_fixed_point_hypothesis':'Failed; retained separately without widened limits in verify-edit-sampling-kernel-hypothesis.py and edit-sampling39-verification-pending.json. No coefficient-identity claim.','native_project_png_reopen_exact':True,'standard':'https://html.spec.whatwg.org/multipage/canvas.html#image-smoothing','sha256':hashes};(out/'edit-sampling39-acceptance-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
