"""Inspect window/worker request metadata and actual cached-workflow outputs."""
import hashlib,json,re,struct
from pathlib import Path
from urllib.parse import urlsplit
from PIL import Image
root=Path(__file__).resolve().parents[3];out=root/'test-results/audit-2026-11-05/mouse'
downloads=Path.home()/'Downloads';hashes={}
def retain(name):
 data=(downloads/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest();return data
def doc(s):return json.loads(retain('mouse-audit-'+s+'.retropaint'))
before=doc('cached-photo');after=doc('cached-photo-after-enhance');painted=doc('cached-painted');cad=doc('cached-cad')
assert before==after and before['layers'][0]['photo']['settings']['brightness']==12
assert before['layers'][0]==painted['layers'][0]==cad['layers'][0]
assert painted['layers']==cad['layers'][:2]
assert cad['layers'][2]['cad']['bodies'][0]['solid']['size']==[20,20,20]
png=retain('mouse-audit-cached-photo-2x-enhanced.png');assert Image.open(downloads/'mouse-audit-cached-photo-2x-enhanced.png').size==(32,32)
stl=retain('mouse-audit-cached-painted-3d-mm.stl');assert len(stl)==684 and struct.unpack_from('<I',stl,80)[0]==12
for suffix in ['', ' (1)', ' (2)']:retain('mouse-audit-fault-log'+suffix+'.json')
log_path=root/'test-results/audit-2026-11-05/fault-controls/requests.jsonl'
entries=[json.loads(line) for line in log_path.read_text(encoding='utf-8').splitlines()]
network_types={'window fetch','worker fetch','XHR','beacon','worker','resource','worker resource'}
urls=set()
for entry in entries:
 event=entry.get('event',{})
 if event.get('type') in network_types:
  detail=event.get('detail','');detail=detail if isinstance(detail,str) else json.dumps(detail)
  urls.update(re.findall(r'https?://[^\s"<>]+',detail))
assert urls and all(urlsplit(url).netloc=='127.0.0.1:65487' for url in urls)
assert not any('unexpected_post' in entry for entry in entries)
for entry in entries:
 if entry.get('method')=='GET':
  path=urlsplit(entry['path']).path
  assert path=='/' or path.startswith(('/assets/','/models/','/openscad/','/audit-')) or path in ['/favicon.svg','/favicon.ico']
first_worker=next(entry['at'] for entry in entries if entry.get('event',{}).get('type')=='worker' and 'super-resolution-worker' in entry['event']['detail'])
first_model=next(entry['at'] for entry in entries if entry.get('method')=='GET' and '/models/super-resolution/' in entry['path'])
assert first_model>=first_worker
assert any('503' in str(entry.get('event',{})) for entry in entries)
cached=[entry for entry in entries if entry.get('status')==304 and '/models/super-resolution/' in entry.get('response_path','')]
resources=[entry['event']['detail'] for entry in entries if entry.get('event',{}).get('type')=='worker resource' and '/models/' in entry['event']['detail']['url']]
assert len(cached)>=8 and len(resources)>=8
assert all(item['transferSize']<=300 and item['encodedBodySize']>0 for item in resources)
report={'request_metadata_scope':'Application window fetch/XHR/beacon, worker fetch, resource timing and loopback server; excludes browser extensions/host traffic',
 'external_application_request_urls':[],'only_local_asset_GETs_plus_visible_audit_metadata_POSTs':True,
 'models_deferred_until_first_enhancement_worker':True,'first_enhancement_worker_at':first_worker,'first_model_request_at':first_model,
 'controlled_missing_model_failure_and_native_successful_retry':True,
 'cached_model_304_responses':len(cached),'worker_cached_model_resources':resources,
 'native_photo_recipe_original_preserved_after_enhancement':True,
 'native_overlay_paint_and_cube_project_retained':True,'sha256':hashes}
(out/'local-request-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['sha256','worker_cached_model_resources']},indent=2))
