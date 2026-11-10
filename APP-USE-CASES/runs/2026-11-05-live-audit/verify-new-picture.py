"""New-paper limits, clean target, two-level history, and native file reopens."""
from pathlib import Path
from PIL import Image
from datetime import datetime
import base64,copy,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';hashes={}
e=json.loads((out/'new43-evidence.json').read_bytes());assert len(e['invalid'])==12 and len(e['cases'])==len(e['reopens'])==8
def actual(s,ext='retropaint'):
 name=f'mouse-audit-new43-{s}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(s):return json.loads(actual(s))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',')[1]))
def same(a,b):assert a.size==b.size and a.tobytes()==b.tobytes()
original=doc('original')
for c in e['invalid']:
 assert c['open'] and 'whole-pixel' in c['error'] and '1 and 4096' in c['error'];assert doc('invalid-'+c['label'])==original
 assert any(not f['valid'] for f in c['fields'])
events=[]
for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text().splitlines():
 event=json.loads(line).get('event',{})
 if event.get('type')=='native pointer':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,event['detail']))
def point(p):
 r=p.get('paperRect',p['rect']);return [(p['clientX']-r['x'])*p['canvas']['width']/r['width'],(p['clientY']-r['y'])*p['canvas']['height']/r['height']]
results=[]
for c in e['cases']:
 label=c['label'];blank=doc(label+'-blank');marked=doc(label+'-marked');w,h=c['width'],c['height'];assert (blank['width'],blank['height'])==(w,h) and blank['drawingMode']=='raster' and len(blank['layers'])==1
 layer=blank['layers'][0];assert blank['active']==layer['id'] and layer['visible'] and layer['opacity']==1 and layer['paper']=='#ffffff' and not layer.get('objects') and layer['live']=={'strokes':[],'fills':[],'sparkles':[]};assert np.all(np.array(pixels(blank))==255)
 assert doc(label+'-draw-undone')==blank==doc(label+'-new-redone') and doc(label+'-new-undone')==original and doc(label+'-draw-redone')==marked==doc(label+'-reopened')
 expected=copy.deepcopy(blank);expected['layers'][0]['image']=marked['layers'][0]['image'];assert expected==marked
 p=[d for at,d in events if c['start']<=at<=c['end'] and d.get('target')=='view'];start=point(next(d for d in p if d['phase']=='pointerdown'));end=point(next(d for d in reversed(p) if d['phase']=='pointerup'))
 for got,wanted in zip(start+end,c['p0']+c['p1']):assert abs(got-wanted)<.002
 a=np.array(pixels(marked));change=np.any(a!=255,axis=2);ys,xs=np.where(change);assert len(xs)>0
 x0=max(0,math.floor(min(start[0],end[0])-7));x1=min(w,math.ceil(max(start[0],end[0])+7));y0=max(0,math.floor(min(start[1],end[1])-7));y1=min(h,math.ceil(max(start[1],end[1])+7));assert xs.min()>=x0 and xs.max()<x1 and ys.min()>=y0 and ys.max()<y1
 yy,xx=np.indices((y1-y0,x1-x0));xx=xx+x0+.5;yy=yy+y0+.5;dx,dy=end[0]-start[0],end[1]-start[1];length=dx*dx+dy*dy;t=np.zeros_like(xx) if length==0 else np.clip(((xx-start[0])*dx+(yy-start[1])*dy)/length,0,1);distance=np.hypot(xx-start[0]-t*dx,yy-start[1]-t*dy);inner=distance<6-math.sqrt(.5);outside=distance>6+math.sqrt(.5);roi=a[y0:y1,x0:x1];assert inner.any() and np.all(roi[inner]==[26,26,26,255]) and np.all(roi[outside]==255)
 saved=image(actual(label+'-marked','png'));same(saved,pixels(marked));same(saved,image(actual(label+'-reopened','png')))
 results.append({'case':label,'dimensions':[w,h],'all_blank_paper_RGBA255_exact':True,'active_target_valid':True,'native_marker_footprint_and_neighbours_exact':True,'draw_and_new_picture_separate_undo_redo_exact':True,'native_project_png_reopen_exact':True})
report={'status':'Pass','invalid_bound_fraction_blank_text_attempts':12,'all_rejections_explain_limits_and_preserve_entire_original':True,'cases':results,'thin_paper_input_note':'For1pixelwidth/heightdocuments, Actualpixels plus threeZoomin clicks makes the thin axis3.375CSSpx. Nativepointereventsareonview, notdesk; sourcegeometryandresolutionunchanged.','sha256':hashes};(out/'new43-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
