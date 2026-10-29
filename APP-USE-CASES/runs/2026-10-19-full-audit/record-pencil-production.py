from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
root=Path(__file__).resolve().parent;repo=root.parents[2];read=lambda file:json.loads((root/file).read_text(encoding='utf-8'));results=read('results.json');reg=read('headless/20261020-pencil-pan-final/report.json');art=read('evidence/ARTWORK-pencil-pan-verification.json');manifest=read('production-pencil-pan-snapshot.json');pinned=read('evidence/build-pencil-pan-source.json')
expected={'painting':231,'layout-1280x720':67,'layout-320x568':68,'layout-390x844':68,'layout-844x390':68};assert reg['status']=='Pass' and len(reg['suites'])==5 and {s['name'] for s in reg['suites']}==set(expected)
for suite in reg['suites']:assert suite['status']=='Pass' and suite['passed']==expected[suite['name']] and suite['failed']==0 and not suite['errors']
assert art['actual_downloads_byte_exact_to_original'] and art['rendered_rgba_save_reopen_and_previous_build_exact'];assert manifest['source_files']==pinned['source_files'];checked=[]
for item in manifest['source_files']:
    name=item['path'].replace('\\','/')
    if name=='index.html' or name.startswith('src/'):
        assert hashlib.sha256((repo/name).read_bytes()).hexdigest()==item['sha256'];checked.append(name)
for item in reg['source_files']:
    name=item['path'].replace('\\','/')
    if name in checked or name in ['tests/painting.ts','tests/mobile.ts']:assert hashlib.sha256((repo/name).read_bytes()).hexdigest()==item['sha256']
for item in manifest['build_files']:assert hashlib.sha256((Path(manifest['build_directory'])/item['path']).read_bytes()).hexdigest()==item['sha256']
consistency=dict(at=datetime.now(timezone.utc).isoformat(),unchanged_application_files=len(checked),manifest='production-pencil-pan-snapshot.json',pinned_before_build_source='evidence/build-pencil-pan-source.json',latest_complete_regressions='headless/20261020-pencil-pan-final/report.json',app_source_and_entry_html_exact=True,scope='Every current application source/entry HTML matches the source-pinned immutable production build and complete latest regression run. Painting/mobile check sources also unchanged. Later native acceptance runners are separate from app/build sources.')
(root/'evidence/application-source-consistency-pencil-pan.json').write_text(json.dumps(consistency,indent=2)+'\n',encoding='utf-8');s=results['supplementary_checks'];s['browser_regressions']=dict(status='Pass',count=231,evidence='headless/20261020-pencil-pan-final/report.json',scope='Complete painting/components, separate from349 acceptance cases.');s['desktop_layout']=dict(status='Pass',count=67,evidence='headless/20261020-pencil-pan-final/layout-1280x720.txt')
for width,height in [(320,568),(390,844),(844,390)]:s[f'phone_{width}_layout']=dict(status='Pass',count=68,evidence=f'headless/20261020-pencil-pan-final/layout-{width}x{height}.txt',scope='Complete isolated headless suite; physical input/assistive technology not certified.')
s['headless_execution']=dict(status='Pass',browser=reg['browser'],evidence='headless/20261020-pencil-pan-final/report.json',scope='No desktop, existing user browser/profile or artwork-tab access.')
s['production_build']=dict(status='Pass',evidence='production-pencil-pan-snapshot.json; evidence/build-pencil-pan.log; evidence/build-pencil-pan-source.json',notes='TypeScript/Vite success,109 modules,1m16s. Existing externalized-module/chunk-size diagnostics retained. Immutable8101 build, source hashes pinned before compilation.')
s['artwork_production_roundtrip']=dict(status='Pass',evidence='evidence/ARTWORK-pencil-pan-verification.json',scope='Four actual downloads in two fresh contexts. Both editable files exactly match immutable original bytes; all save/reopen/previous-build rendered pixels exact, independent layer composition within1/255.')
s['source_consistency']=dict(status='Pass',evidence='evidence/application-source-consistency-pencil-pan.json',count=len(checked));results['updated_at']=consistency['at'];(root/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Recorded complete231/67/68/68/68, pinned production/source and original artwork roundtrip. Acceptance cases are unchanged until their full native independent checks finish.')
