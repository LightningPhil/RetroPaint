# Coverage gaps found on 5 November 2026

The 349-case catalogue was authored before commit `066f05a`. Its shape value
`callout` means a speech-bubble shape; it does not cover connected text labels.
The following supplemental cases are required. Current results are in the
[supplemental execution ledger](supplemental-execution.json); all22supplemental cases now pass (sixLABEL,twelveCODE,fourWIKI). Each must include cancellation, Undo/Redo where applicable, independent
output checks and real saved-project reopening under the shared protocol.

| ID | Workflow and expected result | Required variants / failure path |
| --- | --- | --- |
| LABEL-001 | Text → Label + arrow creates editable, auto-sized text and a connected arrow. | Raster and vector preference; blank and long wrapping text; Cancel. |
| LABEL-002 | Drag the arrow target independently of its box. | Every side and rounded corner; zoom; outside-paper placement. |
| LABEL-003 | Drag the box centre while retaining the target. | Arrow reconnects to nearest box edge; rotation and resize. |
| LABEL-004 | Edit label words and styling through Selection options. | Foreground/background, size, width, border on/off, square/rounded corners; dismiss draft. |
| LABEL-005 | Label a CAD sheet and retain the model. | Paper selected below CAD; CAD selected; existing annotation sheet; one-step Undo removes any newly created sheet. |
| LABEL-006 | Duplicate, copy/paste, Undo/Redo, save and reopen labels. | Copies independent; exact words, transforms, tip and styles retained. |
| CODE-001 | Open Code studio and render a starter without changing scene. | Preview, F5, Ctrl+Enter; orbit, fit, close; reopen draft. |
| CODE-002 | Load and render each of all ten named starter models. | Five original and five advanced; one numeric parameter variation each; inspect connected, closed STL output. |
| CODE-003 | Edit numeric Parameters and preserve unrelated source. | Exponent notation, repeated names, comments, strings and module-local constants; invalid numbers. |
| CODE-004 | Add rendered code to scene; edit source; Update selected. | Placement, scale, colour, rotation retained; one-step Undo/Redo; stale preview disables Add/Update. |
| CODE-005 | Render actual OpenSCAD language operations. | Functions, modules/children, loops/comprehensions, transforms, Minkowski, text and solid booleans. |
| CODE-006 | Open standalone .scad, then Save .scad. | Unicode source, cancelled chooser, invalid source, 2 MB boundary; actual downloaded source bytes. |
| CODE-007 | Open a folder and choose its entry independently of Edit file. | Relative include/use/import, nested paths, helper edits and real project round trip; missing/conflicting files. |
| CODE-008 | Add assets, fonts and external libraries. | Bundled MCAD, project library paths, SVG/STL/heightmap/fonts; missing dependencies and size/count limits. |
| CODE-009 | Recover from syntax and dependency errors. | Correct file/line selected; echoed ERROR text remains echo; bounded output; 2D/empty geometry receives actionable explanation. |
| CODE-010 | Enable Auto preview, edit, cancel and retry. | Close while rendering, replacement file load, failed import and late responses cannot overwrite newer draft or scene. |
| CODE-011 | Save/reopen a project with source and dependencies. | Exact dependency bytes, entry and edited helper files retained; draft versus applied source; older formats. |
| CODE-012 | Combine a code solid with workshop operations and export STL. | Join/Cut, transforms, painting annotations; independent units, volume, edge incidence and normals. |
| WIKI-001 | Open help, search, filter and navigate related topics and Back/Forward. | All 68 core articles and 42 MCAD pages; empty search; focus restored on close. |
| WIKI-002 | Read both teaching levels and jump to examples. | All articles, compact layouts, async MCAD load must retain scroll/focus. |
| WIKI-003 | Render each of all 70 runnable examples in isolation. | Expected visible result and guided variation; dependencies supplied; draft and scene unchanged; cancel/close. |
| WIKI-004 | Copy example code deliberately. | Exact commented source, clipboard denial, subsequent paste into editor; no automatic draft replacement. |

Existing cases also need updated variant mapping: FILE-015 now includes project
formats 11–13 (v11 and v13 now have native round-trip evidence; v12 remains synthetic-only); START-007/SOLID-001 use the approved Advanced-only entry boundary;
ACCESS cases must include the Code studio and wiki overlays. Existing automated
checks of these features are useful starting points, not substitutes for live
acceptance execution.

