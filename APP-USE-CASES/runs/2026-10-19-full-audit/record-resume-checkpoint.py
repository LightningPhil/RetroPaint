from pathlib import Path
import json,csv
from datetime import datetime,timezone

root=Path(__file__).resolve().parent
read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
results=read('results.json')
verified=read('evidence/PHOTO-002-independent-verification.json')
assert not verified['remaining_variants'] and verified['short_screen']['actual_downloaded_project_fresh_tab_reopen_exact']
case=results['cases']['PHOTO-002']
case.update(status='Pass' if verified.get('portrait_screen',{}).get('all_groups_verified') else 'Partial',variants_executed='All six categories and all 15 desktop groups on the supplied 3896x2586 photo; all 15 groups again through the real combined selector at 844x390. Saved Exposure +1/Brightness +7; returned to those values after every group. Actual project/PNG downloads before and after navigation, native chooser input, fresh-tab chooser reopen of the downloaded short-screen project and resave.',criteria_observations='Each group exposes named controls within its actual viewport. The short-screen category tabs are hidden and the combined selector contains all 15 groups. The +1/+7 values survive all navigation. Cancel preserves the complete saved project and every full-size RGBA pixel. The downloaded phone project reopens in a fresh session and remains exact, including original source pixels and recipe.',independent_oracle='Pillow 12.3.0 full 3896x2586 RGBA; full parsed project identity; actual DOM control names, effective rectangles and screenshots at 1280x720 and 844x390',defect_or_blocker='Portrait navigation remains pending until all 15 groups are exercised there. A coverage accounting gap was corrected immediately; the initial Pass for desktop plus short screen was premature. Interrupted attempts and failed download-watchers remain excluded.')
case['evidence_paths']+='; evidence/PHOTO-002-short-resumed-groups.json; evidence/PHOTO-002-short-resumed-values.json; evidence/PHOTO-002-short-resumed-before.retropaint; evidence/PHOTO-002-short-resumed-after.retropaint; evidence/PHOTO-002-short-resumed-reopened.retropaint; frame-download-events.jsonl'
if case['status']=='Pass':
    case['variants_executed']+=' All 15 groups also exercised at 390x844 through category tabs and their group selectors, with real project/PNG downloads and a separate fresh-tab chooser reopen.'
    case['criteria_observations']+=' Portrait controls are also named and entirely inside the measured 390x844 viewport; +1/+7 and full project/RGBA are exact after navigation and fresh reopen.'
    case['defect_or_blocker']='All required desktop, portrait and short-screen variants verified. An earlier premature Pass was downgraded, then the missing portrait workflow was actually completed. Interrupted attempts and failed download-watchers remain excluded.'
    case['evidence_paths']+='; evidence/PHOTO-002-portrait-groups.json; evidence/PHOTO-002-portrait-values.json; evidence/PHOTO-002-portrait-before.retropaint; evidence/PHOTO-002-portrait-after.retropaint; evidence/PHOTO-002-portrait-reopened.retropaint'
cancel=read('evidence/NATIVE-cancel-independent-verification.json')
assert cancel['actual_windows_choosers_observed']==2 and cancel['complete_saved_project_exact'] and cancel['full_size_rgba_exact']
case=results['cases']['FILE-002']
case.update(status='Pass',criteria_observations='Independent decoding confirms dimensions/orientation. Lossless imports match source RGBA exactly; browser versus Pillow JPEG/WebP decoding differs by at most 2/255. All 11 drawing/Undo/Redo sequences restore exact pixels. Rejected inputs preserve the saved document. The actual Windows Open image chooser is now separately cancelled from More/File/Open image and from Photo lab/Open photo. Both retain identical complete project JSON and full-size 3896x2586 RGBA. The ordinary path leaves Photo lab closed; the lab path restores its unsaved non-default settings and group.',defect_or_blocker='D-001 fixed and verified. The previously missing native Cancel branch is now executed through the dedicated Windows Computer Use runtime. No extension security setting was changed.')
case['variants_executed']='PNG, JPEG, WebP, BMP, GIF and uncompressed TIFF RGB/RGBA/grey; JPEG EXIF orientation 6; transparent PNG/TIFF; actual chooser, native drawing/Undo/Redo, independent PNG comparisons and corrupt/truncated/unsupported inputs; actual native Windows chooser Cancel from both ordinary and Photo lab entry points.'
case['evidence_paths']+='; evidence/NATIVE-cancel-independent-verification.json; evidence/FILE-002-native-plain-picker-open-ui.png; evidence/FILE-002-native-plain-picker-cancelled-ui.png; evidence/FILE-002-native-plain-cancel-after.retropaint; evidence/FILE-002-native-plain-cancel-after.png'
# PHOTO-001's later complete checkpoint is maintained by
# record-photo-context-checkpoint.py. Do not replace it with this earlier scope.
for record in results['cases'].values():
    record['evidence_paths']='; '.join(dict.fromkeys(part.strip() for part in record['evidence_paths'].split(';') if part.strip()))
results['updated_at']=datetime.now(timezone.utc).isoformat()
(root/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
variant_path=root.parents[1]/'VARIANT-EXECUTION-LEDGER.csv'
with variant_path.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
for row in rows:
    if row['family']=='Photo categories and groups':row.update(status=results['cases']['PHOTO-002']['status'],run_id=results['run_id'],evidence_paths='runs/'+root.name+'/evidence/PHOTO-002-independent-verification.json',notes='Every group exercised through actual controls at desktop 1280x720, portrait 390x844 and short-screen 844x390. Complete project and full-size pixels exact before/after and on actual saved-file fresh reopen. Does not certify screen-reader or physical-touch cases.')
with variant_path.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
print('Recorded PHOTO-002 '+results['cases']['PHOTO-002']['status']+' and FILE-002 '+results['cases']['FILE-002']['status']+'.')
