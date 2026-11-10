"""Independent format/orientation decode, delivered mouse footprint, atomicity."""
from pathlib import Path
from PIL import Image,ImageOps
from datetime import datetime
import base64,copy,hashlib,io,json,math
import numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';folder=root/'test-results/audit-2026-11-05/fixtures/import-formats';hashes={}
e=json.loads((out/'import43-evidence.json').read_bytes());plan=json.loads((folder/'plan.json').read_bytes());assert len(e['cases'])==len(e['reopens'])==8 and plan['recorded_before_import_execution']
for f in plan['files']:assert hashlib.sha256(Path(f['file']).read_bytes()).hexdigest()==f['sha256']
def actual(s,ext='retropaint'):
 name=f'mouse-audit-import43-{s}.{ext}';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(s):return json.loads(actual(s))
def image(b):return Image.open(io.BytesIO(b)).convert('RGBA')
def pixels(d):return image(base64.b64decode(d['layers'][0]['image'].split(',')[1]))
def same(a,b):assert a.size==b.size and a.tobytes()==b.tobytes()
events=[]
for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text().splitlines():
 event=json.loads(line).get('event',{})
 if event.get('type')=='native pointer':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,event['detail']))
def position(p):
 r=p.get('paperRect',p['rect']);return [(p['clientX']-r['x'])*p['canvas']['width']/r['width'],(p['clientY']-r['y'])*p['canvas']['height']/r['height']]
results=[]
for c in e['cases']:
 label=c['label'];before=doc(label+'-before');marked=doc(label+'-marked');assert len(before['layers'])==1 and before['drawingMode']=='raster' and not before['layers'][0].get('objects')
 expected=ImageOps.exif_transpose(Image.open(folder/c['file'])).convert('RGBA');a=np.array(expected);a[a[:,:,3]==0]=0;expected=Image.fromarray(a);source=np.array(pixels(before)).astype(int);assert (before['width'],before['height'])==expected.size==(c['rect']['paperWidth'],c['rect']['paperHeight'])
 delta=abs(source-np.array(expected).astype(int));stats={'case':label,'dimensions':list(expected.size),'decode_RGB_MAE':float(delta[:,:,:3].mean()),'decode_RGB_max':int(delta[:,:,:3].max())}
 if c['format']=='JPEG':assert stats['decode_RGB_MAE']<=1 and stats['decode_RGB_max']<=5 and np.all(source[:,:,3]==255)
 else:assert not delta.any()
 assert doc(label+'-undone')==before and doc(label+'-redone')==marked==doc(label+'-reopened')
 scope=copy.deepcopy(before);scope['layers'][0]['image']=marked['layers'][0]['image'];assert scope==marked
 p=[d for at,d in events if c['start']<=at<=c['end'] and d.get('target')=='view'];down=next(d for d in p if d['phase']=='pointerdown');up=next(d for d in reversed(p) if d['phase']=='pointerup');start=position(down);end=position(up)
 for measured,wanted in zip(start+end,c['points'][0]+c['points'][1]):assert abs(measured-wanted)<.001
 w,h=expected.size;yy,xx=np.indices((h,w));xx=xx+.5;yy=yy+.5;dx,dy=end[0]-start[0],end[1]-start[1];t=np.clip(((xx-start[0])*dx+(yy-start[1])*dy)/(dx*dx+dy*dy),0,1);distance=np.hypot(xx-(start[0]+t*dx),yy-(start[1]+t*dy));inner=distance<6-math.sqrt(.5);outside=distance>6+math.sqrt(.5);shown=np.array(pixels(marked));assert np.all(shown[inner]==[26,26,26,255]);assert np.array_equal(shown[outside],source[outside]);assert np.any(shown!=source)
 saved=image(actual(label+'-marked','png'));same(saved,image(actual(label+'-reopened','png')));same(saved,pixels(marked))
 stats.update(native_mouse_capsule_interior_and_unchanged_exterior_exact=True,whole_undo_redo_native_project_png_reopen_exact=True);results.append(stats)
failure=doc('failure-before');assert failure==doc('picker-cancelled')==doc('corrupt-rejected')==doc('jpeg-exif6-before');assert e['failure']['pickerCancelled'] and 'could not be opened' in e['failure']['message'] and e['cases'][-1]['retryAfterCorrupt']
report={'status':'Pass','cases':results,'native_picker_cancel_and_corrupt_data_whole_project_unchanged':True,'error_explains_supported_formats_and_retry_succeeds':True,'source_encoder':plan['encoder'],'jpeg_decoder_budget':'Predeclared mean<=1,max<=5; measured values retained per case. EXIF6 orientation/transposed dimensions exact.','mark_oracle':'12pxround-capsule around actual native down/up, pixel centres safelyinside distance<6−sqrt(.5) exactBlack26alpha255, safelyoutside distance>6+sqrt(.5) unchangedsourceexact. Antialias boundary not assigned an implementation-specific kernel.','sha256':hashes};(out/'import43-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
