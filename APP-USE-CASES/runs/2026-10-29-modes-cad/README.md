# Basic / Advanced workspace and 3D verification — 2026-10-29

The user requested a whole-app Basic / Advanced split and particular attention to 3D correctness. This focused change does not complete the existing 349-case acceptance audit or change its historical pass counts.

## Workspace behavior

- Basic is the default painting-and-play workspace. It hides vector authoring, Layers, Photo lab, enhancement, precision piece controls and the 3D entry point.
- Advanced exposes those tools. Its switch is in More, alongside an explanation of both modes, and is remembered on this device.
- Both modes use the same document. Switching does not flatten or replace artwork, insert a history step, or discard the document's vector preference. New Basic shapes, text, stamps and Spiro drawings use raster authoring. Existing editable pieces remain selectable for compatibility.
- Opening a CAD layer in Basic explains how to enable Advanced. The launch guard also covers a mode change while the lazy-loaded workshop code is arriving.
- The earlier Basic-to-CAD auto-promotion expectation is explicitly superseded by the user-requested mode boundary. See the dated decision in `../../BEHAVIOR-DECISIONS.md`.

## 3D defects corrected

1. **Entered tube wall thickness was scaled again by Apply size.** A 40 × 40 × 40 mm tube with a requested 2 mm wall exported approximately 18,082.66 mm³ instead of the expected 9,550.44 mm³. Tube size editing now absorbs the dimensions into the primitive and keeps the entered physical wall thickness. The candidate geometry is validated before replacing the model or adding history. Impossible walls are rejected instead of silently clamped; correction, Undo and Redo are tested.
2. **Precision reconstruction changed unevenly scaled tube cavities.** An unchanged source behind a suppressed finish rebuilt at about 3,518.49 mm³ instead of 4,523.89 mm³. The native precision builder now scales both inner ellipse axes with the outside. Uneven, mirrored and height-scaled variants pass the regression. [Failing-before evidence](../../../test-results/headless-2026-10-29T15-28-07-821Z/report.json) and [focused passing-after evidence](../../../test-results/headless-2026-10-29T15-28-26-626Z/report.json) are retained.

## Verification

- **531 regression checks pass:** 256 painting/component checks, 68 desktop UI checks and 69 at each of 320 × 568, 390 × 844 and 844 × 390. No failed checks or uncaught page errors. Existing CAD coverage includes sketches, constraints, transformed geometry, edges, fillets/chamfers, shells, lofts, sweeps, STL import, history, mixed picture layers and project persistence. [Final report](../../../test-results/headless-2026-10-29T15-33-26-994Z/report.json).
- **23 native-control workflows pass on the production build:** mode visibility and persistence at four layouts; retained vector content and Basic raster text; all eight primitive families; exact tube wall/size and rejected-wall recovery; union/subtraction/intersection/hull; enclosed-shell Preview/Cancel/Apply; ruled loft and straight sweep; Undo/Redo and exact saved-project reopening. [Production report and artifacts](../../../test-results/workshop-2026-10-29T15-34-29-940Z/report.json).
- Actual downloaded STL bytes are checked independently using triangle determinants, edge incidence/orientation, bounds and analytic expected volumes. Expected geometry is not calculated using the app's solid kernel or STL importer.
- The protected original artwork was reopened in two isolated contexts through real file controls. Saved editable project bytes remain identical. [Artwork preservation report](../../../test-results/protected-artwork-modes-cad/ARTWORK-headless-ui.json).
- TypeScript and the production Vite build pass. Output is in `test-results/build-modes-cad`; the existing tracked `dist` was not changed. Existing dependency externalization and large-chunk warnings remain.

All checks used owned, isolated headless Chrome sessions. No existing user browser/profile/artwork tab was accessed. This is software verification, not physical printer, pen, touch-device or assistive-technology certification. It is representative native workflow coverage plus the existing broader regression suite, not every possible CAD construction.

## Re-run

`npm test` runs the painting, geometry and responsive UI checks. `npm run test:workshop` runs the native controls and independent file checks in a disposable development server. For a separately served production build, run `node tests/workshop-acceptance-headless.mjs --origin http://127.0.0.1:8189/`.

Test output goes into fresh timestamped `test-results` folders, now ignored by Git. Original failed runs are retained. The initial native harness had an incorrect position-tab selector and omitted the required shell-face preparation; those harness failures are not counted as product defects or successful workflows. The final runs use the normal visible controls and retain the original geometry expectations.


## Follow-up: interactive Codex browser workshop audit

The later user-authorized audit operated the in-app browser directly with native clicks, typing, scrolling and screenshots. The existing user model was inspected without edits; modelling took place in separate test-preview tabs. This supplements the earlier isolated headless run above.

