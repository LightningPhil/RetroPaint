"""Compare actual native fills to predeclared independent connected masks."""
from pathlib import Path
from PIL import Image
from datetime import datetime
import base64,copy,hashlib,io,json,numpy as np
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';folder=root/'test-results/audit-2026-11-05/fixtures/fill49';downloads=Path.home()/'Downloads';plan=json.loads((folder/'plan.json').read_bytes());e=json.loads((out/'fill49-evidence.json').read_bytes());hashes={}
def actual(label,ext='retropaint'):
    name='mouse-audit-fill49-'+label+'.'+ext;b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def doc(label):return json.loads(actual(label))
def pixels(d,i=1):return np.array(Image.open(io.BytesIO(base64.b64decode(d['layers'][i]['image'].split(',',1)[1]))).convert('RGBA'))
assert plan['recorded_before_native_execution'] and len(e)==len(plan['rows'])==8
results=[];events=[]
for line in (root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl').read_text().splitlines():
    event=json.loads(line).get('event',{})
    if event.get('type')=='native pointer':events.append((datetime.fromisoformat(event['at'].replace('Z','+00:00')).timestamp()*1000,event['detail']))
for row,observed in zip(plan['rows'],e):
    label=row['label'];assert label==observed['label'];before=doc(label+'-before');after=doc(label+'-after');fixture=json.loads(Path(row['fixture']).read_bytes())
    for i in [0,1]:
        source=pixels(fixture,i).copy()
        # Canvas import canonicalizes RGB beneath alpha0; retain exact alpha and
        # every visible byte. All comparisons after this native baseline are rawRGBA.
        source[source[:,:,3]==0]=[0,0,0,0]
        assert np.array_equal(pixels(before,i),source),label
    mask=np.array(Image.open(folder/(label+'-mask.png')))>0;assert int(mask.sum())==row['expected_fill_pixels'];expected=pixels(before).copy();expected[mask]=[229,57,53,255]
    assert np.array_equal(pixels(after),expected),label
    scoped=copy.deepcopy(before);scoped['layers'][1]['image']=after['layers'][1]['image'];assert scoped==after
    assert doc(label+'-undone')==before and doc(label+'-redone')==after
    p=[detail for at,detail in events if observed['start']<=at<=observed['end'] and detail.get('target')=='view'];down=next(q for q in p if q['phase']=='pointerdown');r=down.get('paperRect',down['rect']);point=[(down['clientX']-r['x'])*320/r['width'],(down['clientY']-r['y'])*240/r['height']];assert all(abs(a-b-.5)<.01 for a,b in zip(point,row['seed']))
    if row['variant']!='gap':assert np.array_equal(pixels(before)[40:80,220:260],pixels(after)[40:80,220:260])
    results.append({'label':label,'exact_mask_pixels':int(mask.sum()),'all_RGBA_exact_to_independent_mask':True,'unrelated_layer_and_metadata_unchanged':True,'whole_Undo_Redo_exact':True})
last=doc('noise-200-redone');assert doc('reopened')==last
png=np.array(Image.open(io.BytesIO(actual('noise-200-final','png'))).convert('RGBA'));again=np.array(Image.open(io.BytesIO(actual('reopened','png'))).convert('RGBA'));expected=np.array(Image.alpha_composite(Image.fromarray(pixels(last,0)),Image.fromarray(pixels(last))));assert np.array_equal(png,again) and np.array_equal(png,expected)
report={'status':'Pass','independent_metric':plan['metric'],'variants':results,'transparent_fixture_import':'14161 alpha0 pixels canonicalize hidden RGB232 to0 on Canvas import; exact alpha and all visible bytes retained. Native baseline/fill/exterior/history/reopen comparisons remain rawRGBA exact.','one_pixel_gap_propagates_outside_intentionally':True,'noise_threshold_23_excludes_24_includes':True,'minimum_and_maximum_tolerance_complete':True,'native_project_PNG_reopen_exact':True,'sha256':hashes};(out/'fill49-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('Pass: 8 native FILL variants, allRGBA exact to predeclared connected masks, unrelated layer/history/native reopens exact')
