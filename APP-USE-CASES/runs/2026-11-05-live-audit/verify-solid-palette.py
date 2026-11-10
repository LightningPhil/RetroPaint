"""All visible solid swatches, measured mouse capsules and untouched older marks."""
from pathlib import Path
from PIL import Image
from datetime import datetime
import base64,copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';plan=json.loads((root/'test-results/audit-2026-11-05/fixtures/palette45-plan.json').read_bytes());e=json.loads((out/'palette45-evidence.json').read_bytes());hashes={}
assert plan['recorded_before_execution'] and len(e['rows'])==13
def actual(label,ext='retropaint'):
    name='mouse-audit-palette45-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label):return json.loads(actual(label))
def pixels(d):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][0]['image'].split(',',1)[1]))).convert('RGBA'))
events=[]
for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text().splitlines():
    event=json.loads(line).get('event',{})
    if event.get('type')=='native pointer':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,event['detail']))
previous=doc('before');assert np.all(pixels(previous)==[80,80,80,255]);yy,xx=np.indices((640,960));results=[]
for row,wanted in zip(e['rows'],plan['rows']):
    assert row['name']==wanted['name'] and row['hex']==wanted['hex'] and row['pressed']=='true';current=doc(row['label']);scoped=copy.deepcopy(previous);scoped['layers'][0]['image']=current['layers'][0]['image'];assert scoped==current
    p=[detail for at,detail in events if row['start']<=at<=row['end'] and detail.get('target')=='view'];down=next(q for q in p if q['phase']=='pointerdown');up=next(q for q in reversed(p) if q['phase']=='pointerup')
    def point(q):
        r=q.get('paperRect',q['rect']);return [(q['clientX']-r['x'])*q['canvas']['width']/r['width'],(q['clientY']-r['y'])*q['canvas']['height']/r['height']]
    start,end=point(down),point(up)
    for a,b in zip(start+end,wanted['start']+wanted['end']):assert abs(a-b)<.01
    distance=np.sqrt((xx-np.clip(xx,start[0],end[0]))**2+(yy-start[1])**2);a,b=pixels(previous),pixels(current);rgb=[int(row['hex'][i:i+2],16) for i in [1,3,5]];interior=distance<=9;exterior=distance>=13
    assert np.all(b[interior]==rgb+[255]) and np.array_equal(a[exterior],b[exterior]);changed=int(np.any(a!=b,axis=2).sum());assert changed>1500
    results.append({'name':row['name'],'expected_RGB':rgb,'opaque_interior_exact':True,'unchanged_older_marks_and_exterior_exact':True,'changed_pixels':changed});previous=current
assert doc('undone')==doc('12-White') and doc('redone')==previous==doc('reopened')
final=np.array(Image.open(io.BytesIO(actual('final','png'))).convert('RGBA'));reopened=np.array(Image.open(io.BytesIO(actual('reopened','png'))).convert('RGBA'));assert np.array_equal(final,pixels(previous)) and np.array_equal(final,reopened)
report={'status':'Pass','all_standard_swatches':results,'return_to_first_colour_and_old_marks_stable':True,'White_visible_on_separate_contrasting_PLAY_copy':True,'whole_project_Undo_Redo_and_native_reopen_exact':True,'native_PNG_reopen_RGBA_exact':True,'sha256':hashes}
(out/'palette45-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Pass: all12colours +returnRed, exact interiorRGB/untouchedRGBA, whole Undo/Redo/nativeproject/PNG reopens')
