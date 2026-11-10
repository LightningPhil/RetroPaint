# Live acceptance audit — 5 November 2026

This audit is in progress. The 349 original cases remain the specification; a
successful component check or a single happy path does not close a case's
failure branches and required variants.

Current accounting: **326 Pass, 21 Partial, 0 Not run, 2 Blocked**. The exact 960 x 640
birthday journey and all three prescribed 20mm complex-shell variants have
now passed. See [independent fixture verifier](verify-exact-fixtures.py) and
`test-results/audit-2026-11-05/mouse/exact-fixtures-verification.json`.
Historical progress notes below retain the earlier incomplete attempts.

The latest full regression passes **809 checks, zero failures and zero page
errors** (`all-eighty-seven-fixes/report.json`), including the Photo lab scroll/target changes. The production build also passes; a focused 291×516 target and reachability check passed separately.
Automated checks remain separate from acceptance-case accounting.

The latest production audit used http://127.0.0.1:56184/, selected by a loopback socket assigned by Windows. The temporary audit server and tab have been closed; other development servers and tabs were left alone. Native Windows mouse input and the connected Chrome tab were used for live interaction. Text entry and explicitly keyboard-oriented
cases also use keyboard input.

## Evidence and accounting

- [Fresh execution ledger](execution.json) starts all original cases at Not run.
  Partial means a named subset was exercised, not a pass.
- Native screenshots and accessibility observations are under
  `test-results/audit-2026-11-05/mouse/`. Connected browser screenshots are also
  retained in this chat's tool history.
- `baseline.retropaint` is an actual downloaded project containing the first
  blue marker and biro strokes. Later named brush PNG/project downloads retain
  subsequent test marks.
- The separate regression report at
  `test-results/audit-2026-11-05/regression/report.json` passed 583 checks:
  272 painting/geometry, 77 desktop layout, and 78 at each of three compact
  layouts. This is supplementary evidence, not 583 acceptance cases or physical
  touch/pen/screen-reader certification.
- The later full run at `test-results/audit-2026-11-05/all-seven-fixes/report.json`
  passes 593 checks: 274 painting, 79 desktop and 80 at each of three compact
  layouts. The polygon-summary wording fix followed this run; its production
  recheck is recorded separately. The production build is served on a second
  Windows-assigned loopback port, 54690. Build output stays under `test-results`
  and does not replace the repository's tracked `dist`.
- The extension file chooser API initially failed because file-URL access was disabled. The supported Windows native picker fallback subsequently succeeded, without changing that setting. Real mixed-project and photo-recipe round trips now have exact saved-data comparisons. The development tab's multiple-download prompt was left unchanged; serialized production downloads work. No browser permission or security setting was changed.


## Defects

**LIVE-001: Toolbox accessible name remains Basic mode after switching to
Advanced.** The drawer's accessible name was copied from its initial heading
once. The visible heading and mode switch updated, while the region retained
the initial name. `src/ui.ts` now names that drawer with `aria-labelledby`
pointing to `workspaceModeTitle`. Live Chrome observation confirmed both
Advanced → Basic and Basic → Advanced update the region name. Other drawer
names retain their existing behavior.

**LIVE-002: Circle exceeds its dragged bounds (PLAY-002).** A native drag from
page coordinates (680,145) to (750,210) created an approximately 191-pixel-wide
circle around the first point, clipped by the top of the paper and overlapping
the previous rectangle. `shapePoints` used the drag diagonal as a radius;
editable circles duplicated that formula in their analytic SVG. Both now use
the drag midpoint and half its smaller dimension, so forward and reversed
drags create the same inscribed circle. Cardinal samples are included exactly
to keep analytic curves and selectable bounds consistent. The original failing
live screenshot remains in this chat. Two new raster/vector regression checks
verify independent expected bounds and interior/exterior pixels. The first
after-run exposed a 0.112-pixel vector bounding error caused by missing cardinal
samples; this failure is retained in `circle-regression/report.json`. The
cardinal-sample fix passes both checks in `circle-focused/report.json`.

The original neon-preview regression fixtures now use non-degenerate diagonal
circle drags, retaining their preview-versus-commit assertions. Existing saved
path geometry is not reconstructed or altered by this authoring change.

**LIVE-003: Repeated wiki previews exhaust graphics contexts and erase CAD
picture previews.** All 70 runnable wiki examples rendered, but returning to
Paint produced empty CAD sheets. Independently decoded project downloads show
zero alpha in both CAD layer images while all 12 solid recipes remained. Each
temporary renderer disposed its resources without releasing its WebGL context.
Wiki, Code studio and temporary CAD picture renderers now explicitly release
the context. A focused reproduction failed at preview 16 before the fix and
passes 20 previews at all four layouts afterward. Repeating all 70 examples
live after the fix retains visible CAD pictures. Independently decoded before
and after downloads prove that model recipes, paint and annotations were not
changed. See `wiki-context-before`, `wiki-context-after`, and
`wiki-context-independent` under the audit results.

**LIVE-004: Linear tone-curve preset cannot be selected.** The live combobox
contained bare “Linear” text instead of an option because its markup had a
malformed closing tag. Correcting the option restores selection. All four
presets were exercised on each of RGB, Red, Green and Blue in the live UI.
The extended photo regression passes at all four layouts. Initial focused
test runs also exposed a pre-existing test setup dependency on Advanced mode;
those TypeErrors are harness failures, not extra application defects. The
independent setup is retained in `linear-preset-after-independent`.

**LIVE-005: Pasting copied editable pieces can insert a stale system image.**
Copying vectors updated only the internal clipboard; native paste prioritised
an older image on the system clipboard. Copy now publishes a PNG preview with
a session marker. Paste recognises the marker and retains editable originals;
unrelated image paste remains raster. A pending-write guard covers fast paste,
and image-only paste events can check the retained text marker. Duplicate no
longer replaces the clipboard, and raster copy clears stale object copies.
Native focused mouse Copy followed by keyboard paste visibly remains a Vector
piece; the Paste button does too. Regression checks cover pending writes,
combined and image-only clipboard events, duplication and external image paste
at all four layouts. Unfocused browser clipboard writes were also encountered
during automation; the final native check explicitly focuses Chrome.

**LIVE-006: Phone Photo lab loses the previously open Layers palette.** A real
pointer-down outside Layers dismissed it before Photo lab's click handler
captured its open state. The compact outside-dismiss handler now leaves the
Photo lab launcher to perform that transition. The existing regression now
sends the preceding pointer event: it failed at 390×844 and 844×390 before the
fix and passes all four layouts afterward. Native phone Layers → Photo lab →
Cancel visibly restores the open interactive palette.

**LIVE-007: Narrow phone tool targets shrink below 44 CSS pixels.** The original
layout check asserted height only. Seven forced columns yielded approximately
35×52 CSS-pixel buttons at the live 291-CSS-pixel viewport (320 physical pixels
with Chrome at 110% zoom); the 320-CSS-pixel regression also failed after adding
width to its assertion. Narrow portrait layouts now wrap tools using columns
with a 44-pixel minimum and an automatically sized toolbar row. The live targets
are approximately 51×52 there. All four focused layout checks pass. Landscape
already meets the width requirement and retains its existing layout. Real
touch input remains a separate untested capability.

**LIVE-008: A four-point polygon is labelled Rectangle in its summary.** Native
polygon input retained its correct polygon feature and non-rectangular points,
but the summary inferred shape from point count. It now uses the recorded
sketch kind. The original failure is retained in the production UI history;
the geometry was a valid 3.24 cm³ prism. This is a wording change, not a change
to saved outlines or solid geometry.

## Independently decoded downloads

[verify-exports.py](verify-exports.py) decodes the actual mouse-driven image,
project and STL downloads without importing application code. Its report is
`test-results/audit-2026-11-05/mouse/independent-verification.json`.

All six images decode at 960×640. Opaque PNG, BMP, WebP and TIFF agree exactly;
JPEG is lossy and GIF quantized. Project layer images decode independently.
The mixed project retains all eight primitive families, nine bodies, the
specified cube dimensions/placement/rotation/colour, and the independently
renamed and proportionally resized wedge copy.

The actual STL contains 18,268 triangles, closed consistently oriented edges,
outward triangle normals, dimensions 140×110×40 mm and volume
81,013.0804 mm³. Its minimum Z is zero. These independent measurements agree
with the Print panel. A 50 mm X build volume reports too small; restoring
200 mm reports that the model fits. Leaving cutaway inspection restored the
full displayed solids before export.

[verify-live-scenes.py](verify-live-scenes.py) independently checks the recovered
CAD preview alpha, unchanged recipes, two editable Castle labels, all 131 stamp
cells and object counts/kinds, and exact Spiro Reset preservation. Its report is
`test-results/audit-2026-11-05/mouse/live-scenes-verification.json`.

[verify-enhancement.py](verify-enhancement.py) decodes the actual completed
neural-job downloads at 1280×960 (2×) and 2560×1920 (4×). It confirms their
opaque alpha, that they differ from nearest-neighbour scaling, and byte-exact
source pixels plus unchanged editable project data across enhancement. This
uses opaque artwork; transparent-margin, seam-stress, CPU fallback and large
source variants remain incomplete. The saved `castle-gatehouse.scad` is the
actual `main.scad` download, including comments and `tower_height=33`.

## Execution cautions

The live ledger deliberately uses Partial for a happy path with required
branches or independent oracles still outstanding. Neither the 593 regression
checks nor the 131 stamp placements are 349 acceptance passes. The ten complete
journeys must also be executed as journeys, rather than assembled from
unrelated successful component checks.

Fast automation occasionally clicked before the CAD panel finished changing
layout. The retained workflows therefore observe the updated panel before the
next dependent native click. Invalid dimensions, missing piece selections,
busy clear animation and self-crossing outlines produce explicit rejections;
their corresponding valid paths are recorded separately.

## Coverage review

The original October catalogue predates several current features. See
[coverage gaps](COVERAGE-GAPS.md). Historical execution results are preserved;
they are not silently carried forward as fresh passes.

## Native reopen and further production checks

The Windows native file picker successfully reopened the actual saved labels/CAD project. Its downloaded re-save is whole-project JSON equal to the original (four layers, 12 CAD bodies, two Castle labels). See `test-results/audit-2026-11-05/mouse/native-reopen-verification.json`. Native picker fallback removes the earlier extension file-URL blocker for real file reopening; older blocked notes describe the first attempt. Production multiple-download permission is still pending.

The rebuilt production bundle visibly labels a four-point polygon correctly after LIVE-008. Further live checks include four Boolean operations (12/4/4/12 cm³), empty-intersection safe rejection, all 15 alignment axis/match combinations, line/radial pattern boundaries, and three-section smooth/ruled loft construction and history. These remain Partial where saved geometry, failure variants or independent oracles are incomplete.

**LIVE-009: Gradient presets have no accessible names.** Live AX showed four unnamed controls. `src/ui.ts` now supplies Sunset/Rainbow/Ocean/Candy gradient names and matching hover tooltips. Native live recheck exposes all four names; TypeScript passes. Full regression after nine fixes is in progress.

[verify-native-workflows.py](verify-native-workflows.py) independently validates actual native-picker imports, exact mixed/photo project round trips, atomic damaged-project rejection, all four bounded gradient exports, exact cancellation/Undo restoration, and 7000 versus 21000 tolerance-fill pixels with the disconnected island preserved.

The full run after all nine fixes passes **593 checks, zero failures and zero page errors**, at `test-results/audit-2026-11-05/all-nine-fixes/report.json`. TypeScript and production build pass. The reused production output folder is named `production-seven-fixes` but now contains all nine fixes.

JOURNEY-001 was executed continuously and verified: birthday background, stamps, hearts, greeting, a deliberate mistake recovered with Undo, and actual final PNG. Intermediate downloads retain each transition. Its final project equals the pre-mistake project exactly; PNG pixels equal the saved layer. This is the first complete fresh acceptance case; remaining partial component checks are not promoted.

**LIVE-010: CAD fit clips models after empty selection and in narrow perspective views.** Live orthographic Fit selected after Escape retained the previous tight span, clipping the model. It now falls back to visible model bounds when selection is empty or hidden. The independent projected-corner regression also caught perspective clipping at390x844: the fit now accounts for the effective field of view and viewport aspect using a bounding sphere. The corrected test fails before the fallback fix and passes allfourlayouts inbothprojections after both changes. Initial test setup/raster-timing diagnostic failures are retained separately. TypeScript passes; final full regression and production live recheck are in progress.

Chrome also now holds the long journey3Spiro project download behind the development origin multiple-download prompt. Its PNG exists, but its project does not. Permission for both localorigins has been requested; no download setting was changed. The draft remains in the app.

The final full run after LIVE-010 passes **597 checks, zero failures and zero page errors**, at `test-results/audit-2026-11-05/all-ten-fixes/report.json`. The rebuilt production live check now fits the complete visible model after clearing selection; see `mouse/live-010-fit-fallback-after.png`.

**LIVE-011: CAD layer rename and visibility discard the new value.** Native visibility clicks failed to hide the model. `pushHistory()` synchronously refreshes the layer controls, so reading their value afterwards reads the original value. Both handlers now capture the entered name/checked state before pushing history. The new regression fails on the old rename handler and passes four layouts after the fix, including Undo/Redo and unchanged solid recipes. TypeScript and production build pass; the full eleven-fix run is in progress.

The full eleven-fix regression passes **601 checks, zero failures and zero page errors** (`all-eleven-fixes/report.json`).

**LIVE-012: Retired canvas reports a false paused-workshop warning after reopen.** Reopening a healthy workshop surfaced the disposed canvas context-loss message. The context-loss handler now ignores disposed viewports. The new deterministic retired-canvas test fails before the guard and passes four layouts afterwards. TypeScript/build pass; the full twelve-fix run is in progress.

Saving one file per separate action delivered the production project, PNG and STL without changing browser permissions. The earlier blocked attempts remain recorded; the long development Spiro project still needs retry. [verify-desk-container.py](verify-desk-container.py) independently verifies the custom40x30x30deskcontainer delivery, JSON/pixel-exactrealreopen, unchangedvisiblecachedartoutsidecaptionbounds, outwardclosedSTL, analyticvolume andstraight/curved/junction/floor3mmsectionrays. See `mouse/desk-container-verification.json`. This does not replace the prescribedunscaled20mmcomplex-cap/oppositecap/one-third-overlap variants.

Accounting correction: JOURNEY-001 was briefly markedPass after its640x480version completed. The cataloguePLAYsetuprequires960x640, so it isPartial untiltheexactfixtureisrepeated. The640variantanditsindependentproofremainpreserved.


## Natural photo and file workflows

[Photo provenance](photo-provenance.json) records the public-domain natural
2100 x 1398 source. [Independent photo verifier](verify-natural-photo.py)
checks original retention, exact native project reopen and cancelled crop
inspection, separate caption sheet, 1800 x 1200 PNG and repeated output.
The print PDF contains one image pixel-exact to the PNG; cancelling a second
print leaves the whole project unchanged. JOURNEY-004 now passes. The earlier
synthetic photo checks did not substitute for this natural photograph.

[File and recovery verifier](verify-files-and-recovery.py) checks actual
format-aware, reserved-character and empty filenames, exact one-Undo keyboard
text recovery, chosen draft identity and exact recovery Undo/Redo. EDIT-024
and FILE-011 pass. Recovery and printing component cases remain Partial where
their exact MIX fixture or failure branches are still outstanding.


## Fixed-plane History correction and material checks

**LIVE-013:** Opening History converted a current fixed-plane pull of30mm
to a face-attached29.98mm feature. Legacy upgrade inference now requires the
old signed0.02mm contact offset and skips modern sketch metadata. The new
regression fails before the fix and passes afterwards; the older face-tool
upgrade regression still passes. Production live History shows30mm exactly.
[Independent pull verifier](verify-fixed-pulls.py) validates both prescribed
positive and negative STL endpoints,9000mm3volumes, closure and winding, saved
pulls and exact native negative-project reopen. SKETCH-007 now passes.

The full regression after thirteen fixes passes **606 checks, zero failures
and zero page errors** (`all-thirteen-fixes/report.json`). TypeScript and build
pass. The production output folder retains its historical seven-fixes name.

[Material verifier](verify-materials.py) checks separate blue/pink neon tints,
unchanged earlier pigment, actual translucent PNG halos, white-backed JPEG,
unchanged editable project and stationary gold glitter across waiting/zooming.
INK-007 and INK-008 now pass. Glitter opaque pixels and alpha are exact; low-alpha
Canvas compositing differs by at most1premultiplied channel level.


## Exact live-ink journey completed

The earlier640x480development draft could not download its long project, but
the full journey was repeated at960x640on production. All water, conveyor,
rainbow and Spiro transitions have actual project files, plus final PNG and
native project reopen. [Independent live-journey verifier](verify-live-journey.py)
confirms exact whole-project reopen, supported water/conveyor animation in
two decoded frames, and the explicit rainbow baking exception. The static
rainbow/Spiro region is pixel-exact to the saved raster across all exports.
JOURNEY-003 now passes. The continuous curved-path branch of INK-006 remains
Partial because the native mouse API supplies straight endpoint drags only.


## Full MIX fixture, external paste and LIVE-014

[MIX generator](prepare-mix-fixture.py) retains a genuine mouse-created dog
stamp and independently prepares the prescribed named four-layer960x640scene.
The first native export equals its independent reference pixel-for-pixel.
[MIX/paste verifier](verify-mix-and-paste.py) then validates genuine alpha at
100/50percent Character opacity, white-backed JPEG and unchanged source stacks.
LAYER-010 now passes on its full fixture, beyond the earlier neon variant.

Actual Windows Paint image copy and native Chrome Ctrl+V insert exactly the
source pixels at the dragged position. Other layers remain identical; one Undo
restores the full project. Browser-use virtual clipboard was empty, so the
system clipboard shortcut through native Chrome was required for this test.

**LIVE-014:** Text-only clipboard content could silently do nothing or reuse
an older in-app image through the fallback. Explicit non-image clipboard data
now reports guidance and returns without pasting stale artwork. Normal text
field paste remains unaffected. A new regression fails in all four layouts
before the fix and passes afterwards. Native production recheck displays the
guidance and preserves the whole MIX project. The Paste button also offered
its Ctrl/Cmd+V or Insert image fallback without altering the document. No
clipboard permission setting changed. FILE-004 now passes.

TypeScript and the fourteen-fix production build pass. The full regression
after fourteen fixes passes **610 checks, zero failures and zero page errors**
(`all-fourteen-fixes/report.json`).


## Keyboard navigation, shortcut scope and native drop limitation

ACCESS-005 and ACCESS-007 pass on Windows. All five actual tablists were
exercised, including all nine CAD tabs, Home/End/wrapping and the hidden Basic
Advanced-tab skip. Field arrows stayed in their editors. Paint and CAD modal
dialogs blocked background shortcuts. All named Paint tools and CAD W/E/R/F
reached their intended controls. Actual Ctrl+S files differ appropriately:
Paint PNG versus CAD editable project. [Keyboard preservation verifier](verify-keyboard-preservation.py)
checks those bytes and unchanged multilayer/model data.

FILE-005 is Blocked by native cross-application drag targeting. File Explorer
was opened to disposable fixtures and positioned beside Chrome; the tool
rejected the drag into another application. Same-window Chrome downloaded-file
row/icon drags did not establish a real Files drop. This is not evidence of an
application defect or a successful drop. Open/Insert/system-clipboard routes
are independently verified. No original file was moved or removed.


## Measured compact layouts and calibrated tracing

Chrome110% made earlier viewport overrides smaller in CSS pixels than their
requested dimensions. Corrected overrides were measured through the rendered
document:929×429→844×390,429×929→390×844,352×625→320×568.
The earlier runs remain useful smaller-layout observations, but are not proof
of the named exact CSS sizes. The automated suite uses exact CSS sizes.
Viewport overrides were reset after the native checks.

The photo/cropped CADMIX project has independent native reopen/edit/Undo and
PNG checks in verify-cadmix-photo.py. The orthographic mixed-photo variant and
longer compact history paging remain pending, so these cases stay Partial.
The calibrated guide tracing journey passes; verify-trace-plate.py checks the
actual closed STL against entered dimensions and the analytic hole volume.

LIVE015 labels the Inspect size report as world bounds. A scaled/rotated
noncube gives42.14×32.99×4mm, while a newly selected Cube gives20×20×20mm.
TypeScript/build and native production verification pass. The prior full
610-check regression predates this label-only fix.


## TIFF, layer boundaries, circular finishes and legacy migrations

FILE-010 and LAYER-012 pass with actual native import/save bytes checked by
verify-tiff-and-limits.py. RGB/RGBA/greyscale TIFFs are pixel exact, and nine
rejected variants leave the whole prior document exact. Sixteen sheets and
the exact64-million-pixel boundary disable Add with the correct explanation;
removal releases capacity. Three4096² sheets are accepted; four are blocked.

verify-circular-finishes.py checks actual outer-cylinder and hole entrance
finishes against analytic volumes and horizontal cross sections, including
unchanged bottom rims/bores. Whole circle references and native name persistence
are verified; additional nested references and dependent reselection remain.

verify-legacy-imports.py verifies producer hashes and current native migration
roundtrips for authentic versions1/2/9. Versions1/2 render pixel-exactly;
version9 has three one-level red preview differences after canvas decoding.
Its rebuilt STL is byte-identical to the historical cube. Authentic versions
3–8 remain unavailable; historical status is not reused as a fresh pass.

