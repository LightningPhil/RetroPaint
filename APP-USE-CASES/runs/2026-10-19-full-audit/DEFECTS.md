# Defects found during the acceptance run

## D-001 — Damaged TIFFs expose internal errors or import incomplete pixels

Cases: FILE-002 and FILE-010. Fixed and retested.

Opening the independently truncated TIFF through **More → File → Open image** showed “Offset is outside the bounds of the DataView”. An independently assembled two-strip fixture with its final strip omitted was accepted instead of rejected. These are separate failures: an unclear message and loss of image content through partial decoding.

The decoder now checks the entire header, directory, referenced values and strip table before allocating or copying image pixels. Incomplete files give a damaged-file explanation with recovery options. Unsupported compression retains its specific explanation.

Regression evidence before the fix: [failing checks](evidence/FILE-002-TIFF-regression-before.txt). After the fix: [passing checks](evidence/FILE-002-TIFF-regression-after.txt). The independent fixture tests both byte orders. Atomic rejection tests compare the entire project, not only the canvas. Real chooser tests cover nine damaged/unsupported inputs; [saved-document and reopen comparisons](evidence/FILE-010-independent-verification.json) are exact.

The original failing inputs and evidence remain in this run. No acceptance criterion or tolerance was relaxed.

## D-002 — WebP export introduces strong colour fringes on crisp artwork

Case: FILE-007. Fixed and retested on the current built-in Chromium browser.

At quality 0.95, the actual WebP download retained alpha but changed boundary channels by up to 99/255 after composition. A one-pixel red/blue regression fixture failed with a 93/255 error. The original download is retained as `EXPORT-alpha-webp-before-fix.webp`.

WebP now requests the browser encoder's maximum-quality mode. The exact same regression limit passes. The real chooser workflow was repeated: Pillow independently confirms exact alpha and exact colours over white and black for the test artwork. JPEG retains its existing quality setting. WebP file sizes can increase; the test export is 20,800 bytes.

Evidence: [failure](evidence/EXPORT-webp-failure.json), [regression before](evidence/EXPORT-webp-regression-before.txt), [regression after](evidence/EXPORT-webp-regression-after.txt), [actual downloads and reopen comparison](evidence/EXPORT-independent-verification.json).

## D-003 — Dismissing More by touching the paper edits the document

Case: START-003. Fixed and retested.

A real mouse click on paper outside More closed the drawer and added an unwanted dot: 413 changed pixels, bounds (707,480)–(730,503). It also introduced an unwanted Undo step and discarded an existing Redo branch.

The pointer-down handler now consumes a drawer-dismissal gesture before painting receives it. The following gesture draws normally. Real-input before/after downloads and saved projects match exactly for dismissal, and the next gesture changes 2616 pixels. The UI regression covers mouse, touch and pen event types, preserved Redo, subsequent drawing and one-step Undo. Synthetic events supplement the real mouse evidence.

Scope correction: testing exposed that consuming every tool drawer's first gesture also blocked colour sampling and text anchoring. That initial fix was too broad. Consumption is now restricted to More. A real first tap correctly selects #0000ff, and a separate regression verifies first-tap colour sampling and exact text placement. Both the introduced failure and its correction are retained in `D-003-picker-*` evidence. The final More flow, all four tabs and subsequent one-gesture Undo were repeated in `START-003-final-*` files.

Evidence: `START-003-after-outside.png` retains the original failure. The fixed comparison is in [independent verification](evidence/START-independent-verification.json); the [regression output](evidence/START-003-regression-after.txt) is retained.

## H-001 — Mobile regression harness retained a replaced canvas

Harness defect, repaired. Destructuring `base` and `baseCtx` from a dynamic import froze references to the initial canvas. After replacing the document, some assertions inspected stale pixels. The harness now uses live ES module imports. Earlier mobile pixel passes are not accepted as current acceptance evidence. The full suite was rerun, exposing the Close target failure below. No application expectation was weakened.

## D-004 — Desktop drawer Close target is 40 × 40

Found by the rerun mobile/layout harness at 1280 × 720. Fixed; all 57 desktop checks subsequently passed.

The real Close control measured 40 × 40 CSS pixels. It now measures 44 × 44; heading padding also accommodates its larger area. Evidence is retained in `ACCESS-018-drawer-close-before.json`, `ACCESS-018-drawer-close-after.json` and the corresponding screenshots. This isolated correction does not establish that all phone/CAD targets meet ACCESS-018.

The same rerun also found 40-pixel stamp-bank tabs and 39.333-pixel Spiro tooth choices. Their minimum heights are now 44 pixels. The final desktop output is `regression-mobile-current.txt` (57 Pass). The phone/CAD findings below are a separate defect.

## D-005 — Invalid project layer references replace unsaved artwork

Cases: FILE-015 and FILE-016. Fixed and retested on twenty corrupted inputs, including photo/live recipes and bad workplanes.

A project whose `active` ID did not exist was accepted and silently selected its first layer. The real file-input workflow replaced the disposable unsaved picture, changing 21,048 composition pixels. A fractional inactive layer ID was also accepted. Truncated JSON exposed a raw SyntaxError, and a genuine RetroPaint file from an unknown future version incorrectly received a generic file-type instruction.

Layer IDs must now be positive integers, unique, and contain the active ID before any image decoding or geometry construction. Damaged JSON gets a recovery instruction; future versions get an explicit explanation. The valid project opens after each rejection without reloading the app.

[Original failure](evidence/FILE-016-validation-failure.json), [three failing regressions](evidence/FILE-016-regression-before.txt), [passing regressions](evidence/FILE-016-regression-after.txt), and [twenty exact document comparisons](evidence/FILE-016-independent-verification.json) are retained.

Eight further actual chooser tests reject malformed photo value types, unordered photo curves, unknown photo looks, unknown live ink kinds/modes/brushes, parallel CAD workplane axes and a left-handed workplane. Each saved rejection document is identical to the preserved unsaved baseline. A valid file opens immediately after each failure; the final exported pixels are also exact. The linked independent report now contains all twenty inputs.

## D-006 — Compact controls fit by shrinking below usable target sizes

Case: ACCESS-018. Fix and responsive verification in progress; no acceptance Pass claimed.

Actual 390 × 844 frame measurements found 40-pixel paint sliders, a 40 × 42 Redo control, a 22 × 32 draft button, 32-pixel workshop header buttons, 40-pixel layer eyes and scaled CAD actions only 28.677 pixels high. Evidence is retained in `ACCESS-018-phone-*-before.json` and screenshots.

Compact CAD editors now keep natural scale, use a contained scrolling panel and a horizontal tool-tab strip. Targets, fields, layer eyes and header actions retain 44-pixel dimensions. The paint sliders and workspace actions are also enlarged. The first repaired 390 × 844 measurement has no undersized standard CAD controls; feature editors and the other required layouts remain under test.

The previous component checks required all CAD fields to fit simultaneously without scrolling. Their eight resulting phone failures are retained in `regression-phone-390-before-reachability-assertions.txt`. That constraint depended on the defective shrinking. Desktop fit expectations remain. Compact checks now require natural scale, a contained scroll area, no horizontal field overflow, each full target reachable within the panel, and at least 44 × 44 effective pixels. This is an implementation change to meet the recorded usability target; the 44-pixel acceptance criterion is unchanged.

The full 320 × 568 run also found a 28.21875-pixel Strength slider and overflow in workshop help. Balanced size/Strength controls retain their minimum target width. Help has a contained text area and a fixed Done action; all paragraphs must remain fully reachable. Those original failures are preserved in `regression-phone-320-before-final-fixes.txt`. Latest full 320 × 568 and 844 × 390 runs each pass 61 checks. Physical-device testing remains unavailable.

## H-002 — Disposable layout tests leaked replacement document dimensions

Harness defect, repaired. New small-image tests left their replacement canvas active for later zoom checks. The tests now capture and restore the document/history, changed settings and tool mode; cleanup also closes a failed test's tool drawer. An isolated passing zoom test was insufficient: the complete 57-check desktop sequence was repeated successfully.

For the historical v2 fixture, filling numeric crop fields did not commit their values. Independent saved-byte inspection caught the unchanged crop. The earlier exposure-only files are preserved. Real keyboard entry followed by Tab committed each field, producing the intended 768 × 192 crop with the 1024 × 256 original retained. All migration comparisons were repeated using that genuine download.

## D-007 — CAD reports a join ready while its viewport mesh is still pending

