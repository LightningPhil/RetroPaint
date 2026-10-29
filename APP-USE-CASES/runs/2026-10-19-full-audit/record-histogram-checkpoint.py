from pathlib import Path
from datetime import datetime, timezone
import json
root=Path(__file__).resolve().parent
read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
results=read('results.json'); reg=read('headless/20261020-histogram-full/report.json')
assert reg['status']=='Pass'
counts={'painting':229,'layout-1280x720':62,'layout-320x568':63,'layout-390x844':63,'layout-844x390':63}
assert len(reg['suites'])==5
for suite in reg['suites']:
    assert suite['status']=='Pass' and suite['passed']==counts[suite['name']] and suite['failed']==0 and not suite['errors']
art=read('evidence/ARTWORK-histogram-verification.json')
assert art['actual_downloads_byte_exact_to_original'] and art['rendered_rgba_save_reopen_and_previous_build_exact']
photo=read('evidence/PHOTO-017-independent-verification.json')
assert all(photo[k] for k in ['before_after_histogram_restoration_exact','empty_histogram_and_warnings_zero','undo_redo_and_fresh_project_reopen_exact','original_source_and_complete_cancelled_documents_exact'])
assert photo['actual_downloads_verified']==26 and photo['full_size_exposure_oracle_max_error_255']==0
results['cases']['PHOTO-017']=dict(status='Pass',variants_executed='Actual production UI imports six known PNGs: opaque luminance ramp, almost clear black and white padding, clear padding, empty image and flat RGB patches. Real +1 EV, Before/After, Cancel, Done, Undo, Redo and actual downloaded project fresh-context reopen. Twenty-six real project/PNG downloads.',criteria_observations='Independent pixel counts and channel peaks match the public plotted output. RGB peaks move from 64/128/192 to independently predicted 90/176/255. Before/After restores exact plots. Transparent pixels contribute zero; alpha 1/255 extremes no longer dominate. Empty output has zero warnings. Full-size ramp agrees exactly with the independent sRGB equation; full-size and preview clipping both report 0%/27%. Original data, Cancel, Undo/Redo and fresh saved-file reopen are exact.',independent_oracle='Pillow 12.3.0, NumPy, independent published sRGB +1 EV math, opacity-weighted bin/count calculations and exact parsed saved project comparisons; actual UI plots and downloads',evidence_paths='evidence/PHOTO-017-independent-verification.json; headless/PHOTO-017-before/PHOTO-017-headless-ui.json; headless/PHOTO-017-complete/PHOTO-017-headless-ui.json; headless/PHOTO-017-complete/events.json; headless/PHOTO-017-complete/fresh/events.json; fixtures/HIST-manifest.json; headless/HIST-regression-before/report.json; headless/HIST-regression-after/report.json; production-histogram-snapshot.json',defect_or_blocker='D-011 fixed: nearly clear black or white pixels previously produced 50% clipping. Original failing evidence is retained. Declared peak tolerance 2.01 canvas pixels and preview clipping tolerance one percentage point; actual full-size math error and clipping discrepancy are zero. PHOTO-013 endpoint controls remain untested and are not passed by this shared transparency branch.')
s=results['supplementary_checks']
s['browser_regressions']=dict(status='Pass',count=229,evidence='headless/20261020-histogram-full/report.json',scope='Complete final application source painting/component suite; acceptance counts separate.')
s['desktop_layout']=dict(status='Pass',count=62,evidence='headless/20261020-histogram-full/layout-1280x720.txt',scope='Complete isolated headless desktop suite.')
for width,height in [(320,568),(390,844),(844,390)]:
    s[f'phone_{width}_layout']=dict(status='Pass',count=63,evidence=f'headless/20261020-histogram-full/layout-{width}x{height}.txt',scope='Complete headless suite; physical devices and assistive technology remain uncertified.')
s['headless_execution']=dict(status='Pass',browser=reg['browser'],evidence='headless/20261020-histogram-full/report.json',scope='Ephemeral isolated headless contexts; no desktop or existing user browser access.')
s['production_build']=dict(status='Pass',evidence='production-histogram-snapshot.json; evidence/build-histogram.log',notes='TypeScript and Vite pass; immutable production build at 8094. Existing build warnings retained in log.')
s['artwork_production_roundtrip']=dict(status='Pass',evidence='evidence/ARTWORK-histogram-verification.json',scope='Two fresh headless production contexts; actual chooser input and downloads. Both project files byte-identical to immutable backup; full rendered save/reopen pixels exact. Existing user artwork tab unaccessed.')
results['updated_at']=datetime.now(timezone.utc).isoformat()
(root/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Recorded PHOTO-017 Pass and verified latest full regressions/build/artwork roundtrip.')