| User goal | Browser outcome |
| --- | --- |
| Drill a central 6 mm through-hole in a 20 mm block | Passed; the hole is open through the block. |
| Add a 4 × 4 × 4 mm boss beside that hole | Initially failed because face attachment probed the hole at the face centre; repaired and passed. |
| Cut a 4 × 4 × 3 mm pocket into the same part | Passed; hole, boss and pocket remain one editable solid. |
| Undo and redo the pocket | Passed; preceding geometry remains intact. |
| Make a hollow revolved vessel and move it beside the part | Passed. New revolve now defaults to New piece instead of inheriting Cut. |
| Preview a 270° revolve, then cancel | Passed; full 360° vessel restored. |
| Build a vessel and draw/pull a face rectangle at 320 × 568 | Passed through the actual phone-layout UI, including scrolling and Apply. |

Readability repairs: panel tabs now reserve their actual height; the sketch action bar replaces competing movement hints and clears the timeline; the depth handle uses the actual canvas bounds; compact timeline buttons have separate touch-sized rows, with the redundant scrub slider hidden; face selection updates its active-tool highlight; profile axes use no fill, removing a black triangle that obscured the revolve outline; through-hole instructions no longer refer to a hidden depth handle.

Geometry repair is shared by the mesh and precision engines: attachment probes the sketch footprint and adjusts only the plane's normal offset. A regression checks the combined hole/boss/pocket material volume and closed geometry through both engines.

Validation: 536 checks passed in the complete regression run (257 painting/geometry, 69 desktop, 70 at each of three compact sizes). The final timeline changes were rechecked with all 279 layout checks. Production build and type checking passed. Formal catalogue cases remain separate from these focused scenarios.

Evidence: [combined part](../../../test-results/codex-browser-workshop/hole-boss-pocket.png), [part and hollow vessel](../../../test-results/codex-browser-workshop/parts-and-vessel.png), [partial revolve preview](../../../test-results/codex-browser-workshop/partial-revolve-preview.png), [phone timeline](../../../test-results/codex-browser-workshop/phone-timeline-fixed.png), [phone pull preview](../../../test-results/codex-browser-workshop/phone-pull-preview.png). Reports: [full regression](../../../test-results/headless-2026-10-29T16-47-40-130Z/report.json), [final layout checks](../../../test-results/headless-2026-10-29T16-50-53-600Z/report.json).

These checks establish the listed workflows and layouts, not exhaustive support for every model, browser or physical touch device. Face sketches currently require flat faces.

## Connected annotations and layer grip follow-up

The 3D layer grip now selects its sheet without opening the workshop; pointer dragging and Alt+arrow reordering retain their existing history behavior. The layer thumbnail still opens 3D editing.

Advanced Paint offers **Text → Label + arrow**. Labels auto-size to their words, wrap at the chosen width, and default to a white background, black text, a thin black border and slightly rounded corners. Text colour, background, size, border and corner style are editable. Select exposes separate blue handles for the arrow target and the box centre. Moving the centre keeps the target fixed; the line reconnects to the closest edge, including rounded corners. Selection options includes Edit label. Labels remain editable through duplicate, undo and project save/reopen; annotation projects use version 11, with older projects still supported. Creation above a 3D sheet automatically inserts an annotation layer when necessary, including when Paper beneath the model is selected.

Native Codex browser verification covered actual 3D layer reordering, annotating a rendered cube, moving the arrow, moving the box independently, editing Component 1 to Box, automatic resizing, and draft reopening. A 320×568 preview also exercised custom text/background colours, border removal, square corners and scrolling to the placement controls. Browser testing found and fixed a hidden Edit label button and a preview occluded by the 3D layer; newly placed tips are kept within the paper.

Validation: 257 painting checks passed in `test-results/headless-2026-10-29T17-42-15-601Z/report.json`; 291 layout checks passed in `test-results/headless-2026-10-29T17-36-25-848Z/report.json`. Final annotation regressions passed at all four sizes in `test-results/headless-2026-10-29T17-44-06-547Z/report.json`. Type checking, production build and diff whitespace checks passed. Evidence is in `test-results/callout-browser/box-annotation.png` and `phone-coloured-label.png`. Production demo: http://127.0.0.1:8194/ (build output: `test-results/build-callouts`).

## OpenSCAD-style Code studio

Advanced 3D workshop now includes Code: an isolated code/preview editor with five starter models, numeric parameter controls, F5 and automatic preview, local .scad opening/saving, and Add/Update actions. Applied solids retain editable source in project version 12 and use the existing solid geometry, boolean, undo and STL paths. This is an independent supported language subset, not the OpenSCAD engine; compatibility and limits are documented in the editor and main README.

