# Shapes symmetry stamps and Spiro

22 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Shape and pattern previews must remain temporary until their normal completion action. Every selectable family has a parameter expansion in the coverage matrix. Changing a pattern tool does not recolour the paper.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="play-001"></a>

## PLAY-001 Draw straight lines and constrained lines

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to draw straight lines and constrained lines, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Line and drag a sloping segment.
2. Repeat with Shift.
3. Undo each line.

**Acceptance criteria:**

- Endpoints follow the drag.
- Shift snaps direction to the intended 45 degree increments.
- One Undo removes one whole line.

**Alternative and failure path:** A zero length line has a safe defined tap outcome rather than invalid coordinates.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-002"></a>

## PLAY-002 Draw rectangles circles and ovals

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to draw rectangles circles and ovals, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Drag each basic shape in both directions.
2. Repeat with Shift.
3. Compare bounds.

**Acceptance criteria:**

- Each shape fits the intended drag bounds.
- Shift preserves the relevant equal proportions.
- Reverse drags do not create negative or missing geometry.

**Alternative and failure path:** Exercise thin wide and tiny bounds as well as an ordinary shape.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-003"></a>

## PLAY-003 Choose outline and fill independently

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to choose outline and fill independently, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw a rectangle with brush solid and no outline.
2. Repeat with no primary and secondary fill.
3. Compare a known inside and outside pixel.

**Acceptance criteria:**

- Each outline mode has the intended stroke character.
- Fill uses the chosen source colour.
- No fill preserves the background inside.

**Alternative and failure path:** No outline plus no fill must not secretly replace the area with an opaque default colour.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-004"></a>

## PLAY-004 Tell a story with geometric shapes

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to tell a story with geometric shapes, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use triangles right triangles diamonds pentagons and hexagons.
2. Place one of each.
3. Undo and redo the last.

**Acceptance criteria:**

- Every chosen outline has the expected vertex structure.
- Placement is independent of earlier shapes.
- Redo restores the same shape.

**Alternative and failure path:** Small or reversed bounding boxes must preserve the selected family rather than falling back to rectangles.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-005"></a>

## PLAY-005 Decorate with stars hearts and lightning

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to decorate with stars hearts and lightning, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw four five and six point stars then a heart and lightning.
2. Change fill and outline.
3. Save a frame.

**Acceptance criteria:**

- Each decoration is recognisably different.
- Concave regions are filled consistently.
- Downloaded appearance matches the composed image.

**Alternative and failure path:** Check sharp corners and internal notches for incorrect bridging or holes.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-006"></a>

## PLAY-006 Point with arrows and rounded rectangles

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to point with arrows and rounded rectangles, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw arrows in all four directions and a rounded rectangle.
2. Resize their bounds.
3. Place beside a drawing.

**Acceptance criteria:**

- The arrow points in the selected direction.
- Rounded corners remain rounded.
- Shape size changes do not move surrounding content.

**Alternative and failure path:** A very narrow arrow or rounded rectangle must remain bounded and must not invert its outline.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-007"></a>

## PLAY-007 Give a character a speech bubble

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to give a character a speech bubble, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose rectangular oval and thought bubbles.
2. Draw each beside a stamp.
3. Add text in the intended area.

**Acceptance criteria:**

- The three bubble families have appropriate outlines.
- The tail stays connected.
- Fill and text do not erase the character behind them.

**Alternative and failure path:** Changing the bubble family while a preview is active must not leave a stray earlier preview on the picture.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-008"></a>

## PLAY-008 Build a polyline and finish it

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to build a polyline and finish it, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Tap four separate points with Polyline.
2. Finish with its button or Enter.
3. Undo then repeat with Escape before completion.

**Acceptance criteria:**

- Segments connect the chosen points in order.
- Completion produces one edit.
- Escape discards an unfinished path.

**Alternative and failure path:** With fewer than two usable points Finish must not create corrupt or unbounded geometry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-009"></a>

## PLAY-009 Draw a smooth spline

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to draw a smooth spline, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Spline and tap a curved sequence of points.
2. Finish the path.
3. Compare with the same points as a polyline.

**Acceptance criteria:**

- The spline is visibly smooth rather than angular.
- It follows the intended control sequence.
- Undo removes the whole finished spline.

**Alternative and failure path:** Repeated or extremely close points must not cause large loops or invalid numbers.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-010"></a>

## PLAY-010 Close a custom polygon

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to close a custom polygon, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Polygon and enter an irregular outline.
2. Complete it by the available finish action.
3. Inspect the last to first edge.

**Acceptance criteria:**

- The polygon closes once.
- Fill remains inside the closed outline.
- The committed shape can be undone.

**Alternative and failure path:** A self crossing or degenerate outline needs a consistent safe result or clear rejection without document corruption.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-011"></a>

## PLAY-011 Mirror a picture across an axis

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to mirror a picture across an axis, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable vertical symmetry and draw off centre.
2. Repeat with horizontal symmetry on a fresh copy.
3. Turn symmetry off.

**Acceptance criteria:**

- Each gesture has its correct reflected counterpart.
- The axis passes through paper centre.
- Turning symmetry off affects future marks only.

**Alternative and failure path:** A mark on the axis must not gain an unintended darker duplicate simply because two copies overlap.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-012"></a>

## PLAY-012 Make every radial symmetry pattern

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to make every radial symmetry pattern, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose 4 6 8 10 and 12 ways in turn.
2. Draw one asymmetric motif in each.
3. Count the repeated sectors.

**Acceptance criteria:**

