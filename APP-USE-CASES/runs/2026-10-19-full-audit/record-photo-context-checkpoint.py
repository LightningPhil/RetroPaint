from pathlib import Path
from datetime import datetime,timezone
import json,re

root=Path(__file__).resolve().parent
read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
verified=read('evidence/PHOTO-001-independent-verification.json')
assert all(verified[key] for key in ['hidden_target_rejection_preserves_complete_project_and_pixels','new_photo_import_remembers_group','new_photo_receives_fresh_values','actual_project_fresh_production_reopen_exact','production_reverse_photo_import_verified','native_picker_cancel_restores_complete_draft'])
art=read('evidence/ARTWORK-photo-context-verification.json')
assert art['actual_downloads_byte_exact_to_original'] and art['rendered_rgba_save_reopen_and_previous_build_exact']
painting=read('evidence/regression-painting-photo-context.json')
assert len(painting['results'])==228 and all(row['status']=='pass' for row in painting['results'])
checks={}
for name,count in [('desktop',60),('phone-320',62),('phone-390',62),('phone-844',62)]:
    path=f'evidence/regression-{name}-photo-context.txt'
    content=(root/path).read_text(encoding='utf-8')
    assert len(re.findall(r'^PASS ',content,re.M))==count and not re.search(r'^FAIL ',content,re.M),name
    checks[name]=(count,path)
results=read('results.json')
results['cases']['PHOTO-001']=dict(status='Pass',variants_executed='Actual Photo lab Open photo chooser on desktop and phone layouts; supplied Laukka sunset.jpg 3896x2586 and Sunset.jpg 4031x2267. Hidden active target rejection; normal close/reopen; non-default Noise reduction context across a second import; new source fresh values; native Windows chooser Cancel restoring Exposure -4/Brightness -100/Temperature +100; real saved-project fresh production reopen and reverse production photo import.',criteria_observations='Hidden target receives a Show this layer explanation and exact full saved data/pixels remain. Ordinary reopen retains the chosen group. Before D-008 a new photo reset Noise reduction to Light; the corrected real workflow retains Noise reduction. The new photo targets a distinct visible layer and starts with zero adjustments despite the earlier non-default draft. Independent source JPEG comparison differs by at most 2/255 across decoders; embedded source/export pixels are exact. Actual production project reopen preserves full JSON and RGBA. Native file chooser cancellation restores the prior group and complete draft.',independent_oracle='Pillow 12.3.0, independent source JPEG bytes/hash and full RGBA; exact parsed project identity; actual UI groups/values/target/dimensions and native chooser observations',evidence_paths='evidence/PHOTO-001-independent-verification.json; evidence/PHOTO-001-hidden-before.retropaint; evidence/PHOTO-001-hidden-after.retropaint; evidence/PHOTO-001-hidden-rejected.txt; evidence/PHOTO-001-import-context-before.json; evidence/PHOTO-001-import-context-before-fix.json; evidence/PHOTO-001-context-regression-before.txt; evidence/PHOTO-001-context-regression-after.txt; evidence/PHOTO-001-import-context-after-fix.json; evidence/PHOTO-001-new-source-after-fix.retropaint; evidence/PHOTO-001-new-source-reopened-production.retropaint; evidence/PHOTO-001-production-context.json; evidence/NATIVE-cancel-independent-verification.json; production-photo-context-snapshot.json; ui-events-current.jsonl',defect_or_blocker='D-008 fixed and verified. The pre-fix actual import and failing regression remain retained. The regression file-input fixture is supplementary UI integration coverage; actual chooser workflows and actual downloaded bytes provide acceptance evidence.')
s=results['supplementary_checks']
s['browser_regressions'].update(status='Pass',count=228,evidence='evidence/regression-painting-photo-context.json',scope='Complete final-source 228-check painting/component sequence; separate from acceptance case count.')
s['desktop_layout'].update(status='Pass',count=60,evidence=checks['desktop'][1],scope='Complete final-source 60-check desktop sequence, including new photo-context UI regression and existing CAD/layer regressions.')
for width,height in [(320,568),(390,844),(844,390)]:
    s[f'phone_{width}_layout']=dict(status='Pass',count=62,evidence=checks[f'phone-{width}'][1],scope=f'Complete final-source sequence in measured {width}x{height} frame; mouse/keyboard and synthetic component events. Physical touch/pen and screen-reader execution not certified.')
s['production_build'].update(status='Pass',command='npm run build -- --outDir <new immutable photo-context build directory>',evidence='evidence/build-photo-context.log',notes='TypeScript and Vite pass. Build/source hashes are recorded in production-photo-context-snapshot.json; prior build and artwork tab remain intact. Existing externalized node:module and chunk-size warnings remain.')
s['artwork_production_roundtrip']=dict(status='Pass',evidence='evidence/ARTWORK-photo-context-verification.json',scope='New production build: actual original-artwork chooser open/save, fresh-tab actual chooser reopen/save. Both downloads byte-identical to immutable backup SHA-256 612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28; all rendered pixels exact to both reopened and prior production output. User-facing artwork tab on 8088 untouched.')
results['updated_at']=datetime.now(timezone.utc).isoformat()
(root/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Recorded PHOTO-001 Pass, final 228/60/62/62/62 regressions and byte-exact production artwork roundtrip.')
