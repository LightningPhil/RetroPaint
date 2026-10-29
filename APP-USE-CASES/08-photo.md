# Photo lab workflow light and looks

19 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Photo edits are saved recipes on the selected sheet. Done commits the draft, Cancel discards that draft, and Before is a comparison. Original pixels and hidden crop margins must remain recoverable. A photograph need not look better to every viewer: acceptance checks isolate the effect being requested.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="photo-001"></a>

## PHOTO-001 Open a photograph directly into Photo lab

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to open a photograph directly into Photo lab, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable Advanced mode and choose Photo lab Open photo.
2. Choose a supported photo.
3. Inspect the selected sheet and category.

**Acceptance criteria:**

- The chosen photo becomes the intended editing target.
- The lab reopens with useful remembered context.
- The import does not silently edit an old hidden layer.

**Alternative and failure path:** Cancelling the file chooser restores the previous draft and its settings rather than resetting the lab.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-002"></a>

## PHOTO-002 Explore every photo adjustment group

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to explore every photo adjustment group, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Browse Light Colour Curves Detail Effects and Geometry.
2. Choose every group within each category.
3. Return to an earlier group.

**Acceptance criteria:**

- Controls are named and reachable.
- Current values survive category changes.
- Navigation alone does not change the photo.

**Alternative and failure path:** Short screens may use a combined group selector but every function must still be reachable.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-003"></a>

## PHOTO-003 Compare Before and After without committing

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to compare Before and After without committing, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Change exposure and saturation in a draft.
2. Press Before then After.
3. Cancel the draft.

**Acceptance criteria:**

- Before shows the defined original source comparison.
- After restores the current draft preview.
- Comparison does not add an edit or replace the original.

**Alternative and failure path:** A comparison toggle during an asynchronous render must not show an old unrelated draft as the current result.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-004"></a>

## PHOTO-004 Cancel only my current photo experiment

**Primary user:** L2 adventurous older child. **Priority:** P0. **Execution:** Not run.

**User story:** As an adventurous older child, I want to cancel only my current photo experiment, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Save one adjustment with Done.
2. Reopen and make a very different draft.
3. Press Cancel.

**Acceptance criteria:**

- The earlier saved recipe remains.
- New draft changes are discarded.
- The original pixels and other sheets are unchanged.

**Alternative and failure path:** Photo lab Close and Escape must cancel the current draft, like Cancel. A late preview worker reply must not restore the discarded draft.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-005"></a>

## PHOTO-005 Save editable photo adjustments with Done

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to save editable photo adjustments with Done, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Adjust brightness and a curve.
2. Choose Done.
3. Reopen Photo lab and change them again.

**Acceptance criteria:**

- Done preserves the underlying original source.
- Reopening exposes the saved values.
- The next edit can revise the same recipe.

**Alternative and failure path:** A save or apply failure must leave the draft recoverable and must not report success before its commit completes.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-006"></a>

## PHOTO-006 Undo a completed photo edit

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to undo a completed photo edit, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Save one photo change.
2. Make a separate paint mark on another sheet.
3. Undo the mark then the photo edit and Redo both.

**Acceptance criteria:**

- History restores the intended recipe at its own step.
- Painting remains separate.
- Redo reproduces the same rendered result at a fixed time.

**Alternative and failure path:** An open unsaved photo draft must not consume or corrupt the ordinary document Undo sequence.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-007"></a>

## PHOTO-007 Reset one adjustment group

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to reset one adjustment group, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Set values in Light and Colour.
2. Reset only the current group with its reset control.
3. Inspect the other group.

**Acceptance criteria:**

- Only that group's settings return to their defaults.
- Other adjustments remain.
- The preview and numeric values agree.

**Alternative and failure path:** Double clicking a single slider resets only that slider rather than the entire photo.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-008"></a>

## PHOTO-008 Reset all saved photo adjustments

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to reset all saved photo adjustments, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Reopen a photo with tone curves grain and lens corrections.
2. Choose Reset.
3. Save with Done.

**Acceptance criteria:**

- All adjustment groups return to the defined defaults.
- The original remains available.
- The result can be undone.

**Alternative and failure path:** Cancel after Reset must restore the previously saved recipe rather than permanently clearing it.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-009"></a>

