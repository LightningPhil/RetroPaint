"""Write an evidence-linked stopping point and full unfinished-case inventory."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import io
import json

root=Path(__file__).resolve().parent
catalogue=root.parents[1]
read=lambda relative:json.loads((root/relative).read_text(encoding="utf-8"))
results=read("results.json")
verification=read("evidence/wrapup-final-verification.json")
assert verification["status"]=="Pass" and not verification["acceptance_audit_complete"]
rows=list(csv.DictReader((catalogue/"EXECUTION-LEDGER.csv").open(encoding="utf-8-sig",newline="")))
assert len(rows)==349
counts=Counter(row["status"] for row in rows)
assert dict(counts)==verification["case_status_counts"]
remaining=[row for row in rows if row["status"]!="Pass"]
assert len(remaining)==267
output=io.StringIO(newline="")
writer=csv.DictWriter(output,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(remaining)
(root/"remaining-cases.csv").write_text(output.getvalue(),encoding="utf-8")
areas=defaultdict(Counter)
for row in rows:areas[row["case_id"].split("-")[0]][row["status"]]+=1
table="\n".join(f"| {area} | {sum(values.values())} | {values['Pass']} | {values['Partial']} | {values['Not run']} |" for area,values in areas.items())
date=datetime.now(timezone.utc).date().isoformat()
text=f'''# Audit handover — {date}

Work stopped at the user's requested time-limited handover. The full 349-case acceptance audit is **incomplete: 82 Pass, 3 Partial, 264 Not run**. No new case was started during this wrap-up. INK-008 was the last completed case; its independently verified result has now been recorded.

The [final verification](evidence/wrapup-final-verification.json), [authoritative results](results.json), [canonical execution ledger](../../EXECUTION-LEDGER.csv) and [complete unfinished inventory](remaining-cases.csv) agree. All 349 original IDs and order remain intact. Every evidence reference in all 85 recorded results exists. Regression counts below are supplementary and add no acceptance passes.

## Artwork and final checks

- The [original editable artwork backup](backups/artwork-before-acceptance-audit.retropaint) remains 171,748 bytes with SHA-256 `612e2d0b4db85c61a4722de26aff3810fa2c4b17e5c5dc49391ca349e1fcfa28`.
- [Two fresh isolated contexts](headless/ARTWORK-wrapup-final/ARTWORK-headless-ui.json) opened the actual protected file, downloaded projects/PNGs and reopened the saved project. All four downloads are hashed; both editable copies exactly equal the original bytes. [Independent verification](evidence/ARTWORK-wrapup-final-verification.json) confirms saved/reopened/previous-production RGBA exact and Pillow layer composition within the original 1-byte rounding allowance.
- The [fresh complete regression run](headless/20261021-wrapup-final/report.json) passes 255 painting/component checks, 68 desktop checks and 69 at each of 320×568, 390×844 and 844×390: 530 checks, no failed checks or uncaught page errors. This includes the complex joined-cylinder/cube shell and persistent Workshop Layers regressions. It does not establish Pass for unexecuted CAD acceptance cases.
- A [fresh TypeScript/Vite build](evidence/build-wrapup-final.log) succeeds in a new output directory. Every output file is byte-identical to the already tested immutable production build. [Pinned hashes](evidence/build-wrapup-final-source.json) and [source consistency](evidence/application-source-consistency-wrapup-final.json) verify 112 app/entry files, two dependency manifests and two regression sources against both complete suite and build. Existing externalized-module/chunk-size warnings remain recorded.
- [Whitespace verification](evidence/git-diff-check-wrapup-final.log) succeeds. No commits or pushes were made. The large existing dirty tree remains available for review.

All wrap-up browser tests used our own isolated headless Chrome contexts. No computer use, desktop input, user browser/profile connection or access to the artwork tab at 8088 occurred. Original `dist`, protected backup, prior failed attempts and immutable builds were not overwritten. These checks verify the protected backup; they do not claim to capture edits made later in the untouched user tab.

## Last acceptance results completed

INK-006 Rainbow passes 8 original/reversed workflows, 24 gestures and 176 downloads. Independent hue progression, family coverage, locality, complete histories and actual saved source/pixels/fresh input pass under the documented procedural-save rule.

INK-007 Neon passes 4 layouts, 8 Blue/Pink lines and 72 downloads, including independent bright-core/graded-halo/tint/falloff checks, transparent export, whole histories and fresh source/RGBA. The initial incomplete Basic-mode Layers navigation attempt remains retained under H-030.

INK-008 Glitter passes 4 layouts, 12 Blue/Pink/Gold patches and 100 downloads. Real one-second waits and actual zoom prove static metallic colour retention. Eight separately painted Water/Static controls actually animate inside their own footprints while all Glitter/outside pixels stay unchanged. Complete histories and transparent-file fresh input pass. See [independent report](evidence/INK-008-independent-verification.json), [original plan](fixtures/INK-008-plan.json) and [actual UI report](headless/INK-008-glitter/INK-008-ui.json).

## Resume point and unavailable inputs

Resume **INK-009**, the seven-texture case. It has **not been executed**. Test brick, dots, weave, grass, stone, water and static as actual separately labelled painted patches and supported bounded fills. Verify recognisable structure, tiling, zoom, prior-material retention, five stationary versus two animated materials, complete histories and actual project save/reopen. Glitter's positive controls do not satisfy this separate case. No new INK-009 plan or fixture was committed during the wrap-up.

Three cases remain Partial:

- **PAINT-020:** 32 software fast-curve workflows/320 downloads passed; physical pen coverage is unavailable. Browser pen emulation is not physical pen evidence.
- **ACCESS-018:** software/layout measurements exist; physical touch/pen and actual assistive-technology operation remain unverified. Accessibility metadata is not screen-reader execution.
- **FILE-015:** genuine historical versions 1, 2 and 9 pass migration/save/reopen checks. Authentic versions 3–8 are unavailable; the user confirmed no older files exist. Do not relabel modern files as historical fixtures.

The user's permitted photographs are in `F:/WebDev/RetroPaint/Example_Images`. Existing fixtures include actual layered/live/object/photo MIX and CADMIX producers; inspect their manifests before reuse. The [variant ledger](../../VARIANT-EXECUTION-LEDGER.csv) is independently scoped: case passes do not automatically pass an entire material/option family.

| Area | Total | Pass | Partial | Not run |
| --- | ---: | ---: | ---: | ---: |
{table}
| **Total** | **349** | **82** | **3** | **264** |

## Evidence preservation and continuation

Keep [DEFECTS.md](DEFECTS.md), raw bytes, failed or interrupted runs, executed harness copies, event traces and independent reports. Harness corrections H-026–H-030 are retained; H-029 proves exact native associated-RGBA identity for translucent serializer aliases and keeps opaque negative controls distinct. It does not permit wider pixel tolerances or raw saved-data normalisation.

Do not rerun old result recorders or `audit_support.py snapshot`/`backup`: those can replace historical state. `audit_support.py ledger` is the safe canonical ledger sync. Existing source/build manifests are immutable; new source fixes require failing-before evidence, focused after checks, a complete suite, a fresh build and new artwork verification. Use fresh output folders; never count a fixture, prefix or UI-only completion as a case Pass.

The latest machine-readable stop point is [live-headless-checkpoint.json](evidence/live-headless-checkpoint.json). No unattended continuation or scheduled automation was created.
'''
(root/"WRAP-UP.md").write_text(text,encoding="utf-8")
print(f"Wrote handover and{len(remaining)} unfinished rows;counts={dict(counts)}")
