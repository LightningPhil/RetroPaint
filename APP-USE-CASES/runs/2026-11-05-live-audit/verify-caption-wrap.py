"""Native narrow/long/empty captions on the four-layer MIX scene."""
from pathlib import Path
from PIL import Image
import base64,copy,hashlib,io,json,re
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'caption-wrap41-evidence.json').read_bytes())
def actual(label,suffix,ext='retropaint'):
 name=f'mouse-audit-caption-wrap41-{label}-{suffix}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label,s):return json.loads(actual(label,s))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def layerim(d):return image(base64.b64decode(d['image'].split(',')[1]))
def same(a,b):assert a.size==b.size and a.tobytes()==b.tobytes()
def composite8(background,piece,at):
 b=np.array(background).astype(float);f=np.zeros_like(b);x,y=at;f[y:y+piece.height,x:x+piece.width]=np.array(piece)
 sa=f[:,:,3:4];da=b[:,:,3:4];alpha=np.floor(sa+da*(255-sa)/255+.5);sp=np.floor(f[:,:,:3]*sa/255+.5);dp=np.floor(b[:,:,:3]*da/255+.5);p=np.floor(sp+dp*(255-sa)/255+.5);rgb=np.floor(p*255/np.maximum(alpha,1)+.5)
 return Image.fromarray(np.concatenate((rgb,alpha),axis=2).clip(0,255).astype('uint8'))
assert len(e['cases'])==8 and len(e['reopens'])==6
results=[]
for c in e['cases']:
 label=c['label'];b=doc(label,'before');assert (b['width'],b['height'],len(b['layers']),b['active'],b['drawingMode'])==(960,640,4,103,c['mode'])
 if c.get('empty'):
  assert b==doc(label,'after') and all(o['drawerVisible'] and not o['selectionVisible'] for o in c['observations'])
  # Compare to this same active-layer state before empty placement, independent of drawing mode.
  reference=image(actual('vector-long-word' if c['mode']=='vector' else 'raster-transparent-v2','before','png'));same(reference,image(actual(label,'after','png')))
  results.append({'label':label,'empty_and_whitespace_opaque_place_no_op':True});continue
 placed=doc(label,'placed');assert doc(label,'undone')==b and doc(label,'redone')==placed==doc(label,'reopened')
 before_png=image(actual(label,'before','png'));placed_png=image(actual(label,'placed','png'));same(placed_png,image(actual(label,'reopened','png')))
 cp=image((out/f'caption-wrap41-{label}-copy.png').read_bytes());w,h=cp.size;long='long-word' in label;assert (w,h)==(120,202 if long else 137)
 expected=copy.deepcopy(b)
 if c['mode']=='raster':
  expected['layers'][2]['image']=placed['layers'][2]['image'];source=layerim(b['layers'][2]);source.alpha_composite(cp,(100,240));same(source,layerim(placed['layers'][2]))
 else:
  objects=placed['layers'][2]['objects'];assert len(objects)==len(b['layers'][2].get('objects',[]))+1 and objects[:-1]==b['layers'][2].get('objects',[])
  obj=objects[-1];assert {k:obj[k] for k in ['kind','font','size','align','color','paper','underline','strike','width','height','opacity']}=={'kind':'text','font':'24px "Arial"','size':24,'align':'center','color':'#1A1A1A','paper':'#fdd835' if c['opaque'] else None,'underline':False,'strike':False,'width':120,'height':h,'opacity':1}
  assert obj['matrix'][:4]==[1,0,0,1] and abs(obj['matrix'][4]-100)<.001 and abs(obj['matrix'][5]-240)<.001
  lines=[l['text'] for l in obj['lines']];assert lines==(['ABCDEF','GHIJKLM','NOPQRS','TUVWXY','Z0123456','789'] if long else ['One','narrow','caption','Two lines'])
  assert ''.join(lines)==c['text'] if long else ' '.join(lines)==c['text'].replace('\n',' ')
  for i,l in enumerate(obj['lines']):assert l['x']==60 and abs(l['y']-(4+i*24*1.35))<1e-9 and 0<l['width']<=112
  expected['layers'][2]['objects']=objects
 assert expected==placed,(label,'unrelated project content changed')
 same(composite8(before_png,cp,(100,240)),placed_png)
 a=np.array(cp);yellow=np.array([253,216,53,255]);black=np.array([26,26,26])
 if c['opaque']:assert np.all(a[:4]==yellow) and np.all(a[:,:4]==yellow) and np.all(a[:,:,-1]==255)
 else:
  assert np.all(a[:4,:,-1]==0) and np.all(a[:,:4,-1]==0);assert np.any(a[:,:,-1]>0) and np.any(a[:,:,-1]==0)
  shown=np.array(placed_png)[240:240+h,100:220];old=np.array(before_png)[240:240+h,100:220];assert np.array_equal(shown[a[:,:,3]==0],old[a[:,:,3]==0])
 # Full-frame native preview and placed view use identical regions, without selection handles.
 r=c['rect'];box=tuple(round(v) for v in (r['x']+100/960*r['width'],r['y']+240/640*r['height'],r['x']+220/960*r['width'],r['y']+(240+h)/640*r['height']))
 same(Image.open(out/f'caption-wrap41-{label}-preview.jpg').crop(box),Image.open(out/f'caption-wrap41-{label}-placed.jpg').crop(box))
 results.append({'label':label,'whole_project_scope_exact':True,'clipboard_source_composition_and_transparency_exact':True,'preview_placed_exact':True,'whole_undo_redo_native_project_png_reopen_exact':True})
for a,b in [('raster-transparent-v2','vector-transparent'),('raster-opaque','vector-opaque'),('raster-long-word','vector-long-word')]:same(image((out/f'caption-wrap41-{a}-copy.png').read_bytes()),image((out/f'caption-wrap41-{b}-copy.png').read_bytes()))
report={'status':'Pass','cases':results,'same_source_bitmap_in_both_modes':True,'original_interrupted_raster_transparent_artifacts_retained':'First helper exceeded orchestration30s limit after redone save. Repeated as raster-transparent-v2 on fresh tab730 with60s call limit; only complete repeat counted.','sha256':hashes}
(out/'caption-wrap41-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