Regression coverage checks closed geometry for all five examples, boolean volumes, profile holes, module loops, transform order, cones, invalid and excessive programs, project source round trips, joining a scripted cube to an existing sphere, and STL serialization. UI coverage checks preview isolation, stale preview protection, add/update, source-preserving undo, errors, and layouts at 1280x720, 320x568, 390x844 and 844x390.

Validation: 557 checks passed (262 painting/geometry, 73 desktop and 74 at each compact size), with zero failures or page errors, in `test-results/headless-2026-10-29T19-57-45-477Z/report.json`. Type checking, production build and diff whitespace checks passed. Native Codex browser testing on the production build changed the flange from six to eight holes through Parameters, rebuilt it, added it to the scene and reopened its retained source. Evidence: `test-results/script-browser/code-studio-flange.png`. Production demo: http://127.0.0.1:8195/ (build output: `test-results/build-code-studio`).

## Official OpenSCAD engine follow-up

Code studio now runs the checksum-verified official OpenSCAD 2026.10.27 WebAssembly engine in a cancellable disposable worker. The old interpreter is no longer the editor runtime. The standard MCAD library and Noto Sans are bundled locally. Open .scad handles standalone files; Open folder preserves include/use/import paths and exposes an entry-script selector. Add files supplies dependencies/fonts. Project format 13 preserves source, entry and dependency bytes. Licence and provenance records live in public/openscad/NOTICE.txt.

Verified native functions, child modules, declarations, comprehensions, arbitrary transforms, mirror, Minkowski, offset, text, SVG/STL imports, heightmaps, relative libraries, bundled MCAD, missing-dependency errors, cancellation, path validation and dependency round trips. All five starters and two unchanged upstream examples render closed solids. The revolved bowl exposed collapsed STL triangles at its axis; only the native-engine transfer now discards collapsed faces, retaining the normal closed-edge validation. Ordinary STL imports keep their strict behavior.

Final validation: 266 painting/geometry checks passed in test-results/headless-2026-10-29T20-21-08-834Z/report.json; 299 layout checks passed in test-results/headless-2026-10-29T20-17-08-782Z/report.json, including folder/entry workflows at four sizes. Type checking, production build and diff checks passed. An earlier combined run exposed test-state leakage from a deliberately invalid draft; the folder test now waits for compilation to finish rather than for that unrelated draft to become valid.

Native production-browser checks confirmed engine rendering, Add, retained source, recovery and the repaired bowl. The native local-file picker check was blocked by the browser's upload approval gate (permission declined); it was not bypassed. File/folder handling remains covered by automated tests. Evidence: test-results/openscad-browser/native-engine.png and native-bowl.png. Demo: http://127.0.0.1:8196/; build: test-results/build-openscad.

Compatibility boundary: real OpenSCAD rendered-solid semantics, not a replacement for desktop OpenCSG preview or animation. STL does not retain colours; pure 2D output needs extrusion. Project-local external libraries/fonts must be supplied. Browser/workshop size, duration and mesh limits are stated in the editor and README; universal compatibility with every desktop project is not claimed.

## OpenSCAD editor refinement and regression audit

Separated the file currently being edited from the entry script being rendered. Helpers and libraries can now be edited without attempting to render them as standalone solids; all edited sources persist with the applied model. Native diagnostics select the affected project file and line. Parameter controls now use source ranges and expose only unique top-level numeric constants, excluding comments, strings, locals and repeated assignments, with exponent notation supported.

Fixed auto-preview enabling, immediate stale-preview invalidation during asynchronous file reads, cancellation/close/reopen races, and old file reads overwriting newer edits. Failed imports remain visible even with auto-preview enabled. The editor labels previous geometry as stale until rebuilding. Combined dependency size, UTF-8 source size and conflicting file/directory paths are checked. Native render metadata is snapshotted before execution so later caller mutations cannot alter retained source.

Diagnostic output is bounded, echoed ERROR text no longer falsely fails a model, real errors are not duplicated, and 2D/empty output receives an actionable extrusion/cut explanation. Added regressions for these cases, multi-file editing and error navigation, noisy output, delayed reads, cancellation, failed imports, and joining a native OpenSCAD cut solid to a workshop sphere before a closed STL round trip with preserved volume.

Final full regression: 572 checks passed (269 painting/geometry, 75 desktop, 76 at each of three compact sizes), zero failures or page errors. Report: test-results/headless-2026-10-29T20-32-23-800Z/report.json. Type checking, production build and diff checks passed. Native browser testing created a rounded two-hole mounting plate using Minkowski and difference, enabled auto-preview, changed width from 40 to 60 mm, added the model and reopened its source. Evidence: test-results/openscad-refined-browser/mounting-plate.png. Production demo: http://127.0.0.1:8197/; build: test-results/build-openscad-refined. Native local-file picking was not retried; file workflows were exercised by the automated suite.

## Code studio help wiki

