# Selections text and image transformations

24 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

A preview is distinguishable from a committed edit. Whole picture and selection scope must be explicit. A raster placed beyond paper is trimmed deliberately; editable vector geometry has a different retention rule. Test both rather than expecting one behavior everywhere.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="edit-001"></a>

## EDIT-001 Select a rectangular piece

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to select a rectangular piece, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Select and Rectangle.
2. Drag around a red patch.
3. Move it to an empty area and Place.

**Acceptance criteria:**

- The selection bounds match the chosen area.
- The moved patch arrives at the intended coordinates.
- One Undo restores the pre move picture.

**Alternative and failure path:** A drag outside the paper clips safely and a zero area selection must not delete the image.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-002"></a>

## EDIT-002 Cut around an irregular subject

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to cut around an irregular subject, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Lasso.
2. Trace a nonrectangular object.
3. Move it and Place.

**Acceptance criteria:**

- Only pixels within the closed lasso are included.
- The outside background stays behind.
- The selection edge follows the lasso.

**Alternative and failure path:** Ending near the start or outside the paper must close the lasso consistently without an enormous stray region.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-003"></a>

## EDIT-003 Select connected colour with the wand

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to select connected colour with the wand, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [FILL — Connected regions and tolerance](TEST-DATA.md#fill) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Colour wand and low tolerance.
2. Tap one coloured island.
3. Increase tolerance on a fresh copy.

**Acceptance criteria:**

- Selection contains connected qualifying pixels.
- Another disconnected matching island is excluded.
- The tolerance setting changes the intended boundary.

**Alternative and failure path:** Transparent areas and antialiased edges require explicit checks rather than treating every near colour as selected.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-004"></a>

## EDIT-004 Select all and invert a selection

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to select all and invert a selection, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select all then make a smaller rectangle.
2. Choose Invert.
3. Delete the inverted region and Undo.

**Acceptance criteria:**

- Select all covers the intended editing scope.
- Invert selects the complement in that scope.
- Undo restores all removed pixels.

**Alternative and failure path:** Invert with no existing selection needs a defined full scope outcome or an explanatory disabled control.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-005"></a>

## EDIT-005 Copy and cut without confusing them

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to copy and cut without confusing them, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Copy a patch and paste it.
2. Repeat using Cut on another patch.
3. Undo the cut and paste.

**Acceptance criteria:**

- Copy retains the source.
- Cut removes only its selected source.
- Paste creates a movable new instance.

**Alternative and failure path:** If the system clipboard is denied the in session copy must still be usable with an honest message.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-006"></a>

## EDIT-006 Place a floating raster selection

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to place a floating raster selection, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move a cut patch then resize its corner.
2. Choose Place.
3. Undo and Redo.

**Acceptance criteria:**

- Place commits the shown transform once.
- The floating handles disappear.
- Undo and Redo restore the correct source and placement.

**Alternative and failure path:** Changing tools uses the documented settlement rule and must not leave two copies of the same cut content.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-007"></a>

## EDIT-007 Cancel a floating raster selection

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to cancel a floating raster selection, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Cut and move a piece without placing it.
2. Press Escape or Cancel.
3. Compare with the saved before state.

**Acceptance criteria:**

- The unplaced operation is cancelled according to the raster selection contract.
- The original region is restored.
- No changed pixels survive the cancel.

**Alternative and failure path:** Do not apply the editable object Escape rule to an ordinary floating raster selection.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-008"></a>

## EDIT-008 Move and resize with clear constraints

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to move and resize with clear constraints, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move a piece freely.
2. Resize a corner with Shift.
3. Repeat without Shift.

**Acceptance criteria:**

- Unconstrained resizing changes width and height independently.
- Shift preserves aspect ratio.
- Handles match the effective transformed bounds.

**Alternative and failure path:** Dragging through a crossed or tiny bound must not create singular transforms or lose the piece.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-009"></a>

## EDIT-009 Use exact selection dimensions

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to use exact selection dimensions, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a 100 by 80 patch.
2. Open Image and Transform the selection.
3. Resize to 200 by 160 pixels.

**Acceptance criteria:**

- The selection reaches the entered size.
- Other document pixels retain their coordinates.
- Paper dimensions do not change.

**Alternative and failure path:** Blank zero negative or nonnumeric dimensions must be rejected before the edit is committed.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-010"></a>

## EDIT-010 Keep white transparent when placing a piece

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep white transparent when placing a piece, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Copy an image with white surround and coloured centre.
2. Enable Transparent white paper.
3. Place over blue.

**Acceptance criteria:**

- White background pixels follow the transparent selection policy.
- The coloured subject remains.
- Blue shows through the removed white.

**Alternative and failure path:** Near white and antialiased boundaries need a documented threshold or exact white rule rather than assuming automatic subject detection.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-011"></a>

## EDIT-011 Bring a partly lost piece back to paper

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to bring a partly lost piece back to paper, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Drag a selected patch partly beyond each edge.
2. Move it fully back before placement.
3. Use Bring selection to paper when offered.

**Acceptance criteria:**

- The complete uncommitted source can be recovered before placement.
- The desk overhang is visible and draggable.
- The bring action centres or returns the piece without resampling it.

**Alternative and failure path:** Dragging from the off paper preview must reach the same selected piece rather than drawing on the desk.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-012"></a>

## EDIT-012 Trim a placed raster overhang deliberately

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to trim a placed raster overhang deliberately, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move and rotate a raster across the left edge.
2. Place or deselect as documented.
3. Move the resulting piece back and Undo.

**Acceptance criteria:**

- Only in paper raster content survives permanent placement.
- Its transform and retained source resolution are preserved.
- Undo restores discarded pixels.

**Alternative and failure path:** Repeat at all four edges and completely outside the paper with a defined empty result that does not corrupt the layer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-013"></a>

## EDIT-013 Keep vector overhang recoverable

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep vector overhang recoverable, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move a vector fully beyond the paper.
2. Place then select it through the piece list.
3. Return it to the paper.

**Acceptance criteria:**

- The complete vector geometry survives outside the frame.
- Its piece remains addressable.
- Returning it restores the whole shape.

**Alternative and failure path:** Raster trimming rules must not be applied to vector paths or text geometry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-014"></a>

## EDIT-014 Flip and rotate a selected piece

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to flip and rotate a selected piece, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Flip horizontally then vertically.
2. Rotate by 90 degrees and by an arbitrary angle.
3. Undo the sequence.

**Acceptance criteria:**

- Each transform uses the selected piece centre or defined pivot.
- Neighbouring pixels stay unchanged.
- Undo restores exact earlier placement.

**Alternative and failure path:** Alpha edges must not acquire black or white fringes after repeated transforms.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-015"></a>

## EDIT-015 Resize a whole picture in pixels and percentages

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to resize a whole picture in pixels and percentages, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Turn off selection scope.
2. Resize to 480 by 320 then test 200 percent on a fresh copy.
3. Compare exported dimensions.

**Acceptance criteria:**

- Pixel and percent entry agree with their units.
- All intended layers transform consistently.
- Export dimensions match the resulting document.

**Alternative and failure path:** Reject dimensions beyond the supported edge or total layer pixel budget before allocating a destructive replacement.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-016"></a>

## EDIT-016 Change paper size without scaling artwork

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to change paper size without scaling artwork, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Change paper size.
2. Increase then reduce the canvas dimensions.
3. Compare a known 100 pixel square.

**Acceptance criteria:**

- The square keeps its source pixel dimensions.
- New paper area has the intended background or transparency.
- Undo recovers clipped content.

**Alternative and failure path:** A paper size change must not secretly invoke image scaling or alter a vector's geometry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-017"></a>

## EDIT-017 Choose smooth or crisp resizing

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to choose smooth or crisp resizing, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PIXEL — Crisp pixel art](TEST-DATA.md#pixel) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Resize identical copies by a noninteger factor with Smooth on and off.
2. Inspect edge colours.
3. Download both.

**Acceptance criteria:**

- Crisp resizing retains nearest source colour structure.
- Smooth uses interpolated edges.
- The selected option affects the actual output.

**Alternative and failure path:** The control must apply to the intended selection or image scope and not merely its on screen preview.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-018"></a>

## EDIT-018 Crop a selected image region

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to crop a selected image region, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a known 200 by 100 rectangle.
2. Choose Crop.
3. Undo.

**Acceptance criteria:**

- The new image extent matches that selected region.
- All intended document layers align to the new origin.
- Undo restores original dimensions and content.

**Alternative and failure path:** A missing selection must not crop to an arbitrary default area.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-019"></a>

## EDIT-019 Rotate flip and skew a whole image

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to rotate flip and skew a whole image, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose whole image scope.
2. Apply rotation flips and horizontal or vertical skew on independent copies.
3. Undo each.

**Acceptance criteria:**

- Every intended layer follows the same document transform.
- Output bounds include the transformed content according to the operation.
- Undo restores layer alignment.

**Alternative and failure path:** Use asymmetric corner labels to expose swapped axes incorrect sign or accidental mirroring.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-020"></a>

## EDIT-020 Invert or remove a flat background

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to invert or remove a flat background, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [FILL — Connected regions and tolerance](TEST-DATA.md#fill) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Invert the whole image on one copy.
2. On another choose background removal from the top left connected region.
3. Undo each.

**Acceptance criteria:**

- Invert affects the intended RGB channels and preserves alpha.
- Background removal follows connected corner colour and tolerance.
- Unconnected matching islands remain.

**Alternative and failure path:** This feature must not be presented or accepted as general AI subject segmentation.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-021"></a>

## EDIT-021 Write and place a caption

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to write and place a caption, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Text and enter two lines.
2. Tap a position and choose Place text.
3. Move the resulting selection.

**Acceptance criteria:**

- The visible words match the entered lines.
- Placement follows the selected paper position.
- The placed caption can be transformed and undone.

**Alternative and failure path:** Closing or cancelling an unfinished text draft must not leave partial letters in the saved image.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-022"></a>

## EDIT-022 Style a caption completely

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to style a caption completely, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose each available font in turn.
2. Set size alignment bold italic underline and strike through.
3. Place styled text.

**Acceptance criteria:**

- Every control changes the intended text property.
- Alignment and line breaks are coherent.
- The placed image matches the preview.

**Alternative and failure path:** If a platform substitutes an unavailable font the outcome must remain readable and the limitation must be recorded in the test evidence.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-023"></a>

## EDIT-023 Give text a readable background and width

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to give text a readable background and width, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Set a narrow text box and centre alignment.
2. Toggle second colour background.
3. Place over a busy picture.

**Acceptance criteria:**

- The width and wrapping follow the box settings.
- The opaque background uses the secondary colour.
- Transparent text leaves surrounding artwork visible.

**Alternative and failure path:** A very long word or empty text must not overflow controls or create an unexplained opaque rectangle.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).

<a id="edit-024"></a>

## EDIT-024 Use keyboard text placement without shortcuts firing

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to use keyboard text placement without shortcuts firing, so I can arrange and revise an illustration accurately without losing the source.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Type letters that are also tool shortcuts.
2. Press Ctrl or Cmd Enter to place.
3. Undo the result.

**Acceptance criteria:**

- Typing stays in the text field.
- The modifier Enter action matches Place text.
- One Undo removes the caption placement.

**Alternative and failure path:** Normal Enter within a multiline text field must not unexpectedly finish an unrelated path or trigger CAD controls.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/selection.ts](../src/selection.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/text-tool.ts](../src/text-tool.ts), [src/editor.ts](../src/editor.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/workspace-overlay.ts](../src/workspace-overlay.ts), [src/input.ts](../src/input.ts).
