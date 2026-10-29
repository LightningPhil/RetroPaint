"""Record only the independently completed INK-008 acceptance result."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

root = Path(__file__).resolve().parent
repo = root.parents[2]
read = lambda name: json.loads((root / name).read_text(encoding="utf-8"))
sha = lambda data: hashlib.sha256(data).hexdigest()
results = read("results.json")
check = read("evidence/INK-008-INK-008-glitter-independent.json")
ui = read("headless/INK-008-glitter/INK-008-ui.json")
manifest = read("production-hole-input-snapshot.json")
assert "INK-008" not in results["cases"], "Do not overwrite an existing case result"
assert check["status"] == "Pass" and not check["failures"]
assert len(check["rows"]) == 4 and check["actual_downloads_verified"] == 100
assert check["actual_native_glitter_gestures"] == 12
assert check["actual_native_motion_controls"] == 8
assert ui["status"] == "Pass" and not ui["errors"]
assert ui["origin"] == manifest["url"] and len(ui["rows"]) == 4
assert all(row["glitter_in_basic_mode"] for row in ui["rows"])
assert sha((root / "headless/INK-008-glitter/executed-harness.mjs").read_bytes()) == ui["harness_sha256"]
assert results["supplementary_checks"]["source_consistency"]["status"] == "Pass"
assert sha((root / "backups/artwork-before-acceptance-audit.retropaint").read_bytes()) == "612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28"

# Recheck actual download provenance without replacing any earlier raw report.
downloads = []
for row in ui["rows"]:
    folder = root / "headless/INK-008-glitter" / row["id"]
    for relative in ["events.json", "fresh/events.json", "motion/events.json"]:
        for event in json.loads((folder / relative).read_text(encoding="utf-8")):
            if event["action"] == "download":
                data = Path(event["path"]).read_bytes()
                assert len(data) == event["bytes"] and sha(data) == event["sha256"]
                downloads.append(event)
assert len(downloads) == 100
for item in manifest["source_files"]:
    name = item["path"].replace("\\", "/")
    if name == "index.html" or name.startswith("src/") or name in ["tests/painting.ts", "tests/mobile.ts", "package.json", "package-lock.json"]:
        assert sha((repo / name).read_bytes()) == item["sha256"]
for item in manifest["build_files"]:
    assert sha((Path(manifest["build_directory"]) / item["path"]).read_bytes()) == item["sha256"]

canonical = root / "evidence/INK-008-independent-verification.json"
assert not canonical.exists(), "Preserve previous independent evidence"
canonical.write_text(json.dumps(check, indent=2) + "\n", encoding="utf-8")
results["cases"]["INK-008"] = dict(
    status="Pass",
    variants_executed="All four layouts;12 native Blue/Pink/Gold Glitter patches in Basic mode;8 separate actual Water/Static moving controls;100 actual downloads, all hashes rechecked. Real one-second waits, actual zoom in/out, separate three-gesture histories and transparent-file fresh input.",
    criteria_observations="Metallic light/dark core variation and selected tint satisfy the independently recorded plan. Glitter and prior patches remain RGBA exact through real idle/zoom. Water and Static each change more than100 pixels inside their own separate control path during actual elapsed time;every pixel outside those paths,including Glitter,stays unchanged. Locality,clear alpha,guide preservation,independent dark-scene composition,whole Undo/Redo histories and actual transparent saved source/export/fresh-input RGBA all pass. No fake clock or app material factory supplies expected values.",
    independent_oracle=check["oracle"],
    evidence_paths="evidence/INK-008-independent-verification.json; fixtures/INK-008-plan.json; headless/INK-008-glitter/INK-008-ui.json; headless/INK-008-glitter/executed-harness.mjs; production-hole-input-snapshot.json; evidence/application-source-consistency-hole-input.json",
    defect_or_blocker="No product defect observed in the tested scope. Layer setup and the guide-eye alpha branch use actual Advanced navigation;main Glitter gestures remain Basic. Public/native alpha comparisons use the previously established exact associated-RGBA representation model;raw source,history,download and fresh-input comparisons remain strict. This result does not pass the separate seven-material paint/fill INK-009 case or physical-device coverage."
)
results["updated_at"] = datetime.now(timezone.utc).isoformat()
(root / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("INK-008 Pass:4 layouts/12 Glitter patches/8 actual moving controls/100 verified downloads.")
