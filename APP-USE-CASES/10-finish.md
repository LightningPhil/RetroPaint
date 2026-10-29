# Photo detail effects geometry and lens corrections

24 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Detail needs source resolution checks. Geometry can alter a layer within a shared document frame. Crop retains source margins in projects. Grain must be stable between renders, not a random animated overlay.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="finish-001"></a>

## FINISH-001 Sharpen real edges with amount radius and threshold

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to sharpen real edges with amount radius and threshold, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Increase Sharpness then vary Radius and Threshold separately.
2. Inspect a line and a smooth patch.
3. Reset the group.

**Acceptance criteria:**

- Amount controls strength and radius controls the neighbourhood scale.
- Threshold protects suitable low contrast areas.
- Source dimensions remain unchanged.

**Alternative and failure path:** High settings must remain bounded and should not inject colour into a fully transparent border.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-002"></a>

## FINISH-002 Separate texture and clarity

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to separate texture and clarity, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Change Texture then Clarity on separate copies.
2. Inspect fine texture and broad local contrast.
3. Compare Before.

**Acceptance criteria:**

- Both controls have their intended distinct scale of effect.
- Their values remain independent.
- Resetting one does not reset the other.

**Alternative and failure path:** The test must use fine and broad features so a duplicate implementation cannot pass both cases by looking merely sharper.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-003"></a>

## FINISH-003 Try Pop as a creative enhancement

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to try Pop as a creative enhancement, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Increase Pop moderately.
2. Compare Before and After.
3. Reset it and use manual controls instead.

**Acceptance criteria:**

- Pop produces its defined combined presence effect.
- Its amount is controllable and reversible.
- The app does not claim proprietary third party processing.

**Alternative and failure path:** A highly saturated photo may be less pleasing and must remain recoverable without accepting a subjective improvement as a test oracle.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-004"></a>

## FINISH-004 Remove or add haze deliberately

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to remove or add haze deliberately, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use positive Dehaze on a hazy fixture.
2. Use negative on another copy.
3. Inspect contrast and neutral patches.

**Acceptance criteria:**

- The directions have opposite atmospheric effects.
- The amount remains bounded.
- The original is still available.

**Alternative and failure path:** At extreme values no channel may become nonfinite and alpha must be preserved.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-005"></a>

## FINISH-005 Reduce luminance speckles

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to reduce luminance speckles, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Apply Luminance noise reduction to a seeded noisy grey patch beside a sharp edge.
2. Compare local variance and edge position.
3. Reset.

**Acceptance criteria:**

- Variance falls in the flat patch.
- The strong edge remains positioned correctly.
- Alpha and dimensions do not change.

**Alternative and failure path:** Do not use an already smooth image as the only proof that noise reduction works.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-006"></a>

## FINISH-006 Reduce coloured noise separately

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to reduce coloured noise separately, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Apply Colour noise reduction to seeded coloured speckles.
2. Compare with luminance noise reduction.
3. Reset.

**Acceptance criteria:**

- Spurious chroma variation falls in the neutral patch.
- The control is independent from luminance smoothing.
- Large real colour boundaries remain identifiable.

**Alternative and failure path:** A uniform desaturation of the entire image is not an acceptable substitute for colour noise reduction.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-007"></a>

## FINISH-007 Frame a subject with a dark or light vignette

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to frame a subject with a dark or light vignette, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Apply negative and positive vignette settings on separate copies.
2. Inspect centre and corners.
3. Reset.

**Acceptance criteria:**

- The corners change in the labelled dark or light direction.
- The centre is relatively protected.
- The effect is stable after export.

**Alternative and failure path:** A cropped frame must use a consistent vignette coordinate policy rather than shifting unpredictably as panels open.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-008"></a>

## FINISH-008 Shape a vignette with its three controls

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to shape a vignette with its three controls, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Vary Midpoint Feather and Roundness one at a time.
2. Compare a uniform input.
3. Save the result.

**Acceptance criteria:**

- Midpoint changes reach.
- Feather changes transition softness.
- Roundness changes the contour while all remain independent.

**Alternative and failure path:** At all accepted endpoint values the effect must remain finite and within the picture bounds.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-009"></a>

## FINISH-009 Add deterministic film grain

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to add deterministic film grain, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Apply a fixed Grain amount.
2. Render the unchanged recipe twice.
3. Export a matching frame.

