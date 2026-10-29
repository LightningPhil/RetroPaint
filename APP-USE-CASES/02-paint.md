# Brushes spray smudge and erasing

20 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

A pointer gesture is one edit. Paint follows paper coordinates at every zoom. Affected regions include the tool footprint, while unrelated layers and pixels stay unchanged. Random tools need distribution and containment checks rather than identical screenshots.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="paint-001"></a>

## PAINT-001 Draw a broad marker line

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to draw a broad marker line, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Marker at size 22 and full Strength.
2. Draw a curve then a short tap.
3. Undo each gesture separately.

**Acceptance criteria:**

- The curve is continuous with rounded joins.
- The tap leaves one intentional mark.
- The size preview corresponds to the affected paper area.

**Alternative and failure path:** Rapid pointer samples must not produce holes or join the end of this stroke to the start of the next.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-002"></a>

## PAINT-002 Sketch with a biro

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to sketch with a biro, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Biro and a dark colour.
2. Make slow and fast curved strokes.
3. Compare with the marker sample.

**Acceptance criteria:**

- The biro produces its own visibly finer pen character.
- Curves follow the hand.
- Switching applicators does not change previous marks.

**Alternative and failure path:** Returning from Spray restores a drawing applicator rather than spraying under a biro label.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-003"></a>

## PAINT-003 Make calligraphy with a shaped nib

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to make calligraphy with a shaped nib, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Calligraphy.
2. Draw horizontal vertical and diagonal strokes at one size.
3. Change colour and repeat.

**Acceptance criteria:**

- Stroke character depends on the nib direction.
- Joins remain continuous.
- Changing colour affects only subsequent marks.

**Alternative and failure path:** Sharp turns and very short strokes must not create huge spikes or an unpainted gap.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-004"></a>

## PAINT-004 Paint with textured poster colour

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to paint with textured poster colour, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Poster Paint and fill a small area with strokes.
2. Paint over one part again.
3. Undo the second pass.

**Acceptance criteria:**

- The mark has visible material texture rather than a flat marker clone.
- Overlap responds consistently to Strength.
- Undo restores the first pass.

**Alternative and failure path:** Texture should stay attached to the picture when zoom changes rather than sliding across existing paint.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-005"></a>

## PAINT-005 Build a watercolour wash

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to build a watercolour wash, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Watercolor at reduced Strength.
2. Make one wash then several overlaps.
3. Wait and compare the result with a saved frame.

**Acceptance criteria:**

- Overlapping washes visibly build colour.
- Edges remain soft within the footprint.
- The intended wet or static appearance is retained on export.

**Alternative and failure path:** A nearly transparent wash must not silently become opaque when the tool is changed or the project is saved.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-006"></a>