LABEL-005 route clarification: selecting a CAD sheet opens the isolated workshop; Text is inert there. Paint returns to the first valid paint sheet (Paper in the fixture), after which an existing annotation sheet can be selected explicitly. The live audit verifies this actual supported route and the separate automatic annotation-sheet creation from Paper below CAD.

## Deferred review queue — 7 November 2026, with subsequent updates

User requests cost-conscious testing: fix straightforward defects and retain harder findings for later Sol/Astra review. Do not confuse an unexecuted branch with a confirmed product defect. Current authoritative statuses remain in execution.json.

| Finding | Status and evidence | Next action |
| --- | --- | --- |
| Continuous curved mouse paths, continuous right-button drags and modifier-held drags | Input capability gap. Documented CUA and Windows sky drag APIs take only endpoints; Shift browser/native probes did not yield Shift in actual pointer events. PAINT/INK/PLAY/EDIT branches remain Partial. | Use a documented path/modifier-capable input interface or physical input; retain native PointerEvent evidence. Do not substitute released segments for a continuous stroke. |
| Physical pen, touch scrolling and screen-reader interaction | Hardware/input validation gap; software regressions and mouse flows pass, including phone146 matrix. | Physical device or suitable accessible test environment required. Changing reasoning model alone does not certify hardware behaviour. |
| Genuine version3–8 project files | Resolved: recovered six complete historical producer trees and saved genuine files through their UIs. FILE-015 remains Partial pending authentic format 12 and any missing defaults not covered by the v3 checks recorded in `execution.json`. | See `legacy-recovered/manifest.json`, retained original/migrated/reopened files and `mouse/legacy-curves309.png`. |
| Large neural enhancement above32MP | ENHANCE-012 now Pass: actual47MP4x photo726tiles, decoded fullPNG/CRC/zlib/allrows, sourceprojectbyteexact. Prior bothscale clear-image edge-limit streams remain separate evidence. | Completed enhance156; hardware-specific resource exhaustion is not universally certified. |
| Enhancement overview border/letterbox mapping | Confirmed and fixed as LIVE-061. Native expected461,985 selected476,975 before; exact after. Blank-margin press ignored and drag clamping retained. | Fixed; four-layout red/green checks pass. Keep native enhance150 evidence. |

Enhancement cancellation: enhance155-verification.json proves actual tile2 Close, tile16 Escape, source byte identity and clean restart. The first visible Starting state did not prove download-stage cancellation: worker progress had advanced before Close arrived. For ENHANCE-009 retain a controlled slow uncached-model-download branch; no confirmed defect.

Resolved geometry safety gap LIVE-067: nativeunconstrainedcrossingprofileexportedfalseClosedsolidwith4facesononeedge. Sharedraw/solvedoutlinevalidationnowrejectscrosses/touches/collapsed/noarea;nativecorrectedconcaveLclosed6000mm3/raynotch/sourceatomic;full786checks pass. No deferredproductfix remains for this finding.

### TAPER-193 — twisted extrusion volume accuracy (deferred geometry review)

Confirmed discrepancy; SKETCH-011 stays Partial. On production61747/build67, draw an XY rectangle [(0,0),(20,0),(20,10),(0,10)], pull30mm, top size0.5, twist+90°. Actual closed STL volume3568.0599375mm³ versus continuous analytic3500mm³: +1.94457%. History-edit the same extrusion to top size0.75 and twist−45°: actual4578.7044472 versus4625mm³: −1.00098%. Every mesh ring matches the intended linear scale and angle; 34Zlevels/268triangles. Untwisted taper and restored neutral solid are exact. Invalid0top/721° drafts, Cancel and multi-preview single Undo/Redo passed with actual native project comparisons.