Discovered in the full 320 × 568 run: the workplane-join check reached the ready state before `work.nodes` contained the joined mesh. The original failure is retained in `regression-phone-320-before-mesh-ready-fix.txt`.

A deterministic regression delays viewport synchronization after the real Create solid control. Before the fix it fails with “Joining reported ready before its pending viewport mesh was available.” Sketch joins/cuts and boolean operations now await viewport synchronization before reporting success or removing the busy state. The same delayed test passes, along with all four boolean operators on overlapping 20 mm cubes (independent expected volumes 12,000, 4,000, 4,000 and 12,000 mm³). Evidence: `CAD-ready-regression-before.txt`, `CAD-ready-regression-after.txt` and screenshots. The full desktop sequence passes 59 checks; the 320 × 568 and 844 × 390 sequences each pass 61, including both readiness checks and positive/negative workplane endpoint checks.

## H-003 — The compact-layout helper accidentally recursed on desktop

Harness defect introduced and corrected during this audit. A mechanical conversion of CAD fit assertions also matched the desktop branch inside the new helper itself. That branch called itself, causing a stack overflow and a cascade of ten desktop failures. The full output is preserved in `regression-desktop-helper-recursion-failure.txt`. The desktop branch again uses its original scroll-height assertion; the conversion script is constrained to the actual checks. The complete corrected desktop sequence subsequently passed all 59 checks.

## D-008 — Opening another photo discards the remembered adjustment group

Case: PHOTO-001. Fixed and independently verified.

Using the actual Photo lab controls, choosing Detail → Noise reduction, closing/reopening the lab and importing the supplied `Sunset.jpg` retained the chosen group on ordinary reopen but reset it to Light → Exposure & contrast after import. The intended remembered context is recorded before the input in `PHOTO-001-import-context-before.json`; the actual failed result and screenshot are retained under `PHOTO-001-import-context-before-fix`.

The successful-import handler no longer resets the category and group. The new photo still starts with its own fresh adjustment recipe. The new UI integration regression supplies a genuine encoded PNG through the image input, checks the new visible target and known original pixel, requires the remembered Noise reduction group, and rejects leakage of the previous draft's non-default noise value. It also checks that a hidden target is rejected with an explanation. The original regression fails specifically with “Opening another photo discarded the chosen adjustment group”; output is retained in `PHOTO-001-context-regression-before.txt`.

The same regression now passes. Actual imports of both supplied landscape photographs retain Noise reduction and give the new source zero settings. Hidden-target rejection and native chooser Cancel retain complete saved data. The [independent report](evidence/PHOTO-001-independent-verification.json) verifies original JPEG pixels, fresh values, distinct visible target and an actual saved-file fresh production reopen. The final full suites pass 228 painting checks, 60 desktop checks and 62 checks at each of the three phone sizes. The new production build also saves/reopens the original artwork byte-for-byte; the user's existing artwork tab is untouched.

Coverage accounting correction: PHOTO-002 was briefly marked Pass after desktop and short-screen checks. It was downgraded when the required portrait variant was found, then all 15 portrait groups were actually exercised, downloaded and reopened. Its current Pass is supported by all three layouts and exact full-size comparisons. The earlier interrupted native attempts were never substituted for these reruns.

## D-009 — Desktop CAD forms clip after fractional zoom reflows controls

Discovered by the isolated headless Chrome suite. The existing desktop category and loft tests failed; a focused regression independently reproduced a 419 px loft outline inside a 413 px panel. The previous fit used only the unscaled height. Chrome's rounding and reflow at the calculated zoom left the content taller than the available panel, whose overflow is hidden.

`fitPage` now measures the resulting layout and makes bounded corrections. Compact layouts still use natural size and contained scrolling. The focused regression fails before the fix and passes after it. Production inspection verifies all seven loft panes fit, with the outline now 405.375 px inside the same 413 px panel. Original failures and before/after measurements/screenshots are retained under `headless/CAD-layout-regression-before`, `headless/CAD-layout-regression-after` and `evidence/CAD-headless-layout-*`. The full rerun is recorded separately.

## D-010 — Short portrait enhancement dialog clips content and has small controls

At 320 × 568, headless Chrome measured 544 px of content inside a 542 px dialog. Before/Enhanced buttons were only 36 px high and the sample selector was 30 px. The initial full layout suite and the new focused regression retain the failure.

The portrait dialog now gives its preview the flexible space left between its fixed controls. The comparison buttons and sample selector have minimum 44 px targets. The focused regression now passes; the production dialog has matching 542 px content/client heights and all action buttons remain fully visible at their intended sizes. Evidence: `headless/ENHANCE-layout-regression-before`, `headless/ENHANCE-layout-regression-after`, and `evidence/ENHANCE-headless-layout-before/after.json` and PNGs. This is software layout verification, not physical touch or assistive-technology certification.

## D-011 — Nearly clear pixels dominate Photo lab clipping warnings

Cases PHOTO-013 (transparency branch) and PHOTO-017. A genuine 1024 × 256 PNG with equal areas of opaque grey and alpha 1/255 black showed **50% shadow clipping**; replacing the almost clear half with white showed **50% highlight clipping**. The public UI output, actual source/cancelled downloads and original failing unit regression remain under `headless/PHOTO-017-before` and `headless/HIST-regression-before`.

Histogram bins and clipping counts now use alpha as visible coverage. Equal areas with opacity weights 255:1 give the nearly clear extreme 1/256 of the visible contribution (0.390625%, displayed as 0%). Fully transparent pixels contribute zero. Fractional total coverage is normalised without rounding it up, and an empty image has a defined zero result. This meets the existing requirement that nearly clear pixels must not dominate; it does not change photograph pixels, saved recipes or export processing.

The focused component regression passes. The production UI checks opaque ramps, near-black/near-white padding, clear padding, empty images, and known RGB channel peaks. Before/After restores the exact plot. An independent Pillow/NumPy report verifies peak columns 64/128/192 and 90/176/255 after +1 EV, matching full-size clipping percentages, unchanged originals, Undo/Redo and actual fresh saved-file reopen. Twenty-six actual downloads support `evidence/PHOTO-017-independent-verification.json`. The earlier 50% warnings remain retained as failures.

## H-004 — A fresh-context acceptance driver replaced its earlier event list

The initial PHOTO-019 runner created a new driver for each fresh browser context but pointed each to the same event file. Later writes replaced earlier download entries. Actual files and UI actions were retained, but the log was incomplete. The executed harness source and genuine saved fixture remain in `headless/PHOTO-019-complete`. The driver now carries the continuous event list into each context. The complete fresh-session workflow was rerun in `headless/PHOTO-019-verified`, with all 21 actual downloads independently hashed, decoded and compared. No acceptance Pass was recorded from the deficient event log. This was a test harness issue; application data and tolerances were unchanged.

## D-012 — Compact Layers covers the toolbar and blocks Save/Open

LAYER-002 exposed this at844×390 after returning from Layer options to the list. More remains visible/enabled but the Layers aside intercepts every actual pointer click. The preserved screenshot shows the panel starting at y28 over the header. Original180-second and bounded20-second failures are in `headless/LAYER-002-complete` and `headless/LAYER-002-after-scoped-name`. The corrected focused regression fails specifically with “Layer stack covers toolbar: top26, toolbar bottom52” in `headless/LAYERS-toolbar-regression-before-corrected`.

The compact list now limits its height using the measured toolbar bottom and existing safe-area/bottom spacing. Its own bounded scrolling remains available; it no longer grows over the toolbar. Layer options retain their existing focused layout. The focused regression passes at desktop and all three phone sizes. The complete final suites pass229 painting,63 desktop and64 at each phone size. TypeScript/Vite build succeeds. The actual four-viewport rename rerun and its88 downloads now pass independent verification; the formerly blocked More/save path works. The latest production artwork save/reopen again matches the immutable original bytes and exact rendered pixels. Evidence: `headless/20261020-layers-full/report.json`, `evidence/LAYER-002-independent-verification.json`, `production-layers-snapshot.json` and `evidence/ARTWORK-layers-verification.json`.

Harness failures are distinguished: the initial focused test lacked a canvas-dimension import (`LAYERS-toolbar-regression-before`); it was corrected before reproducing the actual defect. The initial opacity run also used an ambiguous unscoped Name textbox; the common driver now scopes it to File. That failed attempt remains under `LAYER-004-before`. Visibility's first phone attempt failed to open the collapsed colour palette; its rerun uses the real Colours & ink toggle. These setup failures are not reported as product defects or passed workflows.

## D-013 — Open Layers covers the Photo lab entry on a narrow phone

