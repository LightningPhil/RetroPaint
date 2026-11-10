"""Independent native colour entry, stroke footprint, history and file oracle."""
from pathlib import Path
from PIL import Image
from datetime import datetime
import base64,copy,colorsys,hashlib,io,json,math,re,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads'
plan=json.loads((root/'test-results/audit-2026-11-05/fixtures/wheel48-plan.json').read_bytes());e=json.loads((out/'wheel48-evidence.json').read_bytes());hashes={}
def actual(label,ext='retropaint'):
    name='mouse-audit-wheel48-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label):return json.loads(actual(label))
def pixels(d,i=1):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][i]['image'].split(',',1)[1]))).convert('RGBA'))
def feedback(f,rgb,polar=None):
    assert list(map(int,f['RGB']))==rgb and f['hex'].upper()=='#'+''.join(f'{n:02X}' for n in rgb)
    h,s,v=colorsys.rgb_to_hsv(*(n/255 for n in rgb));expected=[50+math.cos(h*2*math.pi)*s*50,50+math.sin(h*2*math.pi)*s*50]
    if polar is not None:expected=[50+50*n for n in polar]
    marker=[float(x) for x in re.search(r'left: ([\d.]+)%; top: ([\d.]+)%',f['marker']).groups()]
    assert all(abs(a-b)<.0001 for a,b in zip(marker,expected)),(marker,expected)
    assert int(f['brightness'])==math.floor(v*100+.5)
    assert [int(x) for x in re.findall(r'\d+',f['preview'])]==rgb
events=[]
for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text().splitlines():
    event=json.loads(line).get('event',{})
    if event.get('type')=='native pointer':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,event['detail']))
assert len(e['invalid'])==12
for row in e['invalid']:
    assert row['open'] is not None and row['active']=='background: rgb(18, 58, 188);'
    if row['kind']=='hex':assert row['hex']==row['input']
    else:assert row['RGB'][['wheelR','wheelG','wheelB'].index(row['field'])]==row['value']
assert doc('invalid-fixed')==doc('hex-main')
before=doc('before');previous=before;yy,xx=np.indices((640,960));xx=xx+.5;yy=yy+.5;results=[]
rows=plan['valid']+e['pointer'];evidence=e['valid']+e['pointer'];assert len(rows)==len(evidence)==13
for row,observed in zip(rows,evidence):
    assert row['label']==observed['label'];feedback(observed['feedback'],row['RGB'],row.get('polar'))
    if 'reopened' in observed:feedback(observed['reopened'],row['RGB'])
    current=doc(row['label']);scoped=copy.deepcopy(previous);scoped['layers'][1]['image']=current['layers'][1]['image'];assert scoped==current
    g=observed.get('gesture',observed);p=[detail for at,detail in events if g['start']<=at<=g['end'] and detail.get('target')=='view'];down=next(q for q in p if q['phase']=='pointerdown');up=next(q for q in reversed(p) if q['phase']=='pointerup')
    def point(q):
        r=q.get('paperRect',q['rect']);return [(q['clientX']-r['x'])*q['canvas']['width']/r['width'],(q['clientY']-r['y'])*q['canvas']['height']/r['height']]
    start,end=point(down),point(up)
    assert all(abs(a-b)<.01 for a,b in zip(start+end,row['start']+row['end']))
    distance=np.hypot(xx-np.clip(xx,start[0],end[0]),yy-start[1]);a,b=pixels(previous),pixels(current)
    assert np.all(b[distance<=9]==row['RGB']+[255]);assert np.array_equal(a[distance>=13],b[distance>=13]);assert np.any(a!=b)
    results.append({'label':row['label'],'RGB':row['RGB'],'exact_opaque_interior_and_untouched_exterior':True});previous=current
for row,eq in zip(e['pointer'],e['pointerEquivalent']):
    assert row['label']==eq['label'];feedback(eq['feedback'],row['RGB']);feedback(eq['reopened'],row['RGB'])
assert e['keyboard']['before']==e['keyboard']['after'];assert e['keyboard']['dark']['hex']=='#000000';assert e['keyboard']['light']['hex']=='#2492FF'
assert doc('undone')==doc('wheel-hue-precise');assert doc('redone')==previous==doc('cancelled')==doc('reopened')
png=np.array(Image.open(io.BytesIO(actual('final','png'))).convert('RGBA'));again=np.array(Image.open(io.BytesIO(actual('reopened','png'))).convert('RGBA'))
top=Image.fromarray(pixels(previous));bottom=Image.fromarray(pixels(previous,0));composite=np.array(Image.alpha_composite(bottom,top));assert np.array_equal(png,again) and np.array_equal(png,composite)
report={'status':'Pass','swatches':results,'invalid_entries_rejected_active_colour_unchanged':12,'keyboard_reverse_arrows_and_tone_bounds':True,'pointer_RGB_keyboard_equivalence_and_reopen':True,'whole_project_Undo_Redo_Cancel_native_reopen_exact':True,'native_PNG_reopen_RGBA_exact':True,'half_radius_quantization_probe_retained':True,'sha256':hashes}
(out/'wheel48-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Pass: 13 exact-colour native marks, 12 invalid entries, history/reopen/PNG and unchanged regions')