LIVE016 fixes stale Print validation: geometry/history, relevant selection,
scope and bed-setting changes clear old size/fit output and require a fresh
check. Starting a check also clears old success before a possible failure.
The corrected regression fails before the fix and passes allfour layouts
after it; native production bed/geometry changes were verified. The first
test attempt used an invalid callback and is retained as a test diagnostic.
TypeScript/build and the full sixteen-fix regression pass614checks with
zero failures and zero page errors (`all-sixteen-fixes/report.json`).


COLOUR-015 and COLOUR-017 pass: verify-colour-boundaries.py independently checks native steep/adjacent curve outputs, unchanged alpha/source and exact pure-black/white composites.


VECTOR-004/015/018 pass. verify-vector-transforms.py checks retained text/raster sources and independent transform/render oracles; verify-vector-roundtrip.py checks fresh composition, targeted edits of each kind and atomic malformed-object rejection. Optional static wet/liveSize importer normalization is recorded explicitly.


JOURNEY-005 passes. verify-comic-journey.py checks actual duplicate independence, native reopen/PNG, exact wrong-piece Undo and targeted second-label revision. The completed native scene is retained as comic-revised-live.png.


JOURNEY-006 passes with a reproducible synthetic photographic restoration source. verify-restoration-journey.py checks the separate480×320ESRGAN output, unchanged editable restoration, exact original reset and exact Undo.


FEATURE-024/028 pass. verify-copied-constrained-forms.py checks both saved-source/current-drawing copy independence, profile placement, driving dimension/relation persistence, rejected conflict, model-exact Undo/Redo/fresh reopen and four closed analytic STL oracles (6750/8380/8250/2400mm³).


LIVE017 clips both CAD picture-helper canvases to the shared document crop.
Camera coordinates and geometry remain in full-document coordinates. The
targeted test fails before and passes after at all four layouts, checking
transparent outside pixels and independently expected half/quarter opacity.
Native cropped photo/annotation and half-opacity delivery were verified.
Full seventeen-fix regression:618 passed,0 failed,0 page errors.

FILE-022 passes actual native Chrome Duplicate, different edits and separate
reload/resume files (verify-tab-isolation.py). DELIVER-010 and JOURNEY-010 pass
the actual delivery/reopening set (verify-delivery-set.py). CAD orbit, wheel,
Fit and Pin are covered; native right-drag pan is unavailable and is not claimed.


## Explicit failure and resource controls

fault-server.py serves production bytes on a random loopback origin with
visible acceptance controls. Original production files remain unchanged.
Seams wrap standard browser APIs, never inspect or mutate application state:
project encoder gate/null, disposable storage denial, one stalled CAD request,
worker WebGL denial and request metadata/canvas-call counters. These runs are
labelled controlled failures, distinct from normal production mouse runs.

verify-fault-files.py checks actual native snapshot/reopen, later working edit,
failure retries and source preservation. The unshortened CAD45s timeout and
successful restarted worker were observed. Obsolete-message injection remains.

LIVE018 corrects a null PNG encoder's misleading “Choose PNG” message. A
targeted independent failure/retry test fails before and passes after; native
fixed feedback/retry, TypeScript/build and all619 regression checks pass.


verify-enhancement-boundaries.py decodes actual native32×32CPU/GPUESRGAN
copies pixel-exact, plus8192²/16384²transparent streamedPNGs with every CRC,
zlib completion and row checked. Source projects remain whole-document exact.
The large transparent path does not prove near-limit opaque neural inference.

verify-moving-material.py checks native fixed-time transforms, material period,
alpha clipping on an explicitly prepared clear-backing fixture, unchanged
neighbouring live artwork and animation after clock resume. The native Paste
failure was investigated: a focused regression passes existing fallback behavior;
no speculative clipboard source change was made. The four new layout checks
supplement the619-check full eighteen-fix regression.

verify-local-requests.py checks application-window/worker/server request capture,
deferred local models, recoverable503, eight cached304model resources, saved
Photo/painting/CAD/enhancement files and no external application requests.
Browser extensions and host traffic are outside this case's stated boundary.


## Native folder fallback and current desktop blocker

CODE-007 now passes through the Windows folder chooser, without enabling
extension file-URL access. verify-code-folder.py checks every source/dependency
byte, independent entry/helper selection, same-path replacement, exact native
reopen, targeted Update/Undo/Redo, nine closed STL outputs and unchanged models.
The accepted fourteen-file set includes custom Courier, nested modules, SVG,
STL and a heightmap; MCAD loads from the local bundled library. Independent
TrueType outlines use fontTools4.68.0 installed only in ignored audit tooling.

Windows switched to its secure lock screen while opening the next folder
chooser. Live native input requires the owner to unlock Windows; no credential
entry or security bypass is attempted. File-count/byte-boundary fixtures under
fixtures/code-limits are prepared, not executed. The current browser/file-picker
state is retained for continuation. The audit is not complete; Partial statuses
still mean required criteria or variants remain unverified.


Windows became accessible again and native testing resumed. The temporary
lock-screen blocker above is historical, not a current stop.


## LIVE-019: File chooser cancellation closes Code studio

The native file input's bubbling cancel event reached the studio's dialog
cancel listener, which treated it as Escape on the dialog and closed it.
Reopening Edit selected then replaced the unapplied draft with saved source.
Native29mm helper edits visibly reverted to28mm after cancelling the chooser.
The listener now closes only when event.target is the dialog itself.

The targeted test fails before and passes after at all four layouts. Native
folder, standalone source and additional-file chooser cancellation now retains
the29mm draft and11file project; Save .scad retains exact29mm helper bytes.
Explicit Escape on the studio still closes it. Rejected2,000,001byte source,
20,000,001byte dependency, oversized combined dependencies and2,001file folder
retain the draft and allow a valid29mm retry. The applied document remains
whole-JSON exact before/after. Accepted maxima are being checked separately.

Full nineteen-fix regression:276painting +87desktop +3×88compact =627passes,
zero failures and zero page errors. TypeScript and production build pass.


## Exact Code import boundaries and recovery

Native Windows pickers accepted exactly2,000files,20,000,000dependency bytes
and2,000,000source bytes. Counts/sizes one above the limits and combined
over-budget additions reject without losing the draft. Unicode filename and
source export bytes are exact. The complete37MB,12-model project was actually
reopened and saved again: whole JSON is identical. Allthree boundary models
rebuilt from their reopened sources. Four selected STLs have independently
verified12-triangle closed outward meshes and exact24/105mm³ volumes.
See [verifier](verify-code-limits.py) and
`test-results/audit-2026-11-05/mouse/code-limits-verification.json`.

Native F5/Ctrl+Enter, error-line selection, bounded echo output, pure2D/empty
geometry errors, automatic preview, CPU-render cancellation, close/reopen,
replacement source and failed import while rendering were exercised. The
whole applied document remains unchanged after these draft-only operations.
The screenshot/DOM evidence is retained. CODE-001/006/008/009 now pass;
CODE-010 remains Partial pending adversarial late-message delivery. The
supplemental ledger has5Pass/17Partial; the main349-case counts are unchanged.
The source-length string returned by the observation transport was truncated
in one record; the in-page length computation and independent downloaded
bytes both establish exactly2,000,000, without relying on that truncated string.


## LIVE-020: Signed exponent parameter appears blank

OpenSCAD accepts `width = +1e1`; HTML number inputs reject the leading plus.
The live model rendered10mm while its width control was blank. Parameter
controls now display the parsed numeric value, preserving the original source
notation until an intentional edit. Four layout checks fail before and pass
after. Native production shows10, then a real parameter edit replaces only
that literal; comments, strings, repeated names, expressions and module-local
constants remain exact. Empty/non-finite entries preserve valid source.

Native Update of a scaled, rotated, placed and purple code model retains ID,
name, colour and all transforms. One-step Undo/Redo restores exact source and
geometry. Native Join/Cut retains both original code recipes, transforms and
all neighbouring photo/paint/model data. Actual full project reopen is exact.
Independent binary STL checks verify375/3600/8592/2592mm³, closed outward
meshes, bounds and removed/retained-point ray probes. See
[independent verifier](verify-code-workshop.py).

The full twenty-fix suite passes276painting +88desktop +3×89compact =631,
zero failures and zero page errors. TypeScript and production build pass.
Supplemental CODE-003/004/012 now pass:8Pass and14Partial overall.

## Obsolete worker handlers and current requests

Native visible local harness stalls two actual precision jobs; production45s timers measured45.012751/45.014281seconds. Old terminated CAD message/error handlers explicitly invoked with current new requestID26; busy job remains intact and next successful CheckPrint returns10x60x6mm/2.59cm^3/20triangles. Old OpenSCAD message/error handlers invoked during different active fib(44)job leave new source/Rendering/Adddisabled intact; cancel and valid11x7x3retry succeeds. Downloaded whole project exact before/after. Independent verify-stale-workers.py passes. Earlier no-effect attempts while harness was outside workshop isolation were corrected by relocating only labelled harness controls into visible workshop/dialog; successful deliveries are logged.

FEATURE-029 and CODE-010 now pass; supplemental9Pass/13Partial.

## Legacy script format round trip

Explicit synthetic v12 compatibility fixture uses genuine native2x3x4mesh and retrocad-1 source; not claimed as historical download. Actual native Open preserves metadata and independently decoded image pixels (browser losslessly re-encodes Pillow PNG). Preview leaves applied legacy source/version12; intentional Update changes only script metadata toOpenSCAD/version13, exact mesh/ID/transforms preserved. One-step Undo restoresv12; Redo and actual whole native project reopen exactv13. Existing native dependency/entry/helper/applied-vs-draft round trips also verified. verify-code-legacy.py passes.

CODE-011 now passes; supplemental10Pass/12Partial.

## LIVE-021: Main tool selection lacks accessible state

Main tool buttons changed only CSS active styling and exposed no selected state. They now expose aria-pressed and a visible tick, including independent symmetry mode state. Four targeted layout checks fail before and pass after; full276painting +89desktop +3x90compact =635passes, zero failures/errors. Production native and all compact UI checks confirm state and legible marker. Actual CSS breakpoint sizes were measured; earlier one-pixel-smaller attempts are retained, then exact390x844/844x390 reruns passed.

START-001/002/003/004 now pass after independently checked actual stroke snapshots, whole-document Undo/Redo, native toolbox dismissal, all tools, settings retention and real file reopening. See [pixel verifier](verify-paint-history.py). Main ledger41Pass/304Partial/4Blocked; other variants remain in progress.

## LIVE-022: An untouched resumed draft disappears on another reload

Loading a draft forks a fresh working ID for tab isolation. Resume marked that
ID saved without writing a record under it, so a second reload offered no
Resume, even after four idle seconds. A copy is now atomically persisted under
the new ID before Draft restored is reported. A post-load open/revision guard
prevents the awaited write from changing a newer document's UI state.

The corrected-setup red regression restores once then fails on cycle2; green
passes three exact cycles. The first green attempt exposed misuse of the
pre-load revision guard, which is invalidated by its own successful load; the
post-load guard fixes that. Native production reproduces the old second-reload
failure and now passes three untouched reload/resumes. Genuine native Chrome
Duplicate was rechecked: independent Blue/Green rectangles reload to each
own whole document exactly. See [mode/recovery oracle](verify-modes-recovery.py)
and [post-fix tab oracle](verify-postfix-tab-isolation.py).

Full final22-fix regression:276painting +89desktop +3×90compact +1normal-app
three-cycle recovery check =636passes, zero failures/page errors. TypeScript
and production build pass. Earlier interrupted and setup/guard failures remain
in their own evidence folders; only `all-twenty-two-fixes-final` is current.

START-005/006/007/009 now pass after complete native Clear, mode and help
variants. Main45Pass/300Partial/4Blocked. FILE-019 remains Partial for its
unsettled gesture/text/photo checkpoint branches; this fix is not a blanket
recovery acceptance pass. A raster `wet:false` field is omitted on initial
native file open; all other metadata/pixels are exact, and subsequent recovery
cycles compare entire JSON without normalization.

## Native language and target identification

CODE-005 now passes with [per-operation analytic/font/STL oracle](verify-language-operations.py); supplemental11Pass/11Partial. START-008 passes with [target and real-key oracle](verify-targets.py); main46Pass/299Partial/4Blocked. All40 earlier independent saved-output verifiers reran successfully after22fixes; the two new oracles also pass.

## Undoing a mixed editable draft restore

FILE-021 passes: native one-step Undo/Redo restores entire distinctMIX/code/photo/live/vector documents exactly. The older originalGreen stored entry remains exact afterUndo; selecting it again does not recover an overwritten current copy. [Independent oracle](verify-restore-mix.py) also checks the new70x50Redpath and all8draft cards across3pages. Main47Pass/298Partial/4Blocked. InitialBackdropactivation omits optionalclip:null; this no-clip normalization is explicit in [target oracle](verify-targets.py), with wholeJSON comparisons thereafter unchanged.

## LIVE-023: explain Undo while an effect runs

Toolbar Undo previously returned silently during Clear. It now displays “Let the current effect finish first.” without interrupting the effect or adding a history step. The actual native message was visible746ms after starting Clear. One subsequent Undo restored the entire pre-Clear document and Redo cleared it. The four-layout regression failed before the fix and passes after it; the full23-fix suite passes640 checks with zero failures or page errors. TypeScript and production build pass. `verify-prerequisites.py` independently verifies disabled-action attempts, prerequisites, pointer-coordinate stroke geometry, merge pixels and exact saved history. All ten START cases are now Pass.

## All ten native code starters

Each starter and one controlled numeric variation was added, saved, exported as a selected STL, undone and redone through the live UI. Twenty independent mesh oracles verify units, expected bounds, analytic volumes where applicable, feature probes, closed paired edges, connectedness and outward unit normals. The actual downloaded ten-model project was reopened through the native picker. Editable data, source, identities and transforms remain exact. Recreated CAD thumbnails show at most two pixels of one-level RGB rounding; the verifier reports these separately. `verify-starter-variations.py` passes. All twelve supplemental CODE cases now pass; six LABEL and four WIKI cases remain Partial.

## LIVE-024: narrow wiki reading column

A long related-topic button forced horizontal article scrolling at320px. Related buttons now wrap inside the reading column. A new regression visits all110articles atfourlayouts: narrowphone fails before, allfour pass after. TypeScript/build pass; full24-fix run passes644checks withzero failures/pageerrors. Native660section jumps cover110articles atbothlevels onallthree compact sizes. Real delayedMCADcatalogue load preserves topic/focus/scroll. Normal anddeniedclipboard nativecopy/paste preserve exact commentedsource; whole savedproject before/after bytesidentical. `verify-wiki-reading.py` passes. Supplemental accounting:15Pass/7Partial (sixLABEL plusWIKI003).

## All70wiki guided exercises

All70originalexamples andtheirprintedguidedchanges were run through thelivewiki/CodeStudio UI. Actual supplied helper/SVG/DAT assets were imported withthenativefolderpicker. StandardWorker input/output observation retains genuine engineSTLs. `verify-wiki-guides.py` checks139successfulmeshes plusoneexpectedassertion against independent recipe geometry; zero-area rotation-axis triangles inrawOpenSCADoutput are explicitlyreported andomitted, matching importer cleanup. Additionalminimumclamp,negative-widthfailure/recovery,wallrestore,repeatedsame-seedSTL andactive-previewcancel/retry pass. Allisolatedpreviews preserve theirprecedingdraft; wholeactualsavedproject before/afterbyteidentical. Supplemental accounting:16Pass/6Partial, withonlyLABEL casesremaining.

## Six editable-label workflows complete

`verify-labels.py` passes59actual saved/exportedartifacts,12native drags and8rendered arrow-attachment states. Blank/cancel/wrapping were exercised inbothdrawingpreferences. IndependentlyverifiedCourierNewadvances,autosize,styles,worldtransforms,tip/boxindependence,offsheets,zoom,resize/rotate,copyindependence andallhistory surviveactualnativeprojectreopen. EacharrowPNGhasfivecomputedsegmentpixelprobes. BrowserkeyboardCtrlV deliversbothmarker/PNG andcreatesaneditablecopy; explicitPastealso passes. Windows-level keyinjection deliveredstaleOStext andwasnotcredited; diagnostic trace retained. CADselectioncorrectlyopensworkshop withTextinert; PaintreturnsPaper, andAnnotationscanbeselectedexplicitly. All22supplemental cases nowPass. Main349-caseledger remains48Pass/297Partial/4Blocked.

## LIVE-025: readable recovery failures and focused retry

The missing-draft toast was hidden behind the blurred dialog, and disabling the clicked card lost its focus. Recent drafts now displays errors inside the dialog with rolealert and reenables/refocuses the card. Compact error content stays inside a scrollable bounded dialog. Four-layout regression fails before and passes after for actual missing, truncatedJSON and corruptPNG records in an isolated test store. Native controlled standardIndexedDBresult failures preserve the whole five-layer MIX; successful retry restores the original store entry exactly, with exactUndo/Redo. `verify-recovery-failures.py` passes. An introduced UTF8editing error was corrected; the intermediatefullrun was interrupted and the final648check suite passes withzero failures/pageerrors. TypeScript/build pass. Main49Pass/296Partial/4Blocked; supplemental22Pass.

## Recovery checkpoints exclude unfinished work

`verify-unsettled-drafts.py` passes native committed-edit + unfinishedtext/Photo sessions, with automaticdraftsaving pending beyond36/38seconds. Refresh/Resume restores exact five-layer settled copies, excluding unappliedtext, brightness35 andpending layernames. The documentedbrowserTabclick duration also holds a realmouse press: after3866ms, Draftpending andpointerdown remain; actualnavigation finishes before7500msrelease. Resumeexactcheckpoint. FILE019 nowPass. Thisnewlyconfirmedcapability reopens ACCESS012fromBlocked toPartial forinterruption variants; main50Pass/296Partial/3Blocked.

## LIVE-026: interrupted 3D handle remains busy

Physical Chrome-omnibox capture loss while a real7500ms handle press was pending left CAD Undo disabled until the delayed release. CAD now ends TransformControls dragging and the document gesture on lost capture, pointer cancellation and window blur, and removes its blur listener on disposal. Correctly prepared four-layout tests fail before and pass after; native fixed Undo becomes enabled at879ms before the scheduled release. The following native move is exactly8mm alongX; model recipes Undo exactly, whole Redo exact, all paint untouched. Regenerated GPU thumbnails across a build reload differ at6pixels by oneRGBlevel, explicitly reported separately. The initial full652check run exposed preexisting non-bubbling synthetic pointer contamination in the new component check; reopening its control listeners and bubbling its own events resolves that test isolation problem. Final four-layout run375checks passes without errors; painting276 and normal-app recovery also passed. See verify-interruptions.py.

## LIVE-027: a live outline preview redraws but stays one colour

A native mixed-layer polyline preview produced zero changed screenshot pixels even while its counters showed continuous redraws. Raster brush outlines now preview conveyor ink with the same live stroke renderer and clock as committed strokes. A deterministic exactRed/Yellow test fails before and passes after without changing project data. Native repeated preview changes12685pixels, while the committed live stroke changes3255. Cancellation and final3px stroke history/reopen are independently checked by verify-redraw.py. ACCESS013 nowPass; main51Pass/295Partial/3Blocked. The final27-fix full regression passes653checks (277painting,93desktop,3x94compact,1normal-app recovery), zero failures/pageerrors. TypeScript and production build pass. The earlier648check25-fix result remains historical.

Native multipoint-path investigation also attempted a held click with native zero/one-pixel scroll and browser scrolling. Zero is rejected, native positive scroll loses capture, and browser scroll queues after release. These traces do not close curved-path or irregular-lasso cases. Real window blur/pointercancel remains distinct from observed capture loss.

## Desk preferences across reload and storage failure

ACCESS008 nowPass: allfour themes persist through realreloads, sixdecodedPNGexports equal independent source composition, actualprojects andnativeNightreopen exact. StandardStorageAPI unknown-value anddeniedread/write failures fallbackMint whileLilacremainsusable for thevisit; actualBlackstrokes andUndo/Redo workafterbothfaults. OriginalMintrestored. verify-desk-preferences.py passes. Main52Pass/294Partial/3Blocked.

ViewFullScreen API entry/exit events anddenial were observed; a deniedrequest leavescompleteMIX andsubsequenteditingintact. NativeChrome capture/controlledviewport bounds didnotexpand, soACCESS017 remainsPartial for physicalfull-screenlayout/browserexit. No falsefull-screen claim is inferredfromtheAPIeventalone.

## Reduced motion preserves intentional artwork

ACCESS010 nowPass. NativeMIX, realpreferencecheckbox anddrawerworkflow: toolicontransition0s underreducedmotion,0.16safterrestore. Liveinkcontinueschanging; motorAuto draws46750newsourcepixels insidethering. Frozen-clockactualPNGexports before/afterpreference pixelidentical. FullUndo/Redo/nativeprojectReopenexact; allotherlayers andexistinglivedefinitions preserved. verify-reduced-motion.py passes. Main53Pass/293Partial/3Blocked.

## Sound controls stay coherent and silent when required

ACCESS009 nowPass. Nativebutton/M/preferences/marker workflows, actualstandardWebAudio observations: mastergain0/.45/1, no sourcesstart duringmuted/zero attempts, paintingoff suppressesdrawingbutkeepsexplicitfeedback. Muted45/paintingoff andenabled0/paintingon bothpersistthroughrealreloads; speaker/M toggles agreewithallcontrols. Originalsoundsettings andwholepainting restoredexact. verify-sound-controls.py passes. This verifiesbrowseraudiograph behavior, notphysicalspeaker/hearing. Main54Pass/292Partial/3Blocked.

## Every stamp in both rendering modes