LAYER-015 fails at320×568 open-Cancel: the layer list's New layer control covers the toolbar Photo lab tile, and the actual pointer click times out. The screenshot and complete failed attempt remain in `headless/LAYER-015-complete`. The focused regression reproduces “Layers covers Photo lab and has no reachable alternative” in `headless/LAYERS-photo-entry-before`.

The Layers header now includes a labelled `Edit <layer name> in Photo lab` button. It invokes the existing public Photo lab control, retaining its hidden-layer guard and previous palette state. The header entry is hidden inside CAD, whose tools retain their own target. The focused regression passes at all four viewports, checks native reachability, Done/Cancel restoration and hidden-layer rejection. The final LAYER-015 report verifies20 complete production variants and192 actual downloads, including native open/Cancel/Done and basic-mode transitions at every viewport. D-013 is fixed; no acceptance result is inferred from the focused test alone.

## D-014 — Photo lab covers More on short screens

After D-013, actual LAYER-015 execution reaches the320×568 basic-mode branch, where Photo lab's close button intercepts More. The failed native attempt and screenshot are in `headless/LAYER-015-fixed`. The new hit-test assertion in the existing Advanced-mode regression reproduces the blockage at320×568 and844×390 in `headless/PHOTO-toolbar-regression-before`; its former synthetic `.click()` did not detect obstruction.

The compact panel now reserves the measured toolbar height. Its optional portrait preview yields space within the panel. The toolbar regression passes at all four sizes, but the first full rerun exposes a short-portrait Tone curves overflow in `headless/20261020-photo-toolbar-full`. The final repair also puts the More drawer above Photo lab, gives short portrait sliders two columns, and keeps tone-curve/crop fields within the reserved space. Every group fits at all four sizes, and the native20-variant palette workflow passes independent verification. Complete final regressions pass229/65/66/66/66, with byte-exact original artwork save/reopen. Evidence: `PHOTO-toolbar-final-regression`, `20261020-layer-limits-final`, `LAYER-015-independent-verification.json` and `production-layer-limits-snapshot.json`. A broad filtered `Photo lab` test selection also lacked state established by earlier component checks; its unrelated setup failures remain under `PHOTO-toolbar-layout-after` and are not interpreted as product regressions.

## D-015 — Layer limits disable Add without explaining the limiting condition

At16 actual sheets the Add/Duplicate buttons are disabled. The visible hint says only “Painting on Layer16. Tap another sheet to switch.” and Add has no title. `headless/LAYER-012-explanation-before` retains the actual input, fifteen additions, rejected native attempt, full saved before/after states and failed explanation assertion. The UI now gives distinct visible count/pixel-budget explanations and disabled-button titles. All three actual boundary workflows pass:16 sheets; exactly64,000,000 stored pixels; and the nearest invalid64,000,006. Rejected Add retains complete data, removal releases capacity, retry gives a fresh identity, and Undo/Redo/real project reopen remain exact. The independent report verifies27 actual downloads. The component regression fails before and passes at four sizes after. Evidence: `evidence/LAYER-012-independent-verification.json`, `fixtures/layer-limits/manifest.json`, `LAYER-012-fixed`, and `LAYERS-limit-explanation-regression-before/after`.

## H-005 — Limit explanation assertion accepted a layer name

The initial count-only runner's regex accepted a bare `16`, which matched the active name `Layer16`. Its report's raw hint/title revealed the mistake before any acceptance Pass was recorded. The assertion now requires `16 layers/sheets`, an explicit full-stack/limit explanation, or the pixel-budget condition. The corrected unchanged-app workflow fails as expected in `LAYER-012-explanation-before`. All initial artifacts remain under `LAYER-012-before`; application fixtures and numerical boundaries were not changed.


## H-006 — Artwork verifier paired historical build bytes with later source sampling

The first D-014 artwork verification sampled current source after later curve/limit edits. Artwork bytes and rendered output were genuinely verified, but those source hashes did not identify the historical build. No source-consistency Pass was recorded from that sample. The original metadata remains in `production-photo-toolbar-snapshot-initial-mispaired.json`; its corrected historical manifest uses the contemporaneous source hashes in `20261020-photo-toolbar-full/report.json`, captured before the later app edits. Production source hashes are now captured before compilation with `capture-build-source.py` and reused by artwork verification. The final build/source check independently matches111 application/entry files to both the pinned production source and complete latest regression manifest.

## H-007 — Responsive test prerequisites needed actual navigation

The first LAYER-015 landscape setup attempted a category button that the short-screen design hides in favour of the combined adjustment selector. Its15 completed variants remain intact; all five landscape variants subsequently completed through the real combined selector on the same immutable8098 build. The independent report verifies all192 downloads and excludes the unfinished setup. The driver now records the actual category-button/combined-selector route.

Duplicate-test failures also retained genuine missing setup: the original artwork opens with its CAD row already selected (its accessible name has the selected suffix); File closes the compact Layers palette; completed selection options must be closed before opening File; short landscape Exact size & arrange hides the basic object actions until collapsed. The corrected workflows use those real controls and preserve every expected saved field/history state. They do not force clicks or alter fixtures. Each completed viewport is independently verified; unfinished attempts are excluded.

The first full D-015 regression also hit-tested an internally scrolled More control without bringing it into view. The component reachability check now scrolls each target within the real drawer before hit-testing, as the existing CAD checks do. The final full source run passes. Actual native More/Advanced input in all20 LAYER-015 variants independently confirms the repaired app path.

## H-008 — CAD hand-off setup read off-page controls and covered paper

The first two hand-off runners read the working-layer selector before visiting its page, when it has not populated options. The real selected layer row was correct. The corrected runner reads that visible row, then verifies the selector after opening Layers. Compact layouts hide the header Project control; the runner now uses the documented CAD Ctrl+S shortcut there, retaining actual browser downloads and recording the route. Desktop header saves remain tested. A caption candidate landed on the visible status control at320px; the rerun chooses the first actual paper hit from two predeclared source anchors, logs the hit and verifies the resulting text matrix within2px. It does not force covered clicks, change the fixture or simplify the solid.

The independent LAYER-013/LAYER-014 reports verify all eight pre-recorded rows per case, combining two fully completed desktop rows with six fully completed compact rows on the same immutable8098 build. Earlier unfinished attempts stay retained and excluded. Every original body/recipe/ID survives, saved camera error is exactly0, final pictures and fresh projects are exact, and all16 actual native STL downloads equal the independently closed/oriented original mesh. No product defect is inferred from these harness setup failures.

## H-009 — Unavailable-action test needed the fold and a real history probe

The first START-010 main setup omitted More edits & transforms, leaving the legacy transform controls intentionally hidden. The next attempt incorrectly assumed the always-enabled Undo button reflected history availability. Source and actual UI confirm that Undo remains enabled even on blank paper. The final workflow opens the real fold, performs every disabled native pointer attempt, then actually presses Undo and verifies Redo remains disabled. This detects an unwanted undoable step directly. Both failed setups remain in `START-010-main` and `START-010-main-final`; only `START-010-main-verified` contributes completed main variants.

The separate busy branch uses the genuine3896×2586 photo worker. Native telemetry captures the second trusted pointer on disabled Apply while busy=true and records only one handled click. All106 main/busy downloads pass independent source-pixel, recipe, alpha-composite, history and fresh-file checks. No worker stub, synthetic click handler or fake downloaded bytes were used.

## D-016 — Minimum-size Marker taps disappear at fractional paper positions

PAINT-001's native mouse workflow produces zero changed pixels for a size1/Strength15% tap at800,200. At another layout, size1/full Strength changes only two nearly white pixels. The actual source coordinate is799.9999718569885,200. Independent decoded PNG deltas are retained in `evidence/PAINT-001-tap-defect-before.json`; the failing connectivity oracle and native input remain linked. A component regression reproduces0.015686 covered pixels for the observed repeated stationary path in `MARKER-tap-regression-native-before`.

Stationary round nibs previously used a0.01px stroked path. Chrome can discard its round caps for fractional or repeated points. The renderer now fills one round nib, retaining its coverage, filter and Strength. Circles up to2px diameter use16×16 subpixel area integration per affected pixel, avoiding a native arc's large AA overestimate. The first arc-only repair genuinely failed the unchanged0.5–1.1px area bound (`MARKER-tap-regression-after`); that failure is retained. The integrated repair passes the same bound and minimum visible15% contribution at six declared fractional positions, for single, repeated and near-stationary input (`MARKER-tap-regression-integrated-after`). Full production acceptance and regression results are recorded separately; a focused component Pass alone does not close the case.

