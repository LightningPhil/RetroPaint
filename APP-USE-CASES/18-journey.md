# Complete creative journeys across experience levels

10 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

These journeys intentionally combine smaller cases. They count as integration use cases, not as additional proof that each component has passed. Keep every intermediate saved artifact so a failure can be located at the correct transition.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="journey-001"></a>

## JOURNEY-001 Make a first colourful birthday picture

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to make a first colourful birthday picture, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Paint a background with broad marks.
2. Add stamps hearts and a short greeting.
3. Undo a mistake then Save PNG.

**Acceptance criteria:**

- A beginner can discover the required tools by labels and illustrations.
- The greeting and decoration are legible.
- The decoded file matches the final picture.

**Alternative and failure path:** If a mistake occurs recovery uses Undo rather than starting over or asking an adult to reconstruct the drawing.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-002"></a>

## JOURNEY-002 Make a symmetrical space creature

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to make a symmetrical space creature, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw a character with vertical symmetry.
2. Turn symmetry off for a name and stars.
3. Save a still.

**Acceptance criteria:**

- The body mirrors correctly.
- Later asymmetric details stay single.
- The final file has the intended composition.

**Alternative and failure path:** A forgotten symmetry mode must be visible enough to diagnose repeated text or stamps and recover the affected action.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-003"></a>

## JOURNEY-003 Make a moving water and Spiro scene

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to make a moving water and Spiro scene, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Paint a water area and live colour marks.
2. Make a Spiro decoration.
3. Save a project and a still image.

**Acceptance criteria:**

- The project reopens with supported live behavior.
- The image is one finished frame.
- The child can distinguish the two saved outcomes.

**Alternative and failure path:** The rainbow baking exception must be checked explicitly rather than promising every special material remains animated.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-004"></a>

## JOURNEY-004 Improve and caption a family photograph

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to improve and caption a family photograph, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open a photo and correct light and colour.
2. Crop it then Done.
3. Add a separate caption sheet and save project plus PNG.

**Acceptance criteria:**

- The finished photo and caption align.
- The project preserves the original and hidden crop margins.
- The image is a shareable finished composition.

**Alternative and failure path:** Use an ordinary local fixture for testing rather than uploading or publishing a real child's private photograph.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-005"></a>

## JOURNEY-005 Design a comic panel with reusable pieces

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to design a comic panel with reusable pieces, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Arrange characters speech bubbles and editable text.
2. Duplicate a character and change its pose through transforms.
3. Save reopen and revise one panel.

**Acceptance criteria:**

- The duplicated content remains independent.
- Layer and piece order make the dialogue readable.
- Reopening permits a targeted revision.

**Alternative and failure path:** Moving the wrong overlapping piece must be recoverable through selection controls and Undo without flattening the scene.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-006"></a>

## JOURNEY-006 Restore an older photo and inspect a larger copy

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to restore an older photo and inspect a larger copy, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Apply noise reduction gentle curves and a neutral correction.
2. Compare Before.
3. Preview enhancement then keep or reject the larger PNG.

**Acceptance criteria:**

- The user can compare every major change.
- The enhanced file is separate from the editable restoration.
- The original remains recoverable.

**Alternative and failure path:** Invented enhancement detail must not be represented as recovered historical fact or force the user to keep a worse result.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-007"></a>

## JOURNEY-007 Build a labelled printable desk container

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to build a labelled printable desk container, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [SHELL — Joined cube and cylinder plus simple shell oracle](TEST-DATA.md#shell) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Join a cube and partly embedded cylinder.
2. Shell the complex cap at 3 mm.
3. Pin a camera view add a caption and export project plus STL.

**Acceptance criteria:**

- The hollow model retains its intended outer size and wall floor thickness.
- The label stays on a paint sheet.
- The STL contains the actual cavity.

**Alternative and failure path:** The annotation must not be mistaken for raised printable lettering because a picture caption is not CAD geometry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-008"></a>

## JOURNEY-008 Trace a guide into a measured 3D part

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to trace a guide into a measured 3D part, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open a background drawing and an orthographic CAD view.
2. Build a dimensioned sketch with holes.
3. Hide the guide and check the model.

**Acceptance criteria:**

- The guide can be hidden from the open Layers palette.
- Dimensions are independently entered and checked.
- The geometry remains valid without the guide image.

**Alternative and failure path:** A photo guide is not automatically calibrated physical measurement, so dimensions require an explicit known scale reference.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-009"></a>

## JOURNEY-009 Revise a saved design without rebuilding it

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to revise a saved design without rebuilding it, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open a project containing constrained sketches a cut shell and edge finish.
2. Edit an earlier dimension and Preview.
3. Apply Undo then save a new project.

**Acceptance criteria:**

- Later features rebuild from retained inputs.
- One Undo restores the earlier design.
- The newly saved project reopens with the revised editable history.

**Alternative and failure path:** If an old face reference is no longer valid the draft must stop with a repair path instead of silently changing design intent.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).

<a id="journey-010"></a>

## JOURNEY-010 Prepare a complete delivery set

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to prepare a complete delivery set, so I can finish something meaningful while keeping a path back to the editable work.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Save an editable project a finished picture and an STL with chosen scope.
2. Reopen each independently.
3. Record dimensions geometry and file hashes.

**Acceptance criteria:**

- Each file has its intended role and genuine content.
- The picture and solid are consistent with the chosen final model.
- The project preserves future editability.

**Alternative and failure path:** The delivery is incomplete if only filenames or a success toast exist without readable valid file bytes.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [README.md](../README.md), [index.html](../index.html), [src/ui.ts](../src/ui.ts), [src/project.ts](../src/project.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/object-ui.ts](../src/object-ui.ts), [src/cad-ui.ts](../src/cad-ui.ts).
