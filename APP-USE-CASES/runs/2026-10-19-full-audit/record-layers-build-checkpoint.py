from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
root=Path(__file__).resolve().parent;repo=root.parents[2];read=lambda name:json.loads((root/name).read_text(encoding='utf-8'));results=read('results.json');reg=read('headless/20261020-layers-full/report.json');art=read('evidence/ARTWORK-layers-verification.json')
counts={'painting':229,'layout-1280x720':63,'layout-320x568':64,'layout-390x844':64,'layout-844x390':64};assert reg['status']=='Pass' and len(reg['suites'])==5
for suite in reg['suites']:assert suite['status']=='Pass' and suite['passed']==counts[suite['name']] and suite['failed']==0 and not suite['errors']
assert art['actual_downloads_byte_exact_to_original'] and art['rendered_rgba_save_reopen_and_previous_build_exact']
manifest=read('production-layers-snapshot.json');checked=[]
for item in manifest['source_files']:
    path=item['path'].replace('\\','/')
    if path=='index.html' or path.startswith('src/'):
        assert hashlib.sha256((repo/path).read_bytes()).hexdigest()==item['sha256'];checked.append(path)
consistency=dict(at=datetime.now(timezone.utc).isoformat(),unchanged_application_files=len(checked),manifest='production-layers-snapshot.json',latest_complete_regressions='headless/20261020-layers-full/report.json',app_source_and_entry_html_exact=True,scope='All current application source matches the D-012 production build. Later acceptance harness readiness/navigation corrections do not change application sources.')
(root/'evidence/application-source-consistency-layers.json').write_text(json.dumps(consistency,indent=2)+'\n',encoding='utf-8')
s=results['supplementary_checks'];s['browser_regressions']=dict(status='Pass',count=229,evidence='headless/20261020-layers-full/report.json',scope='Complete latest-source painting/component suite; acceptance counts remain separate.')
s['desktop_layout']=dict(status='Pass',count=63,evidence='headless/20261020-layers-full/layout-1280x720.txt',scope='Complete suite including D-012 toolbar reachability.')
for width,height in [(320,568),(390,844),(844,390)]:s[f'phone_{width}_layout']=dict(status='Pass',count=64,evidence=f'headless/20261020-layers-full/layout-{width}x{height}.txt',scope='Complete isolated headless suite; physical devices/assistive technology remain uncertified.')
s['headless_execution']=dict(status='Pass',browser=reg['browser'],evidence='headless/20261020-layers-full/report.json',scope='Ephemeral isolated contexts; no existing user browser/profile or desktop access.')
s['production_build']=dict(status='Pass',evidence='production-layers-snapshot.json; evidence/build-layers.log',notes='TypeScript/Vite pass;109 modules,12.82s build, existing externalized module/chunk warnings retained. Immutable8095 production build.')
s['artwork_production_roundtrip']=dict(status='Pass',evidence='evidence/ARTWORK-layers-verification.json',scope='Two fresh headless production contexts and four actual downloads. Both editable files byte-identical to immutable backup, rendered save/reopen/previous-build pixels exact. User artwork tab unaccessed.')
s['source_consistency']=dict(status='Pass',evidence='evidence/application-source-consistency-layers.json',count=len(checked))
results['updated_at']=datetime.now(timezone.utc).isoformat();(root/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Recorded229/63/64/64/64 complete regressions and byte-exact latest artwork roundtrip.')