The repaired production workflow completes all14 pre-recorded rows. `evidence/PAINT-001-independent-verification.json` verifies308 actual downloads, every criterion, all three gesture history states and fresh file input. Minimum taps remain visible; no curve gaps, spikes or bridges occur. The complete suite passes230 painting,65 desktop and66 at each of the three compact layouts. The pinned immutable8099 build matches111 application/entry files, and the original artwork saves/reopens with identical editable bytes and rendered pixels (`ARTWORK-marker-verification.json`). D-016 and PAINT-001 are closed by these results; hundreds of other acceptance cases remain unrun.

## H-010 — Marker setup needed a rendered label and reachable paper view

The original acceptance runner read the Strength label before its next rendered frame. It now waits for the actual visible size/Strength label; input values and intended ranges are unchanged. Short landscape places the floating paper controls over the planned upper curve. The runner now hit-tests every planned source point and uses the actual Zoom out control when needed, recording each step before drawing. It retains the same source curves, tap,41 native samples and timing. It never hides the floating control or forces a covered pointer click. Earlier failed setup reports in `PAINT-001-complete` and `PAINT-001-remaining` stay intact; all14 rows rerun on the repaired production build.

## H-011 — Biro setup looked for a name in the size label

The first Biro runner incorrectly expected `Biro` in `workspaceToolDetail`, which displays size/Strength. The actual applicator button was selected correctly. That timeout and its unchanged Marker download remain in `PAINT-002-complete`. The rerun uses the real Biro button's `aria-pressed` state, visibly opens Brushes after Spray to inspect that selected choice, and verifies the actual resulting fine tap independently. No product change or acceptance Pass is inferred from the incorrect-label setup.

## D-017 — One-pixel Pencil shades the chosen pixels grey

Actual32×32 fixture input, Pencil selection and native staircase/tap downloads reproduce this independently. All23 intended staircase cells are occupied, but every colour is wrong: mostly117/117/117, with124 and132 near the start, instead of the selected opaque26/26/26. The single Fit tap is69/69/69. No extra occupied cells were found in this native example, so the defect is recorded as incorrect Pencil AA/colour. Raw files, declared exact expected PNGs and mismatched cells remain in `PAINT-006-before` and `evidence/PAINT-006-pixel-before.json`.

Pencil used the generic antialiased round coverage path. It now visits source grid cells with an integer line and deposits a binary circular nib. Ink/Strength still applies once through the existing common pigment mask. Captured segments are clipped before integer traversal to bound work outside the paper. The exact-cell regression fails before and passes after; it additionally requires binary alpha/exact ink and the circular footprint for22/96 nibs. Full native core/boundary reruns, complete regressions and production artwork verification are required before the case closes.

## D-018 — Actual pixels clamps small pictures and distorts thin ones

PAINT-006's actual More/View/Actual pixels action leaves its32×32 source at180% on desktop, as shown in the retained failure screenshot/readout. The corresponding four-layout regression fails before repair. This is a real product failure, not a test setup failure. It also attaches to ACCESS-003's coherent Fit/Actual scale criterion; its remaining PATCH/pan/wheel branches remain unrun.

Actual scale now uses the measured canvas source scale, with limits that permit a true100% view for small images. Fitted content reserves the stage border and keeps fractional dimensions. A first repair passed desktop and landscape but the unchanged portrait assertions exposed a4096×1 strip rendered4096×0.859/0.870 CSS pixels (`ACTUAL-pixels-regression-after`). Browser CSS layout rounds the tiny fitted axis to fractions of a pixel. The final view transform corrects each axis against the source aspect and reports the measured scale. The unchanged checks now pass32×32,1×1,1×4096,4096×1 and64×48 at every viewport (`ACTUAL-pixels-regression-ratio-after`). The intermediate failure stays intact. Full source/build/artwork and native use-case verification remain pending.

## D-019 — Fitted paper cannot move edge cells clear of the status controls

The repaired Pencil workflow completes desktop but its unchanged320×568 staircase meets `workspaceIdle` instead of the paper at a lower source cell. The raw native failure is in `PAINT-006-fixed-core`; its completed desktop files are retained, and the interrupted portrait gesture is excluded from completed results. The status bar floats over the fitted32×32 paper. Existing Move paper clamps a fitting image to zero translation and prevents a zoomed image moving past the viewport edge, so it cannot reveal these cells at a usable grid scale. This is separate from the corrected Pencil colour and Actual-pixel defects.

The intended repair permits bounded view padding when panning, retaining a visible part of the paper and preserving its source pixels. The same planned staircase and tap coordinates will be exposed through actual Move paper gestures. No status control will be hidden, no covered click forced, and no source fixture simplified. A focused four-layout regression is retained before repair. Complete regression/build/artwork and native source-coordinate reruns remain required.

## H-012 — The first Space pan attempted to move past a reached clamp

The first ACCESS-003 hand drag focuses the known Blue patch and reaches both positive pan bounds. Its following Space drag requested another+20,+20, so the correct bound prevented further movement. The early setup failure remains in `ACCESS-003-complete`. The rerun drags inward by−20,−20, retains the original source patch/fixture and every wheel/modal branch, and records pan geometry before its assertion. All four complete rows and96 actual downloads pass independent verification. The slider/modal native Ctrl-wheels preserve exact measured view rectangles, readouts and window/device scale. No app change or relaxed tolerance was used to make this setup pass.

### D-017/D-018/D-019 final verification

All three fixes are verified in the source-pinned immutable8101 production build. `evidence/PAINT-006-independent-verification.json` checks all four strict32×32 core workflows and all14 native Pencil size/Strength/layout boundary rows, with380 actual downloads. The same original23 staircase cells and both tap cells are exactly selected Black, all neighbours remain byte-exact, PNG/project reopen is exact, and real Move paper reveals the original cells without changing zoom or hiding controls. The boundary matrix has one known Strength contribution without extra AA shades. Earlier failed/interrupted or historical8100 runs are excluded from this Pass.

`evidence/ACCESS-003-independent-verification.json` checks every PATCH pan, Space, paper/slider/modal Ctrl-wheel, known source tap, Actual/Fit, history and fresh-file branch at all four layouts, with96 actual downloads. Actual pixels is960×640 CSS pixels at100%. The unchanged small/narrow regression also covers32×32,1×1,1×4096,4096×1 and64×48; the fitted-edge regression passes at all four sizes. The complete suite passes231 painting,67 desktop and68 at each phone layout, with no page errors. TypeScript/Vite succeeds. All111 current app/entry files match the pinned production source and full regression run. Original artwork project bytes and save/reopen/previous-build pixels remain exact (`ARTWORK-pencil-pan-verification.json`). Both acceptance cases now pass; the complete349-case audit remains in progress.

## H-013 — Concurrent Classic runs did not establish their timing/readiness preconditions

Classic Brush's first fast native gesture was not faster than its delayed comparison, so it did not establish the required fast variant. The other concurrent runs timed out at the public size/Strength readiness guard on rowp7; their failure captures did not establish the intended rendered readiness. The failed reports, including six completed rows for Oil/Crayon/Natural, remain in `PAINT-007-*-complete`. They are excluded from the forthcoming case result. The first four-layout material-only run is retained separately too.

The complete56-row boundary and four-row material workflows now rerun one isolated headless Chrome browser at a time. Each context actually activates its own invisible page, observes visible/hidden state and records that foreground precondition. This does not connect to the user's browser/profile or control the desktop. The original1s label guard, source geometry,15ms/no-delay inputs, actual elapsed fast/slow condition and all pixel tolerances remain unchanged. No hidden-state override or fake event is used. New failures also retain the public visibility, range values and label for diagnosis. Only complete independent verification of the full new sequence can establish PAINT-007 Pass.

All56 boundary rows and four main workflows subsequently completed. `evidence/PAINT-007-independent-verification.json` checks1,392 actual downloads, every material preview/paint family, complete gesture history and exact fresh source/RGBA. PAINT-007 now passes. The visibility observations establish that the isolated pages are visible; they do not establish that opening another headless page would background them. The later focus capability probe below explicitly distinguishes these facts.

## H-014 — Headless target activation does not generate blur or hide the original tab

The first Spray sequence completes all12 Mist painting workflows and the first native emulated-touch cancellation, then times out waiting for the original page to become hidden after another isolated tab is activated. The original failed report and files remain in `headless/SPRAY-foreground`. This is a failed cancellation setup, not evidence of an app blur-handling failure.

