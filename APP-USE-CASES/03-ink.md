# Colours textures gradients and live ink

19 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Material selection affects future marks unless an explicit edit is active. Freeze time when comparing rendered animation frames. Static image downloads capture one frame; projects retain the supported live definitions, with the specific rainbow baking exception described in decisions.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="ink-001"></a>

## INK-001 Choose bright palette colours

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to choose bright palette colours, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Tap each standard colour swatch.
2. Make a short mark after each.
3. Return to the first colour.

**Acceptance criteria:**

- The chosen swatch is marked selected.
- Marks use their chosen colours.
- Changing the palette does not recolour old ordinary marks.

**Alternative and failure path:** Run every swatch including white against a nonwhite background so an invisible mark cannot masquerade as success.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-002"></a>

## INK-002 Borrow a colour from the visible picture

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to borrow a colour from the visible picture, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Pick colour.
2. Sample a known composite overlap and a plain patch.
3. Paint a test swatch.

**Acceptance criteria:**

- The borrowed colour represents the visible composition.
- The magnified preview identifies the sampling area.
- The new swatch matches the sampled RGB value.

**Alternative and failure path:** Hidden layers must not influence the sampled colour and sampling must not paint a dot.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-003"></a>

## INK-003 Keep a second colour ready

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep a second colour ready, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Set primary red and secondary blue.
2. Right drag with a drawing tool.
3. Right sample a green patch then swap colours.

**Acceptance criteria:**

- Right button drawing uses the secondary colour.
- Right sampling changes the secondary colour.
- Swap exchanges the two choices visibly.

**Alternative and failure path:** A browser context menu must not consume the app gesture when right button drawing is supported.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-004"></a>

## INK-004 Choose an exact hex colour

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to choose an exact hex colour, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open the colour wheel.
2. Enter #123ABC and commit.
3. Paint and read the saved patch.

**Acceptance criteria:**

- The wheel swatch and numeric fields agree.
- The resulting fully opaque flat patch is RGB 18 58 188.
- The chosen colour persists after the dialog closes.

**Alternative and failure path:** Malformed or incomplete input must be rejected or left editable without committing a different unexplained colour.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-005"></a>

## INK-005 Choose colour with the wheel and RGB fields

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to choose colour with the wheel and RGB fields, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move hue and tone selectors.
2. Enter RGB 32 128 224.
3. Reopen the wheel.

**Acceptance criteria:**

- The marker and all displayed values agree with the chosen colour.
- Reopening restores the selection.
- Keyboard entry can reach the same result as pointer input.

**Alternative and failure path:** RGB bounds 0 and 255 work and values outside the accepted range cannot corrupt the active colour.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-006"></a>

## INK-006 Paint a travelling rainbow

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to paint a travelling rainbow, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select Rainbow.
2. Draw a long curve and two separate short strokes.
3. Save a frame.

**Acceptance criteria:**

- Several hues follow the path rather than a single solid colour.
- The ordering is consistent with the stroke direction.
- The exported frame matches the visible stroke.

**Alternative and failure path:** Joining samples must not produce colour discontinuities or start every segment again at the same hue.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-007"></a>

## INK-007 Choose the colour of neon

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to choose the colour of neon, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose blue then Neon.
2. Make a dark background line.
3. Choose pink then Neon for another line.

**Acceptance criteria:**

- Each neon line has a bright centre and a halo of the selected tint.
- The blue line remains blue when pink is selected.
- The halo is visible in PNG.

**Alternative and failure path:** Partly transparent halo pixels must not become a hard opaque rectangle on export.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-008"></a>

## INK-008 Sprinkle stationary glitter

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to sprinkle stationary glitter, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose a tint then Glitter.
2. Draw a broad patch.
3. Wait then zoom and export.

**Acceptance criteria:**

- Glitter has metallic looking variation.
- Its committed pigment does not randomly move or flash.
- The exported patch retains the tint and alpha.

**Alternative and failure path:** Comparison must distinguish stationary glitter from animated water or static texture.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-009"></a>

## INK-009 Paint every repeating texture

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to paint every repeating texture, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose brick dots weave grass stone water and static in turn.
2. Make a separate labelled patch for each.
3. Zoom in and out.

**Acceptance criteria:**

- Each material has its named recognisable structure.
- Patterns tile without gross seams.
- Previous patches retain their material.

**Alternative and failure path:** Animate only materials designed to move and verify all seven textures rather than one representative texture.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-010"></a>