Code studio now has a Help wiki with 68 authored articles covering the core OpenSCAD modelling operations, language constructs, built-in calculations, files, diagnostics and practical projects. Each reference article supplies syntax, parameter explanations, usage advice and examples, with related-topic navigation. Search and section filters also cover a catalogue of all 42 bundled MCAD source files, including declared signatures and expandable original source/comments. Experimental and desktop-only features are explicitly distinguished from supported rendered-solid workflows.

The 70 runnable examples open in a separate orbitable preview using the actual bundled OpenSCAD engine. They cannot replace the user's draft or add/change scene objects. Copy code, Back/Forward, keyboard dismissal and responsive reading layouts are included.

Validation: all 70 examples rendered closed, positive-volume solids with zero warnings. Full regression passed 578 checks (271 painting/geometry, 76 desktop, 77 at each of three compact sizes), with zero failures or page errors. Report: test-results/headless-2026-10-29T21-09-58-490Z/report.json. Type checking, production build and whitespace checks passed. Native production-browser verification confirmed readable reference layout, function search, the hollow-bowl preview and Escape returning to the article. Evidence: test-results/code-wiki-browser/function-reference.png and bowl-preview.png. Demo: http://127.0.0.1:8198/; build: test-results/build-code-wiki.

## Two-level wiki teaching and commented examples

Expanded all 68 core articles with a plain-language Level 1 introduction and a Level 2 explanation of the mechanics, followed by the detailed syntax, parameters and pitfalls. All 42 MCAD catalogue pages now have both reading levels, including how to load files, distinguish modules from functions and interpret signatures. Original third-party sources remain intact. Start here is first in the contents. Search indexes the new explanations and exercises; section buttons jump with keyboard focus to either level or commented examples.

Rewrote all 70 runnable examples as commented teaching code, each with an expected visual result and a specific change to try with its predicted outcome. Supplied SCAD helpers and the SVG asset are commented too; the numeric height grid is explained as data. All five Code studio starters now include concise comments. Refined the vector-axis example to produce a visible tilt, the nut recess to open through the top, and the MCAD box example to use the current roundedCube API. Adjusted the introductory Minkowski sphere resolution to avoid an engine fallback warning. Strengthened tray floor constraints in two examples.

Fixed asynchronous MCAD loading rebuilding the current article and losing its section position/focus. Regression coverage checks both learning levels, searchable teaching content, comments in code/helpers, expected results/exercises and section navigation at four screen sizes. All 70 wiki examples render closed positive-volume solids with zero warnings. Full regression passed 578 checks (271 painting/geometry, 76 desktop, 77 at each compact size), with zero failures or page errors. Report: test-results/headless-2026-10-29T21-35-36-634Z/report.json. Type checking, production build and diff whitespace checks passed.

Native production-browser verification covered the commented starter, beginner lesson, function search, section jump, complete annotated bowl code, guided exercise and isolated preview. Evidence: test-results/code-wiki-learning-browser/two-level-lesson.png, commented-example.png and annotated-bowl-preview.png. Demo: http://127.0.0.1:8199/; build: test-results/build-code-wiki-learning.

## Five advanced Code studio starters

Added Spiral lattice lantern, Orbital sculpture, Twisted wave pen pot, Rocket desk organiser and Castle gatehouse to Example > Load example, bringing the menu to ten starters. Each is self-contained native OpenSCAD code with concise comments, editable numeric dimensions, input checks and suggested variations. The original five subset examples remain separate fixtures for legacy project compatibility; the editor exposes both groups.

The models demonstrate crossing twisted extrusions, revolved rings, formula-generated profiles, tapered hollow stock, hull-built fins, repeated battlements and arched cutters. The lantern explicitly limits profile subdivision while retaining 48 height slices: its production mesh uses 12,104 triangles instead of 150,984, with the same intended lattice construction.

Validation: all five defaults and one parameter variation per model render without warnings, with positive volume, closed edges, a single connected surface and no geometry below the bed. Tests also confirm that parameter changes alter volume. Report: test-results/headless-2026-10-29T21-53-36-727Z/report.json. Example-menu loading and previews passed at 1280x720, 320x568, 390x844 and 844x390 without changing the scene: test-results/headless-2026-10-29T21-50-49-383Z/report.json. Native starter/upstream regressions passed in test-results/headless-2026-10-29T21-49-40-088Z/report.json; legacy subset fixtures passed in test-results/headless-2026-10-29T21-52-59-870Z/report.json. Type checking and production build passed. Existing dependency externalization and chunk-size build warnings remain.

Native production-browser inspection rendered all five models and confirmed their visible features. Screenshots: test-results/code-studio-showcase-browser/lantern.png, orbital.png, wave-pot.png, rocket.png and castle.png. Demo: http://127.0.0.1:8200/; build: test-results/build-code-studio-showcase. Earlier demo tabs were left intact.