## PAINT-006 Draw exact pixel art with Pencil

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to draw exact pixel art with Pencil, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PIXEL — Crisp pixel art](TEST-DATA.md#pixel) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose the one pixel Pencil.
2. Draw a staircase on the enlarged pixel grid.
3. Save and reopen PNG.

**Acceptance criteria:**

- The pencil selects its intended one pixel width.
- Occupied source pixels align with the grid.
- Reopened dimensions and exact pixel colours match.

**Alternative and failure path:** At fit zoom a tap still changes the intended source pixel rather than a whole screen pixel block.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-007"></a>

## PAINT-007 Use every classic brush character

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to use every classic brush character, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open Classic brushes.
2. Repeat the same path with Classic Brush Oil Brush Crayon and Natural Pencil.
3. Compare samples and Undo each.

**Acceptance criteria:**

- Each named tool has a distinct usable appearance.
- The selected sample matches the actual mark family.
- Old marks do not change when another classic brush is selected.

**Alternative and failure path:** Run each listed brush with both a tap and a bent stroke rather than treating one brush as coverage for all four.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-008"></a>

## PAINT-008 Control size without rescaling old artwork

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to control size without rescaling old artwork, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Make a mark at size 1.
2. Repeat at 22 and 96.
3. Move the pointer at two zoom levels.

**Acceptance criteria:**

- The affected source footprint increases with size.
- The cursor indicates that footprint at each zoom.
- Old marks and document dimensions remain unchanged.

**Alternative and failure path:** Test both ends of the size range and rapid changes while the pointer is not drawing.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-009"></a>

## PAINT-009 Control Strength predictably

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to control Strength predictably, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw on white and coloured areas at Strength 1 then 0.15.
2. Overlap the weaker mark.
3. Undo the overlap.

**Acceptance criteria:**

- Lower Strength produces a weaker contribution.
- Overlap accumulates predictably for the selected applicator.
- Undo restores exact previous pixels.

**Alternative and failure path:** The strength label and actual active value must agree after switching tools and reopening a drawer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-010"></a>

## PAINT-010 Spray fine mist

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to spray fine mist, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Fine Mist.
2. Hold briefly then sweep across a contained area.
3. Repeat with a larger size.

**Acceptance criteria:**

- Pigment is distributed inside the intended spray region.
- Holding deposits paint without requiring movement.
- Size changes the area rather than the paper resolution.

**Alternative and failure path:** A long stationary press must stop depositing immediately when the pointer is released or cancelled.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-011"></a>

## PAINT-011 Make splatters intentionally

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to make splatters intentionally, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Splatter and a bright colour.
2. Spray near the middle then near an edge.
3. Undo the edge gesture.

**Acceptance criteria:**

- Drops have the chosen colour and splatter character.
- Edge marks clip at the document boundary.
- One Undo removes the entire spray gesture.

**Alternative and failure path:** Random drops outside the paper must not wrap around to the opposite edge.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-012"></a>

## PAINT-012 Celebrate with coloured confetti

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to celebrate with coloured confetti, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Paper Confetti and Rainbow.
2. Spray several short bursts.
3. Switch to a solid colour and spray again.

**Acceptance criteria:**

- Rainbow bursts contain several colours.
- Solid bursts use the chosen solid material.
- Confetti remains confined to the intended footprint.

**Alternative and failure path:** Undo and Redo must restore the committed burst rather than generate a visibly different random arrangement.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-013"></a>

## PAINT-013 Smudge wet colours together

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to smudge wet colours together, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [SMUDGE — Two wet colour regions](TEST-DATA.md#smudge) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Smudge and drag red towards blue.
2. Reduce Strength and repeat on a fresh copy.
3. Undo.

**Acceptance criteria:**

- Paint is displaced locally in the drag direction.
- The edge is feathered.
- Weaker Strength produces a smaller displacement.

**Alternative and failure path:** Dragging through transparent pixels must not inject opaque black or sample another layer accidentally.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-014"></a>

## PAINT-014 Erase on Paper and on a clear sheet

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to erase on Paper and on a clear sheet, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Scrub a mark on Paper.
2. Repeat on a transparent paint layer.
3. Undo both gestures.

**Acceptance criteria:**

- Paper erases to its defined paper colour.
- The transparent layer erases to alpha zero.
- Underlying visible layers show through the cleared region.

**Alternative and failure path:** Erasing a hidden sheet must not unexpectedly erase a visible neighbouring layer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-015"></a>

## PAINT-015 Pull paint into a black hole

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to pull paint into a black hole, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Black Hole eraser.
2. Hold and move through a painted region.
3. Release then Undo.

**Acceptance criteria:**

- The effect has a visible local shrinking or clearing action.
- Its scope follows the tool footprint.
- Release stops the effect and Undo restores the source.

**Alternative and failure path:** Pointer cancellation or leaving the browser must not leave the destructive effect running.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-016"></a>

## PAINT-016 Pixelate only the brushed area

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to pixelate only the brushed area, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Pixelate eraser.
2. Brush a small face detail.
3. Undo and compare surrounding areas.

**Acceptance criteria:**

- Pixels inside the footprint become visibly blockier.
- Areas outside remain unchanged.
- Undo restores the original detail.

**Alternative and failure path:** A smaller size must not pixelate the entire image or the entire selected layer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-017"></a>

## PAINT-017 Invert only the brushed area

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to invert only the brushed area, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Invert eraser.
2. Brush once over known RGB patches.
3. Repeat over the same region and Undo.

**Acceptance criteria:**

- Affected RGB values invert within the painted mask.
- Alpha is preserved.
- Two full inversions of fully covered pixels return their original RGB values.

**Alternative and failure path:** Partly covered antialiased edges require mask weighted comparison rather than expecting exact full inversion.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-018"></a>

## PAINT-018 Emboss a local texture

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to emboss a local texture, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Emboss eraser.
2. Brush across a high contrast edge.
3. Compare the brushed and untouched areas.

**Acceptance criteria:**

- The effect makes a local relief appearance.
- Untouched detail and transparency remain intact.
- Undo restores the source.

**Alternative and failure path:** A transparent border must remain clear rather than acquiring an opaque embossed fringe.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-019"></a>

## PAINT-019 Finish a stroke safely outside the paper

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to finish a stroke safely outside the paper, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Start drawing inside the paper.
2. Drag outside then release.
3. Start a new mark elsewhere.

**Acceptance criteria:**

- The first mark is clipped to the paper.
- Release ends the gesture even outside.
- The next mark starts independently.

**Alternative and failure path:** Repeat pointercancel lost capture and window blur with no stuck drawing state or false connecting line.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).

<a id="paint-020"></a>

## PAINT-020 Keep a fast pen curve smooth

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep a fast pen curve smooth, so I can express a particular mark rather than fight the painting tool.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw a fast looping path with mouse and pen.
2. Repeat while the display is busy.
3. Inspect the saved source image.

**Acceptance criteria:**

- Available intermediate pointer samples contribute to the path.
- The result remains continuous.
- Pressure or hardware variations do not change document scale.

**Alternative and failure path:** An unsupported coalesced sample API must fall back to ordinary pointer input without crashing.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/brush.ts](../src/brush.ts), [src/stroke-renderer.ts](../src/stroke-renderer.ts), [src/input.ts](../src/input.ts), [src/draw.ts](../src/draw.ts), [src/smudge.ts](../src/smudge.ts), [src/effects.ts](../src/effects.ts), [src/ui.ts](../src/ui.ts), [src/types.ts](../src/types.ts).
