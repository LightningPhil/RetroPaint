# Larger enhanced image copies

12 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Enhancement creates a separate image copy. It does not resize flatten or replace the editable document. The source is the finished visible composition. Generated detail is estimated and must be compared with the original.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="enhance-001"></a>

## ENHANCE-001 Open enhancement on a finished composition

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to open enhancement on a finished composition, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable Advanced mode and choose Super resolution.
2. Inspect the captured preview.
3. Close without processing.

**Acceptance criteria:**

- The source includes visible layers photo adjustments and the shared crop.
- The source dimensions are clear.
- Opening and closing do not alter the document.

**Alternative and failure path:** A hidden reference sheet must not unexpectedly appear in the enhancement source.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-002"></a>

## ENHANCE-002 Choose exactly double or quadruple size

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to choose exactly double or quadruple size, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select 2 times then 4 times on a known 160 by 120 input.
2. Inspect output dimensions.
3. Enhance and decode a copy.

**Acceptance criteria:**

- The choices produce 320 by 240 and 640 by 480 respectively.
- The selected scale is visible.
- The editable original stays 160 by 120.

**Alternative and failure path:** Unsupported scale values are rejected and an output edge above 16384 requires a clear alternative.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-003"></a>

## ENHANCE-003 Choose a representative preview detail

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to choose a representative preview detail, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move the yellow area by clicking then dragging.
2. Choose 64 128 and 256 pixel areas.
3. Preview each.

**Acceptance criteria:**

- The selected source area is consistent between overview Before and Enhanced.
- The area stays inside the source.
- Each listed size is usable within smaller images.

**Alternative and failure path:** A click in overview letterboxing must not select an unrelated or invalid source rectangle.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-004"></a>

## ENHANCE-004 Move the preview area with the keyboard

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to move the preview area with the keyboard, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Focus the overview.
2. Use arrow keys then Shift arrows.
3. Preview the chosen detail.

**Acceptance criteria:**

- Arrows move by the defined 8 source pixels and Shift arrows by 32.
- Clamping retains a valid region.
- The new selection invalidates an obsolete result appropriately.

**Alternative and failure path:** At source boundaries repeated keys must not wrap the selection to the opposite corner.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-005"></a>

## ENHANCE-005 Compare original and generated detail

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to compare original and generated detail, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enhance the selected detail.
2. Switch Before and Enhanced repeatedly.
3. Inspect edges and lettering.

**Acceptance criteria:**

- Both views show the same source region at comparable presentation size.
- The labels state which is shown.
- The user can reject invented or degraded detail.

**Alternative and failure path:** A larger interpolated source presented as the neural result is not acceptable evidence of enhancement.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-006"></a>

## ENHANCE-006 Enhance the whole image and save it

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to enhance the whole image and save it, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Enhance whole image.
2. Observe tile progress.
3. Save enhanced PNG and decode it independently.

**Acceptance criteria:**

- The complete visible composition is processed.
- The final PNG has the selected output dimensions.
- The original editable project remains intact.

**Alternative and failure path:** The successful preview tile must not be passed off as a completed whole image result.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-007"></a>

## ENHANCE-007 Keep transparent margins clean

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep transparent margins clean, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enhance a semitransparent coloured object with clear padding.
2. Decode the PNG.
3. Inspect over black and white.

**Acceptance criteria:**

- Clear pixels stay clear.
- Alpha is resampled separately as designed.
- Coloured edges avoid black contamination from transparent RGB padding.

**Alternative and failure path:** Inspect all four margins and tile boundaries rather than one opaque centre patch.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-008"></a>

## ENHANCE-008 Avoid seams between processed tiles

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to avoid seams between processed tiles, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enhance a grid and continuous gradient crossing tile boundaries.
2. Compare boundary bands with nearby bands.
3. Decode the whole PNG.

**Acceptance criteria:**

- There are no systematic seam lines or repeated edge strips.
- The output covers the whole source once.
- Mirrored border handling is coherent at outer edges.

**Alternative and failure path:** A tile progress counter alone cannot establish that every output row was written correctly.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-009"></a>

## ENHANCE-009 Cancel during model loading or processing

**Primary user:** L2 adventurous older child. **Priority:** P0. **Execution:** Not run.

**User story:** As an adventurous older child, I want to cancel during model loading or processing, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [PHOTO — Photographic editing source](TEST-DATA.md#photo) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Start enhancement with uncached models.
2. Close or press Escape.
3. Repeat while tiles are processing.

**Acceptance criteria:**

- Cancellation returns control promptly.
- No stale completion reopens the closed dialog.
- The editable source remains unchanged.

**Alternative and failure path:** A later new enhancement job must not receive progress or output from the cancelled job.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-010"></a>

## ENHANCE-010 Run with a CPU fallback when needed

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to run with a CPU fallback when needed, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [DETAIL — Edges texture and reproducible noise](TEST-DATA.md#detail) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use a disposable environment without worker WebGL.
2. Enhance a small fixed area.
3. Compare with the supported network result tolerance.

**Acceptance criteria:**

- The same model family can run on CPU.
- Progress and cancel remain usable.
- The app reports a useful failure if neither path can run.

**Alternative and failure path:** Do not silently replace neural inference with a different filter and label it the same result.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-011"></a>

## ENHANCE-011 Load enhancement assets locally and on demand

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to load enhancement assets locally and on demand, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [NETWORK — Controlled local resource capture](TEST-DATA.md#network) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open the app without starting enhancement.
2. Record resource requests.
3. Start enhancement once with a local source.

**Acceptance criteria:**

- Large model resources are deferred until needed.
- Models are requested from the app origin.
- No image payload is uploaded to an external service.

**Alternative and failure path:** A blocked or missing model download must preserve the picture and offer a recoverable retry rather than freeze the editor.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="enhance-012"></a>

## ENHANCE-012 Process supported large sources without a fake cap

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to process supported large sources without a fake cap, so I can judge generated detail before keeping a larger copy of my work.

**Setup:** Use a preserved copy of [LIMIT — Boundaries in a disposable session](TEST-DATA.md#limit) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose valid input near supported image limits.
2. Request both supported scales in a controlled resource test.
3. Decode the streamed PNG.

**Acceptance criteria:**

- Accepted output respects the 16384 pixel edge limit.
- Row band streaming can finish without requiring a giant export canvas.
- The old arbitrary 32 megapixel restriction does not block an otherwise supported job.

**Alternative and failure path:** Resource failure must be reported honestly with cancellation or retry and must never damage the original project.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/super-resolution-ui.ts](../src/super-resolution-ui.ts), [src/super-resolution-area.ts](../src/super-resolution-area.ts), [src/super-resolution-engine.ts](../src/super-resolution-engine.ts), [src/super-resolution-worker.ts](../src/super-resolution-worker.ts), [src/enhancement-size.ts](../src/enhancement-size.ts), [src/png-stream.ts](../src/png-stream.ts).
