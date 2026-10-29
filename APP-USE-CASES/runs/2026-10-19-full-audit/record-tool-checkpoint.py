from pathlib import Path
import json,csv
from datetime import datetime,timezone

root=Path(__file__).resolve().parent
results=json.loads((root/'results.json').read_text(encoding='utf-8'))
verification=json.loads((root/'evidence/START-002-independent-verification.json').read_text())
assert len(verification['phones'])==3 and verification['full_saved_project_identity']
results['cases']['START-002']=dict(status='Pass',variants_executed='All 12 illustrated tools, one explicit choice each, close and reopen already-active tool; desktop 1280x720 and actual Chrome frames at 320x568,390x844,844x390. Existing Redo branch retained, then restored by its real control.',criteria_observations='Each main tool has an illustration and meaningful name. Workspace text names each active tool; Symmetry is separately selected as a modifier. Biro, Circle, Yellow, Confetti, size 23, Lasso, Invert, Frog, 4-way, square stator/54 teeth, Georgia and swapped colours survive reopening. Every measured paper rectangle is unchanged. Complete saved project JSON and full white-paper pixels are exact before/after; one Redo restores the earlier blue stroke exactly in each layout.',independent_oracle='Pillow 12.3.0 full RGBA, independent parsed JSON identity, visible DOM labels/settings/rectangles and screenshots; actual uniquely named Chrome downloads correlated to filesystem bytes',evidence_paths='evidence/START-002-independent-verification.json; evidence/START-002-tool-inventory.json; evidence/START-002-controls.json; evidence/START-002-phone320-controls.json; evidence/START-002-phone390-controls.json; evidence/START-002-phone844-controls.json; evidence/START-002-phone320-spiro-retained.json; evidence/START-002-phone390-spiro-retained.json; evidence/START-002-phone844-spiro-retained.json; frame-download-events.jsonl; ui-events-current.jsonl',defect_or_blocker='No app defect found in this case. Phone drawer obscures the rail; the harness was corrected to use the visible Close button. Initial cross-session verifier incorrectly demanded identical allocated Paper IDs (desktop 2, fresh phone 1); each full before/after document is instead checked against its own preserved identity. No physical touch/pen certification claimed.')
s=results['supplementary_checks']
s['browser_regressions'].update(count=228,scope='Complete 228-check sequence passed on the final app source. Component/integration coverage, separate from acceptance cases.')
s['desktop_layout'].update(count=59,scope='Complete 59-check desktop sequence passed after compact layout, mesh readiness and harness repairs.')
for width,height in [(320,568),(390,844),(844,390)]:
    s[f'phone_{width}_layout']=dict(status='Pass',count=61,evidence=f'evidence/regression-phone-{width}-current.txt',scope=f'Complete sequence in measured {width}x{height} responsive frame; real mouse and synthetic regression events. Physical touch/pen and assistive technology not certified.')
s['production_build'].update(evidence='evidence/build-production-snapshot.log',notes='Final app TypeScript and Vite build passed; immutable output source/build hashes in production-snapshot.json. Existing node:module externalization and chunk-size warnings remain.')
s['artwork_production_roundtrip']=dict(status='Pass',evidence='evidence/ARTWORK-production-verification.json',scope='Original backup, real production chooser open/save, fresh-tab chooser reopen/save: all three actual project files have identical SHA-256 612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28. Full rendered pixels exact; independent layer composition within 1/255.')
case=results['cases']['ACCESS-018']
case['variants_executed']='Measured responsive frames at 320x568,390x844,844x390; actual 390x844 UI solid creation and exact 12.5mm position application; 61 supplementary checks per phone layout, including all feature field reachability, help and delayed mesh readiness.'
case['criteria_observations']='Original standard controls ranged from 15/22 to 40px and some actions shrank to 28.677px. Compact editors now retain natural scale and 44px targets with contained scrolling. All three complete layout sequences pass. Physical touch remains unavailable. The original frame STL download watcher did not capture bytes; no STL pass is claimed from that attempt. Uniquely named Chrome frame project/PNG downloads now provide genuine byte evidence for START-002.'
case['defect_or_blocker']='D-006 software correction verified across all three layouts; physical touch/pen unavailable. Further actual feature workflows and hardware-specific behavior remain pending.'
case['evidence_paths']+='; evidence/regression-phone-320-current.txt; evidence/regression-phone-844-current.txt; evidence/START-002-independent-verification.json'
results['updated_at']=datetime.now(timezone.utc).isoformat()
(root/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
path=root.parents[1]/'VARIANT-EXECUTION-LEDGER.csv'
with path.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
for row in rows:
    if row['family']=='Painting tools':row.update(status='Pass',run_id=results['run_id'],evidence_paths='runs/'+root.name+'/evidence/START-002-independent-verification.json',notes='All 12 named tools actually exercised on desktop and three responsive phone layouts with mouse input. Physical touch/pen remains unavailable and is not certified.')
with path.open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
print('Recorded START-002 Pass and final supplementary verification counts.')