- Each mode produces its specified number of arranged copies.
- Sector angles fill a full turn.
- One Undo removes the complete symmetric gesture.

**Alternative and failure path:** Use an asymmetric motif away from the centre so an incorrect repeat count cannot be hidden by coincident copies.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-013"></a>

## PLAY-013 Work inside a symmetry mask

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to work inside a symmetry mask, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable Mask in a radial mode and choose a wedge.
2. Draw and fill inside it.
3. Cross its boundary then change the active wedge.

**Acceptance criteria:**

- The active wedge is clearly indicated.
- Edits respect the selected working region and corresponding pattern.
- Crossing a boundary does not teleport a slip into another wedge.

**Alternative and failure path:** Turning symmetry off must restore ordinary full paper interaction without losing earlier masked art.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-014"></a>

## PLAY-014 Choose a stamp from every category

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to choose a stamp from every category, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Browse all illustrated stamp categories.
2. Choose one visible item from each.
3. Place it on the paper.

**Acceptance criteria:**

- Category navigation is usable and labelled.
- The selected stamp preview matches the placed artwork.
- No unrelated category is silently selected.

**Alternative and failure path:** Use the full stamp inventory expansion later to catch missing glyphs and incorrect category entries.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-015"></a>

## PLAY-015 Resize rotate and flip a stamp

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to resize rotate and flip a stamp, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Place a stamp at two sizes.
2. Try fixed and automatic rotation.
3. Toggle horizontal and vertical flip.

**Acceptance criteria:**

- Size changes the stamp rather than paper scale.
- Horizontal and vertical flip directions match their controls.
- Fixed rotation is stable and automatic placement chooses a small random turn within the current plus or minus 14 degree range.

**Alternative and failure path:** Undo and Redo retain the actual committed orientation rather than rerolling automatic rotation.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-016"></a>

## PLAY-016 Preview a stamp before placing it

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to preview a stamp before placing it, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move the pointer around without pressing.
2. Change size and flip.
3. Tap once then leave the paper.

**Acceptance criteria:**

- A translucent preview follows the pointer.
- The preview updates with settings.
- One tap makes one committed stamp.

**Alternative and failure path:** Cursor preview pixels must be absent from downloaded images and saved projects.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-017"></a>

## PLAY-017 Explore Spiro without changing my colours

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to explore Spiro without changing my colours, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose a paper colour and brush ink.
2. Open Spiro then close it without drawing.
3. Return to the brush.

**Acceptance criteria:**

- Opening the kit does not recolour existing pixels.
- Primary and secondary choices remain understandable.
- There is no new mark until an actual drawing gesture.

**Alternative and failure path:** An empty gear choice or cancelled drag must not deposit an accidental dot.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-018"></a>

## PLAY-018 Fit and move a Spiro ring

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to fit and move a Spiro ring, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move the ring away from centre.
2. Resize with the yellow handle.
3. Enter an exact Ring radius.

**Acceptance criteria:**

- The ring follows its centre and radius controls.
- The numeric radius and handle agree.
- The paper artwork does not move with the kit.

**Alternative and failure path:** At the accepted minimum and maximum radius the controls remain reachable or offer a way to return the kit to view.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-019"></a>

## PLAY-019 Choose gears and drawing holes

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to choose gears and drawing holes, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Tap a gear then select a hole.
2. Draw manually.
3. Try dragging a different gear onto the ring.

**Acceptance criteria:**

- The selected gear and hole are visible.
- The resulting path changes with the gear ratio and hole offset.
- Tap and supported drag selection reach the same gear.

**Alternative and failure path:** Dropping a gear outside its valid placement zone must not attach an unintended gear or leave a floating drag ghost.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-020"></a>

## PLAY-020 Wind a Spiro drawing and stop it

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to wind a Spiro drawing and stop it, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Auto and Wind the key.
2. Observe several turns.
3. Stop or reset the kit and Undo.

**Acceptance criteria:**

- The motor draws the configured curve.
- The controls communicate whether it is running.
- Stopping ends drawing and Undo restores the preceding picture.

**Alternative and failure path:** Opening another workflow or cancelling the pointer must not leave a hidden motor changing the picture.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-021"></a>

## PLAY-021 Use every Spiro ring shape

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to use every Spiro ring shape, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Ring Oval Square and Cross.
2. Make a short controlled pattern in each.
3. Change outer and inner teeth.

**Acceptance criteria:**

- Each stator follows its selected shape.
- Tooth choices affect the path predictably.
- Settings are reflected in controls.

**Alternative and failure path:** Invalid or incompatible tooth values must be constrained or explained before a broken path is committed.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).

<a id="play-022"></a>

## PLAY-022 Keep a Spiro pattern editable

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep a Spiro pattern editable, so I can turn playful experiments into deliberate patterns and illustrations.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Switch to Vectors and make a Spiro pattern.
2. Select resize and move it.
3. Save and reopen the project.

**Acceptance criteria:**

- The pattern remains an individually selectable piece.
- Transforms do not flatten neighbouring artwork.
- The reopened pattern retains its geometry and material.

**Alternative and failure path:** Switching back to Raster must not silently merge existing editable patterns.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/shapes.ts](../src/shapes.ts), [src/symmetry.ts](../src/symmetry.ts), [src/symmetry-mask.ts](../src/symmetry-mask.ts), [src/stamps.ts](../src/stamps.ts), [src/spiro.ts](../src/spiro.ts), [src/ui.ts](../src/ui.ts), [src/input.ts](../src/input.ts).
