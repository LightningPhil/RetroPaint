from pathlib import Path
from datetime import datetime,timezone
import json,csv
root=Path(__file__).resolve().parent
read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
results=read('results.json')
common='Actual UI controls and downloads on immutable production build at 8090. Pillow independent full-size RGBA, parsed complete project data, source and layer identity checks. '
def record(id,variants,observations,paths,notes='None.'):
    results['cases'][id]=dict(status='Pass',variants_executed=variants,criteria_observations=observations,independent_oracle=common,evidence_paths=paths,defect_or_blocker=notes)
v=read('evidence/PHOTO-003-independent-verification.json')
assert all(v[k] for k in ['before_exact_to_original_source_display','after_exact_to_current_draft_display','comparison_survives_outstanding_render','latest_draft_distinct_and_restored','cancel_complete_project_identity','cancel_full_size_rgba_exact'])
record('PHOTO-003','Supplied 3896x2586 Laukka sunset; exposure +4 and saturation -100 draft; repeated Before/After; Before during an observed outstanding noise preview; After after completion; Cancel.','Before equals the original source display pixel for pixel. After restores the current draft display exactly. Before remains selected and shows the original after the late worker result. The latest draft is distinct and restored by After. Cancel retains exact complete saved project and full-size original RGBA.','evidence/PHOTO-003-independent-verification.json; evidence/PHOTO-003-asynchronous.json; evidence/PHOTO-003-original-ui.jpg; evidence/PHOTO-003-before-comparison-ui.jpg; evidence/PHOTO-003-after-comparison-ui.jpg; evidence/PHOTO-003-before-after-outstanding-render-ui.jpg; evidence/PHOTO-003-latest-after-ui.jpg; evidence/PHOTO-003-before.retropaint; evidence/PHOTO-003-cancelled.retropaint; ui-events-current.jsonl','Display comparison uses a recorded source inset excluding the navigation overlay. Full-size exported pixels and complete saved data are separately compared after Cancel.')
v=read('evidence/PHOTO-005-independent-verification.json')
assert all(v[k] for k in ['controlled_full_size_apply_failure_preserves_draft','displayed_curve_exact_after_failure','retry_commits_same_retained_draft','no_success_reported_before_commit'])
record('PHOTO-005','Supplied natural photo with distinct neighbouring paint layer. Brightness 25 plus Gentle S RGB curve; deliberate full-size apply error; retained draft retry; actual project download/reopen; revision to brightness -15 and Faded blacks curve; actual fresh production reopen/resave.','An apply error leaves the lab open with the same numeric settings and an exactly unchanged displayed curve. Done is reenabled. Saving state disables commit controls, and success appears only after commit. Retry saves the retained draft. Both recipes and full rendered pixels survive actual downloaded-file reopen exactly. All original pixels, neighbour data and unrelated fields remain exact.','evidence/PHOTO-005-independent-verification.json; evidence/PHOTO-005-fault-manifest.json; evidence/PHOTO-005-fault-worker.js; evidence/PHOTO-005-failed-apply-ui.jpg; evidence/PHOTO-005-first-apply-saving.json; evidence/PHOTO-005-failed-apply.json; evidence/PHOTO-005-retry-saving.json; evidence/PHOTO-005-retry-completed.json; evidence/PHOTO-005-first-commit.retropaint; evidence/PHOTO-005-first-reopened.retropaint; evidence/PHOTO-005-revised-commit.retropaint; evidence/PHOTO-005-revised-reopened.retropaint; ui-events-current.jsonl','The failure branch uses a documented worker-protocol wrapper on disposable loopback origin 8092, not a spontaneous production failure. Original production bytes are unchanged. Initial server connection errors and one locator wait timeout are preserved/excluded; actual completion was subsequently observed.')
for id,key,count in [('PHOTO-009','exposure',10),('PHOTO-010','brightness',8),('PHOTO-011','contrast',10)]:
    v=read('evidence/'+id+'-independent-verification.json')
    assert v['default_min_max_intermediate_executed'] and sum(map(len,v['rows'].values()))==count
    if key=='exposure':
        variants='Opaque 1024x256 neutral ramp and independent alpha/padding/five-patch copy; EV +1, -1, minimum -4, maximum +4 and default 0. Every value set through the accessible real slider and committed/downloaded.'
        observations='All ten full-size exports match the independent published sRGB decode/linear gain/encode calculation within the declared 1/255 limit. +1 EV doubles linear light and -1 halves it before clipping. Every alpha byte and underlying source pixel is unchanged. Neutral reset is RGBA exact.'
    elif key=='brightness':
        variants='Opaque ramp and alpha/padding/five-patch copy; brightness +25, minimum -100, maximum +100 and default 0; all other adjustments neutral.'
        observations='The positive intermediate raises dark, midtone and bright patches; negative brightness lowers them. Every neutral remains neutral, all alpha bytes and original source pixels remain exact, and default 0 restores full source RGBA. At least three nonsaturated patch values differ from +1 EV, proving the controls are distinct.'
    else:
        variants='Opaque ramp and alpha/padding/five-patch copy; contrast +30, -30, minimum -100, maximum +100 and default 0; other controls neutral.'
        observations='Positive contrast increases the separation between independently known levels 96 and 160; negative contrast reduces it. The endpoint ordering is consistent. Values remain encodable/finite, all neutral channels agree and alpha/source bytes remain exact. Default 0 restores full source RGBA.'
    record(id,variants,observations,'evidence/'+id+'-independent-verification.json; fixtures/TONAL.png; fixtures/TONAL-alpha.png; fixtures/TONAL-alpha-manifest.json; photo-tone-events.jsonl; ui-events-current.jsonl','Only this control family is certified by this case. Remaining scalar families and photo workflows are still pending.')
results['updated_at']=datetime.now(timezone.utc).isoformat()
(root/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
variant_path=root.parents[1]/'VARIANT-EXECUTION-LEDGER.csv'
with variant_path.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
for row in rows:
    if row['family']=='Photo scalar settings':
        row.update(status='Partial',run_id=results['run_id'],evidence_paths='; '.join('runs/'+root.name+'/evidence/'+id+'-independent-verification.json' for id in ['PHOTO-009','PHOTO-010','PHOTO-011']),notes='Exposure, Brightness and Contrast: default, minimum, maximum and meaningful intermediate actual UI values, full-size export, original/source and alpha checks on opaque and transparent fixtures. Remaining named scalar families are not yet certified. Values used only to prepare other workflows do not count as endpoint/effect coverage.')
with variant_path.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
print('Recorded five independently verified photo cases; remaining workflows stay pending.')
