# Acceptance testing protocol

## Preserve the original and identify the build

Save an independent editable project before destructive work on an existing picture. Verify its checksum, decode its layer images, and reopen a copy through the actual project input. Keep the original file immutable. Use disposable sessions or copies for corruption, quota, worker termination and permission tests. Documentation editing alone does not require altering artwork.

Record the application revision and a snapshot of dirty source files, browser and operating system versions, hardware, foreground viewport, input device, storage and clipboard capabilities, fixture hashes and execution time. A Git commit alone does not identify a working tree containing uncommitted changes. Test production output as well as development paths when bundling, codecs, model assets or workers are relevant.

## Execute a case as a user would

1. Read the case, its area contract, fixture, decision notes and required variant families before starting. Preserve a before snapshot independently of the implementation being exercised.
2. Set up every precondition visibly. Record layer, mode, crop, selection, live time and camera where relevant. Complete unrelated drafts unless the case explicitly uses them.
3. Use the real controls, pointer or keyboard path in the main flow. A direct call to an internal function is supplementary component coverage, not a substitute for discovering, focusing and operating the user interface.
4. Capture each criterion as a concrete observation. Retain before/after data and a screenshot or interaction recording. Check unchanged neighbouring content as well as the changed region.
5. Run the stated alternative or failure path on a fresh copy. Inspect partial state, the explanation, focus, controls and the ability to correct or retry. Verify that no late worker response changes the recovered document.
6. For a completed mutating action, exercise Undo and Redo when the feature supports them. For a draft, test Preview, explicit commit and Cancel separately. Workspace-only navigation must not create an unexplained data mutation or Undo step.
7. If content is persistent, save actual bytes and reopen through the real file workflow in a fresh session. Compare identity, order, recipes, geometry, source pixels, view and rendered composition as appropriate. Decode exports independently.
8. Run the required variants and document failures or unavailable capabilities. Finish by restoring a usable document and closing only temporary test resources.

## Independent oracles by feature

| Feature | Required evidence beyond a success message |
| --- | --- |
| Paint, fill, erase and selection | Known source pixel coordinates; affected and untouched masks; source dimensions and alpha; gesture-level Undo. Use deterministic input or recorded random state where possible. |
| Text, stamps and vectors | Object kinds, content and supported styling; independent bounds and transforms; target identity; rendered result on the actual supported platform. |
| Layers and composition | Unique sheet IDs, order, active target, visibility, opacity and paper properties; independently computed blending on known patches; supported per-layer data retained. |
| Photo adjustments | Known ramps and patches or seeded noisy inputs; the requested channel/tone/geometry effect; original pixels and recipes preserved; full-size decoded export rather than the small preview alone. |
| Animation and materials | Controlled time snapshots; correct supported live definitions after reopen; stable random or glitter content where specified; no UI overlays in captures. |
| Files and recovery | Actual bytes, genuine codec signatures, independent decoding and dimensions; complete real input round trip; deliberate comparison with the preserved before state. |
| Enhancement | Actual neural job and selected region or whole source; independent PNG decode; chosen scale and source snapshot; alpha and tile boundary checks; original document intact. A model filename in a request is insufficient. |
| CAD | Independent transformed bounds, analytic volumes for simple fixtures, section/ray sampling of cavities, closed oriented surfaces, retained feature recipes and actual STL bytes. Rendering transparency cannot prove physical hollow geometry. |
| Accessibility and layout | Real input reachability, focus and announced state; effective hit rectangles and legibility; actual assistive technology where a case requires it. A panel fitting the viewport is only one check. |
| Resource and privacy behavior | Recorded requests and payload origins, controlled capability failure, busy-state recovery, cancellation acknowledgment and subsequent successful operation. |

Never calculate the expected result by invoking the same serializer, solver, rendering kernel or import repair routine under test. An alternate front end that calls the same faulty kernel is not an independent oracle. Use elementary math, a separate decoder or an explicitly identified independent geometry inspection method. Record its version and tolerances.

## Scope and state rules

Always distinguish whole picture, active layer, selected piece, selected solid, CAD layer, all visible layers and final export scope. Test disabled controls and equivalent keyboard paths. Keep paint, Photo lab, vector selection, CAD feature editing, timeline rollback and long worker jobs from silently committing incompatible state. A rejected operation must preserve the complete valid document, not merely leave the same screenshot on a stale canvas.

View-only controls must not change saved geometry or paper resolution. Saved camera placement is an explicit document action. Crop and permanent raster placement have their own retention rules; do not demand that flattened PNG files retain editable sources or hidden margins.

## Responsiveness and interruption

Foreground interaction is the timing context. Record a proposed product target of one second from delivery of a Cancel or Close input event to visible acknowledgment during a long worker job. This is a normative target, not a measured claim about the current implementation. Exclude browser scheduling of background tabs from this measurement, while still testing that background/resume cannot corrupt data. Do not move the target after observing a miss without an explicit requirement decision.

Release outside the paper, pointercancel, lost capture and window blur must leave a coherent interaction and permit the next gesture. Test slow loading, stale asynchronous responses and worker restart. Successful cancellation includes cleanup and a usable retry, not simply a button disappearing.

## Variants and coverage accounting

Use COVERAGE-MATRIX.md and VARIANT-EXECUTION-LEDGER.csv. Execute every named selectable option at least once through the real UI unless it is explicitly identified as a serialized compatibility value. Use meaningful positive, negative, minimum, maximum and intermediate inputs. Required independent encoding, winding, scope and state variants cannot be replaced by a single representative example.

For large interaction spaces use exhaustive coverage for dangerous boundaries and individually named options, then a recorded pairwise plan for lower-risk combinations. Report exactly which combinations ran. Testing one of 131 stamps is one stamp tested, not all stamps; one square face shell is not a complex joined face shell. A valid rejection test does not prove the corresponding valid operation succeeds.

## Status rules and the execution ledger

The initial state is Not run. Allowed execution outcomes are Pass, Fail, Blocked and Partial. A case is Pass only after every required criterion, failure branch and planned required variant has evidence. Use Partial if only some variants ran. Use Blocked for missing fixture bytes, missing permission, absent hardware or an unavailable independent oracle; do not convert a blocked capability into a Pass. Attach each defect to its stable case ID with expected and actual values and reproducible evidence.

The supplied ledger is deliberately blank beyond IDs, titles and Not run. Documentation structure validation is not application testing. Existing regression check names are navigation aids and cannot be imported as Pass outcomes without demonstrating equivalent prerequisites, workflow, oracle and variant coverage.

## Preserve failed expectations

When behavior differs, save the failing input, before and after artifacts, console diagnostics where relevant and the result. Do not change fixtures to a simpler case, hide a layer that makes a defect visible, remove an acceptance criterion, widen a tolerance, rename a failure as unsupported, or substitute a fake downloaded payload just to obtain a pass. A valid product scope change needs an explicit recorded decision, and the old failing evidence stays linked.
