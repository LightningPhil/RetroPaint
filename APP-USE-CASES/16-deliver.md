# 3D inspection mixed pictures STL import and print preparation

23 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Camera changes and inspection are separate from model geometry. STL stores tessellated geometry without source sketches or colours. Checks must examine the exported file independently, including cavity orientation and dimensions. Slicer preparation and physical printing remain external steps.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="deliver-001"></a>

## DELIVER-001 Orbit pan zoom and fit without editing geometry

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to orbit pan zoom and fit without editing geometry, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Orbit drag pan and zoom.
2. Choose Fit.
3. Compare saved model recipes before and after.

**Acceptance criteria:**

- The camera changes while model dimensions and transforms stay the same.
- Fit brings intended geometry into view.
- The selected tool remains coherent.

**Alternative and failure path:** A drag intended to orbit while picking faces edges or measurements must not commit an accidental pick.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-002"></a>

## DELIVER-002 Choose every exact view

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to choose every exact view, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose isometric top bottom front back left and right.
2. Inspect an asymmetric labelled solid.
3. Return to 3D.

**Acceptance criteria:**

- Each view looks along the intended axis with a consistent up direction.
- The solid is not rotated to fake a view.
- The opposite views are genuinely distinct.

**Alternative and failure path:** A symmetric cube alone is insufficient to detect reversed or swapped views.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-003"></a>

## DELIVER-003 Use orthographic projection for a guide

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to use orthographic projection for a guide, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Orthographic and front view.
2. Compare parallel model edges with a guide image.
3. Switch to Perspective.

**Acceptance criteria:**

- Parallel edges remain parallel in orthographic view.
- Perspective gives natural depth.
- Changing projection does not change measured geometry.

**Alternative and failure path:** Fit and window resize must preserve a coherent camera span rather than stretching the model.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-004"></a>

## DELIVER-004 Fit only the selected pieces

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to fit only the selected pieces, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Place a small solid near a distant large solid.
2. Select the small one and Fit selected.
3. Clear selection and fit all.

**Acceptance criteria:**

- The selected scope controls the framing.
- All mode includes the intended visible model bounds.
- Geometry and placement remain unchanged.

**Alternative and failure path:** No selection or no visible selected pieces requires a defined fallback or clear message.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-005"></a>

## DELIVER-005 Measure between two model points

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to measure between two model points, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Pick two points on a known cube.
2. Pick two vertices then a third.
3. Read distance and XYZ differences.

**Acceptance criteria:**

- Vertex snaps use actual model coordinates.
- Distance and deltas match independent geometry.
- The third pick starts a new measurement.

**Alternative and failure path:** For a 20 mm cube the opposite corner distance is square root of 1200 mm, within the recorded mesh picking tolerance.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-006"></a>

## DELIVER-006 Inspect the angle between picked face normals

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to inspect the angle between picked face normals, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Pick points on perpendicular then parallel faces.
2. Read the reported normal angle.
3. Clear measurement.

**Acceptance criteria:**

- The reported angle follows the documented face normal convention.
- Orthogonal faces give 90 degrees within tolerance.
- Clear removes overlays without changing the model.

**Alternative and failure path:** Do not confuse a face normal angle with a free three point angle measurement that the app does not offer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-007"></a>

## DELIVER-007 Inspect dimensions of transformed pieces

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to inspect dimensions of transformed pieces, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a rotated and scaled noncube piece.
2. Read its bounds report.
3. Compare local size controls with world axis extents.

**Acceptance criteria:**

- The report labels and units distinguish world bounds from local dimensions.
- Values agree with an independent transform.
- Selecting another piece updates the target.

**Alternative and failure path:** The reported world box must not be presented as the unchanged primitive local dimensions.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-008"></a>

## DELIVER-008 Use X ray and wireframe temporarily

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to use X ray and wireframe temporarily, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose X ray then Wireframe.
2. Inspect a hollow model.
3. Leave Inspect.

**Acceptance criteria:**

- The display mode shows the intended transparency or mesh edges.
- Leaving restores full display.
- The solid data stays unchanged.

**Alternative and failure path:** Transparent display is not proof of a physical cavity and must not change exported material opacity or mesh content silently.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-009"></a>

