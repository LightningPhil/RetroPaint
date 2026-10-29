# Layers and mixed picture composition

15 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Layer order, identity, visibility, opacity, paper transparency and active target are part of the document. Palette visibility is workspace state. Changing one must not silently change the other.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="layer-001"></a>

## LAYER-001 Add and choose a clear paint sheet

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to add and choose a clear paint sheet, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable Advanced mode and open Layers.
2. Choose New layer.
3. Draw then choose another sheet.

**Acceptance criteria:**

- A new transparent sheet appears adjacent to the working layer.
- Painting here identifies the current sheet.
- New paint affects only that sheet.

**Alternative and failure path:** The normal compact palette may close after an ordinary add or pick while the workshop return exception keeps it open.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-002"></a>

## LAYER-002 Rename a sheet meaningfully

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to rename a sheet meaningfully, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open Layer options.
2. Rename the active sheet to Character.
3. Commit and reopen the palette.

**Acceptance criteria:**

- The name appears consistently in the row target and controls.
- The layer ID and artwork stay unchanged.
- Undo can restore the previous name.

**Alternative and failure path:** Blank names receive a safe defined fallback and long names do not make layer controls inaccessible.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-003"></a>

## LAYER-003 Hide a reference without deleting it

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to hide a reference without deleting it, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Toggle the backdrop eye.
2. Draw on the foreground sheet.
3. Toggle the backdrop back.

**Acceptance criteria:**

- The backdrop disappears from composition and export while hidden.
- Its source pixels stay intact.
- The foreground edit stays on its own sheet.

**Alternative and failure path:** Undo must restore visibility independently from later painting and the hidden layer must not contribute to colour sampling.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-004"></a>

## LAYER-004 Control layer opacity

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to control layer opacity, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose a known red sheet above blue.
2. Set opacity to 50 percent.
3. Undo after releasing the slider.

**Acceptance criteria:**

- The composite follows alpha blending at the chosen value.
- The percentage label agrees.
- The slider gesture forms one useful Undo action.

**Alternative and failure path:** Zero opacity and returning to full opacity must retain the underlying pixels and live definitions.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-005"></a>

## LAYER-005 Reorder by dragging the layer grip

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to reorder by dragging the layer grip, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move a foreground layer below the backdrop by its grip.
2. Return it to the top.
3. Undo.

**Acceptance criteria:**

- Top to bottom display corresponds to compositing order.
- The selected layer identity survives.
- Each real reorder is reversible.

**Alternative and failure path:** A drop in the original position must not add a meaningless history step or duplicate a row.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-006"></a>

## LAYER-006 Reorder and choose layers with the keyboard

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to reorder and choose layers with the keyboard, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Focus a layer row.
2. Use arrows to select neighbouring sheets.
3. Use Alt with Up or Down to reorder.

**Acceptance criteria:**

- Selection and order follow their separate commands.
- Focus remains on a meaningful row.
- The composition matches the resulting order.

**Alternative and failure path:** Top and bottom boundaries must not wrap a reorder into the opposite end of the stack.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-007"></a>

## LAYER-007 Duplicate a complete layer

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to duplicate a complete layer, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Duplicate a sheet with pixels objects live ink and a saved photo recipe.
2. Edit the copy.
3. Undo.

**Acceptance criteria:**

- The copy starts with equivalent visible content.
- The two sheets have separate identities.
- Changes to the copy do not mutate the source.

**Alternative and failure path:** CAD layer duplication must also assign unique body IDs while retaining source recipes.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-008"></a>

## LAYER-008 Remove a sheet and undo it

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to remove a sheet and undo it, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select and remove a middle layer.
2. Inspect the new active target.
3. Undo.

**Acceptance criteria:**

- Only the requested sheet is removed.
- An available remaining layer becomes active.
- Undo restores content order settings and identity coherently.

**Alternative and failure path:** Removing the last remaining layer is prevented or leaves a valid ready document rather than an empty broken editor.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-009"></a>