The separate `headless-tab-focus-probe.mjs` actually activates a second tab and a separate browser window, using only its own headless Chrome process. Every observation remains visible, focused and without any trusted blur/visibility event (`evidence/headless-tab-focus-capability.json`). No synthetic DOM event, focus emulation or visibility override is substituted. All four planned blur rows per style remain explicitly unavailable. Supported painting and actual browser-native touch-cancel workflows continue in `headless/SPRAY-supported`; their independent pixel/source checks remain required. Software touch cancellation does not certify a physical touch or pen device.

The supported scope subsequently completes and is independently verified for all three named styles:12 positive rows and four native emulated-touch cancellation rows each,780 actual downloads total. Complete gesture history, source fields, fresh RGBA, four clipped boundaries, size/footprint and release/cancel acknowledgement remain strict. All three cases stay Partial because the four planned blur rows per style are unavailable.

## H-015 — Ideal continuous colour arithmetic is not a valid oracle for repeated native8-bit deposits

The preplanned ideal Red source-over line within2/255 fails on the real Mist files. The attempted one-step channel endpoint envelope subsequently fails on Splatter too. Their raw assertions and pixel values remain in `PAINT-010-positive-oracle-output.txt`, `PAINT-011-full-oracle-output.txt` and the colour-observation JSON files. No larger tolerance is used to make either assertion pass.

Two separate, application-free native Canvas calibrations reproduce these departures by repeatedly drawing one known Red over white, using either CSS alpha or globalAlpha. The latter can overshoot a colour endpoint by17/255 despite every deposit using exactly the same chosen colour. Results and source are in `headless/SPRAY-color-probe` and `headless/SPRAY-color-probe-global-alpha`. This invalidates the infinite-precision and single-rounding expected models for a many-pass8-bit renderer; it is not evidence that RetroPaint chose another pigment.

The replacement selected-colour check observes and delegates native Canvas fills/gradient stops without changing their arguments or results. All36 original size/Strength/layout combinations repeat through the actual controls, including Rainbow then Red for Confetti. Independent verification requires every observed Red pigment/gradient stop, global alpha and composition to match exactly, and several actual Rainbow colours. The native trace supplies the material observation; the original affected-area/source/history/fresh output checks remain independent and unchanged. Upper/lower hex letter case is parsed as the same RGB value; the earlier string-case assertion is retained too. The original ideal errors stay reported numerically as diagnostics. No application renderer or serializer supplies an expected image.

## D-020 — New picture replaces the document before dimensions or acceptance

`headless/FILE-001-before` contains four actual layouts with native marked PLAY pictures. Clicking New immediately removes the mark and replaces the source with blank default960×640 Paper; there is no size entry or explicit acceptance control. `evidence/FILE-001-defect-before.json` independently decodes16 actual before/after downloads and confirms the disappearance and premature source replacement. This violates FILE-001's chosen-size main flow and atomic invalid-size path. Valid/invalid entry cannot be exercised before repair and is not claimed tested. The case is recorded Fail while the repair and full planned rerun remain pending.

### D-020 final repair and verification

New now opens an accessible modal with width/height, Create picture and Cancel. The existing strict1..4096 whole-pixel validator runs before settling or replacing artwork. Cancel and native Escape leave the old picture and its history intact. Valid acceptance creates one ready white Paper of the requested size, closes the options and focuses the drawing canvas; a vector document receives its supported empty object target. The original size and complete artwork remain recoverable in one creation Undo.

The meaningful four-layout regression fails before and passes after (`NEW-picture-regression-before` / `NEW-picture-regression-after`). The source-pinned immutable8102 build passes the complete231 painting,68 desktop and69 at each compact layout suite, with no page errors. TypeScript/Vite succeeds,110 modules; all112 current application/entry files and regression source files match the pinned build/run. Original artwork save/reopen bytes and all rendered pixels remain exact (`ARTWORK-new-picture-verification.json`).

`evidence/FILE-001-independent-verification.json` checks all512 actual downloads from all20 positive size/layout rows and four complete failure workflows. Sizes1×1,320×240,4096×1,1×4096 and4096×4096 each run at every layout. All nine invalid width/height categories, Cancel, native Escape, correction/retry, old history/Redo and fresh input execute at every layout. Pending public pixels and saved complete source remain exact through rejection/cancel; no navigation history appears. Every new Paper, known centre mark, creation/mark history and fresh source/RGBA is exact. FILE-001 now passes. No planned size, branch, source point or tolerance was reduced.

## D-021 — Pixel filters ignore their enabled Strength setting

All four actual layouts select Invert at15% through its enabled Strength control. Red255/0/0 becomes full Cyan0/255/255; its independently calculated weak contribution is217/38/38. All16 native before workflows and160 actual downloads are retained in `headless/PAINT-017-before` and `evidence/PAINT-017-before-observations.json`. Complete alpha and history remain exact. A separate component probe reproduces ignored15% Strength in Pixelate and Emboss too; those observations do not establish full acceptance coverage of those separate tools.

## D-022 — Pixel filter movement drops dense samples and compounds overlapping dabs

The same native before run uses declared4px and12px sample spacing over the known Red/Blue patches. Every dense row has8,655 wrongly unprocessed interior cells, including unchanged Blue under the swept cursor. Every sparse row has5,642 incorrect interior cells due to repeated inversion of overlapping dabs. The input path applies a filter only when one delivered move exceeds6px, while resetting its last point for every move; overlap is filtered repeatedly from already modified pixels. Actual trusted event coordinates, all first/second PNGs and whole-gesture history are retained. This is not a missing pointer or failed image fixture.

The repair keeps a gesture-owned immutable source and coverage map, blends the selected Strength once per covered pixel, interpolates between all delivered/coalesced samples and flushes the release segment. Captured movement is clipped before sampling to bound outside-paper work. Alpha and pixels outside the intended effect remain untouched. The original four focused checks fail before and pass after (`INVERT-regression-before-typed` / `INVERT-regression-after`). An initial test draft used the PNG-string helper where an alpha array was needed; it had already failed on the genuine product assertion before reaching that branch. Its output is retained; the corrected typed before/after checks are the evidence used. Complete clipping/release checks, full suite, new source-pinned production/artwork roundtrip and expanded actual-control acceptance remain required before closing PAINT-017.

## H-016 — Supplementary recheck metadata and canonical ledger generation

FILE-002 was already a genuine Pass, including earlier native Windows chooser cancellation in ordinary and Photo lab flows. The additional source-pinned8102 headless run completes48 positive,28 rejected and four browser-native cancellation rows, with1,440 independently verified actual downloads. It is retained only as supplementary regression evidence after the editor change. No extra acceptance Pass is counted and none of the older native/Photo lab evidence is replaced.

A duplicate structured recheck field was initially added to its case entry as well as `supplementary_checks`. That field was not a CSV column; the old ledger writer raised after partially rewriting the derived CSV, and its first retry inherited only190 rows. Authoritative `results.json`, the untouched349-case index and all raw evidence remained intact. The duplicate field was removed without losing its supplementary copy. Ledger generation now rebuilds the complete canonical inventory from the index, validates all case fields/status counts before writing, and replaces the CSV atomically. `evidence/ledger-completeness-verification.json` verifies349 unique ordered IDs and exact agreement with64 Pass,1 Fail,5 Partial and279 Not run. No document structure is used to establish application Pass.

The ledger's old hard-coded CUA browser/input label also misdescribed later headless evidence. It now identifies isolated headless versus historical native/mixed provenance from the linked execution reports. Actual matching UI completion times are used where available; absent historical times are not fabricated. Source deltas include added and deleted files as well as modified files, while the original baseline stays immutable. These are audit-tool corrections, not application defects or additional case results.

### D-021/D-022 final verification

All38 expanded native Invert workflows complete on the immutable8103 build and pass independent verification (`evidence/PAINT-017-independent-verification.json`): the same16 core failures,14 size/Strength/layout boundary rows and eight full/weak four-patch rows, with980 actual downloads. All Red/Blue/Green/half-alpha cores, correct Strength, local footprint, shared edge-mask weights, untouched alpha/clear pixels and whole-gesture history/fresh source/RGBA pass. The dense and sparse rows now have zero incorrect interior cells at every layout, compared with8,655 and5,642 before. Two full inversions restore original fully covered RGBA exactly. No original failing point or core tolerance was relaxed; the added half-alpha native-rounding allowance was specified before executing those extra rows.