**Acceptance criteria:**

- The grain pattern remains fixed for the same source and settings.
- Noise is achromatic as intended.
- The amount affects visible variation.

**Alternative and failure path:** A redraw or zoom must not regenerate a completely different random pattern.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-010"></a>

## FINISH-010 Change grain clump size and roughness

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to change grain clump size and roughness, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use fixed Amount and vary Size then Roughness.
2. Inspect spatial correlation and luminance regions.
3. Reset.

**Acceptance criteria:**

- Size changes the texture's spatial scale.
- Roughness changes its structure.
- Grain preserves hue and alpha within the defined algorithm.

**Alternative and failure path:** Use seeded evidence and compare distributions instead of passing any two different random pictures.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-011"></a>

## FINISH-011 Crop by dragging a visible frame

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to crop by dragging a visible frame, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open Geometry Crop.
2. Drag a new box then move it from inside.
3. Resize a corner and choose Done.

**Acceptance criteria:**

- The visible frame follows the selected source area.
- Moving preserves its size.
- Export uses the resulting visible extent.

**Alternative and failure path:** Corners cannot create a zero area or outside source frame and Cancel restores the previous crop.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-012"></a>

## FINISH-012 Crop with a fixed ratio

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to crop with a fixed ratio, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose each offered ratio.
2. Resize the crop box.
3. Compare width divided by height.

**Acceptance criteria:**

- The frame maintains the chosen ratio within pixel rounding.
- Its bounds stay inside the source.
- Switching back to free allows independent proportions.

**Alternative and failure path:** Both portrait and landscape source images must be checked so a fixed ratio cannot be accidentally inverted.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-013"></a>

## FINISH-013 Enter exact crop coordinates

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to enter exact crop coordinates, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Set x 100 y 50 width 200 height 100 on a 960 by 640 source.
2. Apply and export.
3. Undo.

**Acceptance criteria:**

- The output is 200 by 100 and begins at the intended source coordinate.
- Controls represent source pixels.
- Undo restores the prior shared frame.

**Alternative and failure path:** Negative outside zero or incompatible crop dimensions must be rejected without losing the saved frame.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-014"></a>

## FINISH-014 Use the phone preview to crop accurately

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to use the phone preview to crop accurately, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open Geometry on a phone size view.
2. Drag and resize the crop in the miniature.
3. Compare it with the paper overlay.

**Acceptance criteria:**

- Miniature and full paper reference the same source rectangle.
- Letterboxing is accounted for.
- Touch interactions do not scroll the page instead of moving the crop.

**Alternative and failure path:** Touch outside the displayed image must not become an out of range source coordinate.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-015"></a>

## FINISH-015 Recover hidden crop margins later

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to recover hidden crop margins later, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Save a cropped recipe and project.
2. Reopen Geometry in a fresh session.
3. Expand the crop towards original edges.

**Acceptance criteria:**

- Full source margins are still available.
- Expanded content matches the original source.
- The project did not permanently trim the photo.

**Alternative and failure path:** The flattened exported PNG cannot restore hidden margins and must be kept distinct from the project during testing.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-016"></a>

## FINISH-016 Crop a multilayer composition consistently

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to crop a multilayer composition consistently, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Set a crop while editing one photo sheet.
2. Export with a text sheet and another paint layer visible.
3. Reopen the project.

**Acceptance criteria:**

- The shared output frame applies consistently to every visible layer.
- Objects remain aligned.
- Each sheet retains its full source data.

**Alternative and failure path:** A local straighten or lens adjustment on one layer must not be mistaken for a global transformation of every layer.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-017"></a>