## LAYER-009 Combine two paint sheets deliberately

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to combine two paint sheets deliberately, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose a paint layer above another paint layer.
2. Combine down.
3. Undo.

**Acceptance criteria:**

- The displayed composition is retained at the captured frame.
- The resulting sheet has the defined combined scope.
- Undo restores separate originals and live content.

**Alternative and failure path:** Merging a CAD layer or merging into a CAD neighbour is unavailable so editable solids are not silently flattened.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-010"></a>

## LAYER-010 Export clear artwork by hiding Paper

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to export clear artwork by hiding Paper, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Hide Paper while retaining a transparent foreground.
2. Download PNG.
3. Compare with JPEG.

**Acceptance criteria:**

- PNG retains genuine alpha where no visible layer paints.
- JPEG is flattened onto white.
- The editable source stack stays unchanged.

**Alternative and failure path:** A checkerboard background used by the UI must never appear as painted squares in the file.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-011"></a>

## LAYER-011 Keep live layer thumbnails current

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to keep live layer thumbnails current, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw one brief stroke and stop.
2. Observe its row preview.
3. Add live ink and observe again.

**Acceptance criteria:**

- The brief committed mark appears in the correct thumbnail.
- Animated content refreshes appropriately.
- Idle static pictures do not require constant full repaints.

**Alternative and failure path:** A hidden or offscreen palette must not stall the main painting controls or lose the next thumbnail update.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-012"></a>

## LAYER-012 Respect the layer and pixel limits

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to respect the layer and pixel limits, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [LIMIT — Boundaries in a disposable session](TEST-DATA.md#limit) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Add layers until the supported count or 64 million stored pixel budget is reached.
2. Attempt one more.
3. Remove a sheet and retry.

**Acceptance criteria:**

- The app explains the actual limiting condition.
- The rejected add leaves all original layers intact.
- Space released by removal can be used again.

**Alternative and failure path:** Exercise exactly 16 sheets and the nearest safe boundaries of the total pixel budget without rounding past the limit.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-013"></a>

## LAYER-013 Keep Layers beside the 3D workshop

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep Layers beside the 3D workshop, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open the workshop from basic mode.
2. Toggle the backdrop eye in Layers.
3. Use several CAD tools then close the workshop.

**Acceptance criteria:**

- Layers is open and interactive while paint controls behind the workshop are inactive.
- Hiding the guide does not switch the CAD target.
- Layers remains open after returning to Paint.

**Alternative and failure path:** In a narrow phone layout scrolling the layer strip must reach the guide eye without closing CAD or blocking tools.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-014"></a>

## LAYER-014 Choose a paint layer when leaving CAD

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to choose a paint layer when leaving CAD, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. While CAD is open choose a normal paint sheet in Layers.
2. Select Text and position a caption.
3. Return to the solid layer.

**Acceptance criteria:**

- Paint opens on the chosen sheet and Layers stays open.
- The caption is separate from the solid.
- Returning to CAD retains editable geometry.

**Alternative and failure path:** Closing CAD without picking a sheet must choose a valid paint target rather than direct raster painting into the solid preview.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).

<a id="layer-015"></a>

## LAYER-015 Restore the layer palette after Photo lab

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to restore the layer palette after Photo lab, so I can separate parts of a picture and change one part without damaging the others.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open Layers then Photo lab.
2. Finish or cancel the draft.
3. Inspect the layer palette and target.

**Acceptance criteria:**

- Photo lab and layer controls do not compete for the same editing target.
- The prior useful palette state is restored.
- The active sheet and its saved adjustments remain coherent.

**Alternative and failure path:** Changing to basic mode hides advanced controls without deleting the layers or recipes they represent.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/layer-ui.ts](../src/layer-ui.ts), [src/layers.ts](../src/layers.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/cad-ui.ts](../src/cad-ui.ts), [src/photo-ui.ts](../src/photo-ui.ts), [src/project.ts](../src/project.ts).