Reproducible inputs/outputs and hashes: mouse/taper193-ui.json, taper193-verification.json and retained mouse-audit-taper193*.retropaint/*.stl; independent verifier verify-taper-twist.py. The original0.1% volume criterion was retained. Possible tessellation/triangulation effect in cad-kernel.ts fixed32 twist subdivisions is an inference, not a proven root cause. Later review should establish accuracy policy and convergence/performance across subdivision counts, both twist signs, 90/180/720°, and centred/offset profiles before changing geometry. BRep supports taper/twist; do not label it unsupported or centre the fixture to conceal the error.

Resolved LIVE-068 timeline resize: confirmed33pxphone/38pxlandscape step targets; responsivegroups/pageanchors fixed and nativephone72px/selectedstep4/fourlayoutstreepaging/source+meshpreservation verified. Full787checks pass. No deferredfix remains for this issue.

### CANCEL-198 — pending feature rebuild cannot be interrupted (deferred lifecycle review)

Confirmed interaction limitation; FEATURE-004 stays Partial. Production61747/build68, native feature196 saved7mm plate with attached Through all hole and fillet. Open original Plate pull, change depth8, arm existing single-job stall (`POST /audit-command`, body `stall-cad`), then click Preview. During actual busy job, Cancel remains visible and DOM-disabled=false, but native mouse click at its screenshot-confirmed centre leaves busy/editor/depth8 unchanged. The real45-second timeout eventually reports the precision operation took too long and retains the draft. Only then does Cancel restore the original. A fresh8mmPreview on the restarted engine succeeds, and subsequent Cancel also restores the original.

Independent proof: cancel198-ui.json, cancel198-verification.json, pending/retry screenshots and retained mouse-audit-cancel198 project/STL files. Three actual project sources match exactly apart from active layer/CAD presentation image; both actual STLs are byte-identical to the previously verified7mm finished plate. No corruption or stuck engine remains. A late response after **successful cancellation of a pending job** is still uncertified because this interaction cannot currently succeed.

Relevant controls: cad.css makes the working panel pointer-inert; cadFeatureCancel also goes through callbacks.run/solidAction, which returns while busy. This is broader than making one button clickable. Review desired cancellation semantics, worker abort/reset and job/draft generations before changing it; cover obsolete replies, immediate retry, queued jobs and close/file-switch races. Treat the observed inability to interrupt as the finding, rather than claiming an unobserved late commit. Deferred under the user's easy-fixes/hard-notes instruction.

Resolved LIVE-069 overlappingdimensionlabels: actual45mmcentreselectedother0degrule. MeasuredtextboundsseparatewithunclippedviewBox; nativealllabels/fourlayoutshitownIDs, actual50mmgeometry/UndoRedo/reopen/sourcepreservation verified; full788checks pass. No deferredfix remains for this issue.

Resolved LIVE-070 invaliddimensionfeedback: angularboundsincorrectlyreportedmillimetres/workspace; contextualnames/ranges/unitsnowverifiednativeforall4dimensiontypes. Allrejectionrulesunchanged; projectsandSTLsunchanged, full788checksPass.

### SUPPORT-204 — fixed-plane conversion closes a Through all hole (deferred semantics review)

Confirmed discrepancy against the intended recovery; FEATURE-008 stays Partial. Native20mm cube centredZ10, picked top face, D4 circle, requested numericdepth1 with Through all checked. Correctly cuts through20mm. History sourceheight30 correctly rebuilds through boundsZ−5..25. Moving hole centreX100 gives the expected missing-support error, retains the original and offers a fixed plane. Cancel is source/STL exact.

On the valid attached hole, choose fixedXY with explicit originZ25. Conversion clears attachment and `through`, but leaves recipe height−1. The resulting saved mesh is a1mm pocket with floorZ24, closing the opening. Actual material11987.4425993mm³ versus intended through-hole11623.2779756mm³ (same96gon oracle), difference364.1646237mm³. Euler changes0→2 and the centre vertical ray becomes[−5,24]. The original criterion was retained as a failure; it was not relabelled a successful recovery. The sketch plane editor does not show the now-active1mm cut depth when choosing the fixed plane.

Reproduce on production61747/build70 with retained mouse-audit-support204 (10).retropaint, edit original circle sketch, select fixedXY/origin0,0,25, Preview/Apply. Saved (12)/(14) and STL (5) preserve the unexpected pocket. support204-ui.json, support204-verification.json and support204-fixed-plane-pocket.png retain source, mesh, rays and UI evidence. See cad-features.ts `setFeaturePlane` clearing flags and cad-kernel.ts/cad-brep.ts attachment-dependent through-depth resolution. Review whether conversion should preserve resolved depth/Through intent or make the change explicit before applying; cover rotated/scaled supports and plane-origin changes in both kernels.

Verified manual workaround: edit the retained cut extrusion's depth explicitly to30mm Inwards after conversion. Saved (15)/(17), STL (6)/(7) restore the intended hole and match each other byte-for-byte after Redo; sourceUndo/Redo exact. This is a workaround, not a product fix. SKETCH004/008/009 pass their separate support/recess/through criteria; fixed-plane semantics remain deferred under the user's easy-fixes/hard-notes instruction.

### EDGE-207 — supplemental circular-finish precision follow-up

FEATURE-009 stays Partial despite verified picker behavior. Native20mm cube with D4 Through all hole, picked whole top circular rim and applied equal-distance chamfer0.5. Saved mouse-audit-edge207-drilled (1).retropaint contains one closed CIRCLE reference at normalized centre[.5,.5,1], original source exact. Actual STL is closed oriented genus1; material7747.011018071062mm³ versus analytic8000−80π−π*(2*.5²+.5³/3)=7746.970891692122mm³. Error+0.040126378940mm³ exceeds the original0.030mm³ absolute precision criterion. This is a supplemental numerical discrepancy, not proof of a topology or picking defect; retain the failed criterion for tessellation/convergence review, do not widen it. Build70,61747; edge207-reselect208-verification.json retains both value and failed Boolean. Cylinder outer rim passes existing0.02percent curved-volume criterion. Initial cylinder front-rim tap[838,258] selected0; upper-rim[838,210] selected1. Screenshot/render timing has produced stale prior-camera frames in this session, so the first miss is an observation to reproduce with settled view rather than a confirmed product defect.

### SWEEP-217 — tight smooth sweep accepts and saves a nonmanifold mesh (deferred geometry validation)

Confirmed FEATURE-027 failure on production71/61747. Start from valid Section4x2 rectangular profile, roll30°, smooth path [0,0,0;0,0,20;20,0,20], Round transition. Valid STL is closed oriented Euler2, volume326.5392647mm³ vs independent8×Hermite-spine arc40.81980363=326.5584290mm³ within predeclared0.1mm³. Both caps have area8 and expected transported30° corners.

Edit only the path to [0,0,0;0,0,2;2,0,2]. Preview and Apply succeed. Print says “Closed solid geometry” and exports81,070triangles, volume32.64596946mm³. Independent exact raw-float coordinate edge incidence finds119,838edges with2incident triangles,882edges with4, and1edge with6;3triangles have zero area. The same result holds at8/6decimal coordinate precision, so this is not the independent oracle rounding away tiny edges. This is a confirmed nonmanifold-output failure; geometric self-intersection has not been separately proven or claimed. The contract requires safe failure for a bend too tight for the section.

Reproduce with retained mouse-audit-sweep217 (3).retropaint (valid), edit History Sweep path to2mmlegs, Preview/Apply. Saved (4)/(9) contain accepted tight recipe; STL (3)/(5) are byte-identical even after actual project reopen. UI screenshot sweep217-tight-accepted.png, original planned-oracles.json and sweep217-verification.json preserve both successful control variants and failed tight criterion. One Undo restores original valid recipe in (5); final actual reopen/Cancel (10) and STL (2)/(4)/(6) match valid output byte-for-byte. No project was left on the invalid output.

Review cad-brep.ts sweep BRepCheck_Analyzer validity, triangulation and downstream geometric manifold/degeneracy checks, plus Print’s closed-solid claim. Scope needs careful treatment of duplicated-coordinate sheets, real self-intersections, tolerances and performance; avoid a blanket curved-path or small-profile ban. This is deferred under the user’s easy-fixes/hard-notes instruction, alongside TAPER193/CANCEL198/SUPPORT204; EDGE207 is a separate supplemental numerical precision follow-up.

Resolved LIVE-071: enabledno-opAdd/Removeatpath64/2; sharedformsdisabledatpath2..64/profile3..256, nativebuilder+historyboundariesverified, full788Pass. Resolved LIVE-072: fixed18-unitclosegesturelostfourthtinycorner; adaptiveknotspacingradius preservesall4acrosspoly/spline/polygonandstillallowsstartclose. Native/isolatedregressions/actualsources/PNG/history/reopenverified; full789Pass aftertestfixturestylecleanup. Neitherissueisdeferred. Saveprojectintentionallysettlespendingpaths; olduntargetedEscapeattemptwasexcludedandrepeatedwithfocusedcanvas, whichworks.

### AXIS-224/225 — coincident symmetry lanes darken axis marks (deferred cross-pipeline compositing)

Confirmed PLAY-011 failure on production72/61747. Fresh white960x640 Paper, Blue#1e88e5,3px solid outline/no fill, opacity0.5. In vertical symmetry draw (480,100)→(480,200); switchOff and draw control (80,100)→(80,200). Horizontal symmetry draw (100,320)→(200,320); Off control (100,500)→(200,500). Axis lines should have the same centre colour as controls.

Editable-vector export axisRGB[87,166,235] versus controls[143,196,242]; raster export axis[86,165,236] versus controls[142,195,242]. Both match two0.5alpha draws (~0.75opacity), rather than the intended single0.5 mark. Vector project has2paths coincident within0.001px for each axis mark versus1for controls; all objects retainopacity0.5. Independent rawPNG pixels and source geometry confirm both axes/modes. Both actual projects reopen exactly and each PNGpair isRGBAexact. Raster pixels outside the four expected stroke bands are unchanged.

Reproducible files: mouse-audit-axis224 (4)/(5).retropaint and axis224.png/(1).png; mouse-audit-axis225 (5)/(6).retropaint and axis225.png/(1).png. axis224-225-verification.json retains intended-no-darkening=False, RGBcontrols and SHA256s. Globalopacity was restored1aftertesting; subsequent symmetry tests use opaque ink.

Review src/object-scene.ts lane-by-lane alpha, src/objects.ts makePathObject lane generation, src/draw.ts segment/dot plus spray paths, and src/fill.ts shape/fill/outline lanes. A point-level dedupe cannot change lane count midway through a stroke without breaking lane correspondence. Any geometry dedupe needs practical coordinate tolerance, reversed/closed geometry and distinct mask clips; a blanket alpha-grouping change can alter intentional Watercolor or repeated-gesture buildup/live ink. Retained for coherent repair rather than a vector-only or line-only claim. This is the fifth confirmed deferred product finding, alongside TAPER193/CANCEL198/SUPPORT204/SWEEP217; EDGE207 remains a separate precision follow-up.

GUARD233 (2026-11-08): mitigation implemented in src/cad-features.ts. Fixed-plane conversion of an attached through-all extrusion is rejected with instructions to first disable Through all and enter explicit depth. Native original SUPPORT204 fixture: warning observed, Cancel; depth30 Inwards applied, fixedXY originZ25 applied, saved project depth -30/no attachment/through false, native exported STL closed volume11623.277980 and axial ray has no material. Focused regression fixed-plane-guard passes; full suite/live reopen verification pending. This prevents silent damage; it does not automatically retain the dynamic through-all dependency.

CANCEL-198 resolution: CANCEL240 repaired pending-worker cancellation. Native stalled Preview Cancel completed in 427ms; source and STL remained exact, and a subsequent Preview succeeded after worker restart. Full76 regression passed; earlier observations above are retained as history.

### ENHANCE-263 — forced CPU retry duration observation

The controlled post-cancellation retry loaded the 2x model and reported tile 1 of 9 on the explicitly forced CPU backend. After more than 80 seconds without a tile progress update it was manually cancelled to continue testing; no performance threshold or failure is inferred. A 64px preview on the normal backend subsequently completed, and the prior ENHANCE155 run already verified a same-session successful retry. The source remained exact after cancelling the held model download.

EDGE-207 resolution: EDGE268 refined curved mesh angular tolerance to .04. Native STL error .017847mm3 is inside the unchanged .030mm3 criterion; source CAD bodies and reopened STL exact. Triangle count1906→2854 for this specimen. Focused red/green and full79 regression pass; earlier failed observations remain historical.

### TAPER-193 convergence investigation (2026-11-08)

A standalone Manifold experiment using the same 20x10x30 rectangle and interpolation reproduces the +1.94457% error at 32 divisions for +90°/0.5 taper. 512 divisions still misses the original 0.1% criterion (+0.12743%); 1024 passes (+0.06381%) but raises the rectangle from268 to8204 triangles. At +720°, 2048 divisions still miss (+0.25491%); scaling divisions enough to meet tolerance could be costly for a 96-point circular sketch and downstream booleans. The adaptive-mesh/resource strategy needs deliberate review; no tolerance was widened and no production change was made. Reproduce with test-results/audit-2026-11-05/twist-convergence.mjs.

### Mouse multi-waypoint probe (2026-11-08)

Combining a browser-held press with a native Windows drag does not create one continuous gesture. Pointer logs show capture loss at the start of the native drag, then a second pointerdown/move/up and a later stale mouseup from the original hold. This cannot certify curved, sharp-turn or held-modifier branches. Trace: fault-controls259/requests.jsonl at 10:05:36 UTC.

### TAPER-193 diagonal experiment (2026-11-08)

A disposable mesh experiment found that alternating the diagonal of successive side-wall quads largely cancels the first-order volume bias. For the original rectangle and 0.5 taper, 64 subdivisions measured +90° at -0.02633% and -90° at +0.00686%; at 256 subdivisions, +720° was -0.04833% and -720° was -0.03135%. A translated rectangle, concave six-point profile and 96-point circle at ±90° and ±720° likewise returned Manifold `NoError` and errors under 0.053% in this limited volume experiment. Reproduce with `test-results/audit-2026-11-05/twist-flip-experiment.mjs` and `twist-shapes-experiment.mjs`.

This is a promising direction, not a production fix: the prototype identifies matching vertices with a fixed tolerance, reconstructs the mesh, and has not established behavior for tiny/near-coincident features, extreme taper, self-intersections, boolean operations, imported projects, BRep precision features, performance or live preview/undo. The exact 0.1% acceptance threshold remains unchanged. A robust implementation needs those tests and an explicit complexity strategy before replacing the current mesh.
The same prototype was also sampled at taper endpoints 0.01 and 5 for those three profiles and ±90°/±720°; all returned `NoError` and volume error below 0.058% (`twist-extreme-experiment.mjs`). This tests those particular volumes only, not topology under self-intersection or booleans.

### Phone hit areas under review (2026-11-08)

Live production82 at 320×568: Select's Transparent white paper label measures 280×26 CSS px; Spiro ring radius, outer teeth and inner teeth inputs measure 40px high; Pick colour's secondary-colour input is 100×40; colour wheel hex is 266×36 and RGB fields are 60×32. All are operable with a mouse but below the 44px effective target. A grouped compact-layout correction and regression are pending; these findings are not yet resolved.

FIELDS278 resolution: production83 compact controls listed above now measure at least 44×44 CSS px. Drawing mode and save name/format fields were also fixed. `fields278-red/report.json` captures all twelve failing measurements at each compact layout; `fields278-green2/report.json` passes after the fix. Physical touch is still unverified.

FIELDS278 landscape follow-up: the first shared-size change made the exact-piece Size panel scroll by 15px at 844×390; a targeted compact spacing adjustment preserves the 44px controls and removes the overflow. Native production84 measured Size 369/369, Position 364/364 and Arrange 362/362 scroll/client heights; Keep proportions and Resize are 44px high. Full landscape `object278-compact2/report.json` passes after the adjustment.

### Continuous mouse path recheck (2026-11-08)

The supported canvas scroll gesture positions the pointer without pressing a button and made genuine hover testing possible. Combining a held browser click with two such scrolls did not produce a held multi-waypoint stroke: the native observer recorded pointerdown and capture at the start, no pointermove with buttons=1, then pointerup at the original point; only the initial dot was painted. The controls evidently do not share a held-button state. The curve, lasso and modifier-drag gaps remain open; the hover findings must not be presented as a bent drag.

### PHOTO-MOBILE-284 — compact photo lab controls (fixed in build86)

At 320×568, production84 Photo lab is operable by mouse but several actual hit rectangles are smaller than the audit's 44×44 target: Open photo 72×36, close 30×36, look selector 104×36, histogram 42×30, six category tabs 91×32, adjustment selector 244×36, group reset 30×36, slider inputs 136×24, and footer buttons 66×40. The panel already fills the available height, uses two columns for sliders and has `overflow:hidden`; simply increasing minimum sizes would clip the preview, controls or footer. This needs a deliberate scrollable/sectioned mobile layout preserving the mini-preview, category navigation, crop interactions and commit/cancel reachability at portrait and landscape. Existing mouse and synthetic crop tests do not establish physical touch operation. Initial finding before the fix. Reproduce: open a picture, enable Advanced, Photo lab, and measure visible control rectangles at a 320×568 viewport.

Fix: compact Photo lab now scrolls with nonshrinking sections, a visible preview and 44px minimum controls; category tabs remain available in landscape. Live mouse applied a crop, dragged the preview, cancelled an adjustment and expanded the histogram. Full build86 layout matrix and focused target/reachability checks passed; build87 additionally retains the preview at 291×516, where native crop drag and the automated all-category target/reachability check passed. Physical touch remains outstanding.

SHIFT-286 recheck: concurrently holding a browser click with its Shift option and issuing a second browser drag did not carry Shift onto that drag. Observer logged the second pointerdown, every intermediate pointermove and pointerup with `shiftKey:false`; the unshifted sloped line is not a constrained-line result. Same-surface parallel actions therefore do not close the four modifier-drag gaps. See `test-results/audit-2026-11-05/fault-controls281/requests.jsonl`.
A second same-surface probe held Shift using the browser's documented timed key press while issuing the drag; the entire pointer sequence likewise reported `shiftKey:false`. Neither probe demonstrates a product Shift defect or a passing constrained gesture.

BLUR291: a native Windows drag produced a real pointerdown/move/up sequence in roughly 27ms, before the scheduled separate-window action could run; the attempted focus click also lacked current window geometry. No blur was observed and no interruption pass is claimed. The temporary window was closed with its document unmodified.

TAPER-193 precision stress: the alternating-diagonal prototype is not safe to ship as written. At an otherwise ordinary 20×10 profile offset to (9000,9000), 256 slices at ±720° flipped only 332–367 of the expected 516 quads and produced about 0.54–0.71% volume error despite `NoError`. Very thin profiles produced still larger errors. Fixed absolute vertex-matching tolerance and float32 precision are plausible contributors; this experiment does not establish the exact cause. Reproduce with `test-results/audit-2026-11-05/twist-precision-experiment.mjs`. A production solution must identify topology robustly across the allowed coordinate range and verify geometry independently; do not ship the prototype or relax the criterion.

TAPER-297 precision probe: raising the reverse-mapped vertex matching tolerance from 0.001 to 0.05 matched all 516 intended quads for the 20×10 profile at (9000,9000), reducing the tested ±720° errors below 0.05%. It remains unsafe for valid 0.0002-wide profiles: errors ranged from roughly 2% to 70% despite manifold status NoError. Wider tolerance alone is not a general fix; see `test-results/audit-2026-11-05/twist-precision-wide-tolerance.mjs`.

TAPER-298: a further same-ring-versus-cross-ring disambiguation still leaves about 2% error at ±90° and 16–17% at ±720° for the centred 0.0002×1 profile, even when all 516 alternating quads are identified; the far-offset thin profile is worse. A simple matching-tolerance change does not meet the unchanged 0.1% criterion. Prototype: `test-results/audit-2026-11-05/twist-precision-disambiguated.mjs`.

TAPER-299 precision-engine experiment (isolated copy, no production change): OpenCascade extrusion produced 3499.8865 mm³ for the 20×10×30, 90°, 0.5 taper case (expected 3500; ~0.0032% low) but required 16,650 triangles. At +720° the same profile took ~18 seconds and 433,914 triangles (taper 1: ~22 seconds and 504,754 triangles). More seriously, conversion to Manifold rejected the centred 0.0002×1 profile as non-manifold and produced 7–39% errors for the thin far-offset profile; its exact B-rep itself was inaccurate in one tapered direction. This is not a safe replacement across the allowed input space. See `test-results/audit-2026-11-05/brep-twist-thin.txt` and isolated `brep-twist-probe/`.

TAPER-300 centre-face prototype: replacing each side quad with four triangles around its bilinear centre removed the directional bias and met 0.1% for centred rectangular and 0.0002×1 thin profiles at ±720° using 256 subdivisions. It is not safe generally: a 20×10 profile offset to (9000,9000) still erred by 8.37% at ±720°, and a far-offset 0.0002-wide profile produced much larger errors due to precision loss. No production change. Reproducible scripts and outputs: `test-results/audit-2026-11-05/twist-centre-prototype.mjs`, `twist-centre-prototype.txt`, `twist-centre-precision.mjs`, `twist-centre-precision.txt`.

TAPER-301 swept-centre prototype projects each quad centre onto the true intermediate rotation/scale rather than its bilinear centre. Centred thin profiles stayed within 0.02% at ±720°, but the 20×10 profile at (9000,9000) still missed by 3.4–5.8%, and far-offset thin cases were much worse. It is not suitable for production. See `test-results/audit-2026-11-05/twist-swept-centre.mjs` and `.txt`.

TAPER-302 refinement check: increasing the swept-centre prototype from 512 to 2048 subdivisions did not converge for the 20×10 offset (9000,9000), ±720°, 0.5 taper case; errors remained 4.5–17.5%. Higher subdivision alone is not a reliable remedy once Float32 and face reconstruction errors accumulate. See `test-results/audit-2026-11-05/twist-swept-refinement.mjs` and `.txt`.

TAPER-303 centred-warp diagnostic: constructing the side faces around a local profile centre, then applying the rotating offset with Manifold `warpBatch` (Float64), produces internal volumes within 0.04% for the tested centred and far-offset profiles, including the 0.0002-wide one. Reconstructing a Manifold from `getMesh()` (Float32) reintroduces 3.4–5.8% error for the offset 20×10 profile at ±720°, and severe errors for the far-offset 0.0002-wide profile, despite `NoError`. This isolates a significant precision boundary at mesh extraction/re-import; fixing only the internal volume is insufficient for STL/render/boolean fidelity. No production changes. Reproduce using `test-results/audit-2026-11-05/twist-centred-warp.mjs` and its `.txt` output.

The precision limit is observable without the prototype: IEEE Float32 encodes both 9999.0 and 9999.0002 as 9999.0 (the next representable value is 9999.0009765625). The existing sketch validator accepts edges of 0.0002 mm and coordinates within ±10,000 mm. Therefore a world-coordinate Float32 mesh cannot retain every currently accepted edge; a robust fix needs an explicit precision-preserving representation or a clearly specified precision policy, and exported geometry must be checked independently of internal volume.

SKETCH-AREA-304: the existing validator computes area with world-coordinate products, so a 0.00010001×0.49995102 mm rectangle at (9001.462,9001.226) has stable twice-area 0.000100000203 but naive twice-area 0.000099986792, incorrectly below the 0.0001 threshold. A local-origin area calculation passed a focused red/green test, but was reverted: the same otherwise-valid shape extruded by Manifold has positive internal volume and `NoError`, while its exported Float32 vertices all have the same X coordinate, collapsing the solid. Shipping the validator change alone would replace a rejection with invalid output. The temporary `build88` contains that unshipped experiment and must not be treated as current. Diagnostic: `test-results/audit-2026-11-05/sketch-area304-diagnostic.mjs` and `.json`; red/green candidate reports are retained under `sketch-area304-*`. A precision-preserving end-to-end fix is needed.

CAD-PRECISION-305–307: an experimental guard first rejected every zero-area Float32 facet; full desktop/phone suites then exposed two regressions involving normal revolved and complex shell models. A revised guard compared the Float32 signed volume with the double-precision kernel volume (0.1% threshold): focused collapse/distortion cases, 296 painting checks and 127 desktop checks passed. A live build rejected the disposable narrow project with a clear message, and same-build saved projects before/after were exactly equal (`mouse/precision307-before2.retropaint`, `precision307-after2.retropaint`). However, the guard runs during project opening as well as export and therefore prevents users opening affected projects to repair them. It was reverted rather than narrowing access to existing work. Builds 89/90 and their partial regression reports are experimental, not current. The unchanged production source matches build87. A full solution must preserve editability and geometry fidelity; a print-only warning may mitigate export risk but would not by itself resolve the audit.