PLAY014 nowPass. All131editable stamps retainexactproject/PNGdata throughactualnativeopening. All131alsochosenandplaced throughrealRasterUI on8fresh960x640sheets; catalogue/publiclabels, actualmouseevents, sourcepixels, unchangedoutsidecells andlast-stampUndo/Redo checked. All8rasterprojects nativelyreopened andexportedpixel-exact. Glyphclassificationagainstthepreservedknowneditableart catcheswrong/repeatedcategoryitems ormissingglyphboxes. Fivegeometricshapes usecategoricalsilhouettes normalized independently inwidth/height becauseexistingraster/editableheartaspects differ; no equalphysicalgeometryclaim. Initialaspect-preservingclassifierfailure retained. verify-stamp-inventory.py passes.

A30secondCUAbatchtimeout resetthebrowserconnection midfirstRasterAnimalsattempt. Thatpartialwaspreservedasdiagnostic andexcluded. Anewforegroundaudit tab andsmallercheckpointedbatches completedtheinventory. NewtabID676304713; previous676304690waspreserved, notsilentlydiscarded. Nativepicker nowrequiresphysicalWindowsclick afterbrowserreconnection; browserlocator/AXclickfocusedbuttonwithoutshowingchooser. Main55Pass/291Partial/3Blocked; source/build still27fixes, full653checks green.

## LIVE-028: stamp flip state is not announced

The visible active highlight forFlip sideways/Upsidedown hadnoaria-pressedstate. Bothnowexposetheactualbooleanstate. Nativebeforeevidence recordsactive+null, andthefixedUI checksallfourflipcombinations againstthehighlight. Thisisa two-attribute reversibleUIchange; verificationistargetedrealUI ratherthanamirroringunitcheck. TypeScript/build andfull653checkregression passwithoutfailures/pageerrors. Stamptransform/hoverbranches remaininprogress.

## Stamp preview and transform completion

PLAY-015 and PLAY-016 now pass in both Raster and Editable modes. All sixteen
transform placements retain their exact committed orientation through Undo/Redo
and native project reopen. Hover-only keyboard saves exclude the ghost from
both projects and PNGs. Independent verifiers retain measurements and hashes.
The transform image comparison was corrected to enlarge small reference features;
its initial failed attempts are retained. Exact editable angles come from the
saved objects; rendered template fitting is an orientation/range check, because
font hinting changes with glyph size.

## LIVE-029: enlarged pixel grid and ruler rendering

PIXEL32x32 at1455% exposed invisible grid and illegible enlarged ruler numbers (LIVE-029). Guides now use a viewport-bounded screen-resolution surface, independent of source pixels. Native View toggles,100%/Fit/46548%maximum,150x100CSS pan,nearest-neighbour64x48source resize, exact Undo/Redo and native reopen exercised. All five required CSS layouts checked, including compact zooms above/below6px threshold. Independent screenshot measurements align white-cell grid boundaries to known source coordinates; every actual PNG/source pixel and whole view-only project exact. Component red/green also checks crop, panning,18screen-pixel rulers, glyph legibility and bounded extreme-zoom memory. Initial transient-toast/drawer screenshots retained; settled replacement evidence excludes known toolbar occlusions. Pillow exact halfway resize ties differ from Canvas: independent nearest-neighbour math accepts only equally distant source pixels at exact ties; no blended colours allowed.

Additional actual Space-drag probe: browser-only parallel drag queues until key release (diagnostic retained, resulting test stroke exactly undone). Holding Space via browser key API while native Windows mouse drags works: public moving-paper state observed, native drag completes within305ms of6000ms hold, paper moves-45.4545/+45.4545CSS, whole project exact before/after. Exact PATCH-coordinate, Ctrl-wheel/dialog and four-layout combined workflow remain outstanding; case stays Partial.

The initial full29-fix run was reloaded by source edits while running; its results
are retained separately. The final full run hashes the completed sources and passes
654 checks without page errors. TypeScript and production build pass.

## LIVE-030 to LIVE-032: Spiro drop safety and keyboard selection

Native fresh960x640White/Blueink: sixgear taps, invalid/valid geardrops, interrupted gearcapture andkeyboardselection preserve wholeproject andblankPNGexact throughnative precondition reopening. Opening/closingkit andreturningBrushes producesnoart. Additional offered-hole/drive variants remain under the shared Spiro matrix; case stays Partial.

LIVE-030 actual off-paperOrangegear drop wrongly replacedRed. Firstposguardfix stillfailed becausepointercapture producesaClickafterdrop. Completefix ignorespointer-originClick becausepointerupalreadyhandlesit, retainingkeyboard/ATClick. Liveoff-paper andon-paper/outsideRingdrops retainRed; validcentredrop selectsOrange; all6taps work; capturelossduring6sheldpress clearsghostandretainsOrange before/afterrelease. Four-layout regression alsoincludes thecapturedClicksequence. Alloffered-hole/pathvariants stillpending.

LIVE-031 sixSpirogearbuttons exposedselectedclassbutnoaria-pressed. Allsixnowannouncecorrecttrue/false states, verifiedagainstactualpickedhighlightfor6nativetaps. Actualscreen-readerhardware remainsunavailable; case remainsPartial.

LIVE-032 nativeSpaceonfocusedOrangegear leftPinkselected becausepaperpan swallowedthebuttonkey; Enterworked. Spacepan nowexcludesbuttons/links/summary/tabsandtyping. NativeSpace selectsOrange,EnterselectsRed; focusedcanvasSpace+nativeWindowsdrag stillmovespaper-45.4545/+45.4545CSS during6skeyholdwithoutchangingwholeprojectorPNG. Four-layout red/green checks preservebuttondefaultactivation andcanvaspan.

The incomplete position-only fix and its successful but insufficient synthetic
check are retained. Native input exposed the extra captured Click; the regression
now includes that event. The first successful event helper captured an old REPL
object after reassignment, so its JSON lacked the three successful drag records;
that diagnostic is retained and the three actual drags were repeated, saving to
`spiro-drop-fixed32.json` explicitly. `verify-spiro-drop.py` passes.

The earlier31-fix full run reloaded during later edits and is historical only.
The stable32-fix full run hashes the final sources and passes662checks with zero
failures/pageerrors. TypeScript/build pass. Spiro acceptance cases remainPartial
until the required hole/drawing variants are verified.

## LIVE-033: named gears lose offered drawing holes

LIVE-033 namedgearholes were overwritten bycustom-teethformula: purple5ratherthan6,red5ratherthan7,yellow6ratherthan8,green7ratherthan8,orange8ratherthan10. Fixedexactpresetcounts while retainingcustomteethderivedholes. IndependentnativebeforeOrange screenshotcounts8; geometryregressionchecksall44offeredholepenpositions aredistinct. Liveindividual-holematrixusesactualscreenshot-measuredpositions,eachmanualgesturewholeUndo/Redo,sixseparatebankprojectsandnativePNG/projectreopens. Progressandper-bankanalyticverifiersareexplicitlyrecorded; remainingstator/outer/drive/mixed-vectorvariants keepSpirocasesPartial.

The browser screenshot API returns JPEG bytes, even where older evidence files
use a.png suffix. Independent image readers detect the format. The new hole
locator uses measured luminance above the gear interior to handle chroma
subsampling; the original exact-white classifier attempt is retained in tool
history. Native old-orange measurement finds8holes. Each completed bank must
pass its independent curve, history, original-raster, PNG-support and native
round-trip checks.

The curve verifier uses delivered pointer coordinates, which Chrome quantizes
to float32, rather than host-double proposals. Its initial tiny endpoint
mismatch is retained. The independent PNG support mask includes round caps;
Pillow line endpoints alone are flat. No actual failed artwork was discarded.

## LIVE-034 / LIVE-035: exact radius typing and retained motor drawings

LIVE-034 fixed accepted fractional radii rounded in the input, invalid step=1, and keystroke-by-keystroke rewriting that turned native typing 1.5 into 51. Input now permits fractions and preserves accepted numeric text/caret. Actual native typing checks .1→.5, .5, 1, 1.5, 213.33333333333334, 1e7 and 1e8→1e7; all fields valid; Reset returns 640/3. Early fill-only inspection and failed first-fix native typing evidence are retained. Handle/move and remaining shared matrix still require completion.

All six independent manual hole-bank reports now Pass: 44 distinct real mouse drawings; 162 actual project/PNG downloads; exact whole per-hole Undo/Redo and six native project/PNG round trips. Scope Vector/Manual/Ring/outer96 only. Aggregate spiro-all-holes-verification.json records this scope; other stator/outer/drive combinations remain in progress.

LIVE-035 fixed Reset leaving a visible partial vector preview absent from project/PNG, and no motor-running indicator. Motor now exposes pressed Stop drawing; Stop, Reset, switching to Manual and natural completion share one commit path. Real Stop, Reset, custom180/53 Reset, natural96/36 completion and Manual switch each add one analytic editable curve; whole Undo/Redo and native final project/PNG reopen are exact. Original raster remains white. Canvas-key cancellation has synthetic coverage, but two native omnibox attempts did not deliver capture loss during the motor; recorded as unproved rather than Pass. Early numeric fill attempts did not commit change; native typing did, and custom settings are separately recorded. Shared matrix and other-workflow branch remain pending.

The first 35-fix full run was interrupted by the fractional-typing edit and is historical. The final stable run passed672checks with source hashes verified. The targeted combined filter attempt selected zero checks (literal substring matching); separate targeted runs passed. The first motor layout fixture omitted Advanced mode and was corrected before its four-layout pass. The independent motor oracle initially assumed hole0; actual initial geometry uniquely identifies default hole2. Curve-fit checks validate all saved points against that offered hole. A strict monotonic-time assumption also found a tiny initial frame-clock backtrack; no criterion requires monotonic sampling, and all saved points remain on the configured curve.

## LIVE-036: inner-tooth bounds and completed pairwise matrix

Completed live 30-combination gear×outer plan across all six gears, five named outer counts, four stators, Manual/Auto and Raster/Vector. Independent verification finds no missing pair among all five factors, checks every stored vector point analytically, raster/project/export agreement, full expected PNG curve support, whole per-case Undo/Redo and six native project/PNG reopens. 162 actual downloads retained. Together with all44 individual-hole drawings and valid/rejected/capture-loss gear-drop evidence, this completes PLAY-019 required options and branches. This is pairwise coverage, not full Cartesian coverage.

LIVE-036: accepted171/172inner teeth atouter180 were marked invalid byfixedHTMLmax170. Max now followsouter−8, initial88. Four-layout red/green and26actual native input checks cover min/max, decimals, negative/empty/huge inputs, shrinking a ring and oversized named gear. Constrained40/32 andmaximum180/172 actually draw; all34,381and167,665stored points independently fit configured curves, respectively. Whole Undo/Redo andnativeproject/PNGroundtrip exact; earlier artwork unchanged. PLAY-021 stator/ratio options, predictable paths and invalid combinations are complete.

Failed test actions and oracle diagnostics are retained. Pink105 first dragged the Cross stator fromsource360,320 rather than cranking; its original files remain and a new -v2 attempt uses450,320. A one-pixel PNG-mask gap lay1.30pxfromtheactual3pxpen centreline; the independent mask now unions round support at the unchanged3.5pxradius. Square/Cross corner and curve-self-intersection projections now try multiple analytic branches without loosening fit tolerance. Raster hover can change the offered hole: the verifier requires one unique offered-hole curve consistent with the actual pixels, rather than assuming hole2; reports label the inferred hole. A later Green screenshot classifier returned25components, so that measurement is retained as diagnostic and is not proof of a particular selected hole. The first post-fix numeric evidence helper retained an older array binding; the complete26-case native sequence was repeated with an explicit evidence argument, preserving the incomplete file.

## Spiro cases completed

PLAY-017: Fresh960×640 paper filled Yellow with Bucket, then Blue3px marker stroke and Purple second ink. Open/close Spiro, return to Brushes and reject an off-paper Orange drag: whole project and PNG remain exact; Red gear retained and ghost cleared. Blue palette remains pressed and second-colour field stays Purple. A deliberate right-click afterward actually paints Purple at300,100; one Undo removes only that dot. No empty gear UI is offered; the specified cancelled-drag alternative is exercised.

PLAY-018: On the preserved mixed artwork, native ring movement shifts centre approximately50×40sourcepixels without changing radius160. Yellow-handle native drag sets209.58833972645564, matching the delivered mouse endpoint mathematically. Actual typing120.5 changes the rendered ring without moving its centre. Independent JPEG circle fits verify initial/moved/resized/exact/Reset geometry within1.5sourcepixels (approximatelyoneCSSpixel); numeric endpoint check is tighter than1e-8. Accepted.5/1e7 limits retain accessible Reset, returning centred640/3 radius. Whole project and PNG artwork stay exact. Broader native fractional typing and bounds are separately verified in LIVE-034.

PLAY-020: After LIVE-035 Stop/Reset/Manual/natural-finish checks and the native motor35 project/PNG round trip, a real6second canvas-key mouse hold is interrupted by raising another window. Stop becomes idle before release; saved partial curve ends at3.796rad rather than333.009rad, with no late completion after release. Whole Undo/Redo exact. Attempting Photo lab during Auto is rejected with Let the current effect finish first, Photo remains collapsed and Stop stays visible. Each new saved curve independently fits its offered-hole geometry; PNG differences stay within that curve. This completes the real interruption/other-workflow alternative alongside synthetic pointercancel/capture-loss coverage. An additional post-focus native reopen attempt could not be completed because of an owned-dialog input tool fault; supported chooser also requires disabled extension file-URL access. That extra reopen is not claimed. Earlier native motor save/reopen remains separately verified.

PLAY-022: Native-opened exact VECTOR mixed baseline with9pieces: rectangle,line,dog stamp,prior Spiro,transparent partly-off-paper PNG,concave heart,text andtwo independent raster gestures. Added new Blue3px Spiro, selected10.Spiro alone, dragged its gold resize handle by50.0056×30.0007sourcepixels and moved to420,260. Only its transform changes; all9neighbours, original raster bytes, paths, material, IDs and order remain exact. Whole resize/move Undo/Redo exact. Switching to Raster changes only drawingMode, leaving10objects; native project/PNG reopening exact and new Spiro remains individually selectable. Baseline import omits optional wet:false on the two old brush pieces; this exact default normalization is recorded, with every other field and baseline PNG unchanged.

The ring screenshot classifier initially included JPEG colour bleed from the existing Blue artwork. It now identifies pixels nearer the known rig cyan than Blue ink, keeps only a15RGB-distance core, and rejects outliers outside the fitted16CSSpixel stroke. The original1.5sourcepixel geometric tolerance is unchanged. Mixed-scene transform anchor arithmetic differs by3e-14; comparison uses1e-10for floating-point arithmetic, while whole neighbouring objects and Undo/Redo remain exact.

The post-focus owned native dialog rejected child controls even after activation; keyboard actions reached the parent page, so that attempt is not a successful reopen. Additional diagnostic screenshots and tool errors are retained in chat. The supported file chooser explicitly required enabling extension file-URL access; no permission setting was changed. The stuck agent tab676304713 was closed through the browser API, clearing its dialog, and testing resumed in676304719 on the same random-port origin. A failed create-with-visibility option did not open a tab; creation without that unsupported option succeeded. No other app or browser tab was closed.

## Native post-focus reopen recovered

Native post-focus reopen subsequently recovered: Escape closed the leftover owned dialog; explicitly activating current audit tab676304719 aligned the native window and browser controls. The actual focus36-workflow project and PNG now reopen exactly, independently verified by updated spiro-focus36-verification.json. Earlier rejection/extension-permission attempts remain diagnostic history; no permission setting was changed. Immediate AX reads can precede the completed file load.

## LIVE-037: raster rectangle cut fringe

LIVE-037: clipped raster rectangle copied full selected pixels but left30red source-edge pixels atalpha1 aftermoving. Raster rectangle previews/copy/cut now share the displayed floor/ceil pixel bounds; generic floating rectangles used by vector geometry and rotation remain unchanged. Zero-area raster gestures return no selection and preserve Redo. Exact labelled960×640RGBA PATCH fixture imported natively in Raster mode. Native110×90 crop at95,95 moves by150,100; native150×130 clipped crop at0,0 moves by200,200. Actual clipboardPNG crops and every resultRGBApixel match independent Pillow expectations, including unchanged labels and unrelated half-alpha red. Whole Undo/Redo and two native project/PNG round trips exact. Four-layout corrected regression fails with the old input route and passes with the fix; full680checks and TypeScript/build pass.

Initial old PATCH bytes matched the four known rectangles but had no labels; the current independently generated fixture adds labels outside the patches and retains white/black/border variants and a recipe/hash. An initial import while Vector was active preserved the image as Existing artwork when switching to Raster; it is retained as a setup diagnostic. Reimport after selecting Raster gives an object-free source.

Initial component fixture assertions read a selection label before its animation-frame refresh. Later, a tiny20×15selection drag point near a corner grabbed a resize handle; the corrected fixture drags its centre and refreshes the current viewport mapping. Those reports are diagnostic, not the red regression proof. The final corrected fixture was run with only the old rectangle input route restored temporarily: all four layouts fail on the actual cut fringe. The fixed route was restored before the stable full680-check run.

Native file chooser AX snapshots can precede the actual dialog; early helper errors were followed by a visible Open dialog and successful native selection. Triggering the UI in one call and observing/typing in the next avoids treating a delayed dialog as a product failure. The current native audit tab remains676304719.

## Exact selection inversion

Exact labelled RGBA PATCH in Raster mode: Select all reports960x640 and actual clipboardPNG equals every original pixel. Rectangle95,95..205,185 then Invert produces the exact full-scope complement in actual clipboardPNG. Deleting complement leaves only the opaque Red100x80 patch; labels, other patches and transparency outside are removed exactly. Whole Undo/Redo and native project/PNG reopening exact. With no selection, Invert is visibly disabled beside Draw around a piece instructions.

## LIVE-038: clipboard fallback feedback; raster settlement

LIVE-038: actual native raster Copy/Move/Paste retains Red source; Cut removes only the selected Green; pasted Green moves to the expected destination; separate Undo/Redo steps for Cut and Paste restore whole projects exactly. Native project and PNG reopen exact. API-denial controls reject actual navigator.clipboard.write/read without changing browser permissions: OS Blue sentinel remains unchanged, local Red pastes exactly. Before-fix stale Copied notice retained. Paste now explains that the system clipboard is unavailable and the session copy was used. Four-layout regression fails on the old notice and passes after the fix; normal image paste and external-text rejection remain covered. Original overly broad pending lasso note does not apply to this case’s copy/cut/fallback criteria.

Native labelled RGBA PATCH: lift/move Red by150,100 and freely resize110×90 to220×270, then Place. Blue is lifted/moved150,300 and resized220×180 before switching to Brushes. Both settlement paths hide handles and commit once; source removal, transformed destination, all neighbouring pixels and labels independently exact. One Undo/Redo per settlement restores complete before/after projects exactly. Native project/PNG reopen exact. Initial oracle incorrectly assumed nearest-neighbour while Smooth was active; retained observations show1760 edge differences. Correct bilinear interpolation leaves four straight-RGBA compositing rounding differences; an elementary eight-bit premultiplied source-over calculation matches every RGBA pixel exactly, without any tolerance.

Native labelled RGBA PATCH in ordinary object-free Raster mode: lift/move Red then Escape; separately lift/move Green and resize110×90 to165×135 then Cancel. Both remove floating handles and restore the complete before project and PNG bytes pixel-for-pixel. Ordinary Raster cancellation tested separately from editable-object Escape behavior.

The first new regression accidentally read selectionBounds.w; its diagnostic report is retained. The corrected width fixture fails on the old missing message in all four layouts and passes after the product fix. No clipboard permission was changed. Pointer audit observation now also records actual event modifier flags for forthcoming Shift checks.

## Native wand and exact-size matrix

Sixteen native Colour wand runs on all five prescribed320×240 FILL variants. A separate deque BFS implements the documented four-connected seed-relative L1 RGBA metric, including transparent-pixel equality. Exact actual clipboard crops, deleted PNGs, whole project Undo/Redo and native final project/PNG reopen. Closed border excludes the second matching island even at200. One-pixel gap excludes outside at68 and leaks at69; AA ring excluded143/included144; deterministic ±8 variation selects one column at0 and full interior at24. Transparent40×40 centre remains distinct at0/200; half-alpha ring grows from164pixels at129 to12561 at130. Independent eight-bit premultiplication predicts imported grey232 alpha128 becoming231 alpha128, hence threshold130. Initial integer-coordinate variation clicks landed just below the requested pixel boundary; recorded delivered seeds explain the16-column result. Both attempts retained and repeated at pixel centres; no oracle tolerance or fixture simplification.

Native labelled PATCH100×80 Red selection resized to200×160 through Image controls in Pixels and200Percent, with Keep proportions. Exact selection size;960×640paper unchanged; all pixels outside the resulting footprint keep their positions. Blank,zero,negative,text and4097 rejected on both axes before edit, with actionable message and unchanged whole project/PNG. Positive1/4096limits on each axis reach requested preview bounds; cancelling every preview restores exact original project. Whole Undo/Redo and actual native project/PNG reopen exact.

Native free resize independently changes110×90 into220×270; exact Place/source/Undo/Redo verified. Crossing the opposite corner clamps100×80 to1×1; the tiny corner can be dragged again to101×101 and placed with exact RGBA and whole Undo/Redo. A browser-held Shift plus native mouse drag was explicitly probed: actual PointerEvent.shiftKey remained false and resize was unconstrained. This is an input-capability limitation, not evidence of a product Shift defect or a successful Shift path. Native Shift-constrained aspect test remains unproved.

## Transparent-white threshold and alpha