## DELIVER-009 Move a cutaway plane through a model

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to move a cutaway plane through a model, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [SHELL — Joined cube and cylinder plus simple shell oracle](TEST-DATA.md#shell) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable cutaway.
2. Choose X Y and Z with known offsets.
3. Flip the retained side and leave Inspect.

**Acceptance criteria:**

- The clipped display follows axis position and side controls.
- The complete solid returns when leaving.
- Projects and STL retain full geometry.

**Alternative and failure path:** Cutaway is view only and must not be accepted as an actual boolean cut or hollow model.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-010"></a>

## DELIVER-010 Compose picture sheets above and below CAD

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to compose picture sheets above and below CAD, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable surrounding picture layers.
2. Orbit the model in front of a backdrop and behind an annotation.
3. Toggle the layer eyes.

**Acceptance criteria:**

- The normal layer stack determines front and back picture composition.
- Hiding a guide affects only its sheet.
- The solid remains editable.

**Alternative and failure path:** Picture helper canvases must respect visibility opacity and crop rather than draw all sheets at full opacity.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-011"></a>

## DELIVER-011 Pin a useful model view into the picture

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to pin a useful model view into the picture, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Orbit pan and zoom to the intended composition.
2. Choose Keep this view in the picture.
3. Return to Paint.

**Acceptance criteria:**

- The picture shows the chosen model placement.
- The camera recipe is retained.
- Undo restores the previous pinned placement.

**Alternative and failure path:** Model world coordinates must not be altered to imitate the camera placement.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-012"></a>

## DELIVER-012 Add a paint sheet above or below a model

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to add a paint sheet above or below a model, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use Paint above 3D then repeat Paint below 3D in a fresh copy.
2. Draw on each new sheet.
3. Undo.

**Acceptance criteria:**

- A transparent normal sheet is inserted adjacent to the source CAD layer.
- Paint opens on it with Layers available.
- One Undo restores the prior stack.

**Alternative and failure path:** At the layer limit the action must fail before creating a half complete transition or flattening the model.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-013"></a>

## DELIVER-013 Reopen a mixed CAD and photo project

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to reopen a mixed CAD and photo project, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Save the pinned view with backdrop photo recipe text and shell.
2. Reopen through Open project.
3. Return to CAD.

**Acceptance criteria:**

- Camera projection span position target and up are preserved.
- Picture layers retain pixels and recipes.
- The shell remains editable.

**Alternative and failure path:** A cached flat preview is insufficient: rebuild and edit the reopened solid as part of the case.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-014"></a>

## DELIVER-014 Import binary and ASCII STL

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to import binary and ASCII STL, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [STL — Independent mesh input](TEST-DATA.md#stl) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Import equivalent binary and ASCII closed mesh files.
2. Inspect the original mesh feature.
3. Move and cut it.

**Acceptance criteria:**

- Both formats preserve the intended shape and physical dimensions.
- The imported mesh stays as a source feature.
- Later supported solid operations remain editable.

**Alternative and failure path:** Do not claim that STL restores original CAD sketches or design history that the file does not contain.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-015"></a>

## DELIVER-015 Set STL units and bed placement explicitly

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to set STL units and bed placement explicitly, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [STL — Independent mesh input](TEST-DATA.md#stl) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Import a 2 unit cube as mm cm and inches in separate copies.
2. Toggle Centre on bed and bottom at zero.
3. Measure.

**Acceptance criteria:**

- Unit scales produce 2 20 and 50.8 mm edges.
- Enabled centering reaches XY centre zero and minimum Z zero.
- Disabled centering preserves file coordinates.

**Alternative and failure path:** STL has no reliable stored unit metadata, so the selected unit must not be silently guessed from filename or size.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-016"></a>

## DELIVER-016 Repair winding without filling cavities

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to repair winding without filling cavities, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [HOLLOW — Nested oriented mesh shells](TEST-DATA.md#hollow) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Import outward reversed one bad face and mixed shell orientation variants.
2. Inspect sections and volume.
3. Export again.

**Acceptance criteria:**

- Outer closed shells are oriented outward.
- Enclosed cavity shells remain subtractive.
- Disconnected solids and nested material islands remain correct.

**Alternative and failure path:** Taking the absolute volume of each component or orienting every shell outward would fill cavities and must fail.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-017"></a>

## DELIVER-017 Reject corrupt oversized or unsupported STL safely

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to reject corrupt oversized or unsupported STL safely, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CORRUPT — Disposable invalid inputs](TEST-DATA.md#corrupt) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Keep a valid model open.
2. Try truncated nonmanifold excessive triangle and over 20 MB fixtures.
3. Retry a valid STL.

**Acceptance criteria:**

- Invalid data produces a clear explanation.
- The current model stays intact.
- The next valid import still succeeds.

**Alternative and failure path:** Use up to the supported 200000 triangle limit as a separate acceptance boundary and do not reject all complex files merely to avoid the workload.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-018"></a>

## DELIVER-018 Handle imported mesh precision limitations honestly

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to handle imported mesh precision limitations honestly, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [STL — Independent mesh input](TEST-DATA.md#stl) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Try a supported simple imported mesh in shell or finish.
2. Try an unsupported complex surface.
3. Cancel or simplify.

**Acceptance criteria:**

- Supported geometry can use the available precision path.
- Unsupported geometry explains the limit.
- The original mesh is retained.

**Alternative and failure path:** A visual fake bevel or returning the unshelled original must not count as a successful precision operation.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-019"></a>

## DELIVER-019 Check printer volume against world bounds

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to check printer volume against world bounds, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enter a known printer build volume.
2. Check a fitting piece then an oversized transformed piece.
3. Change visibility scope.

**Acceptance criteria:**

- The report uses millimetre world bounds and selected scope.
- Oversize axes are identified.
- Reported volume and triangle count correspond to the actual result.

**Alternative and failure path:** Fitting the bed's drawn outline or camera view is not proof that the printer dimensions are satisfied.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-020"></a>

## DELIVER-020 Export all current or selected visible solids

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to export all current or selected visible solids, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [BOOLEAN — Analytic overlap and cutter](TEST-DATA.md#boolean) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Prepare a multilayer model with overlapping visible pieces, hidden pieces and a selected subset.
2. Export all visible CAD layers, the current layer, and selected visible pieces into three separate files.
3. Decode each actual STL independently and compare its included components, bounds and material volume.

**Acceptance criteria:**

- Each scope includes only its intended visible pieces.
- Overlapping solids are unioned without duplicate internal faces.
- File bounds and volume match the expected set.

**Alternative and failure path:** A hidden layer hidden body or unselected neighbour must not leak into the selected export.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-021"></a>

## DELIVER-021 Put exported STL on the bed deliberately

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to put exported STL on the bed deliberately, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Prepare a model with a known negative minimum Z and separately placed components.
2. Export copies with Place bottom at Z zero enabled and disabled.
3. Decode both files independently and compare Z bounds, dimensions, volume and relative component positions.

**Acceptance criteria:**

- Enabled placement makes minimum Z zero.
- Disabled preserves intended coordinates.
- Dimensions volume and relative component positions stay unchanged.

**Alternative and failure path:** Bed placement must translate the whole export consistently rather than move each component independently.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-022"></a>

## DELIVER-022 Export a real hollow printable surface

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to export a real hollow printable surface, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [SHELL — Joined cube and cylinder plus simple shell oracle](TEST-DATA.md#shell) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Export the complex joined shell as binary STL.
2. Decode with an independent reader and section it.
3. Compare with the editable model.

**Acceptance criteria:**

- The cavity and openings remain present.
- Surface edges form the expected closed printable manifold.
- Bounds and removed volume agree within tessellation tolerance.

**Alternative and failure path:** Triangle count a download name or a successful serializer alone cannot prove that the file is hollow or printable.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).

<a id="deliver-023"></a>

## DELIVER-023 Keep project geometry separate from inspection previews

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep project geometry separate from inspection previews, so I can check a model honestly and use it in both a picture and a printable file.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Roll back a timeline or open an unapplied feature preview.
2. Attempt project or STL save.
3. Return to Latest or apply and save.

**Acceptance criteria:**

- The app requires an intentional valid final state before exporting.
- Temporary cutaways measurements and draft meshes do not enter the saved result.
- The final file represents the complete chosen design.

**Alternative and failure path:** The user must get an explanation rather than a silently saved older step or a partially previewed solid.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-inspect-ui.ts](../src/cad-inspect-ui.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-stl.ts](../src/cad-stl.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-kernel.ts](../src/cad-kernel.ts), [src/project.ts](../src/project.ts).
