# 3D workshop basics transforms and layers

22 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Millimetres are model units, independent of paper pixels and camera zoom. A visible mesh is not enough: appropriate cases require independent bounds, volume and closed surface checks. Workshop operations must respect the active CAD layer, locked state and busy state.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="solid-001"></a>

## SOLID-001 Enter and leave the 3D workshop safely

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to enter and leave the 3D workshop safely, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open More then 3D workshop.
2. Orbit the view.
3. Return to Paint and reopen.

**Acceptance criteria:**

- The workshop opens without replacing the drawing.
- Its controls use millimetres.
- Returning gives a valid paint sheet and retains the solid document.

**Alternative and failure path:** Opening twice must reuse the current workshop rather than create duplicate canvases or an extra 3D layer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-002"></a>

## SOLID-002 Build with every starting primitive

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to build with every starting primitive, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Add Cube Sphere Cylinder Cone Torus Tube Pyramid and Wedge in separate setups.
2. Inspect each from several views.
3. Undo each addition.

**Acceptance criteria:**

- Every listed shape has its recognisable solid form.
- The piece is in the active 3D layer.
- Adding it is one reversible operation.

**Alternative and failure path:** A collapsed or invalid primitive must be rejected rather than committed as an empty printable model.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-003"></a>

## SOLID-003 Understand the bed and model units

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to understand the bed and model units, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create a 20 by 20 by 20 mm cube.
2. Compare it with the bed grid.
3. Change zoom and inspect dimensions.

**Acceptance criteria:**

- Bounds remain 20 mm on each local axis.
- Volume is 8000 cubic mm for an unmodified cube.
- Camera zoom does not change those values.

**Alternative and failure path:** The default bed drawing is a reference and must not be confused with an automatic printer fit guarantee.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-004"></a>

## SOLID-004 Select a piece and multiple pieces

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to select a piece and multiple pieces, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Click one solid then Shift click another.
2. Click a blank workbench region.
3. Choose Select all where offered.

**Acceptance criteria:**

- The selected set is visibly marked.
- Multiple selection contains the intended unique IDs.
- Blank selection does not delete geometry.

**Alternative and failure path:** Hidden or locked pieces follow explicit selection and editability rules rather than accidentally becoming editable.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-005"></a>

## SOLID-005 Move a solid with its coloured handle

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to move a solid with its coloured handle, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a cube.
2. Drag one axis handle across several grid intervals.
3. Release then Undo.

**Acceptance criteria:**

- Only the intended axis changes.
- The gesture stays active across history updates.
- One Undo restores the original position.

**Alternative and failure path:** Losing pointer capture mid drag must end in a coherent committed or cancelled move without a stuck gizmo.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-006"></a>

## SOLID-006 Enter exact position and rotation

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to enter exact position and rotation, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Set position to -12.5 4 and 10 mm and Z rotation to 30 degrees.
2. Apply.
3. Undo and Redo.

**Acceptance criteria:**

- Fields and piece transform agree.
- The model's world bounds reflect the transform.
- The original dimensions are unchanged.

**Alternative and failure path:** Blank nonfinite or out of range coordinates must not replace the last valid transform.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-007"></a>

## SOLID-007 Turn a piece with rotation rings

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to turn a piece with rotation rings, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a non symmetric piece.
2. Drag each rotation ring.
3. Repeat with angle snapping.

**Acceptance criteria:**

- The chosen axis rotates around the intended pivot.
- Snap increments match the control.
- One gesture is one reversible transform.

**Alternative and failure path:** Use an asymmetric piece so a wrong axis rotation cannot pass through visual symmetry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-008"></a>

## SOLID-008 Resize with handles and exact dimensions

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to resize with handles and exact dimensions, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Resize one local axis with its handle.
2. Enter exact local width depth and height.
3. Undo.

**Acceptance criteria:**

- The local dimensions reach the requested values.
- Body placement follows the defined anchor.
- Other selected pieces follow the documented multi selection rule.

**Alternative and failure path:** Zero or negative dimensions and singular scale must be rejected before they become saved geometry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-009"></a>

## SOLID-009 Keep proportions when resizing

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep proportions when resizing, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a 20 by 10 by 30 piece.
2. Enable Keep proportions and set width 40.
3. Compare with a free resize.

**Acceptance criteria:**

- Proportional resize produces 40 by 20 by 60 within geometric tolerance.
- Free mode changes only requested axes.
- The control state is visible.

**Alternative and failure path:** Nonuniform pre existing scale must not unexpectedly compound dimensions twice.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-010"></a>

## SOLID-010 Set a tube wall within its size

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to set a tube wall within its size, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create a tube with known outer diameter and height.
2. Adjust Tube wall.
3. Inspect a section and volume.

**Acceptance criteria:**

- The wall matches the entered thickness within tessellation tolerance.
- The central bore remains open.
- The outside dimensions remain as requested.

**Alternative and failure path:** A wall that closes or inverts the bore must be constrained or rejected with the intact original retained.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-011"></a>

## SOLID-011 Name and colour a solid

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to name and colour a solid, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Rename one piece and choose each palette colour plus a custom colour.
2. Select another then return.
3. Save project.

**Acceptance criteria:**

- The body name and colour remain attached to its identity.
- Colour selection affects only intended pieces.
- The project retains colours.

**Alternative and failure path:** STL is a geometry format and must not be accepted as proof that body colours survived an export.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-012"></a>

