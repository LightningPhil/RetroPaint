"""Verify native font matrix, history, saved files, and corrected preview path."""
from pathlib import Path
from datetime import datetime
from PIL import Image,ImageFont
from itertools import combinations,product
import base64,copy,hashlib,io,json,re
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'caption-font40-evidence.json').read_bytes());plan=json.loads((out/'caption-font-plan40.json').read_bytes());fixed=json.loads((out/'caption-preview41-evidence.json').read_bytes())
def actual(name):
 b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(c,s):return json.loads(actual(f'mouse-audit-caption-font40-{c["label"]}-{s}.retropaint'))
def png(c,s):return Image.open(io.BytesIO(actual(f'mouse-audit-caption-font40-{c["label"]}-{s}.png'))).convert('RGBA')
def rgba(uri):return Image.open(io.BytesIO(base64.b64decode(uri.split(',')[1]))).convert('RGBA')
def same(a,b):return a.size==b.size and a.tobytes()==b.tobytes()
def close(a,b):assert abs(a-b)<1e-9,(a,b)
events=[]
for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text().splitlines():
 event=json.loads(line).get('event',{})
 if event.get('type')=='native pointer':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,event['detail']))
def pointer(c,phase,move=False):
 start,end=(c['moveStart'],c['moveEnd']) if move else (c['start'],c['previewAt'])
 return [d for at,d in events if start<=at<=end and d.get('phase')==phase and d.get('target')=='view']
def xy(d):
 r=d.get('paperRect',d['rect']);return [(d['clientX']-r['x'])*960/r['width'],(d['clientY']-r['y'])*640/r['height']]
def pair_stats(c,prefix,rect,size):
 r=rect;w,h=size;box=tuple(round(v) for v in (r['x']+200/960*r['width'],r['y']+100/640*r['height'],r['x']+(200+w)/960*r['width'],r['y']+(100+h)/640*r['height']))
 a=np.array(Image.open(out/f'{prefix}-{c["label"]}-preview.jpg').crop(box)).astype(int);b=np.array(Image.open(out/(f'{prefix}-{c["label"]}-'+('created.jpg' if prefix=='caption-font40' else 'placed.jpg'))).crop(box)).astype(int)
 return {'label':c['label'],'different_pixels':int(np.any(a!=b,axis=2).sum()),'max_channel_change':int(abs(a-b).max())}