## FINISH-017 Straighten a horizon by drawing a line

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to straighten a horizon by drawing a line, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [GEOMETRY — Coordinate and lens chart](TEST-DATA.md#geometry) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Activate horizon alignment.
2. Drag along the sloping reference horizon on paper then miniature.
3. Apply.

**Acceptance criteria:**

- The indicated horizon becomes level in the intended direction.
- The control reports its correction angle.
- Both input surfaces map consistently.

**Alternative and failure path:** A zero length or nearly vertical sample must have a defined safe response rather than a huge unexplained rotation.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-018"></a>

## FINISH-018 Straighten by an exact angle and fill the edges

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to straighten by an exact angle and fill the edges, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [GEOMETRY — Coordinate and lens chart](TEST-DATA.md#geometry) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enter an angle within minus 45 to plus 45 degrees.
2. Adjust Scale between 50 and 200 percent.
3. Compare clear corners.

**Acceptance criteria:**

- Angle and scale apply to the selected sheet.
- The chosen values are retained in the recipe.
- Increasing scale can intentionally cover transparent corners.

**Alternative and failure path:** A geometry preview must not permanently resize or trim the retained source pixels.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-019"></a>

## FINISH-019 Flip a photo sheet inside its frame

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to flip a photo sheet inside its frame, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [GEOMETRY — Coordinate and lens chart](TEST-DATA.md#geometry) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Apply horizontal and vertical photo flips separately.
2. Compare corner labels.
3. Undo.

**Acceptance criteria:**

- The chosen sheet flips in the indicated direction.
- Other sheets and the shared frame remain aligned.
- Undo restores the recipe.

**Alternative and failure path:** Do not confuse Photo lab sheet flips with whole document Image flips.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-020"></a>

## FINISH-020 Correct vertical perspective

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to correct vertical perspective, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [GEOMETRY — Coordinate and lens chart](TEST-DATA.md#geometry) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use a fixture with converging vertical building lines.
2. Adjust Vertical perspective with the grid visible.
3. Save the recipe.

**Acceptance criteria:**

- The intended vertical convergence changes in the expected direction.
- The grid offers a stable reference.
- The correction is retained without replacing the original.

**Alternative and failure path:** Extreme values must keep output finite and transparent outside samples safe.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-021"></a>

## FINISH-021 Correct horizontal perspective

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to correct horizontal perspective, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [GEOMETRY — Coordinate and lens chart](TEST-DATA.md#geometry) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use a skewed sign fixture.
2. Adjust Horizontal perspective separately.
3. Compare with a vertical only correction.

**Acceptance criteria:**

- The horizontal control addresses the intended axis.
- It remains independent from vertical perspective.
- The frame and source remain coherent.

**Alternative and failure path:** Both positive and negative values must be exercised to expose reversed sign or swapped axes.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-022"></a>

## FINISH-022 Correct barrel or pincushion distortion

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to correct barrel or pincushion distortion, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [GEOMETRY — Coordinate and lens chart](TEST-DATA.md#geometry) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use a bowed grid.
2. Adjust lens distortion in each direction.
3. Inspect straightness and clear corners.

**Acceptance criteria:**

- The control produces the expected opposite radial warps.
- The result can be refined manually.
- The app does not promise automatic lens profile correction.

**Alternative and failure path:** Transparent borders and out of source samples must not wrap or produce opaque garbage.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-023"></a>

## FINISH-023 Align red and blue fringes

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to align red and blue fringes, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [GEOMETRY — Coordinate and lens chart](TEST-DATA.md#geometry) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use deliberately separated red and blue edge channels.
2. Adjust fringe alignment.
3. Compare neutral edge coincidence.

**Acceptance criteria:**

- The colour edge offsets change in the intended direction.
- Unrelated alpha stays intact.
- The value remains editable after save.

**Alternative and failure path:** A global hue shift or blur is not an acceptable substitute for spatial channel alignment.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).

<a id="finish-024"></a>

## FINISH-024 Combine photo geometry without stale previews

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to combine photo geometry without stale previews, so I can refine a photograph without mistaking display tricks for changes to its saved source.

**Setup:** Use a preserved copy of [GEOMETRY — Coordinate and lens chart](TEST-DATA.md#geometry) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Change crop straighten perspective and lens settings rapidly.
2. Wait for the final preview.
3. Save and reopen.

**Acceptance criteria:**

- The final preview corresponds to the latest complete settings.
- Older worker responses cannot replace it.
- Full export uses that same saved recipe.

**Alternative and failure path:** Cancel during an unfinished preview must return to the prior saved state even if an old worker reply arrives later.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-engine.ts](../src/photo-engine.ts), [src/photo-processor.ts](../src/photo-processor.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-guides.ts](../src/photo-guides.ts), [src/film-grain.ts](../src/film-grain.ts), [src/document-frame.ts](../src/document-frame.ts).