## SOLID-012 Duplicate a solid independently

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to duplicate a solid independently, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Duplicate a selected piece.
2. Move and resize the copy.
3. Undo.

**Acceptance criteria:**

- The copy has its own unique identity.
- Its source recipe starts equivalent.
- Editing its transform does not mutate the original.

**Alternative and failure path:** Copying a feature tree must not introduce duplicate child IDs that break later History editing.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-013"></a>

## SOLID-013 Delete an unlocked piece and recover it

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to delete an unlocked piece and recover it, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select an unlocked piece among several.
2. Delete.
3. Undo then Redo.

**Acceptance criteria:**

- Only the intended piece is removed.
- Undo restores its complete recipe and transform.
- Redo repeats the same deletion.

**Alternative and failure path:** Locked pieces must be protected and an empty selection must not delete the whole layer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-014"></a>

## SOLID-014 Hide and lock individual pieces

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to hide and lock individual pieces, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open CAD Layers.
2. Hide one piece and lock another.
3. Try transforms then restore visibility and unlock.

**Acceptance criteria:**

- Hidden geometry is absent from the intended display and export scopes.
- Locked geometry cannot be changed accidentally.
- Restoring state retains recipes.

**Alternative and failure path:** The normal picture layer eye and the piece eye are different scopes and must both be tested.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-015"></a>

## SOLID-015 Create and switch 3D layers

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to create and switch 3D layers, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create a second 3D layer.
2. Add a solid.
3. Switch between layers and select pieces.

**Acceptance criteria:**

- The active layer is named.
- Pieces remain in their owning layer.
- Ordinary paint sheets are not converted into CAD layers silently.

**Alternative and failure path:** Layer count and total document limits still apply when adding a CAD layer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-016"></a>

## SOLID-016 Move pieces to a different 3D layer

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to move pieces to a different 3D layer, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select several unlocked pieces.
2. Choose a destination 3D layer.
3. Move them and Undo.

**Acceptance criteria:**

- Pieces arrive once with their transforms and recipes.
- The destination becomes a coherent editing target.
- Undo restores their original ownership.

**Alternative and failure path:** A full destination layer or selecting the same source and destination must fail safely without duplication or loss.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-017"></a>

## SOLID-017 Snap movement and angles deliberately

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to snap movement and angles deliberately, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose each offered grid and angle increment.
2. Drag a piece and a rotation ring.
3. Turn Snap off.

**Acceptance criteria:**

- Transforms follow the selected increments while snapping is enabled.
- Free movement is available when disabled.
- The numeric result matches the visible controls.

**Alternative and failure path:** Boundary values and negative coordinates must round consistently rather than drifting on repeated moves.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-018"></a>

## SOLID-018 Put a piece on the bed and centre it

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to put a piece on the bed and centre it, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move a rotated solid partly below Z zero.
2. Choose To bed.
3. Use the available centre action.

**Acceptance criteria:**

- The world minimum Z reaches zero.
- Rotation and dimensions stay unchanged.
- Centering uses the intended world bounds.

**Alternative and failure path:** A rotated or scaled piece must not use untransformed local bounds and remain partly under the bed.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-019"></a>

## SOLID-019 Align two pieces accurately

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to align two pieces accurately, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose a target and a moving piece.
2. Try each offered axis and before centre after placement mode with a known gap.
3. Undo.

**Acceptance criteria:**

- The target stays fixed.
- The moving piece reaches the requested relation using world bounds.
- Gap sign and units are consistent.

**Alternative and failure path:** An invalid target or one locked moving piece must be explained without partly transforming the selected group.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-020"></a>

## SOLID-020 Mate two opposite faces

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to mate two opposite faces, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Snap faces together.
2. Pick a face on the moving solid and a face on the target.
3. Inspect contact and normals.

**Acceptance criteria:**

- The chosen faces become coincident in the requested relation.
- Their normals oppose as intended.
- One Undo restores the moving solid.

**Alternative and failure path:** An ambiguous unsupported or identical face pair must not create a random rotation or alter the target.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-021"></a>

## SOLID-021 Repeat pieces in rows and around an axis

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to repeat pieces in rows and around an axis, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use the available linear and radial repeat controls.
2. Enter count spacing and turn values.
3. Undo.

**Acceptance criteria:**

- The intended number of independent copies is created.
- Positions or angles follow the entered series.
- The original stays present.

**Alternative and failure path:** Counts that exceed layer capacity must fail before producing a partial pattern.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).

<a id="solid-022"></a>

## SOLID-022 Mirror a solid without turning it inside out

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to mirror a solid without turning it inside out, so I can turn a simple idea into an accurately placed editable solid.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose each offered mirror axis on an asymmetric solid.
2. Inspect bounds orientation and volume.
3. Export a mesh copy.

**Acceptance criteria:**

- The mirrored shape has the intended handedness.
- Its surface remains outward and closed.
- Volume magnitude is preserved.

**Alternative and failure path:** A negative transform determinant must not yield an inward STL or erase a cavity during later repair.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-launch.ts](../src/cad-launch.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-document.ts](../src/cad-document.ts), [src/cad-model.ts](../src/cad-model.ts), [src/cad-viewport.ts](../src/cad-viewport.ts), [src/cad-camera.ts](../src/cad-camera.ts), [src/cad.css](../src/cad.css).