Native PATCH opaque-white backing plus independently generated40×40copy card: white surround, red20×20subject, RGB249/250 and mixed-channel near-whites, coloured AA side edges and red alpha128row. Actual copyPNG exactly matches source. Copy/paste/move to400,100 over Blue with Transparent off and on, including toggling off/on while floating. Every final RGBA pixel matches separate expected source-over; copied source and all neighbours unchanged. Policy documented before test: remove alpha only if each RGB channel>=250; a single249channel retains the pixel. Half-alpha red remains and blends exactly over Blue. Whole Undo/Redo and native project/PNG reopen exact.

## Four-edge uncommitted raster recovery

Native object-free Raster PATCH100×80Red moved partly beyond all four paper edges. Faint desk overhang and Bring action visible. Each actual mouse drag starts on canvasSlot strictly outside the paper (left−20,right980,top−12,bottom650 source coordinates), returns the same piece fully inside, moves it out again, then Bring selection to paper centres it at430,280. Actual clipboard crops prove complete100×80source retained without resampling; exact final RGBA, unchanged neighbours, whole Undo/Redo and native project/PNG reopen. Standard pointer observer extended only to record public canvasSlot/workspaceOverlay events and view rectangle, never application state.

## Permanent raster clipping in both modes

Editable Raster branch now also complete: actual120×100asymmetric PNG inserted natively over retained PATCH artwork in Vector mode, rotated90degrees without resampling, then positioned and placed across all four edges and fully outside. Independent elementary clipping/source crop/affine calculation verifies retained images120×60(left/right),80×100(top),60×100(bottom), exact sourceRGBA and transforms, rectangular clip geometry, unchanged background object and whole document. Moving left fragment back changes only translation and retains source resolution; discarded pixels remain absent. Fully outside removes only the selected piece. Whole Undo/Redo and native project/PNG reopen exact. Together with ordinary Raster five-position matrix, every EDIT-012criterion and boundary branch is now verified.

## LIVE-039: accepted fractional piece transforms

LIVE-039: exact piece controls accepted fractional values in the transform model while declaring HTMLstep1, producing stepMismatch/invalid fields for accepted textTop278.5 and concave coordinates. Width/Height min0.01 combined with step1 also wrongly rejected ordinary dimensions. The five exact Size, Position and Angle inputs now use stepany, matching the existing finite fractional transform contract. Native typing180.5,120.25,330.5,278.5,22.5 yields valid fields with no stepMismatch. Independent elementary affine composition proves exact resize, translation and centre rotation; every other document field unchanged. Separate Undo/Redo and native project/PNG reopen exact. Four-layout regression fails before the declaration fix and passes after; stable full688checks, TypeScript/build and diff checks pass.

Native mixed VECTOR scene: Rectangle, Line, Dog stamp, Spiro path, Concave heart and Text individually placed fully outside at left−2000/top200, reselected through the actual piece picker by stable ID, and returned through Position controls. Every source definition/material/text/path/stamp property and all eight neighbours remain exact; only the selected matrix translation changes. Returned PNGRGBA equals baseline for all six; whole Undo/Redo and actual native project/PNG reopen exact. Concave return has only1.14e−13floating translation roundoff, below the predeclared1e−9matrix arithmetic budget; all geometry and image pixels exact. Raster trim rule is not applied to these six vector pieces.

## Crisp and smooth resize scopes

