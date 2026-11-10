"""Native draft count/budget/cutoff results, genuine snapshot sizes and pixels."""
from pathlib import Path
from PIL import Image
import base64,hashlib,io,json
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse';downloads=Path.home()/'Downloads';folder=root/'test-results/audit-2026-11-05/fixtures/recovery45';plan=json.loads((folder/'plan.json').read_bytes());e=json.loads((out/'recovery45-evidence.json').read_bytes());hashes={}
assert plan['recorded_before_native_execution'];assert len(e['saved'])==14 and all('Draft saved' in c['status'] for c in e['saved'])
def names(kind):
    pages=[p for p in e['pages'] if p['kind']==kind];assert [p['page'].strip() for p in pages]==['1 / 3','2 / 3','3 / 3'];return [n for p in pages for n in p['names']]
assert names('count')==[f'Count {i:02}' for i in range(10,2,-1)]
expected=['Budget 04','Budget 03','Budget 02']+[f'Count {i:02}' for i in range(10,5,-1)]
for kind in ['budget','after-serialized','after-pixels']:assert names(kind)==expected
def actual(label):
    name='mouse-audit-recovery45-'+label+'.retropaint';b=(downloads/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest();return b
def pixels(url):return Image.open(io.BytesIO(base64.b64decode(url.split(',',1)[1]))).convert('RGBA').tobytes()
budget_bytes=[]
for i in range(1,5):
    b=actual(f'budget{i:02}');budget_bytes.append(len(b.decode())*2);d=json.loads(b);source=json.loads(Path(plan['files'][i+9]['file']).read_bytes());assert d['layers'][0]['name']==f'Budget {i:02}' and pixels(d['layers'][0]['image'])==pixels(source['layers'][0]['image'])
assert sum(budget_bytes)>128_000_000 and sum(budget_bytes[1:])+100_000<128_000_000
assert json.loads(actual('budget04-recovered'))==json.loads(actual('budget04')) and e['resumed']=='Budget 04'
eligibility={c['label']:c['status'] for c in e['eligibility']};assert 'too large for automatic drafts' in eligibility['serialized'] and '24 million stored pixels' in eligibility['pixels']
limits=[]
for label,index in [('serialized',14),('pixels',15)]:
    b=actual(label);d=json.loads(b);source=json.loads(Path(plan['files'][index]['file']).read_bytes());assert d['width']==source['width'] and d['height']==source['height'] and len(d['layers'])==len(source['layers'])
    assert json.loads(actual(label+'-reopened'))==d and label in e['manualReopens']
    for a,z in zip(d['layers'],source['layers']):assert pixels(a['image'])==pixels(z['image'])
    pixels_count=d['width']*d['height']*len(d['layers']);characters=len(b.decode());limits.append({'label':label,'stored_pixels':pixels_count,'actual_characters':characters,'manual_Save_project_preserves_all_source_RGBA':True})
    if label=='serialized':assert characters>50_000_000 and pixels_count<24_000_000
    else:assert characters<50_000_000 and pixels_count>24_000_000
for row in plan['files']:assert hashlib.sha256(Path(row['file']).read_bytes()).hexdigest()==row['sha256']
report={'status':'Pass','ten_native_candidates_retain_exact_newest_eight':True,'actual_budget_snapshot_UTF16_bytes':budget_bytes,'four_exceed_128M_three_plus_small_drafts_fit':True,'byte_budget_evicts_oldest_large_preserves_newest_and_five_smaller':True,'independent_eligibility_cutoffs':limits,'neither_cutoff_changes_existing_eight_drafts':True,'newest_valid_draft_native_resume_whole_project_exact':True,'sha256':hashes}
(out/'recovery45-retention-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='sha256'},indent=2))
