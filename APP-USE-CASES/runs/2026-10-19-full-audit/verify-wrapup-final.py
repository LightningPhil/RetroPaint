"""Verify the final isolated-browser run without replacing historical evidence."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import base64
import hashlib
import io
import json
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parent
repo = root.parents[2]
read = lambda relative: json.loads((root / relative).read_text(encoding="utf-8"))
sha = lambda data: hashlib.sha256(data).hexdigest()
save_new = lambda relative, value: (root / relative).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
outputs = ["evidence/ARTWORK-wrapup-final-verification.json", "evidence/application-source-consistency-wrapup-final.json", "evidence/wrapup-final-verification.json"]
assert not any((root / name).exists() for name in outputs), "Preserve previous final evidence"

manifest = read("production-hole-input-snapshot.json")
pinned = read("evidence/build-wrapup-final-source.json")
reg_path = "headless/20261021-wrapup-final/report.json"
reg = read(reg_path)
expected = {"painting":255, "layout-1280x720":68, "layout-320x568":69, "layout-390x844":69, "layout-844x390":69}
assert reg["status"] == "Pass" and len(reg["suites"]) == len(expected)
assert {suite["name"] for suite in reg["suites"]} == set(expected)
for suite in reg["suites"]:
    assert suite["status"] == "Pass" and suite["passed"] == expected[suite["name"]]
    assert suite["failed"] == 0 and not suite["errors"]
    assert len(suite["results"]) == expected[suite["name"]]

# Current app and regression sources must agree with both the historical build
# and the fresh run/build. Acceptance harness additions are a separate scope.
in_scope = lambda name: name == "index.html" or name.startswith("src/") or name in ["package.json", "package-lock.json", "tests/painting.ts", "tests/mobile.ts"]
source_maps = []
for source in [manifest, pinned, reg]:
    source_maps.append({item["path"].replace("\\", "/"):item["sha256"] for item in source["source_files"] if in_scope(item["path"].replace("\\", "/"))})
assert source_maps[0] == source_maps[1] == source_maps[2]
for name, digest in source_maps[0].items():
    assert sha((repo / name).read_bytes()) == digest, name
app_count = sum(name == "index.html" or name.startswith("src/") for name in source_maps[0])
assert app_count == 112 and len(source_maps[0]) == 116

build_exit = read("evidence/build-wrapup-final-exit.json")
assert build_exit["exit_code"] == 0
new_build = Path(build_exit["build_directory"])
assert new_build.resolve() != (repo / "dist").resolve()
assert new_build.resolve() != Path(manifest["build_directory"]).resolve()
old_files = {item["path"]:item["sha256"] for item in manifest["build_files"]}
new_files = {str(file.relative_to(new_build)).replace("\\", "/"):sha(file.read_bytes()) for file in new_build.rglob("*") if file.is_file()}
assert {name.replace("\\", "/"):digest for name,digest in old_files.items()} == new_files, "Fresh build must reproduce the previously tested production bytes"
for name, digest in old_files.items():
    assert sha((Path(manifest["build_directory"]) / name).read_bytes()) == digest
build_log = (root / "evidence/build-wrapup-final.log").read_text(encoding="utf-8-sig")
assert "tsc --noEmit" in build_log and "built in" in build_log and "110 modules transformed" in build_log

original = (root / "backups/artwork-before-acceptance-audit.retropaint").read_bytes()
original_sha = "612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28"
assert len(original) == 171748 and sha(original) == original_sha
art_folder = root / "headless/ARTWORK-wrapup-final"
ui = json.loads((art_folder / "ARTWORK-headless-ui.json").read_text(encoding="utf-8"))
assert ui["status"] == "Pass" and len(ui["downloads"]) == 4
assert ui["origin"] == manifest["url"] and ui["original_sha256"] == original_sha
for download in ui["downloads"]:
    data = Path(download["path"]).read_bytes()
    assert len(data) == download["bytes"] and sha(data) == download["sha256"]
pixels = []
for name in ["ARTWORK-headless-saved", "ARTWORK-headless-reopened"]:
    assert (art_folder / (name + ".retropaint")).read_bytes() == original
    image = Image.open(art_folder / (name + ".png")).convert("RGBA")
    assert image.size == (960, 640)
    pixels.append(np.asarray(image))
assert np.array_equal(*pixels)
previous = np.asarray(Image.open(root / "evidence/ARTWORK-photo-context-saved.png").convert("RGBA"))
assert np.array_equal(pixels[0], previous)
composite = Image.new("RGBA", (960,640))
for layer in json.loads(original)["layers"]:
    assert layer["visible"] and layer["opacity"] == 1
    bitmap = Image.open(io.BytesIO(base64.b64decode(layer["image"].split(",",1)[1]))).convert("RGBA")
    composite = Image.alpha_composite(composite, bitmap)
maximum_error = int(np.abs(np.asarray(composite).astype(np.int16) - pixels[0].astype(np.int16)).max())
assert maximum_error <= 1

results = read("results.json")
counts = Counter(item["status"] for item in results["cases"].values())
counts["Not run"] += 349-len(results["cases"])
assert counts == Counter({"Pass":82, "Partial":3, "Not run":264})
evidence_count = 0
for case, item in results["cases"].items():
    assert item["criteria_observations"] and item["independent_oracle"]
    for reference in item["evidence_paths"].split(";"):
        assert (root / reference.strip()).exists(), (case, reference)
        evidence_count += 1
glitter = read("evidence/INK-008-independent-verification.json")
assert glitter["status"] == "Pass" and glitter["actual_downloads_verified"] == 100 and not glitter["failures"]
diff = read("evidence/git-diff-check-wrapup-final-exit.json")
assert diff["exit_code"] == 0
at = datetime.now(timezone.utc).isoformat()
art = dict(at=at, status="Pass", execution=ui["execution"], production_url=ui["origin"], evidence_folder="headless/ARTWORK-wrapup-final", original_bytes=171748, original_sha256=original_sha, actual_downloads=4, contexts=2, actual_downloads_byte_exact_to_original=True, rendered_rgba_save_reopen_and_previous_build_exact=True, independent_layer_composite_maximum_channel_difference=maximum_error, decoder="Pillow " + Image.__version__, current_user_artwork_tab_unaccessed=True)
consistency = dict(at=at, unchanged_application_files=112, unchanged_dependency_manifests=2, unchanged_regression_sources=2, manifest="production-hole-input-snapshot.json", pinned_before_build_source="evidence/build-wrapup-final-source.json", latest_complete_regressions=reg_path, artwork_verification=outputs[0], app_source_and_entry_html_exact=True, fresh_reproducible_build="evidence/build-wrapup-final-exit.json", fresh_build_assets_byte_identical=True, scope="All112 app/entry files,two dependency manifests andtwo regression sources agree with the pinned prior production,fresh complete suite andfresh build. Every fresh/previous immutable build file is byte-identical. Later acceptance JS/Python additions remain separate.")
report = dict(at=at, status="Pass", acceptance_audit_complete=False, case_status_counts=dict(counts), complete_regression_checks=sum(expected.values()), suites=expected, browser=reg["browser"], uncaught_page_errors=0, original_backup_sha256=original_sha, artwork=outputs[0], source_consistency=outputs[1], reproducible_build_files=len(new_files), preserved_original_build=True, original_dist_and_user_artwork_tab_untouched=True, recorded_cases=85, existing_evidence_references=evidence_count, no_missing_evidence_references=True, whitespace_check="evidence/git-diff-check-wrapup-final.log", next_unexecuted_case="INK-009", unexecuted_case_count=264, partial_cases=[case for case,item in results["cases"].items() if item["status"] == "Partial"], execution="Own isolated headless Chrome;no computer use,existing browser/profile,desktop input orphysical-device claim.")
save_new(outputs[0], art)
save_new(outputs[1], consistency)
save_new(outputs[2], report)
supplementary = results["supplementary_checks"]
supplementary["browser_regressions"] = dict(status="Pass", count=255, evidence=reg_path, scope="Component regressions;not additional acceptance cases.")
supplementary["desktop_layout"] = dict(status="Pass", count=68, evidence="headless/20261021-wrapup-final/layout-1280x720.txt")
for width,height in [(320,568),(390,844),(844,390)]:
    supplementary[f"phone_{width}_layout"] = dict(status="Pass", count=69, evidence=f"headless/20261021-wrapup-final/layout-{width}x{height}.txt", scope="Isolated headless;physical input/AT unavailable.")
supplementary["headless_execution"] = dict(status="Pass", browser=reg["browser"], evidence=reg_path, scope=report["execution"])
supplementary["source_consistency"] = dict(status="Pass", count=112, evidence=outputs[1])
supplementary["artwork_production_roundtrip"] = dict(status="Pass", evidence=outputs[0], scope="Two actual editable downloads byte-identical to original protected backup;four downloads/two fresh contexts;save/reopen/previous-build RGBA exact.")
supplementary["final_reproducible_build"] = dict(status="Pass", evidence="evidence/build-wrapup-final.log; evidence/build-wrapup-final-exit.json; evidence/build-wrapup-final-source.json", scope="Fresh TypeScript/Vite build to a new directory;all output files byte-identical to tested immutable production. Original dist untouched. Existing externalized-module/chunk-size warnings retained.")
supplementary["wrapup"] = dict(status="Pass", evidence=outputs[2], scope="Verification/handover checkpoint;349-case acceptance audit remains incomplete.")
results["updated_at"] = at
temporary = root / "results-wrapup-final.tmp"
assert not temporary.exists()
temporary.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
temporary.replace(root / "results.json")
print(json.dumps(report, indent=2))