assert len(e['cases'])==18 and len(e['reopens'])==18
results=[];old_previews=[]
for c in e['cases']:
 label=c['label'];b=doc(c,'before');created=doc(c,'created');moved=doc(c,'moved');w,h=c['box'];assert (b['width'],b['height'],b['drawingMode'])==(960,640,c['mode']) and len(b['layers'])==1 and not b['layers'][0].get('objects')
 assert np.all(np.array(rgba(b['layers'][0]['image']))==255)
 settings={v['id']:v for v in c['settings']};assert all(v['valid'] for v in settings.values())
 for key,value in [('textContent',c['text']),('textFont',c['font']),('textAlign',c['align']),('textSize',str(c['size'])),('textWidth',str(c['width'])),('opacity','1'),('secondaryColour','#fdd835')]:assert settings[key]['value']==value,(label,key)
 assert settings['textOpaque']['checked']==c['opaque'] and c['object']==(c['mode']=='vector') and w==c['width'] and h==int(2*c['size']*1.35+8)
 cp=Image.open(out/f'caption-font40-{label}-copy.png').convert('RGBA');assert cp.size==(w,h)
 placed=png(c,'created');shifted=png(c,'moved');tap=xy(pointer(c,'pointerdown')[-1]);drag0=xy(pointer(c,'pointerdown',True)[0]);drag1=xy(pointer(c,'pointerup',True)[-1]);delta=[drag1[i]-drag0[i] for i in range(2)]
 assert all(abs(tap[i]-[200,100][i])<.001 for i in range(2)) and all(abs(delta[i]-[200,150][i])<.001 for i in range(2))
 if c['mode']=='raster':
  expected=Image.new('RGBA',(960,640),'white');expected.alpha_composite(cp,(200,100));assert same(expected,placed),(label,'raster creation')
  expected=Image.new('RGBA',(960,640),'white');expected.paste(placed.crop((200,100,200+w,100+h)),(400,250));assert same(expected,shifted),(label,'raster move')
  for d in (created,moved):
   expected=copy.deepcopy(b);expected['layers'][0]['image']=d['layers'][0]['image'];assert expected==d
 else:
  assert len(created['layers'][0]['objects'])==1;obj=created['layers'][0]['objects'][0];mo=moved['layers'][0]['objects'][0]
  font=('italic ' if c['italic'] else '')+('bold ' if c['bold'] else '')+f'{c["size"]}px "{c["font"]}"'
  for key,value in {'kind':'text','font':font,'size':c['size'],'align':c['align'],'color':'#1A1A1A','paper':'#fdd835' if c['opaque'] else None,'underline':c['underline'],'strike':c['strike'],'width':w,'height':h,'opacity':1,'id':c['id']}.items():assert obj[key]==value,(label,key)
  assert [l['text'] for l in obj['lines']]==['One','Two lines'] and 'callout' not in obj
  for i,l in enumerate(obj['lines']):
   close(l['x'],4 if c['align']=='left' else w/2 if c['align']=='center' else w-4);close(l['y'],4+i*c['size']*1.35);assert 0<l['width']<=w-8
  assert obj['matrix'][:4]==[1,0,0,1]
  for i in range(2):close(obj['matrix'][4+i],tap[i]);close(mo['matrix'][4+i],tap[i]+delta[i])
  expected=copy.deepcopy(obj);expected['matrix']=mo['matrix'];assert expected==mo
  for d in (created,moved):
   expected=copy.deepcopy(b);expected['layers'][0]['objects']=d['layers'][0]['objects'];assert expected==d
 assert doc(c,'move-undone')==created==doc(c,'text-redone') and doc(c,'text-undone')==b and doc(c,'move-redone')==moved==doc(c,'reopened')
 assert same(png(c,'reopened'),shifted)
 stats=pair_stats(c,'caption-font40',c['previewRect'],c['box']);old_previews.append(stats)
 if c['mode']=='raster':assert stats['different_pixels']==0
 results.append({'label':label,'mode':c['mode'],'source_properties_and_native_pointer_translation_exact':True,'whole_undo_redo_and_native_project_png_reopen_exact':True})
assert set(c['font'] for c in e['cases'])==set(f['family'] for f in plan['font_files'])
for f in plan['font_files']:
 b=Path(f['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==f['sha256'];assert ImageFont.truetype(f['file'],18).getname()==(f['family'],f['style'])
factors=['font','align','mode','bold','italic','underline','strike'];pairs=[]
for a,b in combinations(factors,2):
 expected=set(product(set(c[a] for c in e['cases']),set(c[b] for c in e['cases'])));seen={(c[a],c[b]) for c in e['cases']};assert seen==expected,(a,b);pairs.append([a,b,len(seen)])
assert len(fixed['cases'])==10;new_previews=[]
for c in fixed['cases']:
 size=list(map(int,re.findall(r'\d+',c['selectionSize'])[:2]));stats=pair_stats(c,'caption-preview41',c['rect'],size);assert stats['different_pixels']==0,stats;new_previews.append(stats)
 d=json.loads(actual(f'mouse-audit-caption-preview41-{c["label"]}-placed.retropaint'));actual(f'mouse-audit-caption-preview41-{c["label"]}-placed.png');obj=d['layers'][0]['objects'][-1];assert obj['opacity']==c.get('strength',1)
report={'status':'Pass','native_rows':18,'fonts':6,'alignments':3,'all_21_factor_pairs_covered':pairs,'installed_font_metadata_and_hashes_verified':True,'limitation':'Installed Windows fonts verified. Impact bold/italic may be synthesized; unavailable-font substitution not triggered on this platform. Pairwise coverage is not a full Cartesian product.','cases':results,'pre_fix_preview_comparison':old_previews,'fixed_all_nine_vector_rows_and_half_strength_opaque_exact':new_previews,'sha256':hashes}
(out/'caption-font41-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ('sha256','cases','pre_fix_preview_comparison','all_21_factor_pairs_covered')},indent=2))
