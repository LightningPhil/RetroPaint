from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json
root=Path(__file__).resolve().parent
read=lambda p:json.loads((root/p).read_text(encoding="utf-8"))
results=read("results.json")
counts=Counter(c["status"] for c in results["cases"].values())
counts["Not run"]+=349-len(results["cases"])
wrap=read("evidence/wrapup-final-verification.json")
assert wrap["status"]=="Pass" and wrap["case_status_counts"]==dict(counts)
checkpoint=dict(at=datetime.now(timezone.utc).isoformat(),state="Stopped at user-requested time-limited handover;acceptance audit incomplete",active_cases=[],next_case="INK-009",case_status_counts=dict(counts),origin="http://127.0.0.1:8106/",production_manifest="production-hole-input-snapshot.json",regression="headless/20261021-wrapup-final/report.json",regression_counts=[255,68,69,69,69],artwork="evidence/ARTWORK-wrapup-final-verification.json",verification="evidence/wrapup-final-verification.json",handover="WRAP-UP.md",remaining_inventory="remaining-cases.csv",workflow="INK001..008 andPAINT001..019 independently complete. PAINT020 remainsPartial forphysical pen. All530 final component/layout checks pass;fresh build reproduces tested immutable production bytes. Original artwork SHA/source/pixels/save/reopen verified withfour new downloads/two isolated contexts. INK008 records4 layouts/12 Glitter patches/8 actual Water-Static controls/100 verified downloads. No INK009 execution started.",pending="264 Not run cases plus three Partial cases. Resume INK009:all7 textures in actual labelled paint patches andsupportedfill workflows;separately provefive static/two animated materials,zoom,history,save/reopen. Do not infer its Pass fromGlitter's positive controls. Physical pen/real assistive technology andauthentic historicalv3..8 files remain unavailable. See remaining inventory andcase/variant ledgers.",constraints="No computer use/desktop/existingbrowser/profile/artwork-tab8088 access. Own isolated headless only. Neveroverwrite originaldist,immutable builds,protected backup orfailed evidence. No commits/pushes/subagents. Do not run audit_support snapshot/backup orold recorders;ledger is safe. Full349 IDs preserved;noPass fromUI completion/component counts/fixtures/prefixes.")
(root/"evidence/live-headless-checkpoint.json").write_text(json.dumps(checkpoint,indent=2)+"\n",encoding="utf-8")
print(json.dumps(dict(state=checkpoint["state"],counts=dict(counts),next_case="INK-009")))