## INK-010 Fill a bounded connected region

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to fill a bounded connected region, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [FILL — Connected regions and tolerance](TEST-DATA.md#fill) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Bucket and a solid colour.
2. Tap inside a closed black outline.
3. Inspect inside outside and the line.

**Acceptance criteria:**

- The connected interior fills.
- The enclosing line and outside region remain intact.
- One Undo removes the fill.

**Alternative and failure path:** A one pixel opening intentionally allows flood propagation and must be tested separately from a truly closed outline.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-011"></a>

## INK-011 Adjust fill tolerance thoughtfully

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to adjust fill tolerance thoughtfully, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [FILL — Connected regions and tolerance](TEST-DATA.md#fill) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use a noisy nearly uniform interior.
2. Fill with low then higher tolerance on independent copies.
3. Compare masks.

**Acceptance criteria:**

- Higher tolerance includes more sufficiently similar connected pixels.
- Disconnected matching islands stay unchanged.
- The control value is visible.

**Alternative and failure path:** At tolerance boundaries the fill must finish without freezing or overwriting unrelated layers.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-012"></a>

## INK-012 Place a preset gradient

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to place a preset gradient, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [FILL — Connected regions and tolerance](TEST-DATA.md#fill) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Sunset Ocean Candy and Rainbow gradients in separate regions.
2. Fill each region.
3. Export a frame.

**Acceptance criteria:**

- The preset stop colours and ordering are recognisable.
- Colour transitions are smooth.
- The fill remains confined to its mask.

**Alternative and failure path:** Each preset must be exercised and a tiny region must not cause an invalid gradient or throw an error.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-013"></a>

## INK-013 Drag my own gradient direction

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to drag my own gradient direction, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [FILL — Connected regions and tolerance](TEST-DATA.md#fill) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable Drag a gradient and choose red and blue ends.
2. Drag across the bounded region.
3. Move each endpoint pin and finish.

**Acceptance criteria:**

- The start and end colours correspond to their pins.
- Moving pins changes direction and transition within the same mask.
- Finishing settles one intentional result.

**Alternative and failure path:** A zero length drag must use a defined fallback without leaving a broken pending fill.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-014"></a>

## INK-014 Keep a pending gradient reversible

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep a pending gradient reversible, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [FILL — Connected regions and tolerance](TEST-DATA.md#fill) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create a bounded pending gradient and move both endpoint pins.
2. Press Escape before the gradient is committed.
3. Repeat and use the ordinary settlement or next drawing action to commit, then Undo.

**Acceptance criteria:**

- Escape cancels the pending gradient and restores the unchanged underlying region.
- A deliberately settled gradient is committed once within its existing mask.
- Undo restores the exact region from before that committed gradient.

**Alternative and failure path:** Changing tools alone may leave a pending gradient until the next settlement action in the current source. The intended contract requires that no hidden pending preview leak into a saved project. Record this transition separately and report any mismatch instead of redefining cancellation after the result.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-015"></a>

## INK-015 Build a colour conveyor

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to build a colour conveyor, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open Live ink.
2. Add red yellow and blue stops.
3. Choose Snap then Ooze and paint in each mode.

**Acceptance criteria:**

- Snap changes between the chosen stops.
- Ooze blends between them.
- Marks use the configured sequence and direction.

**Alternative and failure path:** Removing stops down to an empty or one colour list must leave a usable defined material and no runtime error.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-016"></a>

## INK-016 Control the speed of living ink

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to control the speed of living ink, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Paint with live conveyor ink.
2. Change belt speed and compare fixed time intervals.
3. Pause interaction and observe.

**Acceptance criteria:**

- The configured speed has a visible consistent effect.
- Ordinary solid strokes do not start animating.
- The picture continues rendering while live content changes.

**Alternative and failure path:** Speed extremes and rapid mode switches must not accumulate timers or accelerate unrelated old material unexpectedly.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-017"></a>

## INK-017 Arm live ink deliberately

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to arm live ink deliberately, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Make an ordinary mark.
2. Enable Live ink and make another.
3. Disable it and make a third.

**Acceptance criteria:**

- Only strokes intended to use a live material carry that behavior.
- The armed state is visibly identifiable.
- The ordinary marks remain stable.

**Alternative and failure path:** Turning off the live control must not erase existing animation or silently bake every layer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-018"></a>

## INK-018 Save a still from a moving picture

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to save a still from a moving picture, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Prepare live water and conveyor marks.
2. Capture one known time and download PNG.
3. Open the PNG in a separate viewer.

**Acceptance criteria:**

- The file contains one coherent frame.
- All visible layers share the same capture time.
- Opening the downloaded file does not require the app to animate.

**Alternative and failure path:** The file must be decoded for comparison rather than accepting the presence of a download event as proof.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).

<a id="ink-019"></a>

## INK-019 Edit all eight conveyor slots and reverse its travel

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to edit all eight conveyor slots and reverse its travel, so I can choose materials that make my picture feel alive and keep their meaning when I save it.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Fill the eight visible slots with chosen colours.
2. Replace a middle slot and try adding a ninth.
3. Set speed to negative zero and positive values.

**Acceptance criteria:**

- Each slot retains its intended position in the sequence.
- The supported eight slot capacity is enforced.
- Negative speed reverses travel and zero produces a stable phase.

**Alternative and failure path:** Clearing all slots must leave an understandable safe material fallback rather than undefined colours or a permanently armed broken ink.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/materials.ts](../src/materials.ts), [src/color.ts](../src/color.ts), [src/colour-wheel.ts](../src/colour-wheel.ts), [src/fill.ts](../src/fill.ts), [src/live.ts](../src/live.ts), [src/rainbow-stroke.ts](../src/rainbow-stroke.ts), [src/types.ts](../src/types.ts).