Five focused checks pass, including release-only movement and clipped capture from±1,000,000 source coordinates. The complete suite passes236 painting,68 desktop and69 at each compact layout, with no page errors. TypeScript/Vite succeeds,110 modules; all112 current application/entry files, regression sources and immutable build assets match their pinned hashes. Both original artwork projects remain byte-identical to the immutable backup; save/reopen/previous-build rendered pixels remain exact (`ARTWORK-pixel-filters-verification.json`). PAINT-017 is now Pass. Pixelate/Emboss have weak-bound component evidence from the shared repair; their separate acceptance cases remain unrun and are not counted passed.


## D-023 — Smudge darkens pigment at transparent edges

All32 positive native workflows reproduce colour contamination in the declared pure-Red region, across settled and real live-Water sources, sizes1/22/96, full/15% Strength and all four layouts. Straight RGBA interpolation mixes RGB from clear neighbours into visible pigment. Independent two-cell regressions reproduce Red128/0/0/128 instead of255/0/0/128, and hidden Green produces128/128/0/128 instead of pure Red. The actual immutable8103 before run retains all40 workflows and416 downloads in `headless/PAINT-013-before`; `evidence/PAINT-013-PAINT-013-before-independent.json` records every pixel/data/history observation.

The repair interpolates premultiplied colour and alpha, then unpremultiplies visible RGB. Zero Strength/zero displacement preserve the original. Both focused colour regressions pass after the change. Complete suite/build/artwork and all40 actual-control after workflows remain required before acceptance.

## D-024 — Smudge freezes live ink before movement and adds empty Undo actions

All12 live before workflows stop the independently verified Water animation on pointer-down before movement. All8 clear-only workflows add an Undo step over a real layer rename; all four live clear-only rows also replace the live source and remain frozen after release. The controlled10000/10371ms phase probes demonstrate actual different rendered frames in the original fixture, then zero changing pixels while held in the old Smudge. Real RAF scheduling, Date, timers and trusted input remain; no elapsed-time or performance claim uses the fixed render/performance reads.

The repair previews only the active layer and computes whether its pigment actually changes. Only the first actual change records history and bakes that same observed live frame; a press, jitter or empty-space gesture leaves source/live data and previous history intact. The guide is not included in the sampled source. Two input-handler regressions fail before and pass after, including complete live Undo and the prior rename/Redo. Retained vector-object entry behavior is outside these raster-only native rows. Case PAINT-013 remains Fail pending complete after verification; no tolerance or original source point was weakened.


## H-018 — Live composition oracle omitted the preserved Water overlay

The first complete after verifier passed every colour/alpha/direction/Strength/target/history/fresh requirement, but failed independent composition in the four live clear-only rows by255/255. Those rows correctly preserved Water as a live overlay over its saved white backing. The faulty composition used that raw white backing alone, while the predeclared oracle explicitly supplied live-source RGB from the immutable same-phase public frame and known binary source alpha. The original failed report and exact old verifier source remain in `evidence/PAINT-013-live-composition-oracle-failure.json` and `evidence/verify-smudge013-before-live-composition-correction.py`.

Composition now includes that independently observed live source only when the complete after document remains exactly the original before document; any source/live change still fails. The Green/source composition, same-phase PNG, held/released Water motion, exact raw/live data and previous history are all independently required. No tolerance or requirement was reduced, and no application renderer supplies a generated expected image.

### D-023/D-024 final verification

All40 identical-plan native workflows and416 actual downloads now pass (`evidence/PAINT-013-independent-verification.json`). All32 positive rows have zero incorrectly coloured pure-Red cells, local directional displacement and feathering; full Strength exceeds15% displacement in every pair. All12 live rows keep8830 changing Water cells before movement; all4 live empty-space rows keep the same post-release motion. All8 empty-space gestures preserve complete source/live data and the previous rename Undo/Redo. Every actual save/reopen/source/RGBA and unrelated layer remains exact; independent composition is within1/255.

Four focused regressions fail before and pass after. The complete240 painting,68 desktop and69 at each compact layout checks pass with no page errors. TypeScript/Vite succeeds,110 modules,35.41s. All112 current application/entry files and regression sources match the pinned build/run; every immutable asset is rehashed. Original artwork saved/reopened files remain byte-identical to the immutable backup and all previous-build/save/reopen rendered pixels remain exact. PAINT-013 is Pass; the physical/AT and other unrun cases remain unverified.


## H-017 — Compact landscape top-edge fixture point requires normal paper navigation

Pixelate and Emboss each complete the first10 native pattern rows, then their eleventh row stops before the planned alpha-edge tap at source650/64: the fitted844x390 picture places it under the Paper view controls. Both first failed reports, screenshot, partial actual downloads and original executed harness are retained under `PAINT-016-native` / `PAINT-018-native`. No covered click is forced and no source point, mask, size, Strength or criterion is changed.

The continuation uses the already-supported, already-tested actual Move paper control and a native80-CSS-pixel downward drag when needed. It then verifies every original source point reaches the view, the full public canvas PNG is unchanged by navigation, and actual trusted pan input is distinguished from the effect input. Whole-gesture history, complete source and fresh input still have their original strict comparisons. Only the remaining12 rows are run again; original complete rows are reused explicitly and the interrupted eleventh row is not counted complete. This is ordinary view navigation, not an application-source fix. Neither case becomes Pass from a prefix or UI-only report.

The initial Pixelate prefix verifier repeatedly scanned all collinear subsegments. Its source is retained as `evidence/verify-local-filters-initial-prefix.py`. The equivalent faster oracle first proves every planned sample lies on the monotonic straight segment, then measures that identical segment union once. No expected area, tolerance or pixel value changes.


### H-017 portrait menu continuation

The first navigation continuation completes four landscape rows and both desktop portrait rows, then the320x568 portrait setup tries File while the still-open Eraser options panel covers More. Its visible Close button is the ordinary route. Both interrupted attempts and their executed harnesses remain retained. The final six portrait rows for each mode use that actual close button, with unchanged portrait bytes, source points and oracles. All22 original workflows per mode now pass independent verification,388 actual downloads each, but the distinct required Paper-state coverage below is still pending.

## H-019 — Required opaque Paper was confused with opaque pixels on a clear sheet

A coverage-matrix review found that image import creates a transparent-capable sheet (`paper=null`) even for a wholly opaque JPEG. The Invert result had genuine38-row/980-download evidence, including opaque patches and half-alpha, but did not execute the separately required defined opaque-Paper state. Its Pass is explicitly withdrawn to Partial until the missing state is tested. Pixelate/Emboss remain Partial despite their now-complete original22 rows/388 downloads each. This is a coverage-accounting correction, not an application defect and not a change to the normative requirement.

All three filters now have a pre-execution14-row Paper extension using an independently generated opaque checker/White composite and the actual Layer options checkbox to set defined white Paper. Size1/22/96, full/15% Strength and every layout are retained. Actual source alpha255, paper#ffffff, local effect oracle, complete history/fresh source and140 downloads per mode must pass before acceptance. No original required row or failure evidence is removed; no opaque-pixel screenshot is substituted for the saved Paper property.


The first Paper prefix oracle stopped at a case-sensitive `#ffffff` string assertion. The actual UI stores `#FFFFFF`, exactly the same RGB255/255/255. `evidence/PAPER-colour-spelling-observation.json` independently parses all three actual saved sources and verifies fullalpha255; the exact old verifier is retained. The check now parses the defined colour with Pillow and still compares every subsequent saved field/history literally. No colour value, alpha condition, Paper requirement or tolerance changes.


### H-019 complete Paper-state verification

All42 additional native Paper workflows pass:14 per mode,420 independently verified actual downloads, exact defined White Paper/alpha255 and chosen local effect, source fields, whole-gesture history and actual fresh input. Invert is restored to Pass only after this required extension; its original38 transparent-sheet rows remain labelled8103, while the new14 Paper rows use current8104. Pixelate and Emboss each now have36 complete workflows/528 actual downloads, including the actual owned-portrait main flow at full/15% Strength in all four layouts. Invert totals52 workflows/1120 downloads. No original requirement, point, mask or tolerance was removed.

Every current112 application/entry file, painting/mobile source and immutable build asset is rehashed against the complete240/68/69/69/69/regression/build/artwork checkpoint. Native harness hashes are verified against their exact retained executed copies across the explicit continuations. Only three complete case outcomes change; the Eraser variant family remains Partial because Scrub/Black Hole are not tested yet.


## H-020 — Scrub scope calibration and compact layer-panel navigation

