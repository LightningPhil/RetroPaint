"""Separate deque BFS and RGBA oracle for native Colour wand workflows."""
from pathlib import Path
from collections import deque
from PIL import Image
import base64,hashlib,io,json
from datetime import datetime
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';fixtures=out.parent/'fixtures/wand';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'wand38-evidence.json').read_bytes());provenance=json.loads((fixtures/'provenance.json').read_bytes())
pointer_down=[]
for line in (out.parent/'fault-controls/requests.jsonl').read_text(encoding='utf-8').splitlines():
 if 'native pointer' not in line or 'pointerdown' not in line:continue
 event=json.loads(line)['event'];p=event.get('detail',{})
 if isinstance(p,dict) and p.get('phase')=='pointerdown' and p.get('target')=='view':pointer_down.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,p))
def image(data):return Image.open(io.BytesIO(data)).convert('RGBA')
def actual(label,suffix,ext='retropaint'):
 name=f'mouse-audit-wand38-{label}-{suffix}.{ext}';data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(label,suffix):return json.loads(actual(label,suffix))
def pixels(d):return np.array(image(base64.b64decode(d['layers'][0]['image'].split(',',1)[1])))
def imported(source):
 # Independent image-to-8-bit-premultiplied-backing-store conversion.
 s=source.astype(float);a=s[:,:,3:4];p=np.floor(s[:,:,:3]*a/255+.5);rgb=np.floor(p*255/np.maximum(a,1)+.5);return np.concatenate((rgb,a),2).clip(0,255).astype('uint8')
def flood(s,seed,tolerance):
 sx,sy=seed;target=s[sy,sx].astype(int);m=np.zeros(s.shape[:2],bool);q=deque([(sx,sy)])
 while q:
  x,y=q.popleft()
  if not(0<=x<s.shape[1] and 0<=y<s.shape[0]) or m[y,x]:continue
  pixel=s[y,x].astype(int)
  if not(target[3]==pixel[3]==0) and np.abs(pixel-target).sum()>tolerance:continue
  m[y,x]=True;q.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
 return m
results=[]
for case in e['cases']:
 variant=case['variant'];label=case['label'];raw=(fixtures/(variant+'.png')).read_bytes();assert hashlib.sha256(raw).hexdigest()==provenance['sha256'][variant+'.png'];src=imported(np.array(image(raw)));before=doc(variant,'before');assert np.array_equal(pixels(before),src)
 events=[p for at,p in pointer_down if case['start']<=at<=case['end']];assert len(events)==1
 p=events[0];r=p['rect'];delivered=[(p['clientX']-r['x'])/r['width']*320,(p['clientY']-r['y'])/r['height']*240];assert max(abs(a-b) for a,b in zip(delivered,case['seed']))<1
 seed=[int(np.floor(n)) for n in delivered];mask=flood(src,seed,case['tolerance']);ys,xs=np.where(mask);left,top,right,bottom=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1);assert case['size']==f'{right-left} × {bottom-top} px'
 crop=src[top:bottom,left:right].copy();crop[~mask[top:bottom,left:right]]=0;assert np.array_equal(np.array(image((out/f'mouse-audit-wand38-{label}-copy.png').read_bytes())),crop)
 expected=src.copy();expected[mask]=0;after=doc(label,'deleted');assert np.array_equal(pixels(after),expected) and np.array_equal(np.array(image(actual(label,'deleted','png'))),expected)
 complete=json.loads(json.dumps(before));complete['layers'][0]['image']=after['layers'][0]['image'];assert complete==after and doc(label,'undone')==before and doc(label,'redone')==after
 results.append({'label':label,'tolerance':case['tolerance'],'requested_seed':case['seed'],'actual_delivered_seed':seed,'selected_pixels':int(mask.sum()),'bounds':[left,top,right,bottom],'disconnected_island_selected':bool(mask[40:80,220:260].any()),'clipboard_and_delete_RGBA_exact':True,'whole_undo_redo_exact':True})
expected_labels={'base-0','base-200','gap-0','gap-68','gap-69','variation-0','variation-24','variation-centre-0','variation-centre-24','antialiased-0','antialiased-143','antialiased-144','transparent-clear-0','transparent-clear-200','transparent-alpha-129','transparent-alpha-130'}
complete={c['label'] for c in results}==expected_labels
if complete:
 for ext in ('retropaint','png'):
  name='mouse-audit-wand38-reopened.'+ext;data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
  assert (json.loads(data)==doc('transparent-alpha-130','redone')) if ext=='retropaint' else image(data).tobytes()==image(actual('transparent-alpha-130','deleted','png')).tobytes()
report={'status':'Pass' if complete else 'Partial','metric':'four-connected seed-relative L1 RGBA; both-zero-alpha pixels match','independent_import_premultiplication':True,'native_project_png_reopen_exact':complete,'cases':results,'sha256':hashes}
(out/'wand38-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
