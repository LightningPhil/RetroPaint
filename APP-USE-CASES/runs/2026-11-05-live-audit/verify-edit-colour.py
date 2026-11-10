"""Independent inversion and deque-connected-corner mask for all FILL variants."""
from pathlib import Path
from collections import deque
from PIL import Image
import base64,hashlib,io,json
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';fixtures=out.parent/'fixtures/wand';downloads=Path.home()/'Downloads';hashes={}
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def canonical(src):
 s=src.astype(np.uint32);a=s[:,:,3:4];p=(s[:,:,:3]*a+127)//255;rgb=(p*255+a//2)//np.maximum(a,1);return np.concatenate((rgb,a),2).clip(0,255).astype('uint8')
def actual(suffix,ext='retropaint'):
 name=f'mouse-audit-edit-colour39-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(suffix):return json.loads(actual(suffix))
def decode(s):return np.array(image(base64.b64decode(s.split(',',1)[1])))
def connected(src,tolerance):
 height,width=src.shape[:2];target=src[0,0].astype(int);mask=np.zeros((height,width),bool);seen=np.zeros_like(mask);q=deque([(0,0)])
 while q:
  x,y=q.popleft()
  if not(0<=x<width and 0<=y<height) or seen[y,x]:continue
  seen[y,x]=True;p=src[y,x].astype(int)
  if not(target[3]==p[3]==0) and np.abs(p-target).sum()>tolerance:continue
  mask[y,x]=True;q.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
 return mask
e=json.loads((out/'edit-colour39-evidence.json').read_bytes());provenance=json.loads((fixtures/'provenance.json').read_bytes());results=[]
for case in e['cases']:
 variant,label,action=case['variant'],case['label'],case['action'];raw=(fixtures/(variant+'.png')).read_bytes();assert hashlib.sha256(raw).hexdigest()==provenance['sha256'][variant+'.png'];src=canonical(np.array(image(raw)));before=doc(variant+'-before');assert decode(before['layers'][0]['image']).tobytes()==src.tobytes();assert not before['layers'][0].get('objects') and before['drawingMode']=='raster'
 expected=src.copy();mask=None
 if action=='invert':expected[:,:,:3]=255-expected[:,:,:3];expected=canonical(expected);assert np.array_equal(expected[:,:,3],src[:,:,3])
 else:mask=connected(src,case['tolerance']);expected[mask]=0;assert 'connected to the top-left corner' in case['hint'] and 'Best for flat backgrounds' in case['hint']
 after=doc(label);assert decode(after['layers'][0]['image']).tobytes()==expected.tobytes()==image(actual(label,'png')).tobytes();complete=json.loads(json.dumps(before));complete['layers'][0]['image']=after['layers'][0]['image'];assert after==complete and doc(label+'-undone')==before and doc(label+'-redone')==after;assert not case['scopeSelection'] and case['dimensions']=='320 × 240 pixels · 1 layer'
 result={'label':label,'action':action,'RGB_and_alpha_or_connected_corner_mask_exact':True,'whole_document_history_exact':True}
 if mask is not None:result.update(removed_pixels=int(mask.sum()),enclosed_primary_region_removed=int(mask[21:140,21:140].sum()),second_island_removed=int(mask[40:80,220:260].sum()))
 results.append(result)
labels={c['label'] for c in results};required={'base-invert','base-remove68','base-remove69','gap-invert','gap-remove68','gap-remove69','variation-invert','variation-remove200','antialiased-invert','antialiased-remove200','transparent-invert','transparent-remove200'};complete=labels==required
if complete:assert doc('reopened')==doc('transparent-remove200-redone') and image(actual('reopened','png')).tobytes()==image(actual('transparent-remove200','png')).tobytes()
report={'status':'Pass' if complete else 'Partial','cases':results,'native_project_png_reopen_exact':complete,'sha256':hashes};(out/'edit-colour39-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