The first Scrub harness completes three desktop Paper rows, then the320x568 row selects Paper, which normally closes the compact Layers panel, and attempts an eye button in that closed panel. The original failed report, three complete workflows and all partial data remain under `PAINT-014-before`. Its continuation reopens Layers through its actual button before the same eye controls; only the remaining37 rows are scheduled. No forced click or hidden-control shortcut is used.

Before any Character row or case pixel oracle, the initial plan's assumed Scrub radius was also corrected against actual public cursor pixels. Size22/96 rings independently measure17.7200/77.2787 source pixels, agreeing with17.71/77.28 radii; Size1 uses the existing larger minimum visible cue around its .575px paint radius. The original plan is preserved in `fixtures/PAINT-014-initial-plan.json`. The unchanged2px antialias band is measured from the visible tool footprint rather than an incorrectly guessed width.

The same independent, application-free native Canvas calibration tests all256 remaining alpha values. Straight RGB can differ by57 at very low alpha while associated colour differs at most0.9804 byte. The plan now checks associated pigment within1 byte at every nonzero alpha and additionally straight RGB within2/255 at alpha>=128; opaque/alpha tolerances, complete unchanged source/history equality and public composition remain strict. This correction preceded all Character execution and any case-oracle failure, and does not use the app eraser as an expected-image generator. All40 original rows/points and the hidden-target complete visibility Undo requirement remain identical. The tiny-cursor classifier initially excluded the entire minimum cue with its large-radius centre exclusion; its radius/threshold requirement stayed fixed while that classifier was corrected.


## D-025 — Undo of erasing a hidden working sheet leaves it visible

All four native hidden-Character workflows reproduce this genuine defect: raw pixels return exactly after Undo, but original `visible=false` becomes `true`, and the full view changes. Every other undone source field remains exact. The original complete40 workflows/400 downloads, all four layouts, precise expected/actual visibility and initial oracle failures are retained. Two input-handler regressions reproduce the same source/Blue-neighbour/Undo/Redo defect at full and15% Strength.

The repair defers automatic reveal for Scrub until its ordinary gesture history has captured the original hidden state. Existing per-gesture grouping, low-Strength live bake and visible-neighbour target stay intact. Both focused regressions fail before and pass after. Full242-check painting/layout verification, a separate source-pinned production build, original artwork byte/RGBA roundtrip and every same-plan native after workflow remain required. Case PAINT-014 stays Fail while those checks and the independent repeated-edge colour diagnosis are pending. The four original1.0471–1.3961-byte ideal-colour misses are not silently classified as product failures or passed; their application-free/native evidence is separate.


## H-021 — A path has repeated native8-bit rounding, not one ideal composite

The initial full Scrub oracle retains eight misses: four genuine visibility Undo failures (D-025) and four ideal-pigment differences of1.0471–1.3961 associated bytes on repeated main strokes. The original full report/verifier and calibrated plan are preserved. Independent application-free native Canvas observation supplies2032 actual repeated destination-out transitions; the invalid once-per-path ideal colour error reaches3.7490 bytes there without any app code. An attempted original-hue final-view comparison also retains a2-byte counterexample at390x844. Neither failed bound is enlarged or presented as a product defect.

The corrected independent oracle recovers associated integer bytes with Pillow/NumPy, then checks one common inverse-coverage factor for all pigment/alpha components at each actual native contribution. Quantization is the same single8-bit unit per operation; rational interval intersections use exact integer cross products, with no floating pixel tolerance. All2032 independent native transitions satisfy the law.

Four additional actual-control diagnostic main rows delegate the native stroke method unchanged and only observe its state and before/after PNG. All138 actual native operations and22,533 changed pixel transitions satisfy the integer law; each chain starts at the known source with no unobserved writes. Crucially, all four final complete projects, raw pixels and actual visible PNGs are exactly identical to their original uninstrumented runs. Thus observation does not substitute a different arrangement or improve the output. The40 extra downloads are supplemental and never add acceptance cases or replace any original row. The native line-width property is checked against exactFloat32(35.42),35.41999816894531; an initial unsupported1e-8 double comparison is replaced by that exact representation check, without changing image thresholds.

Single-tap pigment1-byte and alpha>=128 straightRGB2 checks, exact alpha/clear/untouched source, the predeclared1-byte independent visible composition, original positions/area band, complete Undo/Redo and fresh source/RGBA remain required. Repeated main pigment uses the stricter operation-chain law plus an exact hash match to original uninstrumented output. No app painter, serializer or kernel supplies an expected image. Case PAINT-014 remains Fail until D-025 and all same-plan after workflows pass on the new verified production build.


### D-025 final verification

All40 identical-input native after workflows and400 actual downloads pass on immutable8105. All four originally hidden working sheets now regain `visible=false` on Undo, with exact complete source/PNG and neighbour state; Redo/fresh input remain exact. Paper/clear source, Strength, footprint, Alpha/Blue composition, captions/stamps and every unaffected field pass all28 boundary/eight main/four hidden rows. The operation-chain correction independently resolves the four invalid repeated-colour assumptions without widening a pixel threshold; original failed reports and plans remain.

Both full/15% focused regressions fail before and pass after. Complete242 painting,68 desktop and69 at each compact size checks pass with no page errors. TypeScript/Vite succeeds,110 modules,41.58s. Every112 current app/entry file, two package manifests, painting/mobile source and immutable build asset is verified. Original artwork editable files remain byte-identical to the immutable backup; all previous/save/reopen rendered pixels stay exact. PAINT-014 is Pass. Black Hole and remaining cases continue separately.


## H-022 — Native blur is available after restoring the library's focus default

The original no-blur/no-hidden probe remains genuine evidence under its actual configuration. Local Playwright1.62.1 source inspection found its automatic `Emulation.setFocusEmulationEnabled(true)` default. A new independent probe disables that override only in owned headless pages, then activates another real tab. It records trusted native Window blur/focus and `document.hasFocus=false/true`; document visibility stays visible and no hidden transition or OS Alt-Tab claim is made. The exact library path/hash and old/new capability observations are retained. No synthetic DOM lifecycle event is dispatched and the user's desktop/profile/tab is never accessed.

All12 originally unavailable spray blur rows now complete,32 actual downloads per style/96 total. Every native input log proves one held mouse-down, real trusted blur, focus return, and only then its sole mouse-up; no early pointerup/cancel/lost capture substitutes for the held-return branch. Paint is exactly stable across inactive/returned-held/cleanup/public/export snapshots, source footprint and headers remain correct, and complete random arrangement Undo/Redo/fresh source/RGBA are exact.

An initial additional oracle compared a snapshot taken before tab creation with a post-blur acknowledgement snapshot, incorrectly calling legitimate intervening paint a post-cancel change. Its verifier is retained and those transition deltas remain diagnostics. The original planned exact post-acknowledgement stability requirement is checked without changing any pixel threshold. The780 earlier positive/touch download artifacts are independently reverified; old Partial reports remain verbatim. Their obsolete `known_source_over_channel_envelope` metadata flag is absent from the fresh report because H-015 already disproved that model; ideal errors remain diagnostic and exact native pigment/gradient/alpha/composition observations remain required.

Mist,Splatter,Confetti are Pass only after all20 planned workflows each:272/272/332 downloads,876 total. No old random arrangements are regenerated, relabelled as current runs or normalised. Source112 app/two dependency manifests/current242-check build/artwork are verified; source builds of earlier positive/touch runs remain explicitly historical. The Spray variant family is Pass. Legacy3–8 and actual assistive/physical input limits remain separate Partial outcomes.


## H-023 — Separate early cancellation qualification from continuous held movement

The first Black Hole harness completes one stationary Paper release row, then its moving row exceeds an added500ms early-effect setup assertion while collecting intermediate geometry through browser round trips. That interrupted row has no acceptance verdict and all raw frames/report/harness remain under `PAINT-015-before`. The original plan is retained.

All32 short stationary-release/touchCancel/native-blur/border/hidden flows keep the original500ms precondition. Eight moving main flows instead test that a continuous held gesture follows the pointer even if it outlasts the legacy680ms one-shot, then require the same exact post-Stop snapshots. This does not relax a product cancellation target or skip movement; it prevents an implementation duration from defining the allowed length of a user's held main gesture. All original40 rows/coordinates/hold/move settings and source/history/stop/alpha criteria remain unchanged. Screen geometry is now preflighted once before holding. The original completed first row is retained and only the remaining39 workflows are scheduled.


### D-026 — Black Hole ignores movement and continues after pointer termination