## PHOTO-009 Increase exposure by a known stop

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to increase exposure by a known stop, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [TONAL — Known luminance ramp](TEST-DATA.md#tonal) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Set all other adjustments neutral.
2. Apply plus one EV then minus one EV on separate copies.
3. Measure nonsaturated neutral patches.

**Acceptance criteria:**

- Plus one EV doubles linear light before clipping and display encoding.
- Minus one halves it.
- Alpha stays unchanged.

**Alternative and failure path:** Do not expect displayed 8 bit sRGB values simply to double and do not use clipped white as the only sample.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-010"></a>

## PHOTO-010 Raise brightness without confusing it with exposure

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to raise brightness without confusing it with exposure, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [TONAL — Known luminance ramp](TEST-DATA.md#tonal) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Apply a moderate positive brightness.
2. Compare dark midtone and bright patches.
3. Reset brightness.

**Acceptance criteria:**

- The intended midtone brightness shift is visible.
- Neutral patches remain neutral.
- Reset restores the baseline recipe.

**Alternative and failure path:** Compare brightness and exposure as distinct controls rather than accepting either one for both cases.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-011"></a>

## PHOTO-011 Add or soften contrast

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to add or soften contrast, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [TONAL — Known luminance ramp](TEST-DATA.md#tonal) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Apply positive then negative contrast on fresh copies.
2. Measure separation around a midtone.
3. Reset.

**Acceptance criteria:**

- Positive contrast increases useful tonal separation.
- Negative contrast softens it.
- The neutral baseline is recoverable.

**Alternative and failure path:** At extreme settings the preview must stay finite and alpha must not change even where RGB clips.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-012"></a>

## PHOTO-012 Recover highlights and lift shadows

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to recover highlights and lift shadows, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [TONAL — Known luminance ramp](TEST-DATA.md#tonal) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Reduce Highlights on a bright scene.
2. Raise Shadows on a dark scene.
3. Inspect protected midtones.

**Acceptance criteria:**

- Highlights primarily affect brighter tonal regions.
- Shadows primarily affect darker regions.
- The controls can be adjusted independently.

**Alternative and failure path:** Detail already clipped in the source must not be described as genuinely recovered information.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-013"></a>

## PHOTO-013 Set white and black endpoints

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to set white and black endpoints, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [TONAL — Known luminance ramp](TEST-DATA.md#tonal) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Adjust Whites and Blacks separately.
2. Inspect the histogram and known endpoint patches.
3. Reset one group.

**Acceptance criteria:**

- Each endpoint control affects its intended tonal region.
- Clipping indicators respond to rendered values.
- Reset restores known baseline values.

**Alternative and failure path:** Nearly transparent or fully clear pixels must not dominate the clipping percentages.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-014"></a>

## PHOTO-014 Try automatic tone adjustment

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to try automatic tone adjustment, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [TONAL — Known luminance ramp](TEST-DATA.md#tonal) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose automatic tone on an unevenly exposed photo.
2. Compare with Before.
3. Reset and repeat.

**Acceptance criteria:**

- The action produces a reproducible sensible tonal starting point.
- The controls show the resulting settings.
- Original pixels remain unchanged.

**Alternative and failure path:** An empty transparent image or constant colour image must not produce invalid numbers or an exception.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-015"></a>

## PHOTO-015 Try every Photo look from one baseline

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to try every Photo look from one baseline, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Set a modest manual baseline.
2. Choose Natural Punchy Black and white Warm film and Cool in different orders.
3. Choose Normal.

**Acceptance criteria:**

- Each look starts from the same pre look baseline.
- Switching order does not accumulate presets.
- Normal restores that baseline exactly.

**Alternative and failure path:** Every look must be tried and the saved baseline must include earlier manual edits rather than factory defaults.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-016"></a>

## PHOTO-016 Know when a look becomes Custom

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to know when a look becomes Custom, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose a look.
2. Change a slider curve crop or automatic correction.
3. Inspect the look selector then choose Normal.

**Acceptance criteria:**

- Each manual or automatic adjustment marks the look Custom.
- The preview represents the actual draft.
- Normal still restores the correct pre look baseline.

**Alternative and failure path:** A category change alone must not mark a look Custom.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-017"></a>

## PHOTO-017 Read the histogram and clipping warnings

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to read the histogram and clipping warnings, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [TONAL — Known luminance ramp](TEST-DATA.md#tonal) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Inspect a known distribution of opaque grey patches.
2. Change exposure until clipping occurs.
3. Compare the histogram with independent pixel counts.

**Acceptance criteria:**

- Channel distributions describe the current rendered comparison.
- Shadow and highlight warnings follow defined thresholds.
- Fully transparent pixels are excluded.

**Alternative and failure path:** An empty image must give a defined zero count result without divide by zero or a false full clipping warning.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-018"></a>

## PHOTO-018 Keep full size photo output consistent

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep full size photo output consistent, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Make a fine detail edit on a large source.
2. Save the recipe and export the full image.
3. Inspect the same detail at source resolution.

**Acceptance criteria:**

- Output uses the full source rather than an enlarged preview cache.
- The saved recipe is honoured.
- Pixel dimensions follow the visible frame.

**Alternative and failure path:** A quick preview's lower detail is not acceptable evidence that the full size export has been verified.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).

<a id="photo-019"></a>

## PHOTO-019 Keep photo settings after project reopen

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep photo settings after project reopen, so I can improve a photograph while keeping the original available for another try.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Save a nondefault look baseline curves and crop in a project.
2. Open it in a fresh session.
3. Choose Normal and reopen geometry.

**Acceptance criteria:**

- All saved recipe values survive.
- Normal uses the saved baseline.
- Hidden crop margins remain available.

**Alternative and failure path:** Malformed external recipe values must reject the project atomically and preserve the open picture.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/photo-ui.ts](../src/photo-ui.ts), [src/photo-session.ts](../src/photo-session.ts), [src/photo-preview.ts](../src/photo-preview.ts), [src/photo-render.ts](../src/photo-render.ts), [src/photo-recipe.ts](../src/photo-recipe.ts), [src/photo-engine.ts](../src/photo-engine.ts).