Native prescribed opaque32×32PIXEL fixture, noninteger1.5resize in whole-picture and selected4×4checker scopes, both Smooth off/on. Fresh additional whole32→50and selection4→7Smooth runs. Independent all-pixel nearest-distance test permits only mathematically equidistant source ties; Crisp adds zero colours. Smooth independently requires edge colours in the local source-colour convex mixture, actual intermediate colours at every edge separated by more than an eight-bit quantization cell from a source endpoint, and exact uniform areas/alpha. Outputs introduce334/32/358/45intermediate pixels; scope, dimensions, other document fields, whole Undo/Redo and native project/PNG reopen exact. Pillow tie decisions differ; nominal smooth comparisons differ by one level. A separately inferred1/256coefficient fixed-point hypothesis fails fresh4→7cross-validation and remains a retained failed diagnostic with its bounds unchanged. It is not treated as a product kernel failure or a passing coefficient identity check: HTML Canvas leaves smoothing algorithm unspecified (https://html.spec.whatwg.org/multipage/canvas.html#image-smoothing), and EDIT-017requires actual interpolation, nearest-source structure and scope/output behavior, all independently verified. No original criterion removed.

## Paper size without scaling

Native paper growth960×640→1200×800 then reduction450×350 in both ordinary Raster PATCH and the nine-piece mixed VECTOR scene. Separate PATCH copy supplies100×100purple square at650,300 missing from original four100×80rectangles; fixture gap corrected in TEST-DATA.md without changing original patches. Every raster source pixel and the square coordinates/dimensions remain exact; transparent new area for imported Raster, opaque white for vector Paper. All nine vector/raster/text/stamp definitions, source bitmaps and matrices remain exact. Complete project Undo/Redo and native project/PNG reopen exact, recovering clipped content. Expanded VECTOR rasterization changes one antialias coverage pixel427,376 on the identical thin Spiro path. Retained failed expanded-PNG-copy hypothesis records before199/225/248 and after142/195/242; independent geometry distance0.2632 with0.175stroke radius plus pixel footprint, and exact blue/white coverage palettes prove the pixel belongs to the unchanged stroke. Pixels outside that footprint, source raster canvases and geometry remain exact. No raster resampling or vector geometry change is accepted.

## Exact crop in PATCH and four-layer MIX

Native prescribed labelled PATCH and four-layer MIX variants: select exact200×100 rectangle90,90..290,190 and Crop through Image. Every sourceRGBApixel matches independent Pillow crop; MIX all four layers crop to the same origin and retained Caption stamp geometry translates by−90,−90without clipping its vector definition. Missing selection produces Select the part of the picture to keep first and leaves complete project unchanged. Exact dimensions200×100, whole Undo/Redo and separate native project/PNG reopens for PATCH and MIX pass.

## Whole-picture pixel and percent resize

Native exact labelled PATCH plus four-layer MIX: whole-picture scope480×320pixel entry and200%from fresh960×640, yielding1920×1280. Additional MIX1×1,4096×1and1×4096positive boundaries. Every layer image independently nearest-source sampled (only mathematically equal-distance ties allowed), all known PATCH colour/alpha rectangles reach exact expected bounds, retained Caption stamp definition unchanged and affine matrix scales independently on both axes. Decoded PNGdimensions and premultiplied composite exact outside the independently bounded emoji glyph; stamp rendering present at both normal sizes. Ten blank/zero/negative/text/4097axis entries reject without changing the complete PATCH;1000%edge and67108864total pixels across four layers reject without changing MIX. Whole Undo/Redo and native project/PNG reopens exact for both scenes.

## RGB inversion and connected corner removal

Twelve native runs on all five prescribed320×240FILL variants: invert each base/gap/variation/AA/transparent source and remove corner-connected background at base68/69,gap68/69,and maximum200for variation/AA/transparent. Independent RGBA inversion preserves alpha exactly, including canonical half-alpha and transparent pixels. Separate deque flood oracle verifies every removed/retained pixel. Closed border preserves14161qualifying grey interior pixels; opening one-pixel gap at tolerance69 removes them, while68does not. Connected second1600pixel island follows colour threshold, and unconnected matching content remains. UI explicitly says connected top-left corner colours and best for flat backgrounds, with no subject-segmentation claim. Whole Undo/Redo and native project/PNG reopen exact.

## LIVE-040: caption numeric controls and accepted bounds

LIVE-040: native caption Size1/BoxWidth1 remained invalid after blur while Place silently used minimumfont6 and bitmap20×40. Text controls now bound preview values consistently, preserve in-progress text/caret, normalize on blur or explicit placement, restore defaults for blank/non-numeric input, retain fractional font sizes (stepany), and round box width to whole pixels. Twenty-one native size/width edits cover below-minimum,zero,negative,minimum,maximum,over-limit,blank,text,36.5font and200.4/200.5widths; all committed fields valid and exact. Minimum placed pixels match the pre-fix accepted bitmap exactly; whole Undo/Redo and native project/PNG reopen exact. Four-layout regression fails before and passes after; full692checks, TypeScript/build and diff check pass. Caption workflow/font/wrapping variants remain Partial until separately verified.

## LIVE-041: vector text preview and font matrix

LIVE-041: flattened bitmap previews differed from directly rendered vector captions, especially at50%Strength with opaque paper (native paired screenshot maxchannel76). Plain vector previews now cache a non-mutating TextObject layout and use the placement renderer. Nine native vector font/alignment/style rows and the50%opaque stress caption now have identical preview/placed screenshot pixels; all nine raster rows already matched. New48-combination regression (sixfonts,twofontsizes,twoStrengths,twoBackgrounds) fails before and passes after on four layouts. Full696checks, TypeScript/build and diffcheck pass.

Eighteen native two-line captions cover all six installed font families and three alignments, Raster/Vector,18/24/36.5px,180/260/360widths,transparent/secondaryYellowpaper, and all21factor pairs of font/alignment/mode/fourstyleflags. Independently verified font metadata/hashes, actualUIvalues, sourceTextObject properties/line breaks, nativepointer placement/move, exactRasterRGBA, unchangedneighbours, completeUndoRedo, and all18nativeproject/PNG reopens. Contact sheet visually confirms readable words and coherent styling. Impact bold/italic may be synthesized; unavailablefont fallback not triggered on this platform. This is pairwise coverage, not a full Cartesian product.

## EDIT-021: unfinished caption drafts

Explicit Cancel leaves whole saved project and opaqueWhitePNG exactly unchanged in Raster and Vector modes. Closing options retains the whole draft preview for editing; reopening thenCancel clears it. Actual nativeClosebutton removes tab722 while an opaqueunfinishedcaption is visible over the4layerMIX; newtab727 RecentdraftResume returns exactoriginal4layerproject andPNG, withoutpartiallettersorbackgroundbox. EarlierCtrlW attemptdidnotclose719 and was not counted; actualtabremovalverifiedbyinventory. Main two-line native placement,move,completeUndoRedo and18project/PNG reopens independently verified by caption-font41-verification.json.

## EDIT-023: narrow text over layered artwork

Eight native4layerMIX variants: Raster/Vector narrow120px centredArial24px transparent/secondaryYellowopaque captions,36character unbrokenword,emptyandwhitespaceopaquePlace. Four coherent normal lines and six longword lines staywithin112pxcontentwidth; everyoriginalcharacterretained. Both modes produce identicalsourceclipboardRGBA. IndependentPillow source-layer composite and8bitpremultiplied fullPNGsource-over match everypixel exactly; unchangedallotherlayers/objects/rootfields; transparentpixels preservebusyartworkexactly; opaqueboxuses#fdd835 withalpha255. Pairednativepreview/placedviewsidentical; wholeUndoRedo andall6nativeproject/PNG reopensexact. EmptyandwhitespacePlacecreatenoselectionandchangeneitherwholeprojectnorPNG. Liveviewvisuallyconfirmsreadablewordwrappingwithoutcontroloverflow. FirstinterruptedRasterhelperartifactsretained; onlycompletefreshrepeatcounted.

## LIVE-042: keep the raster rotation centre fixed

LIVE-042: native120x100Rasterselection90degree turn kept top-left90,90 and shifted centre150,140 to140,150. Rotation now offsets expanded localbitmap bounds to retainpapercentre, matchingeditablepiecebehaviour. Nativefixedquarterturn exactat100,80; H/V/90sourceRGBAexact. ChainedH,V,90,45 ends156squareat72,62 withsamecentre, exactalphageometry/opaquepixels/unchangedneighbours. Four45degree rotations of100x80alpha128pureRed haveexactRedRGBat everyvisibleedge aftereachturn (5/38/57/41alpha levels); final365square atnearestwholepixel268,158 exactRGBA. BothsequencescompleteUndoRedo andnativeproject/PNG reopens exact. Retainedfailedmixedcolourclipboardcomparison: five translucentRed/Blackpixels differup to2straightRedlevels fromOSclipboardPNG; exactarbitrarymixedRGBnotclaimed andconversioncauseunproved. Nochannel tolerance added. SeparatepurepigmentcaseprovesnoBlack/Whitefringes. Isolatedcentre/cancel/placement/historyregression failsbefore andpassesafter; full697checks,TypeScript/build,diffcheck pass.

## LIVE-043: stable export pixels after project reopen

LIVE-043: nativewhole-image skews exposed1–4PNGpixels changing1–2channellevels afterprojectreopen despiteunchangedprojectdata. Export now snapshots sourceRGBA and readsbackthetemporarystoredresult oncebeforecompositing, matchingthecanonicalpixelsretainedbyprojects. Initialone-readbackattemptfailedallfiveaffectedcasesandisretained. Correctedtwo-readbackattempt passesallfiveplusnegative-skewcontrolonfreshMIX/PATCHoperations,withoutchanginganysourceprojectbytes; sixrealnativeproject/PNG reopensexact. Headlessgenerated-blockregressionpassesbeforeaswellasafterandisnottheredproof; liveproductiondownloadsprovidethatproof. Full701checks,TypeScript/build,diffcheckpass. Extraexport-onlyreadbackhasaboundedfull-layerpixelcopycost; drawing/historysourceunchanged.

EDIT-019:20nativeindependentcopies oflabelledPATCHand4layerMIX coverH/Vflips,+90/-90/45turns,+/-20Xskew,+/-15Yskew,andcombined20X/-15Y. AllsourceRasterRGBAbytesexactforflips/quarterturns; everylayerasymmetriccorner, safelyuniformaffineinterior,clearexterior,analyticbounds,unchangedmetadata,andretainedDogstampdefinition/matrixverified. All20wholeprojectUndoRedo/nativefile-reopens exact. PATCHquarter/flipcompositePNGexact; MIXdirectemoji re-render differsinsideanalyticDogboundsplus2pxAA, withallRasterbytesandallothercompositepixelsexact. No kernelidentityclaimfornonuniformarbitraryresamplingboundaries. Original5skewPNG-reopenmismatchesretainedandcorrectedbyLIVE-043; sixnativefixedretestsallPNG/projectexact.

## FILE-006–009: real image exports

FILE-006: Main toolbarSAVEactualdownload on4layerMIXhalfCharacter while rulersandselectionhandlesvisible. PNG960x640compositionexactoutsideanalyticDogstampbounds, knownhalf-opacityRed/Greenexact, editableprojectunchanged, noeditingoverlays, actualOpenimagePNG roundtripexact. AdditionalBackdropPhotoLab+1EVDone/save: independentlinear-sRGBdoubling predicts45,186,255, completecompositeexactoutsideDogbounds, sources/otherlayersunchanged, savedrecipeprojectandPNGnative-reopens exact. InitialasyncPhotoexportcompletioncheckedbeforefileappeared, thenwaitedthroughactualreadyUIwithoutreclicking.

FILE-007: Two-layerPATCHPaperhiddenviaLayers; PNG/WebP/TIFF realdownloadsindependentlydecode960x640withfullRGBAexact(includingallalphaandsemiRed128). ActualWebPoutputisRGBAexactforthisfixture; lossyWebPcapabilitynotgeneralized. NativeOpenimageandPNG/projectretentionexactforeach. Contrastingblack/whitecompositesvisuallyinspected; sourceprojectunchangedaftereveryexport.

FILE-008: TransparentPATCHJPEGand24bitRGBBMPgenuineformats960x640withopaqueWhitematte. BMPeveryRGBbyteexactindependentcomposite. JPEGpredeclaredMAE<=3/PSNR>=32dB/interiorMAE<=3max8/clearmattewithin2; measuredwholeMAE0.1234668andPSNR43.463879dB, interiorswithinbudget; edgechromaRGBdifferencesrecorded(max102notpixelidentity). Transparenteditableprojectunchangedafterboth; actualOpenimage reimports independentlydecodedoutput, nativePNGroundtripsverified.

FILE-009: COLOURrichsourcewith11hue/neutraltiles×alpha0/64/127/128/192/255plusopaqueRGBgradient. RealGIFdecodedP256entries,oneframe,alphaexactbinarythreshold128. OpaquequantisationmaxRGB31/31/85withinpredeclared37/37/85;191997opaqueRGBpixelschanged,RGBMAE10.19/10.10/21.18. Explicitlypalette-limitedstill,nottruecolour,exactblack,partialalphaoranimation. NativeOpenimageandPNG/projectroundtripofrichGIFexact. PATCHbinaryalphaexportalsoexactpolicy; black/whitebackgroundcontactsheetvisuallyinspected.

## FILE-002: independent format imports

EightnativeOpenimage/draw/UndoRedo/reopenflows: independentlyPillowencodedPNG,JPEG,losslessWebP,BMP,GIF,uncompressedRGBATIFF,EXIF6JPEG,andvalidPNGaftercorruptrejection. Five losslessformatdecodesRGBAexactversusindependentPillow(withcanonicaltransparentRGBzero); JPEG/EXIFRGBmax1,MAE0.0003863withinpredeclaredmean1/max5. EXIF6maps320x240source to240x320portrait. Actual12pxBlackMarkerstrokeverifiedagainstnativepointercoordinates: safecapsuleinteriorexactBlack26alpha255, safeexteriorunchangedexact. All8wholeprojectUndoRedo/nativeprojectandPNG reopens exact. NativepickerEscapeandcorruptPNGleavetheentireportraitprojectunchanged; corruptionexplainsformatsandnextvalidimport/markworks.

## FILE-001: new-paper boundaries

Twelve nativeinvalidwidth/height attempts(blank,0,-1,1.5,4097,nativeabc→empty) retaindialog,explainwholepixel1..4096limits,andpreserveentireoriginalprojectafterCancel. Eightvalidsizes1x1,1x240,320x1,320x240,960x640,4096x1,1x4096,4096square produceexactopaqueWhiteRGBAcleanPaper,validactiveID,emptylive/objectsandrequestedresolution. Nativemarkerfootprintalignswithdeliveredpapercoordinates; allneighboursunchanged. DrawingUndo andNewpictureUndo areseparatestepsexact; bothRedosrestoreexactblank/markedprojects. All8nativeproject/PNG reopens exact. ThinaxeszoomedthroughActualpixels+3Zoominto3.375CSSpxbeforemouseinput; resolutionunchanged.

## FILE-003: insertion and source limits

SixcompletednativeMIXinsertionflows: smalltransparent320x240PNGinRaster/Vector,movedbydelivered150,100to470,300; maximum4096squareinbothmodes;4096x1and1x4096Raster. IndependentsourceRGBA/geometry,onlyactiveCharacteraddition/composite,allotherlayers/objects/metadataexact. LargePlacewarnstrim,keepspaper960x640andexpectedPurplefullframe/row320/column480; originalMIXrestoredbyUndo. Native4097width/heightrejectedwithlimitsmessageandentireprojectunchanged; validinsert/moveafterrejectionworks. Rasterfloatinginsert/move/PlaceoneUndo; Vectormoveandinsertseparategestures, bothUndos/Redosexact. Initialsingle-UndoVectorprobe retainedasMoveUndo, completedv2provesInsertUndo. SixnativePNG reopens exact; VectorprojectsaddonlyunusedliveSize960x640toinsertedRasterwithoutlivedata, strictdocumentednormalization; sourceRGBA/matrices/allotherdataexact.

## LIVE-044: project Undo restores drawing mode

LIVE-044: Opening a Vector project over a Raster picture then Undo restored source pixels/layers but retained Vector drawing mode. History now captures/restores drawingMode, its selector and vector-mode presentation using the current Basic/Advanced policy. Native full-document Undo/Redo exact; four-layout regression covers both directions in both UI modes (red before, green after). Full regression705 passes, zero failures/page errors; production build and TypeScript pass.

FILE-013: Native independent mixed project contains four MIX layers, +1EV Photo recipe, Conveyor stroke and two Water fills, nine mixed Vector pieces, Caption Dog and half-opacity Character. Actual downloaded checksummed bytes reopened after fresh app reload; all saved editing fields exact, every decoded source Raster RGBA byte exact. Raw producer absent optional stroke clip normalizes only to null (explicitly asserted); no fields dropped. Controlled12345ms native PNG is byte-for-byte RGBA identical after reopen;23456ms changes86851pixels while saved definitions remain identical. Actual PNG renamed.retropaint rejected with actionable damaged-file message, whole unrelated unsaved project unchanged, valid retry succeeds.

FILE-016: 28 native chooser rejection/retry cycles cover malformed/truncated/nonJSON/renamedPNG, wrong-size layer, invalid/duplicate/missing IDs, singular Vector transform, invalid opacity/crop/photo curve/look/settings/live ink/mode/brush,4097axis limits,17layers,stored-pixel budget,future999,and CADzero scale/unknown solid/duplicate ID/singular camera/parallelworkplane. Every rejection has retained format message; entire original unsaved Raster project including all source pixels/metadata remains exact, no partial layers active. Every immediate native valid opening matches canonical mixed project exactly; Undo returns entire unrelated Raster project and Raster controls exactly. Before-fix first4 rejection attempts preserved separately: later differences were drawingMode leakage from successful-open Undo, corrected byLIVE-044; not partial failed-import replacement.

FILE-015: Unknown future version999 native rejection explicitly explains newer-version incompatibility; whole existing project unchanged, immediate valid retry and Undo exact. Genuine historic producers v1,v2,v9 already migrated/resaved/reopened with independent checks. Authentic v3–8 fixture bytes remain unavailable after producer search and prior user confirmation; modern files with edited version numbers are not evidence. Remaining historical fixture requirement is blocked.

## LIVE-045: preserve saved camera during workshop inspection

LIVE-045: Native CADMIX saved Top orthographic camera changed upY to upZ and nudged position merely opening/closing workshop. Four-layout minimal no-camera-input regression reproduces. Tool switching no longer resets camera.up; OrbitControls is rebuilt when camera/plane basis changes (its orbit quaternion is fixed at construction), disposing prior native listeners. Perspective camera reconstruction also restores saved span through zoom, preserving framing when changing projections. Native canonical repeated inspection whole-project/PNG exact; native5mm solid move/UndoRedo retains exact camera. Focused regression and full709checks pass; TypeScript/build pass. Firstpatchstillfailedperspective-span case; retained before/firstattempt/finalreports.

FILE-014 native CADMIX source has four layers, editable Cube/Cylinder/Join/3mmShell history and callout. Actual picker reopen/resave restores layer order,target,allrecipe/object/body/camera definitions exactly in both orthographic and perspective variants. +1EV Photo recipe and sharedcrop96,64,768,512 reopen with exactproject and768x512RGBA. Afterreopen: Photoexposure+.5,22pxBluePaperstroke,andVectorcallout+80,-40 are independently scoped to intended fields/sourceRGBA, with entire Undo/Redo states exact; combinededitedproject/PNG realreopenexact. Solid5mm edit/UndoRedo retestedafterLIVE-045 preserves exactcamera. Photo drafts committed withDone, workshop deliberately closed beforeSave. Fixturecaveats explicitly verified: booleanpaperflagsbecomenull (notcolourdefinitions); everyRasterRGBAexact. SyntheticTopcameraassignmentretainedolderperspectivebitmap, sofirstworkshopinspectionrebuildsexpectedTopcache; canonicalsecondinspectionproject/PNGexact. Originalfailedinput/cropentryattempts retained andnotcounted; nativecoordinateentrycompletedboth.

## FILE-012: cropped MIX print preview

Prescribed four-layer MIX cropped to200x100: native Print opensChrome one-pagepreview with2:1Red/Bluecomposition. NativeWindows screenshot confirms noeditingcontrols/selectionoverlays inprintedimage; browserheaders/footerareprintsettings. Read-onlyactualiframe srcdocPNG decodedRGBAexacttoactualPNGexport andknownfixtureRed/Blueinteriors. NativeCancel thenactualdownloadedwholeprojectexactbefore/after. Earliernaturalphoto1800x1200PDFimageverificationalsoretained. Physicalprinteroutput/settingsremainexternalintegration, explicitlynotinferredfrompreviewpercasealternative.

## FILE-024: native recovery retention and cutoffs

Dedicated65487audit-origin recovery DB, predeclared16fileplan: ten32square nativeprojectopenings individuallyreachDraftsaved; allthreeRecentdraftspages contain exactlyCount10..03, count01/02evicted. Four2048square opaque randomRGBprojects eachactual19241350characters/38482700UTF16bytes; fourthforces128Mbudgeteviction ofBudget01 whileBudget04..02plusCount10..06remain8. Threebig+smallfit; fourbigexceed128M independentlycomputed. Separate4096square one-layernoise16777216pixels yields76957842characters>50M andautomaticdraftsizemessage; two4096white layers33554432pixels<1Mcharactersyield24Mstored-pixelmessage. BothstatusbuttonsproduceactualeditableSaveprojectdownloads, allsourceRGBAexact, bothmanualfilesnative-reopen/resavewholeJSONexact. Neitherineligibleopeningchangespreexisting8draftcards/order. LatestvalidBudget04nativeResume/resavewholeprojectexact, provingprotectedcontentnotjustcardretention.

## INK-001: all standard palette swatches

All12 standardnamedpalettecolours nativechosen/aria-pressedtrue andseparate22px100%SqueakyMarkerstroke onpreservedPLAYcontrasting#505050copy; originalwhitePLAYunchanged. Red/Yellow/Blue/Green/Black/Pink/Mint/Teal/Gold/Purple/Orange/White allopaqueinteriorRGBAexacttotheirdeclaredpalettehex. ThirteenthreturnRedstroke verified. Everydeliveredsourcepointmeasuredfromnativepointerevents, capsuleinteriorandunchangedexterior/alloldmarkseverybyteexact; onlyactiveRasterimagechanges, allmetadata/live/objectsunchanged. WholeUndo12colourstate/Redo13/nativeprojectreopenexact; actualPNGprojectdecodedRGBAandnativePNG-reopenexact. Whitevisibleagainstdarkbacking, notinvisiblepass.

## INK-002: visible composite sampling

Four actualMIX halfCharacter cases: plainBlue#1E88E5, halfRedoverBlue#8F4472, hiddenCharacterBlue#1E88E5, hiddenBackdropRedoverWhite#FF7F7F. IndependentPillow8bitopacity/source-overderivation exact; originalplan float50%Whitechannel128hypothesisretainedandcorrectedto127becausealpha128leaves127/255White, no tolerancewideningorproductbugclaim. NativeRightpickretainsmagnifierwithcentralpixel/hex, leftpickreturnsmarker; bothsampleswholeprojectunchanged, no dot. VisibleWhite180x80testcardaddedonlytoseparateMIXcopyawayfromsamplepoints. Fournew22pxswatchcapsulesmatchindependentRGB/alpha; sourceRaster/otherlayers/Dog/metadataunchanged, oneCaptionRasterpieceaddedabovestamp. WholeUndo/Redoexact, nativeprojectreopenonlyomitsinactivewet:falseflag, allotherdefinition/imagefields exact; allfouractualPNG-reopenRGBAexact. Rawfixturebooleanpaperflagsnormalizetonullasnon-colourvalues, sourceRGBAexact; documentedinitialno-cardpreviewandWindowsforwardslashpathcorrectionnotcountedascompletedvariant.

## LIVE-046: usable full conveyor replacement

LIVE-046: Fullconveyor middle-slotreplacement wasunavailablefromvisibleLivepicks (notdraggable), anddrop refusedallchangesat8. VisibleLivepicksnowprovidecolourdragpayload; filledslotdrop replacesinplace,emptydropaddswithin8. Directchosen-colourRightclickandShiftF10routesreplace/addwithoutdrag, preservingtap-to-remove; nativemouseandkeyboardbothverifiedslot4Purple/Goldandallother7unchanged. Adddisabledat8,nativeninthclickkeeps8; slotsnamecolourandpicksannouncepressed. Actualnewstrokehasreplacedsequence,older2definitionsunchanged; wholeUndo/Redo/nativeprojectreopenandcontrolledzero-speedPNGexact.24nativemodechangeskeep1pendingrAF/2timeouts/0intervals (nointervalcreated);standardAPIobserver,notappstateaccess. HTMLdragfixpassescomponentchecks;threepostfixnativeendpointdragattemptsdidnotestablishHTMLdrop,soonlydirectreplacementroutesarenativelypassed. Initialregressioncleanupui.syncmistakeretained; correctedredbefore-fix2failsmissingdraggable,greenfocused4layouts; finalfull713passes,zeroerrors. Remainingmulti-speedandone-stopacceptanceongoing; noadditionalcaseclosedbythisfixrecord.

## LIVE-047: single-stop ink matches its colour

LIVE-047: Nativeone-stopYellowbeltpaintedpreviousordinaryRed, andpigmentpreviewretainedmulticolourgradient. Singlelive stopnowresolvesitsownsolidpigmentforbrush/fill/editablepieces/staticSpray, whileemptybeltkeepsordinaryfallback. Currentink/pointer/brushpreviewsuseeffectivepigmentandrefreshonAdd/Clear/remove/replace. NativebeforeRedfailureandfixedYellow/emptyRedcapsulesretained; all9oldlive definitions anduntouchedRasterpixels exact. WholeUndo/Redo/nativeproject/controlledPNG reopens exact. Redpaintingandfour-layoutpreview regressionsgreenafterfix, includingbucketandVectorfill,emptyfallbackandnoexistingpicturemutation. Full718checks,zero failures/pageerrors; TypeScript/buildpass.

NativePLAYconveyormatrix complete: allcounts0..8addedandremoved; fullmiddlePurplemouse/GoldShiftF10replacementandninthAddguard; speed-8/0/+8eachSnap/JumpandOoze/Blend; prescribed3stopRedYellowBlueinbothmodes; ordinaryRedbeforearmingandGreenafterdisarming. IndependentcyclicphaseandroundedRGBinterpolationmatchevery5x5opaqueendcapat12345and23456ms; zeroSnapcontainsall8chosenstops,Oozeblendsnon-stopcolours. Only4nonzerospeedstrokeschange(42912pixels), everyotherRGBAbyte/staticmarkunchanged, all11capturedlivedefinitionspreservedthroughlaterpalette/mode/speedchangesanddisarming.24rapidmodechangeskeep1rAF/2timeouts/0intervals; normal-clocktwoactualPNGscontinueanimatingwithoutdrawingandentireprojectunchanged. FinalprojectandbothcontrolledPNGframes native-reopenexact.0/1boundaryfixedbyLIVE-047: emptyRedfallback, singleYellowactualYellow, matchingpublicpreviewstyles. Initialradius13/integer-gridfootprinthypothesisretained; intentionalLiveMarkerhaloradius13.992plus1AAwithpixelcentresaccountsfor1916initialoutsidechanges, noRGBtolerancerelaxed. NativeHTMLendpointdragsdidnotestablishdrop; actualreplacementpassesviaRightclick/ShiftF10, componentHTMLdropcoveragekeptseparate.

## INK-018: coherent live still in an independent viewer

Actualfour-layerMIXPhoto+1EV/Conveyor/twoWaterfills/nineVectorpieces/CaptionDog nativePNGexportsat12345and23456ms. BothfullRGBAframesexacttopreserved44reference, wholeeditableprojectbefore/afterexact. IndependentcyclicRGBphaseandlinear-sRGB+1EVmatchconveyoropaqueendcapRGB138,149,228then238,255,158. MathematicalWaterpolylinegeometryselectsunambiguousstroke/backgroundpoints(786,473)and(786,537), masksproveonepointineachdisjointfill; bothmatchsameclock+exposureRGB101,255,255then0,164,248. PNGformatoneframe/notanimated. ActualdownloadopenedthroughnativeChromeCtrlT/localfileURLinseparateimageviewer; filenameand960x640title/nativecompositionobserved, imageareaexactbetweentwoScreens. DecodedPNGbytesarepixeloracle,notGUIresampling. Temporaryviewertab734closedandabsenceverified; originalaudittabretained. Nophysicalprinterorinferredanimationclaim.

## LIVE-048: exact colour entry rejects invalid values

LIVE-048: Native #ABCDEFZ was truncated to #ABCDEF and committed; visible RGB999 committed a clamped value. Hex now retains overlength text for validation; required integer RGB bounds are checked before updating the draft or committing. Red/green regression covers four layouts. Native PATCH above separate grey backing: exact #123ABC, RGB32/128/224, each channel0/255, Black/White, three independently predeclared wheel hue/saturation/tone picks. All13 painted opaque interiors exactRGB; measured mouse capsules and all untouched source/backing pixels exact. Twelve invalid Hex/RGB values remain editable and cannot change active pigment. Reopen values/marker agree with independent colorsys; pointer colours reachable through keyboard RGB. Opposite keyboard arrows restore exact selection; toneHome/End work, Cancel preserves project. WholeprojectUndo/Redo/nativefile reopen exact; both actualPNG decodes exact. Initial native empty typing did not clear field (corrected to Backspace); initial wheel-centre click repicked colour (corrected to keyboard focus). Half-radius rounding-boundary probes retained; predeclared non-boundary samples use strictRGB. Marker oracle uses exact prescribed continuous polar coordinates for mouse picks and colorsys from exactRGB for text/reopened picks; first guessed0.25percent quantizedRGB marker allowance failed0.25666percent and was replaced with the correct continuous-coordinate oracle, not widened. Full726checks/zero failures/pageerrors; TypeScript/production buildpass.

## LIVE-049: visible tolerance and exact FILL boundaries

Exact prescribed320x240FILL family natively executed on independent copies with separate unrelated grey backing. Closedoutline mask14161pixels; one-pixel(80,20)gap intentionally propagates76321pixels includingoutside,blacklinepreserved. Antialiased13689andtransparent14161 masks; disconnected40x40matchingisland staysunchanged in closedvariants. Deterministicneutral±8noise: tolerance0/23fills4760middle-stripepixels,24/200fills14161wholeinterior. Independent four-neighbourqueue uses observedRGBA-L1<=threshold metric and predeclaredmasks, exactRGBAfor everyfilled/exteriorpixel. Each8case wholeprojectUndo/Redo exact; unrelatedlayer/metadataunchanged, max/minfinishwithoutfreeze. Nativefinalproject/PNG reopensexact. Transparentfixtureimport canonicalizes14161alpha0hiddenRGB232to0; exactalphaandallvisiblebytesretained, allnativebaseline/fill/historycomparisonsrawRGBAexact. LIVE-049: tolerance had no visible number; output now displays exactsetting, native0/23/24/200 allvisibleandmatchinput. Full726regressionchecks,zero failures/pageerrors; TypeScript/productionbuildpass.

## Preset and custom gradient acceptance matrix

Prescribed320x240FILL plusseparateone-pixelblack-enclosedregion. All4presets Sunset/Rainbow/Ocean/Candy nativelydraggedacrossclosedmask, actualproject/PNG exportedandnative-reopened/resavedexact, eachsingleUndo wholebaselineexact. All4tinyregionfillschangeexactly1pixel/opaquealpha andUndoexact. Independentareaoracle: eachdeclaredstopRGBexactuniquemodeandstrictmajorityinconstant-gradient119pixelcolumn, everysegmentthirdareaaverageprogressestowardsnextstop, constantchannelmodesexact, adjacentjumpsboundedbyanalytic slope+quantization. Originalsingle-rowexactstophypothesisfailedandretained; minorityone-bytebrowserditherexplainsdiscrepancy. PointwisemonotoniccolumnhypothesisalsofailedforOceanR2byte/30pixelchange; retainedspecificfailure, areaorderingisapplicable smoothnessoracle. NativecustomRed#E53935/Blue#1E88E5, initialhorizontaldrag,bothpinsmovedtodiagonal; exactmodalendpointareas/directionchanged,samemask/untouchedRGBA/layer/metadataexact. Escape wholeprojectbaselineexact. Saveexplicitlysettlesonce;Undo/Redo/nativeprojectPNG reopensexact. ChangingtooltoBrush leavespreviewpending,butSave settlesvisiblegradientoncewithnohiddenpreviewleak, oneUndoexactbaseline. Zero-lengthBuckettapusesdefinedsolidBluefallback; nextdisconnectedislandtapworks,eachsingleUndoexact. Allscope/history/fileRGBAcomparisonsstrict, noRGBtolerancewidening. Noadditionalproductfixrequired.

## LIVE-050: text placement preserves live ink

Native 960x640 matrix: all seven textures painted and bucket-filled; independent PNG checks verify 64px periods (Static 48px), declared structure colours, five static textures and four Water/Static animation masks. Whole-project last-fill Undo/Redo and zoom invariance are exact. LIVE-050 reproduced: placing raster text baked all existing live fills. Fixed by retaining original live artwork beneath the placed raster piece; preview cancellation and whole-project Undo/Redo pass the regression. Live retest placed seven labels, exercised Undo/Redo, and observed two animation frames. Project file reopening works after the user enabled extension file access. Fixed labelled project/PNG exports have not yet arrived from Chrome, so their exact preservation and round-trip checks remain pending. Full regression: 728 checks, no failures or page errors; TypeScript and production build pass.

## Texture matrix completed

Native 960x640 matrix: all seven textures painted and bucket-filled; independent PNG checks verify 64px periods (Static 48px), declared structure colours, five static textures and four Water/Static animation masks. Whole-project last-fill Undo/Redo and zoom invariance are exact. LIVE-050 reproduced: placing raster text baked all existing live fills. Fixed by retaining original live artwork beneath the placed raster piece; preview cancellation and whole-project Undo/Redo pass the regression. Live retest placed seven labels, exercised Undo/Redo, and observed two animation frames. Project file reopening works after the user enabled extension file access. Fixed labelled project/PNG exports have not yet arrived from Chrome, so their exact preservation and round-trip checks remain pending. Full regression: 728 checks, no failures or page errors; TypeScript and production build pass. Completion: Chrome file access and downloads are now working. Both labelled frame exports preserve every pixel outside the labels exactly; all original live definitions and raster bytes remain exact. Native project and PNG round-trips are exact. Refined placement bounds are 28x9 pixels; cancellation, Undo and Redo preserve whole project data exactly. INK-009 is now Pass. The current regression report is all-fifty-fixes-cropped/report.json.

## Strength matrix completed

Native 960x640 PLAY white/Blue background, Squeaky Marker22px, Red: full strength and15% on both backgrounds; second weak pass on each. Independent source-over arithmetic verifies9x9centre patches within2/255, and every pixel outside each declared radius13px gesture tube remains exact. Both overlap Undo/Redo pairs preserve whole project JSON exactly. Switching Spray/Bucket/Brushes, reopening brush options and returning to100% all retain matching visible labels and slider values. Control-only changes preserve the document. Native project and PNG roundtrips exact. Initial fixture whole-JSON expectation failed only because Pillow and Chrome compress identical PNG pixels differently; decoded RGBA and all metadata are exact, with native history comparisons still whole-JSON exact. Earlier strength53 exploration is retained separately; strength54 is the fresh complete acceptance matrix.

## Brush size matrix completed

Native Blue marker sizes1/22/96 on960x640PLAY at85% and127% zoom. Six actual saved strokes independently satisfy declared source footprint radii+2pxAA, increasing source heights, unchanged outside pixels and exact metadata; same-sized source heights at both zooms differ by at most2AApixels. Three rapid Home/End cycles do not change whole project data; return-to-fit preserves it exactly. Native cursor screenshots show22/96rings matching paint footprint at both zooms and a visible5px minimum cue for1px. An obscured initial minimum-cursor screenshot was supplemented by a separate native tap and exact Undo. An immediate End-key read caught the previous22px label before repaint; the retained follow-up waits for and verifies visible96px with input96. No application defect found.

## Eraser matrix and fixture correction

Corrected MIX fixture, native Scrub22px/100%: Paper clears to opaque white; transparent Character clears to alpha0 and exported composite reveals exact Blue Backdrop30,136,229. Other layer data and every pixel outside the declared radius20px gesture tube remain exact. Hidden active Character is made visible and erased without changing any neighbour; Undo restores visibility and pixels together. All three whole-project Undo/Redo pairs and native project/PNG roundtrips are exact. Fixture gap: prior synthetic MIX/CADMIX paper booleans were interpreted as null; seven corrected copies now use #ffffff/null, the manual MIX pack and future generators are repaired, and original bytes/results are retained. Earlier eraser56 Paper attempt therefore did not exercise a real Paper layer; eraser57 explicitly asserts the colour metadata first.

The headless launcher now reserves an OS-selected loopback port and uses strict port binding, because Vite treats port0 as default5173. The latest full728-check run passes with zero failures/page errors at http://127.0.0.1:63424. The focused launcher check also passed at http://127.0.0.1:56938.

## Masked pixel effects repaired

Native PATCH matrix at22px/100%: opaque Red/Blue/Green and alpha128 Red invert exactly in fully covered regions, alpha and outside pixels remain exact, two full passes restore centres, and whole-project Undo/Redo is exact. Plain raster masks are binary, so the earlier verifier assumption that AA edge pixels must exist was corrected. Additional Vertical+Mask native taps exposed LIVE-051: mirrored pixel filters source-over composited the source patch, changing5226 alpha values and copying colour into empty mirrored pixels. The shared Invert/Pixelate/Emboss path now applies each destination pixel from its own immutable gesture source through a mirrored coverage mask; maximum per-gesture coverage prevents repeated compounding. Native repaired comparison has zero alpha changes,110 weighted edge pixels with maximum double-pass error1.326/255, exact transparent/outside pixels and exact history. Three focused regressions cover all affected filters. Full731-check regression, TypeScript and production build pass.

## Smudge matrix completed

Native SMUDGE320x240,22px, fixed(120,120)→(200,120): both settled raster and two animated conveyor fills exercised at100% and15%. Independent saved pixels verify rightward red displacement1589.34 versus110.89 pixel-equivalents, feathered alpha, exact pixels outside radius24px, no injected black/green-neighbour sampling, and unchanged neighbour layer. All four whole-project Undo/Redo pairs are exact. Two source animation frames match independently constructed red/blue rectangles exactly; Undo restores live definitions and the exact second animation frame. Verification:smudge60-verification.json.

## Photographic effects completed

Native Pixelate22px/100% on2100x1398 landscape and2615x3269 NASA portrait facial detail. Independent decoded files show24547 and16834 changed pixels respectively, exact alpha and every pixel outside the declared33px-radius gesture tube, and exact whole-project Undo/Redo. Adjacent equal-colour pairs increased2328→9941 in the landscape and182→4173 across the facial core. Smallest1px setting changed only14213 landscape pixels within24px of the same local path, fewer than22px setting. Native56% zoom/pan confirmed visible facial blocks. New public-domain NASA portrait retained with source, licence, dimensions and hash because the existing landscape could not exercise the specified face-detail step.

Native Emboss22px/100% across a high-contrast river detail in the2100x1398 natural photograph:32013 changed pixels, exact alpha and all pixels outside31px-radius tube, local neutral relief (mean chroma66.53→19.96), and exact whole-project Undo/Redo. Additional fixture clears only left20px; native edge-crossing stroke preserves every alpha value, clear border and all outside pixels exactly, with exact whole-project Undo/Redo.

## Exact Pencil flow completed

Native PIXEL32x32 fixture: selecting Pencil automatically sets1px; Blue fit-zoom tap changes exactly intended source(20,22), enlarged-view staircase occupies exactly the independently enumerated11 pixels, with no other changes. Saved PNG and native reopened project preserve all32x32RGBA values exactly. Evidence:pencil65-verification.json, geometry/pixel list and native screenshot.

## Splatter clipping completed

Native Splatter96px/100% Pink:#ef476f middle and right-edge700ms bursts; independent decoded pixels show62 and33 separate drop components with varied sizes, chosen colour within3/255 accumulated translucent-canvas rounding, and no changes beyond declared240px footprint. Rightmost column receives clipped drops; opposite300columns remain exact. One Undo removes the complete edge burst, Redo restores exact whole-project arrangement. verify-splatter.py passes; initial per-channel weight oracle over-amplified rounding in the low-contrast red channel and was corrected to direct channel errors.

## Confetti colour and history completed

Native Confetti96px/100% two short Rainbow bursts followed by Green#43a047 burst. Independent pixels confirm strong red/green/blue hue families, solid Green compositing within3/255 canvas rounding, exact pixels outside declared275px burst footprints, opaque Paper alpha, and exact whole-project Undo/Redo restoring the identical committed random arrangement. verify-confetti.py passes. Colour oracle selects each source pixel highest-contrast channel to avoid unstable opacity division where existing Rainbow is nearly equal to Green.

## Additional fifty-case tranche

Target:172Pass from122. Completed so far:LAYER-002,LAYER-004, with native long/blank names, opacity slider history, decoded export arithmetic and genuine live-ink preservation. Independent layer68-verification.json passes.

Native layer69/70 checks complete LAYER-008,005,006, including last-sheet protection, no-op history, keyboard focus and boundary handling. Current tranche:5 additional passes of50.

LAYER-003 hidden-source export/sampling, isolated foreground paint and separate visibility/paint Undo pass. Current tranche:6 additional passes of50;44 remain to target172.

LAYER-015 desktop/phone Photo handoffs and Basic-mode recipe preservation pass. Phone test-panel obstruction identified; original attempts retained and wrapper summary moved away from footer controls. Current tranche:7 additional passes of50;43 remain.

LAYER-001,013,014 complete: desktop/phone workshop palette and guide, inert underlying paint controls, chosen-paint return, separate caption and exact editable geometry. Current tranche:10 additional passes of50;40 remain to172. Test-panel collapsed phone position verified at y228..262, clear of Photo footer.

VECTOR-001/002/003 complete with native mode transitions, mixed-scene shapes, exact reopening, cropped gesture surfaces, isolated movement and transparent-padding hit test. Current fifty-case tranche:13 additional passes;37 remain to172.

VECTOR-005/006/008 complete: independent stamp flip/reopen, exact group transforms and zoom-independent keyboard movement with field isolation. Current tranche:16 additional passes;34 remain to172.

VECTOR-007/010/016 complete: native Alt cycle, fully offpaper recovery, exact negative coordinates/size/rotation, invalid transforms, Escape/desk settle and source retention. Current tranche:19 additional passes;31 remain to172.

VECTOR-012/013 complete: native mixed clipboard fallback and wet-source duplication isolation with exact history. LIVE-052 fixes perfectly stationary spray timing; red/green regression and native wet creation verified, full run pass2 pending. Audit server restarted on OS-selected http://127.0.0.1:61747/ after original64542 stopped. Current tranche:21 additional passes;29 remain to172.

LIVE-052 stationary spray and LIVE-053 one-step stacking complete. Full733 checks pass, zero failures/page errors; TypeScript and production build pass. Native VECTOR-011 group centre, front/back, one-step order, boundaries and phone44px target independently verified. Current tranche:22 additional passes;28 remain to172.

VECTOR-014 local vector/raster inversion, honest conversion, exact neighbours/history/reopen and oversized rejection pass. Current tranche:23 additional passes;27 remain to172.

LAYER-007 rich live/photo/object layer and CAD duplication pass; exact equivalent PNG, copy-only edit, identities, source recipes and native history/reopening. Current tranche:24 additional passes;26 remain to172.

LAYER-009 captured rich merge passes: maximum1/255RGBAdifference under predeclared2/255 tolerance, exact layer scope/history/reopen and both CAD guard branches. Current tranche:25 additional passes;25 remain to172.

LAYER-011 native static/live/closed-palette thumbnail checks pass. Initial1pxJPEG mark threshold was overly strict; source colour, mapped location and regional screenshot change independently confirmed. Current tranche:26 additional passes;24 remain to172.

PHOTO-003/004/006 complete with source-correlated Before, pending-render After, all cancellation routes, preserved multilayer source and exact independent history/PNG. PHOTO-001 remainsPartial because actual native chooser cancellation is unavailable; import/context/hidden-target branches exercised. Current tranche:29 additional passes;21 remain to172.

PHOTO-002 all15groups/6categories across desktop and three exactCSScompact layouts pass; all saved values and whole document exact after navigation-only Done. New browser viewport capability directly setsCSSdimensions (measured429→429,390→390); earlier historical110%override compensation does not apply to this connection. Current tranche:30 additional passes;20 remain to172.

PHOTO-005 editableDone/reopen/revision and forcedprocessingfailure recoverability pass. Test wrapper only adds visible one-shot Worker.postMessage failure; production code unchanged. Syntax check passes. Current tranche:31 additional passes;19 remain to172.

PHOTO-007/008 individual/group/full reset complete with explicit default and independentoriginal-composite verification; exactsource/history/Cancel. Current tranche:33 additional passes;17 remain to172.

PHOTO-009/010/011 knownTONAL-alpha ramp, independentlinear exposure, brightness, contrast±50/±100 and exactreset/source/alpha checks pass. Current tranche:36 additional passes;14 remain to172.

PHOTO-012/013 tonal isolation, endpoint clipping, exactreset/source/alpha and alpha1coverage fixture pass. Current tranche:38 additional passes;12 remain to172.

PHOTO-014 reproducibleAutoLight/naturalcomparison andclear/constantinput safety pass. Current tranche:39 additional passes;11 remain to172.

PHOTO-015 everylook in twoorders, exactwholeprojects/fullsizePNGs and Normalmanualbaseline restoration pass. Current tranche:40 additional passes;10 remain to172.

PHOTO-016 everyCustomroute andcategoryno-change passes; correctednativecropinput andindependentexactcropPNG retained alongsideinitialuncommittedfieldattempt. Current tranche:41 additional passes;9 remain to172.

PHOTO-019/FINISH-015 freshsavedlook/manualcurve/crop, threeatomicrecipe rejections, exactfullsource recovery andflattenedPNGdistinction pass. Current tranche:43 additional passes;7 remain to172.

## LIVE-054: readable complete histogram

Original42pxminiaturecouldnotbereadcomfortably; existingpolygonclippedthe255whitebinpartwayatrightedge. Expandablechartnowshowsfullwidth80pxhighbarsandvisibleclippingcounts,retainsBefore/Afterandfootercontrols,collapsesbacktoadjustmentswithouteditingrecipe. Discretebarsincludebothendpoints. Focusedfour-layoutredfailedonwhiteendpoint; greenallfourpass. Full737checks,zero failures/pageerrors; TypeScript/productionbuildpass. Nativeknownpeaks/shiftedexposure,exactBefore,emptyplotandallcompactcomparisonsverifiedindependently.

PHOTO-017 complete; currenttranche44additionalpasses,6remain to172. Main audit tab now676304876 on61747; duplicated676304968/971closedafterfilesretained. BrowserviewportAPIactsontheoriginalselectedaudittab; excludeswrongtargetattempts.

COLOUR-001/002 relativeTemperature/Tint nativepatch/skin/alpha/controlindependence andexactreset checks pass. Current tranche:46 additional passes;4 remain to172.

COLOUR-005/006/007 saturationextremes/vibrancecomparison/independentHLS hueandwrap,exactalpha/source/resets pass. Current tranche:49 additional passes;1 remains to172.

COLOUR-004 AutoWBcast/finitegains/exacthistory/empty/artisticreset pass. Additionalfifty-case tranchefrom122to172complete; originalall349liveacceptanceauditcontinues. Remaining174Partialand3Blockedareexplicitlyretained,notclaimedpassed.

## LIVE-055: wide phone preview source mapping

The miniature paints into a400x180bitmap, then CSScontains thatbitmapinsideitsvisiblebox. Oldinputmappingonlyfittedsourcetofinalbox; nativevisiblecastpatchon960x240wideimagehitredneighbour,gains.25/4/4,cast80/230/205. Bothscalesandletterboxesnowaccountedfor; samepointercoordinatesmatchpaper127greyexactlyon390/320phones. Neutralpickspaddingrejectswithoutchangingrecipe;crop-handle hitdistanceusesthesamedisplayscale. Focusedredreproducesonbothphones; greenall4layoutbranchespass. Nativeblack/white/clear/outside/paddingallsourcepixelsretained. Full741checks,zero failures/pageerrors; TypeScript/productionbuildpass.

COLOUR-003complete;173Pass/173Partial/3Blocked. Originalall349auditcontinuesbeyondcompleted50-case tranche.

## LIVE-056: preserve valid exact crop entries

Native width0 previously silently became a1px crop. Numeric crop changes now validate the whole candidate before applying it; empty, nonfinite, negative, subpixel, out-of-picture and incompatible ratio values restore the last valid frame with a useful message. Independent native project/PNG verification covers exact coordinates, all rejection branches, compatible/incompatible Square sizes, unchanged source/settings, history and320px phone. Focused red fails allfourlayouts; green and full745checks pass. FINISH-013 complete;174Pass/172Partial/3Blocked.

## LIVE-057: exact numeric curve coordinates

A pointer point at127.5 displays128. Retyping128 did not fireChromechange and left127.5saved. Edited numeric fields now commit on blur too, while merefocus leaves pointer precision intact; empty/nonfinite edits restore valid text. Native source/project/PNG proof confirms exact128/255 and128->160. Focused red2 failed allfourlayouts; firstred had a corrected test setup API mistake and is retained. Green allfour and full749checks pass; TypeScript and build pass. COLOUR-010/011/012/013/014 complete;179Pass/167Partial/3Blocked.

COLOUR-016 cancelled multipoint natural-photo draft, exact saved recipe/fullPNG and genuine deferred stale-worker reply pass. Wrapper only holds/releases standardWorker callback; no fabricated result or app state injection.180Pass/166Partial/3Blocked.

COLOUR-008/009 complete:24native mousecontrolled HSLexports independentlychecked againstPythonHLS knownpatches/boundaries/redwrap; eightdistinctrecords surviveactualsavedprojectreopenandUI, resettingeachrange preservesunrelatedWB/curves/source. A30sectoolbatchtimeoutlosthelpersbutretainedfiles; restoredconnectionandresumedlastcompletedexport, noappfailure.182Pass/164Partial/3Blocked.

COLOUR-018 refinedmonochrome/source/baseline/actualNormalcolourrecovery andPHOTO-018 full2100x1398natural fine-detailrecipe/output pass. Independent2Dintegralsharpenoraclemax1/255mean<.001; source-sizeoutputdiffersfromenlarged720pxcache; actualprojectreopenPNGexact.184Pass/162Partial/3Blocked.

FINISH-001/002/005/006 complete: preserved1024x768DETAILclean/noisyLCG12345pairwithsharp/fine/broad/alpha features; nativeallcontrols,separateandcombinednoise,resetandsharpeningextremes. Independentstrength/radius/threshold/scale/variance/colourspread/edge/alpha/exactreset/sourcechecks pass.188Pass/158Partial/3Blocked.

FINISH-004 dehazehazyfixture±49andactualmouse-drag±100endpoints independentpixel/contrast/neutral/alpha/source/resetchecks pass. Testhelperclosurekeptoldclickimplementation; directnewhelperreachesexactendpoints; previous±98attemptsretained. Sharpeningalsoverifiedexact150at.5/3radiusandbothnoise100, beyondprior149/99nearboundaries.189Pass/157Partial/3Blocked.

FINISH-003 Pop40naturalphotoexactlyequalsmanualClarity24/Vibrance8/Dehaze6fullPNG,resetRGBAexactprelookbaseline,source/settingspreserved. SmallclickonDehaze6initiallyinsideknob; native6.6pxdragcorrectlysets6; initialprojectretained.190Pass/156Partial/3Blocked.

FINISH-007/008naturalvignettes/cropanchor/stablepanel/reset anduniformPATCHshape/endpoints pass. Independentfullradialmaps andprotected/transitionpixelareasprovereach/softness/contours; source/alpha/clearborder exact.192Pass/154Partial/3Blocked.

FINISH-009naturalphotoGrain25/65 fixedpatternexactfullPNGacrosszoom/comparison/redraw/actualprojectreopen; independentcommonluminancegaincolouroracle, amountvariationandcorrelation pass.193Pass/153Partial/3Blocked.

FINISH-010fixedDETAILgrainSize.5/3,Roughness0/100,Amount100andresetpass independentneighbourcorrelation,commonRGBgain,source/alpha/settingsandexactresetchecks.194Pass/152Partial/3Blocked.

FINISH-011naturalcropnew/move/resize exactsourceslice, nonzero/outsideclamps andCancelwholeproject pass.195Pass/151Partial/3Blocked.

FINISH-012all16nativeportrait/landscaperatios resize/export/edgeclamp/Cancelpass exactsourcePNG/wholeprojectandratio/boundschecks. Initialratio130/131roundedcornerhitstage,excluded;ratio132starts8pxinsideandassertsshrink. ReopenedPhotoLabselectorFree; explicitlyreselectedratioforoutsidechecks,firstOriginal/Squarebranchesrecheckedandretained.196Pass/150Partial/3Blocked.

FINISH-016sharedMIXcropallvisiblepaint/photo/text/stamp/liveinkexactPNGslice,fullsource/reopenandlocal-onlyCharacterstraighten pass. Firstlocalaffected-boundoracleomittedRasterobjectretainedlivefills/strokes; source-boundanalysisnowincludesmaskandstrokeenvelopes; unaffectedcompositepixels exact.197Pass/149Partial/3Blocked.

## LIVE-058: accessible short-landscape Photo paper

At844x390theminiatureishiddenandright-alignedpaperwasmostlybehindPhotoPanel; Fitdidnotresolveit. LayoutnowreservesPhotoPanelwidthwhenenoughhorizontalspaceisavailable, leavingallpaperbesidecontrols. Focusedredfailedlandscapeoverlap, greenall4layoutspass; nativeknownhorizonlinefullyaccessibleandangle-11.3matchespaper/phoneminiatures. Full753checks,zerofailures/pageerrors,TypeScript/buildpass. Wrappercollapsedcontrolsalsomovedleftinshortlayouttoavoidfooterobstruction.

## LIVE-059: no empty horizon edits

Nativezero-lengthclickpreviouslychangedNormaltoCustomandcreatedasavedrecipe/Undostep. Zero/short(<=8sourcepixels)/cancelledhorizonsnowleaveallrecipefieldsunchanged,clearhelperguide,andshortsamplesexplainlongerline. Nativezero/shortsavedprojectsexactbaseline; nearverticalbounded-45; independentchartfitandidenticalpaper/mini/repairedlandscapePNGs pass. Four-layoutredfailsall4;greenpassesall4; TypeScript/buildpass, full59runpending. FINISH-017complete;198Pass/148Partial/3Blocked.

LIVE-059fullregression757pass,zerofailures/pageerrors. FINISH-018exact±45and50/200scale,independentfullgeometry/source/alpha/cornercoverage/resetpass. SourceisretainedidentityRasterobjectinVectormode; correctedinitialoraclethatreademptylayercanvas.199Pass/147Partial/3Blocked.

FINISH-019PhotoH/Vflips exactchartreflections,wholeUndo/Redo andMIXselected-sheetonlywithstationarycaptionstamppixels pass.200Pass/146Partial/3Blocked; auditcontinues.

FINISH-020/021knowninverse-projectiveboth-axis/signfixtures,±75endpoints,wrong-axiscomparison,combined/resetpass independentconvergenceandfullgeometry/source/alpha/framechecks.202Pass/144Partial/3Blocked.

FINISH-022knowninverse-radial±directioncorrections+70/-35,manualrefinement,±100extremes,safealpha/sourceandresetpass independentbowandfullradialpixelchecks.203Pass/143Partial/3Blocked.

FINISH-023fringe±100sixspatialRGBedges<.1pxcoincidence, oppositeworsening,exactGreen/alpha/flats,source/frame/savedrefinement/reset pass.204Pass/142Partial/3Blocked.

FINISH-024tenqueuedgeometrychanges withgenuineheldreply,latestpreview/freshreopenexact,independent760x520fullmappingandactualCancel/newsession/retiredreply exactpaper/project/PNGpass.205Pass/141Partial/3Blocked.

## LIVE-060: nearest crop corner and truthful numeric fields

On320x568a960x240wide sourcewith480x12cropat288,60,draggingNWto192,48selectedSWbecausethelastcornerwithin16pxwon. Saved576x12instead of576x24. FocusedWidthalsoheldstale480afteractualwidth576; reselectinggrouprevealedtruth. Nearest-distancecornerhitnowwins,andphotocanvasgesturesblurthenumericinputbeforeediting. Nativecorrectedcrop576x24/fields/sourcePNGexact; all4corners/focusregressionredfailsall4layouts,greenpassesall4. InitialapparentmovewasstaleWidth,notlayoutshift; interpretationcorrectedandattemptsretained. TypeScript/buildpass; full60runpending. Phone014remainspartialforphysicaltouch.

LIVE-060fullregression761checks pass,zerofailures/pageerrors. FINISH-014native16gesturewide/naturalx320/390matrixsource/size/coordinates/exactPNGs pass,physicaltouchremainsPartial. TestpanelhiddenviavisibleHidecontroltoavoidMiniobstruction. Scope-sourcegitdiffcheckpasses;separateplanninghandoff/defaultdistbuildobservedandleftuntouched.205Pass/141Partial/3Blocked.

ENHANCE-001visiblecroppedMIXcapture/hiddenreference exclusion/unchangedclose pass.206Pass/140Partial/3Blocked. User now requests cost-conscious easy fixes plus reproducible notes for harder issues for later Sol/Astra work.

ENHANCE-002 exact160x120→320x240/640x480 real neural PNGs, exact independently resampled alpha and byte-identical editable original.207Pass/139Partial/3Blocked. Colour-padding twin proof in progress.

ENHANCE-007 real2x/4x semitransparent card, exact independent alpha/all clear RGBA, opaque colour-extension twin proof and black/white inspection pass.208Pass/138Partial/3Blocked.

## LIVE-061: enhancement overview coordinates

Native2100x1398 photo quarter-detail click expected461,985,128,128 but selected476,975,128,128. CSS2pxborder was included in object-fit mapping. Point conversion now uses the content box and initial blank-source presses are ignored; active drags still clamp. Native corrected exact461,985 and actual blank margin leaves it unchanged. Earlier12pxmargin probe actually hits source and is excluded as a blank-margin test. Focused exact-coordinate/border/drag regression fails all4layouts before fix and passes all4 after. Initial filtered test omitted Advanced setup and one half-pixel rounding tie; corrected before valid red/green. Build/typecheck pass. Full61 regression running.

ENHANCE-003/004/005 known photo source selections/native64/128/256 previews, small-source clamping, exact8/32keyboard steps/opposite directions/repeatededge clamp/stale invalidation, true neural and truthful Before/Enhanced lettering comparisons pass.211Pass/135Partial/3Blocked. LIVE061fullregression765checks pass,zero failures/pageerrors.

ENHANCE-006 fullcroppedMIX1600x1120realneuralPNG,5sheets/projectbyteexact,wholeimagecoverage117bands/sourcecorrelation.9954 pass.212Pass/134Partial/3Blocked.

ENHANCE-008 grid/gradient/diagonal2x/4x9tiles, completePNGcoverage and shiftedtileorigin comparison pass.213Pass/133Partial/3Blocked. ENHANCE-009 nativeCancel/ESC/sourceexact/newjob pass, but progress log corrects firstcancellation to tile2afterfastdownload; slow uncached-model-download stage remainsPartial.

ENHANCE-012actual47MPneural4xfullPNG726tiles/CRC/zlib/allrows/source/framebyteexact plusprior2x/4xtransparentedge limits pass. SOLID-001safeentry/reentry/Paint/sourcepreservation and SOLID-003independent20mmclosed8000mm3cubeafterorbit/zoom pass.216Pass/130Partial/3Blocked.

SOLID-002all8actualprimitiveSTLs/4views/manifold/volume/genus/oneUndo/sourceexact and SOLID-009nonuniform20x10x30→40x20x60proportionalvs40x10x30free/actualSTLs/anchor/Undo pass.218Pass/128Partial/3Blocked. InitialemptytypeTextprobeexcludedandgenuineBackSpaceemptyrejected;CADcachedimagechangesexpectedonresize,paint/sourcefieldsretained.

SOLID-010physicaltube2/3mm/radii/bore/volume/outside/rejection/sourceexact and SOLID-011all6palette+custom/7nativeprojects/identity/otherbody/source/reopen pass.220Pass/126Partial/3Blocked. CADpreview2edgepixelsrequantize<=2onreopen,alpha/opaqueexact;sourceunchanged.

SOLID-004unique1/2/2/0/2selection/hidden/locked, SOLID-012nestedcopy/scopedchildrebuild/actual70mmmesh/originalsource/Undo, SOLID-013selectiveDeleteUndoRedo/locked/emptyprotection, SOLID-014pieceandlayerhide/lock/scopedmeshes/source restore pass.224Pass/122Partial/3Blocked.

## LIVE-062: selected STL respects the picture layer eye

NativeSelectedvisiblepiecesexportcheckedhiddenShellmodellayeras35x20x20/6.69cm3whilepieceHiderightlyexcludedhiddenbody. Selectionscopefilteredbody.visiblebutignoredactiveLayer.visible. It now requiresboth,matchingcurrentlayer/allvisiblemodes. Four-layoutfocusedtestfailsbefore/passesafter; build/typecheckpass. NativefreshbuildhiddenlayerCheckandExportbothreject,restoringeyechecks/exportsactualcorrectgeometry. All3hidden scopesreject. InitialonebatchstatuswasstaleSTLreadyandwasrepeatedaftersettling; correctedactualerrorretained. Full62regressionrunning.

LIVE062fullregression769checks pass,zerofailures/pageerrors.

SOLID-015native2CADlayercreation/ownership/16totallayerguard/13Undo, SOLID-016sametarget/full127destinationreject/2bodymoveUndo, DELIVER-020nativeoverlappingmultilayer4actualSTLs exact20000/12000/8000/12000mm3/manifold/nointernalplanes pass.227Pass/119Partial/3Blocked. Capacityfixturedeclaredmodernandderivedfromnativevalidscene. InitialhiddenFarselectionstatusstalep probeexcluded;actualhiddenFarallvisibleSTLprovesomission,selectedhiddenlayerrejectionindependent163164.

SOLID-006exact[-12.5,4,10]/Z30/independentrotatedvertices/worldbounds/8000mm3/UndoRedo/invalidsourcepreservation pass.228Pass/118Partial/3Blocked.

SOLID-005nativeX20/Y10/Z20/XY10,10/oneUndo/20actualprojectsourcechecks andgenuineheldbuttons1captureloss/coherentcancel/newgesture pass.229Pass/117Partial/3Blocked. SOLID-017all5gridincrementspositive/negative+SnapOffpass;angle matrixremains. NewdisposablecaptureAPIcontrolmustbearmedoutsideisolatedCAD(auditpanelisinertwhileCADopen);nativeeventproofretained. Noappsourcechange;node --checkpass.

## LIVE-063: keep numeric CAD drafts across background refreshes

Unchangedscene/previewrefreshesrewroteblurrednumericfieldsfromthecommittedmodel,discardingearlierentrieswhileenteringthenextfield. NumericformstateisnowrefreshedwhenactualdisplayedmodelvaluesorselectedIDschange,notoneverybackgroundrefresh. Newcommittedchangesanddifferentpiece selectionstillreplacethefields;busyupdateswaituntilcompletion. Deterministicfour-layouttestfailsbefore/passesafter,includingsequentialsize/positiondrafts,Apply,externalmodelchangeandotherpiece selection. NativeblurredDepth10survivesactuallayerHide/ShowandApplyproduces20x10x30/3000mm3wedge;actualsavedproject/STL/independentverticeschecked. Earlierwrong-depthnativeentryalsohadunreliablekey-helperinputandisnotclaimedasstandalonecausalproof. Scopedfieldinputusedforreliableliveentry. Build/typecheck/diffcheckpass;full63regressionrunning.229Pass/117Partial/3Blocked.

LIVE063fullregression773checks pass,zerofailures/pageerrors.

SOLID-007asymmetricWedgeall3ringsfree/snapped/6actualSTLs/independentaxis,pivot,vertices,outwardvolume/Undo and SOLID-017all5distinctangularsnapresultsfromsamefreegesturereference+priorall5positive/negativegrids/SnapOff pass.231Pass/115Partial/3Blocked. Browserdownload-eventAPIunreliabledespiteactualdownload; filesystemcompletionused. REPLprimitivecounterclosurestalevaluescorrectedagainstactualfilesandmutableobjectcounters;missingexportsnevercounted.

SOLID-022threeaxisfullyasymmetricnegative-scaleactualSTLs+HOLLOW173mirror/reimport and DELIVER-016sixindependentlyencodednestedcavitywindingvariants/allactualprojects+STLs/32exactvertices/signedcomponents1000,-216,8,64=856mm3 pass.233Pass/113Partial/3Blocked. NativeZ5cutaway retained. Noappsourcechange.

DELIVER-015sixnativeunit/centrecombinations/actualprojectsandSTLs/independent32vertices/cavities pass.234Pass/112Partial/3Blocked.

## LIVE-064: place actual rotated mesh bounds on the bed

Nativefullyasymmetriccompoundatrotation20,30,40andscale1.5,.75,2:ToBedleftactualminimumZ5.25mm,andCentreoffsetXY. Viewport.bounds usedtransformedlocalboundingboxcorners,whichoverestimatean asymmetric rotatedmesh. setFromObject(mesh,true)nowmeasuresactualworldvertices. Focusedcompoundregressionfailsall4layouts oldDropandpassesall4fixed;earlierwedgefixtureindependentlyfailedcentrebefore/passedafter. Nativeoriginalsavedscene reopenedfixedbuild,actualDrop/CentreSTLverticesmatchindependentZYXmatrix/worldminZ0/worldXYcentre0/6894mm3andunchangedshape/paint/source. TwoUndoexact. Build/typecheckpass,full64regressionrunning. SOLID-018Pass;235Pass/111Partial/3Blocked.

LIVE064fullregression777checks pass,zerofailures/pageerrors.

## LIVE-065: reject locked moving alignment groups atomically

Native3selectedpieces withlockedcompanion: Align movedonlyunlockedasymmetricpieceX-13to125.522734andreportedsuccess. Alignnowvalidatesallmovingpiecesbeforemutation,rejectslockedgroupswithUnlockexplanation;fixedlockedreferenceallowed. Fourlayoutvalidredfailsactualpartialmutation,greenpassesincludingunlockedretry/Undo/lockedreference. Initialfocusedtestclickedwhilebusyandfailedbothred/greenatmessagecheck; excluded,waitforreadyaddedbeforevalidred/green. Nativefixedactualbefore/afterprojectsourceexact. All15axis/modeactualprojectsindependentlymatchtrueasymmetricworldboundsandgap/overlap; target/source/paintpreserved,Undoexact. Originalnormalattemptselectedonlymoverandcorrectlyerrored;discardedandreopeneddeclaredtwo-bodyfixture. SOLID019Pass;236Pass/110Partial/3Blocked. Build/typecheckpass;full65regressionrunning.

LIVE065fullregression781checks pass,zerofailures/pageerrors. SOLID021native1/3/30rowand+90/-90circularseries/allactualsource/uniqueIDs/nestedrecipes/Undo,0/31reject,anddeclared127bodycapacity+2atomicreject/+1exact128/Undo pass.237Pass/109Partial/3Blocked.

SOLID008nativeXsizehandle38x10x30/closed5700mm3sixvertices,sharedmultiselectionratios2,.5,1.25/actualsource/anchor/Undo/0negativeemptyoversizerejection pass. Nearzerohandlesactualsource+.1and-.1bothpositivephysical2mm;secondvalidmirror,notobservedsingularerror. Exactfreehandzero notclaimed.238Pass/108Partial/3Blocked.

SOLID020nativefacepair/independentnormalsandcoincidentplane/actualclosed8000mm3STL/targetandothersourceexact/oneUndo,wrongfirstcurvedlockedidenticalrejection pass. All22SOLIDcasesnowPass.239Pass/107Partial/3Blocked.

DELIVER01712nativeinvalidvariants/sourceexact/retryexact20MBASCIIandgenuineclosed200000triangleprism/actualprojectsandSTLs/vectorisedindependenttopology/outwardnormals/analyticvolume pass.240Pass/106Partial/3Blocked.

DELIVER018simpleimportreal2mmShell/3904material/4096cavity/originalsourceandUndo,200000triangleprecisionhonestrejection/sourceexact,verifiedmoveUndo,andactual200016trianglethroughcut/genus1/12000removed/sourceUndo pass. Earlieruncommittedmoveattempt excluded; longcomplexBooleancompleted,noinferredtimeout.241Pass/105Partial/3Blocked.

## LIVE-066: identify oversize printer axes

NativeprinterreportgaveLargerthanbuildvolumewithoutnamingaxes. ReportnowlistsactualoversizeX/Y/Zusingworldmeshdimensionsandenteredbed,same.001mmtolerance. Fourlayoutfocusedredfailsmissingaxes,greenpassesrotatedscaledfixture/selectionvslayer/hidden/volumes/counts. Native9fullyasymmetricworldboundcasesplus3actualindependentlydecodedSTLsproveaxes/scopes/visibility/fit/bedtranslationandsourceunchanged. Earlywrongselection/stalereportattemptsexcludedandrepeatedwithverifiedselectionandinputTab/separateCheck;reloadfilenameunmappedexportexcludedandnamedrepeatretained. Build/typecheckpass;full66running. DELIVER019Pass;242Pass/104Partial/3Blocked.

LIVE066fullregression785checks pass,zerofailures/pageerrors. DELIVER014equivalentbinary/ASCIIactualsourceandSTLs,compleximportnativeMove/Cut/nestedoriginalrecipes/Undo,simplemeshrealShell pass.243Pass/103Partial/3Blocked.

DELIVER00214nativeexactviews/allcorrectaxes/up/asymmetric/sourceexact; DELIVER003orthoparallelvsperspconvergence/bothportraitandlandscape/Fitspan/allworldverticesinside/explicitperspPin/viewportreset; DELIVER007localvsworldbounds/selectionupdate; DELIVER011previousPinUndoRedo/PaintFileSaveCADreopensamecamera pass. Source22desktopSavepreservedpreviouspinnedorthoviewbydesign;helperomittedKeepView,excludedandrepeatedexplicitPin23. Viewportcapcurrentlytargetsmainworkshopnotoldlimit;actualDOMdimensionsverifiedandunusedother-tabsetupnotcounted.247Pass/99Partial/3Blocked.

DELIVER021whole3componentbedtranslation/offon/22actualvertices/volumeandrelativepositionssourceexact and DELIVER022complexjoinShellindependentanalyticinwardarcarea/removedvolume/sevenrays/openingfloorwalls/manifold pass. Expected6688.252184vsactual6687.853948mm3,.398236tessellationdifference.249Pass/97Partial/3Blocked.

DELIVER008allappearancemodes/leavefullopaque,DELIVER009all3sectionaxes/bothsides/Z2,10,15,andDELIVER023rolledhistory/unappliedpreviewexportguards/LatestCancel/finalfulloutputs pass. All14projectswholeJSONincludingCADPNGexact;bothactualSTLsbyteexactpreinspectionreference. InitialhiddenSTLbuttonnotcounted,visiblePrintrouteexecuted. ImmediatepostCancelframewaspreviouspreview;settledfreshfullopaqueimageused.252Pass/94Partial/3Blocked. Noappchangeafter66full785pass.

DELIVER004native2projectionsxselected/empty/hiddenfallback/savedcameraindependentworldvertexfrustum/sourcepreservation;DELIVER005cubeexact34.641diagonal/delta20each/thirdreset/Clear/wholeJSONexact;DELIVER006knownnormal0/45/90/180andorbitbetweenpicks/noaccidentalpoint/sourceexact pass. SomeFitpendingimagescapturedaftervisibilitychanged;reopenedimmutable1/3settledscreenshotsused. ImmediateARIAafterEscapestale,actualcamera2/3bothallfit,oneexcludedasredundant. DELIVER001orbitpickprotectionpassbutrightpaninputgapstillPartial.255Pass/91Partial/3Blocked.

DELIVER012nativefreshcopiesAbove/Belowtransparentnormaladjacent/actualBluepixelstrokesonnewlayeronly/StrokeUndoandLayerUndoexact/sourcecamera/model/photo/annotationpreserved,declared16layerbothguards/sourceexact/nohalftransition pass. Delayedmixedphotosavesretainedwithoutduplicates;completionhelperoldclosurecorrectedusingobjectfunction20seconds. AllDELIVERcasesPass exceptrightpan001inputgap.256Pass/90Partial/3Blocked.

SKETCH001all3cartesianfixedplanes/actualclosed3000mm3/unfinishedplaneanchorsreset;SKETCH002exactrectangleandCirclecentre30,10diameter20/independent96gon/reopenededitablefields;SKETCH00510x10positive30/0emptyrejectthenvalid/oneUndo;SKETCH006negative10belowzero/closedoutward1000mm3/oneUndo pass. All5actualproject/STLoutputsandemptyrestore/sourcepaintexact.260Pass/86Partial/3Blocked.

## LIVE-067: reject unconstrained crossing or touching outlines

Nativebowtie4points0,0/30,30/0,30/30,0wasacceptedandprintedClosedsolid5400mm3/16triangles,butindependentSTLhasedge15,15,0..12sharedby4faces. solveSketchreturnedrawseedwithoutanyoutlinevalidationwhenconstraintsabsent. Sharedvalidatornowappliestoraw,constrainedanddrivencircleresults;nonadjacenttouchesalsoinvalid,adjacentcollinearboundarypointsremainvalid. RealCADworkerregressionredfailsoldexport/greenpassespropercross,touch,collinear,collapsedandvalidconcaveCW/CCW. Nativefixedrejects0pieces,valid6pointLclosed6000mm3/notchunfilled,theninvalidattemptpreservesexistingLexact;oneUndoempty. Build/typecheckpass;full67regression786checks pass,zerofailures/pageerrors. SKETCH003Pass;261Pass/85Partial/3Blocked.

TAPER193 completed native boundary/history/cancel and five independent mesh checks. Untwisted taper exact; twisted volume +1.94457%/-1.00098% beyond unchanged0.1% criterion. SKETCH011 remains Partial; reproducible inputs/outputs and geometry-review plan retained in COVERAGE-GAPS.md. No app change;261Pass/85Partial/3Blocked.

SKETCH012/013/014Pass: REVOLVE194 all3presets/fullnativecutaways, custommousepoints/drag/numericprofile, malformedprofiles/anglesreject, actual180annulusendcaps/360Historyedit/Undo. All6project/STLoutputs decoded independently, exactprofiles/axis/sourcepaint, analyticvolume within0.1%, realcavityrays. All6projectsnativelyreopened. Interruptedunpersistedreopenbatch excluded and repeated in bounded batches. Oneexportclickedbeforeprevioussavefinished didnotarrive; separate settled retry retained. Noappchange;264Pass/82Partial/3Blocked.

SKETCH015/016Pass: BOOLEAN195 nativeall4operations/bothsubtractorders/realgappedUnion2components2000vsHull3000/insidecylindercut, actual9STLs+15projects, independentlyanalyticboundsvolume/topology/cavityrays. Emptyintersectionatomic. Nestedsourcewidth20to30, failed1cubeinsidecutter preservesfinal+draft, Cancel/Undo/Redoexact. All9savedprojects reopened/nestedsourcestrees; unrelatedfarCADlayerandpaintpreserved. Noappchange;266Pass/80Partial/3Blocked.

FEATURE001/002/003/005Pass:196native6names/twopages/actualreopen; source5to6to7Previews/Cancelbyteexact/sourceApplysingleUndoRedo; attachedThroughallhole+filletactual7mmmeshclosed/analytic/rays. SuppressEnableUndoexact, missingfinishsupportclearerror/atomic. Unrelatedphoto/model/annotation/sourceexact. FEATURE004lateworkerCancel and008ambiguousattachmentbranches remainPartial. Observeddesktop timelinegroupingstaleafterphoneviewportchange;197longreproducerinprogress beforefix.270Pass/76Partial/3Blocked.

## LIVE-068: regroup the timeline after responsive resizing

Native197eightstepmodel desktop6buttons remained6after320phone resize, targets33px;844x390landscape38px. CadFeaturePanel nowlistenscompactquerychanges including shortlandscape, preservesinspected/firstvisibleanchor and includesgroupsizeinsignature. Isolated realviewportregression validredfailslostpageanchor/greenpassesdesktop/phone/landscapereturnandselectedstep4/sourceexact. InitialredsetupforgotAdvanced;excludedandcorrectedbeforevalidred. Initialpartialfixstilllandscapeundersize; native38pxconfirmedandqueryextended. Nativefixedphone3x72px, middle4selectedacross390/844/desktop; all10treeentries/fourlayouts/twopages/firstmiddlelast keys stable. Latestprojectsexactbefore/after; actualSTL3expectedcomponents/platevolume+16mm3. InitialemptySelectedexportguardandphoneCtrlSprobeexcluded; visibleLayersSelectAllanddesktopProjectguardexecuted. Instantresizeoldframeexcluded; semanticwaitsused. FEATURE006/007Pass. Build/typecheckpass;full68regression787checks pass,zero failures/pageerrors.272Pass/74Partial/3Blocked.

CANCEL198 pendingfeatureCancel nativeclick ineffective duringactualbusy8mmpreview(singlejobstall), real45stimeoutretainsdraft; CancelaftertimeoutandrestartedenginePreviewCancelrecoverexact7mmproject/STL. Deferredlifecyclefinding recordedwithsourcepaths/repro/evidence, noobservedcorruption. FEATURE004Partial retained. Noappchangeafter68full787pass;272Pass/74Partial/3Blocked.

CONSTRAINTS199 SKETCH017/018/022Pass: actualirregularquad35/40/45drivinglengths/H0/V1; threeclearconflicts preserveoutline, correctinsamedraftpreservespriorIDs; removeV1thennew60degline/source/mesh/UndoRedo. TenactualSTLs matchsourcevertices/independentarea*10/closedtopology; actual45andfinalprojects reopened. Ineffectiveinitial40/H0/empty-errorattempts excluded and explicitly repeated with settledfields, definitions and actualsources; nofalseacceptance. SKETCH021staysPartial: nativeLABELS200centre45mmclickhits0deglabeldueoverlap. LIVE069measuredtextboundsseparation greenrealpointerfourlayouttest; build/full69/nativeproof pending.275Pass/71Partial/3Blocked.

## LIVE-069: separate sketch dimension labels so clicks select the intended rule

NativeLABELS200known5-rulequad:45mmlengthtextsharesmidpointwithtwo0deglabels; centreclick45selectsother0degID/value0. SVGdrawnowseparatesmeasuredtextboundsandexpandsviewBoxforunclippedlabels. IsolatedrealpointerredfailswrongselectedID; greenall6labels/fourlayoutspass/nonoverlap/unclipped. Nativeall4actualsavedlabels/fourlayouts hitownIDs; originalcompactunscrolledclickclippedoutsidepageexcludedandnativepanelscrollrepeated. Label45to50actualsourceonlydesiredvalue+solvedpointschange; closedmeshEuclidean50mm/60degneighbour/independentshoelace903.47369485mm2*10volume; actualUndoRedo/reopenCancelexact, bothSTLsbyteexact. SKETCH021Pass. Initialverifierloopvariableoverwrittenwascorrectedwithoutchangingoraclecriteria. Build/typecheckpass;full69regression788checks pass,zerofailures/pageerrors.276Pass/70Partial/3Blocked. Noappchangeafterfull69run.

SKETCH020Pass: DIAMETER201 nativeellipse20x10centre30,10 becomesround24then30driven96gon, actual3closedSTLs/sourcecentreanddiameter/exactpolygonvolume pluspredeclared0.072percentcontinuousdiscretizationbudget. Zero/conflictingdiametersrejectpreservingoutline, labeleditretainsID, UndoRedo/reopenexact. Polygonaftercirclehasnodiameteroption; actualCancelpreservessource. Noappchangeafter69full788Pass.277Pass/69Partial/3Blocked.

## LIVE-070: contextual sketch dimension limits and units

NativeANGLES202 -1/181anglebetweenvaluesrejectedbutmessageclaimedfinite millimetres/workspacelimits. CADconstraintnumericvalidationnowretainsallsameranges/rejectionmathandreportsdimensionname/exactbounds/units: Anglebetween0..180degrees, AngletoX-360..360degrees, Length0.01..20000mm, Diameter0.01..2000mm. NativeFEEDBACK203all4messages/unchangedoutline/Cancelactualsourcesexact; bothSTLsbyteexactindependentlyverifiedangle110and30mmcircle. Message-onlychangeusesexistingtestsandnativecases; nonewtestmirroringstringsadded. Build/typecheckpass;full70regression788checksPass,zero failures/pageerrors. SKETCH019Pass: all4relationtypes/sixactualmeshes/independentvectors/area/closedtopology/actualreopenCancelsourceexact. NativeSaved-pageimmediateCancelmissrepeatedaftersettledrender; nofalseoutputclaim.278Pass/68Partial/3Blocked.

SUPPORT204 SKETCH004/008/009Pass: Spherecurvedreject/noplanesourcechange; twocubetoptrianglehalveswholefacecentre20; orbitretains4corner10square/Join10far30/volume9000; exactrecessfloor15/500removed/bounds20/UndoRedo/nativeReopen; Throughalloverridesdepth1/height20to30 actualholeZ-5..25/96gonvolume/emptycentre/closedEuler0. Missingfootprintsupportstops/sourceSTLexact. NewdeferredFEATURE008finding: FixedXY25conversionclearsThroughallbutkeepsheight-1, closesintendedholeto1mmpocket/centreRay-5..24/material11987.442599vs11623.277976. Originaloraclefailurepreserved; reportPartialexplicit. Depth30manualworkaroundactualsource/mesh/UndoRedo verified, notproductfix. Hardqueue3findings nowTAPER193/CANCEL198/SUPPORT204. SKETCH010rotatedoppositefacevariantsnext. Noappchangeafter70full788Pass.281Pass/65Partial/3Blocked.

SKETCH010Pass: SUPPORT205 actualoppositerotated/nonuniformscaledcube faces,10square+7outward; bothnormalsfully3D/non-worldZ, volumes18700/27700afterupstreamlocalheight20to30. IndependentRzRyRx+scale/corners/worldbounds/projectionfar7/noepsilonextension, closedEuler2. Padrecipesunchangedwhileattachmentsfollow; bothsizeUndoRedoandactualreopenCancelexact. PreservedSketch-tabentrykeptdeclaredfixturecamerauntilfacepick, no appstateinjection. Noappchangeafter70full788Pass.282Pass/64Partial/3Blocked.

EDGE206 FEATURE010/011/012/015Pass: native12cubeedges/individualtoggles/twoedgesorbit/Clear0; invalid50fillet/chamfer clearerrors and sameeditor2correction. ActualSTLconstantR2vertices/rays/volume7982.822654vs7982.831853(.03mm3budget); chamferrealplane/setbacks2/exact7960; bothclosedEuler2. OneUndoRedoexacteachApply; invalidchamferCancelsource/STLbyteexact; bothsavedprojectsactualreopenCancel exact; nativeX0sectionsretained. Ignoredtransitionexportclickexcluded/repeatedsettled. Noappchangeafter70full788Pass.286Pass/60Partial/3Blocked.

RESELECT208 FEATURE014Pass: earlierfilletoriginal12edgecube/differentbottomfrontedge, PreviewCancelexactsource/STL, Applylaterchamferretained/rebuilt; independent4realSTLsrays/closedEuler2/analytic7942.831853within.03mm3, oneUndoRedo/actualreopenCancel/sourceandfinalSTLbyteexact. EDGE207cylinder2/drilled14wholeedges/circularrefsverified; drilledentrancevolumeerror.040126exceedsoriginal.030mm3, criterionretainedfailedandnoted. FEATURE009remainsPartial. Noappchangeafter70full788Pass.287Pass/59Partial/3Blocked.

RIMS209 FEATURE013Pass: declaredconcentricR9.9/10tube wall.1, nativeinner-topcirclepick, equalchamfer.05; sameCIRCLErank0/group2ref afterupstreamwall.12. ThreeactualclosedEuler0STLsindependentanalyticvolume.1mm3/rays.003mm preserveouter10andlowerbore, innerbevelmoves9.9to9.88. UndoRedo/reopenCancelexactsource; finalSTLbyteexact. Noappchangeafter70full788Pass.288Pass/58Partial/3Blocked.

SHELL210 FEATURE016/017Pass: native20cube3wall topopen4668/sealed5256/twoadjacentopen3954mm3, allrealclosedSTLs/20bounds/independentraysfloor3side3/negative2744sealedcavitycomponent. TwoopeningUndoRedoexact/allthreeactualreopenCancelsourceexact/nativeX0sections. Noappchangeafter70full788Pass.290Pass/56Partial/3Blocked.

SHELL211 FEATURE019Pass: reselectunshelledsource, top/wall3toRight/wall2 belowlaterR1bottomfillet. Canceloldopening/thickness/source/STLbyteexact; Applylaterref+actualR1surface retained, cavities/analytic4663.707963and3387.707963within.03mm3/allclosedEuler2. OneUndoRedo/actualreopenCancel/source/finalSTLbyteexact. Sharedtriangle-rayoraclefactoredintostl_oracle.py; noproductionappchangesafterfull70/788Pass.291Pass/55Partial/3Blocked.

SHELL212 FEATURE020Pass: knownjoinedcube/cylinderShell3, wall50reject/3correctinsameeditor; earliercylinderheight10removesoriginalcomplexcap, explicitreferenceerror/20correctinsameeditor. BothCancelexactsource/STLsbyteexactpriorindependentlyverifiedshell20-top. Noappchangeafter70full788Pass.292Pass/54Partial/3Blocked.

LOFT213 FEATURE021/022Pass: native3orderedrectangles ruledexact40000/3mm3/closedEuler2/onecreationUndoRedo; collapsedplanesreject/Cancel exact; min2max16buttonsdisabled. All3independentsize/centre/originXYZ/turn30edits andexplicitreverse, 5actualclosedSTLs/unrotatedsections/editedanalytic13173.333333within.03/reversephysicalequivalence. Actual3projectsreopened/allpublicprofilevaluesmatch/Cancel/source/finalSTLbyteexact. Smooth3profileinterpolationcontinuouswaistjump.057908vsruled1.5; FEATURE023awaitsconstraintpreservationvariant. Noappchangeafter70full788Pass.294Pass/52Partial/3Blocked.

LOFT214 FEATURE023Pass extendsLOFT213smooth/ruled3profilegeometrywithactualconstrained2profilestylechange. BothruleIDs/points/planes/turnspreserved; bothclosedSTLs/exact8250mm3/linearsections. UndoRedo/actualsmoothreopen2solvedrules35mmlabel/Cancelwholecanonicalsourceexact. Noappchangeafter70full788Pass.295Pass/51Partial/3Blocked.

## LIVE-071: disable form point controls at supported limits

NativeSWEEP215Add64andRemove2remainedenabledandclickswereignored. SharedformcontrolsnowdisableAddatpath64/profile256andRemoveatpath2/profile3, retainingallgeometryguards. NativeSWEEP216history61adds/62removalsconfirmsdisabledstates; builderpath2/64andprofile3/256viacoordinatefixturesalsoverified. Build/typecheckpass; full71regression788checksPass,zero failures/pageerrors. No newmirroringtestforlowimpactbuttonstate; existingregressionplusnativeboundaries. FEATURE025/026Pass: true8x4threepointmiter/1280volume, independentcapsperpendiculartangents/area32/transformedcorners, threeprojectionnativemousedragsandexact22,4,24/allSVGpairs. Actual4closedEuler2STLs/area*pathlength1366.900268/.03budget/UndoRedo/reopenCancel/sourceandSTLbyteexact. Duplicate/closedreject/correctinsameeditor.297Pass/49Partial/3Blocked.

SWEEP217 FEATURE027Partial: straightRoundrealR4/analytic1266.265482within.03; miterroll30area32caps/volume1280; smooth4x2roll30area8caps/independentHermitearc40.81980363/volume326.558429within.1. All4actualvariantsreopened/sourceexact. Newhardfindingtight4x2section+10timescompressedpath accepted/Printclosed, actual81070triSTL883nonmanifoldedges(882degree4+1degree6)/3zeroareatriangles, exactrawcoordinateincidence. ActualbadreopenSTLbyteexact. OneUndo/finalgoodreopenrestorevalidsource/STLbyteexact. DeferredSWEEP217; originaltight-safetycriterionretainedfailed. Full71/788Pass unchanged.297Pass/49Partial/3Blocked.

SHAPES218/219 PLAY004Passfullcoverageexpansion: fivegeometricfamilies normal/reverse/tiny8x6+eachnineoutline/fillcombos,60actualsavedpathsindependentanalyticboundaryvertices. EachfamilyUndoone/Redoexact/allpreviouspieceswhitepaintexact; actualbothprojectsreopenedJSONexact/PNGsRGBAexact. IndependentPNG603274/537927safeinterior/exteriorpixelsmatchanalyticpolygons; antialiasedgeexclusions1.5/3.5pxdeclared. Full71/788Pass unchanged.298Pass/48Partial/3Blocked.

DECOR220 PLAY005Passfullmatrix: star4/5/6heartlightning normal/reverse/tiny8x6+eachnineoutline/fillcombinations.60actualpathboundaries/602903+534255safePNGpixels matchindependentpolygonsincludingnotches/concaveinteriors. EachfamilyUndooneRedoexact/earlierpiecesandwhitepaintexact/bothactualprojectreopenJSONexact/fourPNGsRGBAexactperpair. Full71/788Pass unchanged.299Pass/47Partial/3Blocked.

ARROWS221 PLAY006Passfullmatrix: all4arrowdirections+roundRect normal/reverse/tiny8x6/narrow4x80+9styleseach. All5normalpieces150x80resize targetmatrixonly/localpathexact/top-leftstable/neighbourspreserved; roundcornersremaincurved. All65independentboundaries/5PNGssafepixels598100/597708/525318match. FamilyUndoRedo/lastresizeUndoRedo/actual2projectsreopenJSONexact/PNGpairsRGBAexact. Initialcoveredcanvasselectionexcluded/visiblepiecepickerused. Full71/788Pass unchanged.300Pass/46Partial/3Blocked.

## LIVE-072: keep nearby point-path corners until explicit completion

PATHS222native8x6fourpointPolylinecloses3pointtriangleonfourthtap, usingfixed18document-unitclose-radius. Radiusnowshrinkswithnearestnonzeroknotspacing; ordinary18radius/double-click/explicitFinishretained. Isolatedrealinputredfailsfourthcorner/greenall3familiesFinish+tapstart+oneUndo; nativePATHS223allfourknots/openclosedcorrect. EnterandbuttonUndoBEFOREanySaveprovescompletion; focusedcanvasEscapeexact/onepointFinishnoedit. OlduntargetedEscapeexcluded; Saveintentionallyeditor.settlecompletesdraft, notafailedpreviewguard. NewregressioninitiallyleftshapeOutlinesettingchangedandcausedoneunrelatedmaskedpreviewfailure; testcleanupfixed. Full72pass2:789checksPass/zerofailures/pageerrors, originalfailedfullrunretained. Build/typecheckpass.

PLAY008/009/010Passfullmatrix:13corepaths/3families9styles+reverse, tinyclose/open/normalSplinevsPolylineknots/maxadjacentturn3.884deg, near/duplicatebounded, irregular/bowtie/collinearsafe. Independent606368+600662pixelswith4708+5214strictstrokecorespass; bothactualprojectsreopenJSONexact/4PNGsRGBAexact. Sharedpolygon-distanceoraclenowignoreszeroedgesandbatchespoints; all4earliershapeoraclesrerunPass.303Pass/43Partial/3Blocked.

AXIS224/225 PLAY011Partialfailureconfirmed: halfopacityBlue3pxvertical/horizontalaxismarkdarkensapprox75percentinvectorandraster. Exactnativecontrols/RGB/source2coincidentvectorlanes/bothactualprojectreopenJSONexact/4PNGspreservefailure. Independentexpectedone/twoalphaformula matchwithin1.1channel. Cross-pipelinegeometry/opacity/clippingreviewdeferred, no narrowpartialfixclaimed. Globalopacityrestored1beforefuturetests. Full72/789Pass unchanged; nativefindingnotcoveredbythatregression.303Pass/43Partial/3Blocked.

SYMMETRY226 PLAY-012 Pass: native asymmetric motif in v/h/4/6/8/10/12 on fresh copies. All independent reflection-group paths, distinct sector counts, full turn, exact one Undo/Redo and PNG safe pixels pass. Twelve-part actual project/PNG reopen exact. PLAY-011 remains Partial for AXIS224/225. 304 Pass / 42 Partial / 3 Blocked. Production72 and full789 checks unchanged.

MASK227 PLAY-013 Pass: v/h/4/6/8/10/12 actual boundary-crossing line, enclosed Red bucket fill, exact Undo/Redo, changed working sector with Green motif, then Mask/Symmetry Off ordinary one-mark interaction. Independent clipping/reflection geometry and all21PNG/saved-raster comparisons pass; actual final project/PNG reopen exact. Active-wedge native screenshots retained. Solid RGB permits1level raster resampling; exterior excludes3.5px antialias/resampling band and solid stroke tests exclude2.5px clipping-seam band; exact preservation comparisons unchanged. 305 Pass / 41 Partial / 3 Blocked. No new production changes.

BUBBLES228 / SCENE229 PLAY-007 remains Partial only for held-mouse preview-family switching unavailable through native API. All3families normal/reverse/tiny and9styles (36pieces) match independent geometry/593575+561507safePixels. Undo/Redo, earlierpieces, bothmatrixproject/PNG reopens exact. Native dog+Hello!/Woof!/Thinking captions complete; character ink pixels3396/1241/1241 preserved, earlierobjects/whitepaint exact, actual final scene project/PNG reopen exact. No new production fix.305Pass/41Partial/3Blocked.

CREATURE230 JOURNEY-002 Pass: actual Ziggy forgotten-symmetry decoration produces2reflected stamps, one Undo restores exactbaseline, Off replacement1. Originalbody/name/stars pixel-exact; actual corrected project/PNG reopen exact.306Pass/40Partial/3Blocked.

DESKPOT231 JOURNEY-007 Pass: prescribednative20cube+cylinder20X15 joinedShell3, pinnedview, separatePaintabove3Dcaption, project/PNG/STLdelivery. All3STLs byte-exact earlier independent complexshell; closedoutward/Euler2,35x20x20bounds, wall/floor3mm. Actualreopen noncacheproject/caption/viewexact andPNGpixel-exact; CADpreviewonlyregenerated. Captionatdefaultposition afterpositiontapdidnotmoveit; no preciseplacementclaim. Exportbookkeeping missingmeshesarraycorrected after actualfilearrived.307Pass/39Partial/3Blocked.

PATCH232 PLAY-003 Pass: genuineRasterPATCH all9outline/fill combinations, Calligraphy12pxBluevsSolid12px, primaryBlue/secondaryRed, everyinside/outside knownsourceandPNGpixel correct; alpha128retainedwithnofill; none/nonewholeproject/PNGexact. Nibcrosssections12/10vsSolid12/12. EachfreshbaselineUndoRedoexact; finalactualproject/PNGreopenexact. Initialvectorconvertedsetup0/1excluded; trueRasterbaseline2matchesfixturepixelsandmetadata, onlywhitebackingPNGencodingregenerated.308Pass/38Partial/3Blocked.

GUARD233 FEATURE-008 Pass: through-all fixed-plane conversion requires explicit depth; native warning and 30mm fixed-depth recovery verified with original failing fixture, saved source and closed STL11623.277980, empty axial ray, reopened STL byte-exact. Original support-change and missing-face criteria covered by SUPPORT204. Full73 regression790 checks pass, zero failures/page errors. 309 Pass / 37 Partial / 3 Blocked.

SWEEP-GUARD234 FEATURE-027 Pass: native original tight2mm smooth sweep rejects overlapping mesh edges; Cancel preserves original bodies exactly; actual project reopens and valid STL byte-identical original. Exact-coordinate coincident edges and collapsed triangles rejected, no unverified self-intersection claim. Focused red/green,8sweep tests and full74/791 checks Pass, zero failures/page errors. 310 Pass / 36 Partial / 3 Blocked.

POSTER236 PAINT-004 Pass: native50px Blue Poster Paint50%, partial overlap, texture8RGBs, overlap darkens, outside exact. Undo/Redo exact; zoom85->191 retains exact pixels; actualproject reopen and PNGs pixel-exact. 311 Pass / 35 Partial / 3 Blocked.

WATER237 PAINT-005 Pass: native20% watercolor repeated strokes build gradual colour, measurable soft edges; separate15% wash stays light after tool change/save. Actualproject reopen exact and2PNGs pixel-exact. 312 Pass / 34 Partial / 3 Blocked.

LONG-HISTORY238 ACCESS-002 Pass: 844x390 CSS CADMIX-based declared fixture with10-step union; native 3-step pages through step10, step7 rollback/Latest, history tree both pages, Layers separate. Saved CAD bodies and nonCAD pixels exact; legacy boolean paper metadata normalized, CAD preview regenerated, active layer changed. Prior compact Photo/preferences/help and controls retained. Viewport reset. 313 Pass / 33 Partial / 3 Blocked.

AXIS239 PLAY-011 Pass: unmasked coincident lanes deduplicated for shape, brush and vector. Native vertical/horizontal half-opacity axis/control match within1RGB in raster/vector; projects and PNGs reopen exact. Intentional second stroke builds opacity, 8 masked lanes/clips preserved. Focused red/green,8symmetry+13masked controls; full75 pass2 792 checks pass/zero failures/page errors. Initial full75 failed masked preview due to new test leaking outline state; cleanup fixed, failed/interrupted report retained. 314 Pass / 32 Partial / 3 Blocked.

CANCEL240 FEATURE-004 Pass: stalled Preview Cancel completed in 427ms; original source and STL remained exact and a new Preview succeeded after worker restart. Focused worker test and full76 regression pass (793 checks, zero failures/page errors). 315 Pass / 31 Partial / 3 Blocked.

ACCESS-014 Pass after evidence reconciliation: controlled enhancement-model 503 and native retry preserve source; real CAD timeout, worker restart and valid retry preserve source apart from regenerated preview; retired worker messages/errors cannot resolve a new request. These are controlled failures, not a claim of testing actual system-wide out-of-memory. 316 Pass / 30 Partial / 3 Blocked.

DRAFT242 ACCESS-016 Pass: native CAD draft Save/Paint/Ctrl+Z guarded, Cancel restores unchanged source/STL and worker retry works. Project/Paint/Undo/Redo now visibly disabled during draft, with recovery guidance; timeline preview explains Latest and returns to usable controls. Stale-worker guard independently exercised; four layout suites pass (495 checks, zero failures/page errors). The isolated single-check invocation lacked its required preceding 3D setup; the complete layout suite passed. 317 Pass / 29 Partial / 3 Blocked.

SPRAY257/258 PAINT-010 Pass: real capture loss during held Fine Mist; timed canvas hashes outside wet-drip column identical for 3s before scheduled release, with wet drips allowed to settle. Native20/60 size comparison, moving96 stroke, edge clip, exact Undo/Redo and actual project/PNG reopen verified. Test observer uses standard canvas pixels; no app-state injection. 318 Pass / 28 Partial / 3 Blocked.

HOLE259/260 PAINT-015 Pass: actual capture loss during held Black Hole, unchanged full-view hashes for3s before delayed mouse-up, opaque and transparent affected regions independently checked within radius60, other layers unchanged, Undo/Redo and reopened projects verified. Transparent legacy paper metadata normalizes on load; Undo pixels exact. Opaque PNG reopen exact. 319 Pass / 27 Partial / 3 Blocked.

ENHANCE263 ENHANCE-009 Pass: real uncached model.json held locally, native Cancel closed in322ms, delayed response released afterward, project source exact. Same-page CPU retry loaded and began processing, then was manually stopped due duration; normal-backend small preview completed after page reload. Earlier ENHANCE155 independently verifies tile Escape and successful same-session retry. 320 Pass / 26 Partial / 3 Blocked.

Full77 regression: 793 checks passed, zero failures and zero page errors, including the draft-control fix.

JOURNEY267 JOURNEY-009 Pass: 24mm constrained plate, attached diameter4 constrained Through all hole, edge finish and separate shell; Preview/Apply28mm, exact CAD Undo/Redo, open hole and +280mm3 independent STL proof. Reopened revision remains editable and STL byte-identical; invalid3mm draft reports lost edge/reselection, Cancel preserves source. Separate SUPPORT204 covers missing supporting-face recovery. 321 Pass / 25 Partial / 3 Blocked.

EDGE268 FEATURE-009 Pass: finer .04 angular tolerance reduced circular chamfer error from .040126 to .017847mm3, within original .030mm3; closed genus1 live STL, CAD source exact, reopened STL byte-identical. 2854 triangles vs original1906, and finer trial4630. Focused red/green and full79 regression 797 pass with zero failures/page errors. 322 Pass / 24 Partial / 3 Blocked.

### LIVE-080: Compact history paging targets

On 320- and 390-pixel portrait viewports, and 844×390 landscape, the 3D history timeline previous/next buttons had approximately 16–17×44 CSS-pixel hit areas. Compact styling now reserves 44×44 for each arrow. The focused assertion failed in all three compact layouts before the fix; the full `all-eighty-fixes/report.json` suite passes after it. A reopened four-step plate/hole/finish project was navigated forward and back live. At 320×568 its three step buttons measured at least 54×44, and at 291 CSS pixels wide they measured at least 44.6×44. Physical touch remains unverified; ACCESS-018 remains Partial.

### LIVE-081: Compact text controls

On phone layouts, text-type, font, size, width and alignment controls were 40px high, formatting buttons were 40px wide, and the fill checkbox label was 26px high. Compact styling now provides at least 44×44 CSS-pixel hit areas. Focused red/green checks cover 320×568, 390×844 and 844×390. Native inspection also verified 291px CSS width and toggled Bold and fill. The full `all-eighty-one-fixes` regression passed; physical touch remains unverified.

### LIVE-082: Text formatting names

The accessibility tree exposed the four formatting actions only as B, I, U and S. They now have descriptive Bold, Italic, Underline and Strikethrough names and tooltips while retaining pressed-state announcements. Focused tests passed across all layouts and live Chrome exposed Bold changing from unpressed to pressed. Actual screen-reader use remains unverified.

### LIVE-083 and LIVE-084: Compact field targets and landscape fit

Select transparency, Spiro numeric fields, picker and colour wheel fields, and workspace mode/save fields were below 44px. Shared compact sizing brings them to at least 44×44, with focused red/green coverage at portrait and landscape sizes. The initial fix exposed a 15px overflow in the landscape exact-piece panel; compact spacing now lets its Size, Position and Arrange tabs fit with full-size controls. Native production84 measured Size 369/369, Position 364/364 and Arrange 362/362 scroll/client heights. The full `all-eighty-four-fixes` regression passes. Actual touch remains unverified.

ACCESS-011 completed: native pointer positioning through the supported scroll gesture exposed the previously unavailable hover previews. Low/high zoom brush, eraser, smudge, stamp and picker previews were observed; picker red and white hex values were legible, and before/after hover exports were byte-identical. The output was actually reopened and re-exported with pixel-exact 960×640 RGBA. See execution ledger CURSOR280–282.

PHOTO-001 completed: a passive observer recorded two trusted native file-input cancel events after Escape, and the restored photo draft retained exposure, brightness, temperature and its Colour/White balance context. Saved source pixels matched the input; the saved project actually reopened with those adjustments. Earlier chooser attempts remain documented as inconclusive.