Actual native baseline release, Chrome touchCancel and trusted owned-tab Window blur show thousands of changed pixels after acknowledgement; moving gestures leave the final footprint untouched. All nine newly added lifecycle/alpha/history regressions fail before repair. `headless/HOLE-regression-before/report.json` and `evidence/PAINT-015-PAINT-015-before-prefix.json` retain the evidence. Complete before run and repair verification continue.

### D-027 — Black Hole replaces clear paint with opaque pigment

Actual clear-sheet baseline files add white/opaque pixels instead of revealing the unchanged Green guide. The separate alpha regression reproduces this. Black Hole forces source sample alpha255 and hardcodes white clearing. Repair pending.

### D-025 expanded — hidden targets in other eraser modes

New before regressions prove Black Hole, Invert, Pixelate and Emboss Undo restores pixels but leaves the originally hidden target visible. Scrub is already fixed; the same history-before-reveal ordering needs applying to the other eraser paths. No new acceptance Pass is inferred from these component tests.


### Black Hole repair regression/build verification

D-026 now registers Black Hole as a held input gesture, moves its local effect and stops it on release, cancellation, lost capture, blur or input settling. It retains one history action even after its first680ms animation; moving starts from current committed source so earlier erased paint cannot resurrect. D-027 preserves sampled alpha and clears to the actual Paper colour or transparent zeroRGBA, including masked footprints and selected pieces. D-025 now captures history before revealing any eraser target.

The original nine regressions fail before and pass after. Four added completed-footprint, defined-Paper, long-held/outside recovery and masked-alpha regressions exposed two intermediate repair failures; those failed reports remain in `headless/HOLE-footprint-intermediate`. The corrected13 focused checks and full255 painting/68 desktop/69 at each compact size pass with no page errors. TypeScript/Vite compiles110 modules in25.56s. All112 current app/entry files, both dependency manifests, painting/mobile test sources and every immutable8106 asset agree with pre-build hashes. Both artwork project downloads remain byte-identical to the original protected backup; saved/reopened and previous-production pixels are exact. The identical-input40-workflow native acceptance rerun remains separate and does not inherit a case Pass from these component checks.


### D-026/D-027 final acceptance verification

Original40 workflows/640 actual downloads show143 failed requirements. Same-plan40 after workflows/640 downloads now pass every independent lifecycle/locality/alpha/Paper/neighbour/history/retry/fresh-input criterion on immutable8106. All4 hidden Black Hole targets restore their original invisible state on Undo. The5-mode eraser family is complete for its defined Paper/clear-sheet software scope; physical inputs are not certified.

### H-024 — native cancellation setup exceeded its original deadline

The first after run completed18 rows, then its clear-touchCancel-v1 setup exceeded the original500ms gate before requesting cancellation. It was retained as a harness interruption, with no product verdict from that row. The remaining22 rows, starting with that identical touchCancel case, were retried in a fresh evidence directory with unchanged inputs,hold settings,500ms deadline and strict post-acknowledgement equality. All40 complete case workflows remain independently verified. No tolerance was widened and no awkward case omitted.


### H-025 — Pencil needs its visible Classic brushes navigation

The outside-paper acceptance harness completed20 native Marker/Calligraphy rows, then tried the hidden Pencil control before opening Classic brushes. The timeout and incomplete Pencil setup are retained in `headless/PAINT-019-first`. The corrected harness uses the actual `details.extra-choices summary` and retries all4 original Pencil rows, with identical source coordinates/size/Strength/termination modes/layout pairs. All24 workflows/384 actual downloads pass independent clipping/continuity/termination/next-gesture/history/fresh-input verification. No forced click, changed acceptance tolerance or omitted row is used.


### H-026 — picker oracle assumed a topmost new sheet

The initial independent verifier stopped because it assumed the newly added clear target was last in the layer array. The normal Layers contract inserts above the active Character,below Caption. Original input,order and files remain; the corrected oracle locates the explicit active target ID and requires all original layers/order/fields to stay exact. `evidence/verify-picker002-initial-top-sheet-assumption.py` and `INK-002-initial-layer-oracle-failure.json` preserve the invalid assumption.

### H-027 — picker fresh input uses the documented optional no-clip default

Four main fresh-input strict-JSON checks differed only at `$.layers[2].live.strokes[0].clip`: absent before,explicit null after. All four rendered PNGs are pixel exact and every other value/image is strict. This is the pre-existing documented absent-to-null optional no-clipping representation,not a new product scope change. Original four-failure report/verifier and exact key-presence diagnostic remain retained. The corrected oracle permits only that exact path/default and records it per layout. No pixel threshold or other source field is relaxed.

The main136-download picker scope now passes. A separate112-download sentinel history probe is required before the case can be Pass, because unchanged source/RGBA alone cannot rule out a no-op Undo entry.


### H-028 — history restores the paper viewport,so every later test point needs navigation

The separate picker no-empty-history probe first completed3 layouts,but its new landscape sentinel y80 was covered by workspace controls. Adding that point to the initial normal Zoom-out preflight let the first sentinel run. A second incomplete landscape attempt then showed Undo/Redo restores canvas state and its default paper viewport,covering the next sentinel again. Both failed attempts,harness versions and bytes are retained. The final retry preflights each original sentinel after history and uses actual Zoom out before its unchanged source coordinates. All4 layouts/12 sentinel probes/112 downloads now independently pass. Main136 downloads and300 magnifier cell centres also pass; INK-002 is Pass with248 downloads. No invisible or undelivered input is counted.

The same missing post-history navigation was independently detected by the secondary-colour case: original v2 final Green stroke delivered no native down/move/up to the canvas,so a UI-complete report could not establish acceptance. The original five failed requirements/96-download report and native trace stay retained. A same-coordinate v2 retry uses actual paper navigation; its final independent result remains separate. This is a harness reachability correction,not a product repair or relaxed pixel threshold.


### Secondary-colour H-028 completion

The explicit v2 retry uses the same original source paths/size/Strength/right sample/Swap steps,with normal paper navigation after viewport-restoring history. Three complete original rows plus the corrected v2 pass all4-layout96-download native contextmenu/pigment/source/no-empty-history/fresh-input requirements. The original v2 raw files/24 downloads and five failed requirements remain excluded from successful count. The original UI-complete label was never accepted as an application Pass. INK-003 is now Pass.


### H-029 — straight-RGB edge representations can encode the same exact native canvas pixel

All8 wheel/RGB workflows/80 actual downloads passed their selection,HSV geometry,rendered hue families,actual pointer/keyboard,bounds,opaque cores,locality,full11/15-step histories andsaved/reopened source checks. An extra final public-snapshot comparison initially failed because160 translucent edge pixels used two straight-RGB representations. Examples128/127 atAlpha222 both encode exact native associated byte111. This is not a new numeric tolerance.

The initial eight-failure report andverifier stay retained. Independent NumPy integer arithmetic requires every associatedRGBA byte to be identical,Alpha exact andevery opaque RGB strict. An application-free own headless page decodes both actual PNGs andcomposites them on Black andWhite;every output RGBA pixel is exact for all8 workflows. Positive single-pixel calibrations confirm both representations map to the same native read/PNG pixel. Opaque128-versus127 negative controls remain distinct,so an actual one-byte opaque colour error still fails. No app renderer/converter/kernel supplies expected pixels. Every actual source/PNG andsource/PNG afterfresh input remains rawRGBA exact. The corrected cross-representation assertion uses exact native identity plus same-file native composition evidence,with noepsilon or enlarged threshold. All original requirements remain. INK-005 is Pass with104 opaque marks,24 outside-RGB paths and80 verified downloads.


### H-030 — Neon transparent export needs the normal Advanced Layers navigation

The Neon harness restored Basic mode for both actual painting gestures,but then tried the deliberately hidden advanced-only Layers toggle for its separate guide-eye/transparent-export branch. Native painting/history and14 downloads remain retained;the complete row was never counted. The corrected harness re-enables Advanced through the actual File switch before using the guide eye,then reruns all4 original workflows with identical source paths,colours,criteria andtolerances in a fresh folder. Main Neon painting still runs in Basic. No forced hidden click or product-source change is used.


### H-030 completion

All4 original Neon workflows now pass with8 native Basic-mode Blue/Pink lines and72 complete verified downloads. Advanced is used through the actual File switch only for layer setup/guide visibility during the alpha-export branch. Independent halo hue/brightness/falloff/locality/previous-line retention,opaque-scene exact pixels,complete histories andraw transparent-export/fresh source/RGBA pass. The original14 interrupted setup downloads remain separate. No product code or tolerance changed. INK-007 is Pass.
