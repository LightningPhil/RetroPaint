# Files exports projects and local recovery

24 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

A download event is not proof of file correctness. Save the actual bytes, decode independently and reopen through the visible file workflow. Reject malformed inputs before replacing the live document. Local draft recovery is separate from an independent project file.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="file-001"></a>

## FILE-001 Start a new picture at a chosen size

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to start a new picture at a chosen size, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose New picture and enter supported dimensions.
2. Accept the action.
3. Draw then Undo where supported.

**Acceptance criteria:**

- A valid ready document has the requested dimensions and defined initial paper.
- Old content is not mixed accidentally into the new one.
- The active target is valid.

**Alternative and failure path:** Invalid sizes must leave the previous document unchanged and explain the accepted limits.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-002"></a>

## FILE-002 Open a supported image as a new picture

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to open a supported image as a new picture, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [IMPORT — Image format matrix](TEST-DATA.md#import) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Open image and select each supported fixture format.
2. Inspect dimensions and orientation.
3. Draw a new mark.

**Acceptance criteria:**

- The decoded source appears at the intended size.
- The working document targets that image.
- New marks align with its pixels.

**Alternative and failure path:** Cancelling the file picker retains the prior picture and corrupt data must be reported without partial replacement.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-003"></a>

## FILE-003 Insert an image without replacing the drawing

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to insert an image without replacing the drawing, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Insert image and a small transparent PNG.
2. Position it above the existing scene.
3. Undo.

**Acceptance criteria:**

- Existing sheets remain intact.
- The inserted image becomes the supported movable content.
- Undo removes only the insertion.

**Alternative and failure path:** A very large inserted source must obey size limits without silently discarding the current picture.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-004"></a>

## FILE-004 Paste a screenshot

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to paste a screenshot, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Copy an image in another application.
2. Choose Paste or the supported shortcut.
3. Place the imported content.

**Acceptance criteria:**

- A usable image arrives at the intended target.
- The app communicates clipboard restrictions honestly.
- Existing drawing remains.

**Alternative and failure path:** If browser permission is unavailable or clipboard contains only text the document must remain intact with an actionable message.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-005"></a>

## FILE-005 Drop a picture onto the paper

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to drop a picture onto the paper, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Drag a supported local image over the paper.
2. Drop it.
3. Place and Undo.

**Acceptance criteria:**

- The app inserts or opens it according to the visible drop contract.
- The browser does not navigate away to the file.
- The imported pixels can be positioned.

**Alternative and failure path:** Dropping an unsupported or corrupt file must not replace the document or leave a stuck drop overlay.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-006"></a>

## FILE-006 Download the current PNG with Save

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to download the current PNG with Save, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Finish active selections and drafts.
2. Press Save.
3. Decode the resulting PNG outside the app.

**Acceptance criteria:**

- File content and extension identify PNG.
- Dimensions equal the visible frame.
- Visible layers and supported adjustments appear correctly.

**Alternative and failure path:** Cursor handles rulers desk backgrounds and other editing overlays must not enter the exported pixels.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-007"></a>

## FILE-007 Keep transparency in PNG WebP and TIFF

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep transparency in PNG WebP and TIFF, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Hide Paper and export each alpha supporting format.
2. Decode each.
3. Compare transparent and semitransparent patches.

**Acceptance criteria:**

- Alpha is retained to the capability of each format.
- Opaque pixels keep their intended colours.
- Image dimensions are correct.

**Alternative and failure path:** Use an independent decoder and two contrasting backgrounds so a white flattening error cannot hide.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-008"></a>

## FILE-008 Export JPEG and BMP with a white matte

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to export JPEG and BMP with a white matte, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Hide Paper and export JPEG then BMP.
2. Inspect transparent source areas in the files.
3. Compare dimensions.

**Acceptance criteria:**

- The otherwise transparent region is composited onto white.
- The output uses the selected format.
- The editable project remains transparent.

**Alternative and failure path:** JPEG is lossy so use an agreed perceptual error threshold instead of demanding identical RGB bytes.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-009"></a>

## FILE-009 Export a palette limited GIF honestly

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to export a palette limited GIF honestly, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [COLOUR — Hue and neutral samples](TEST-DATA.md#colour) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Export a colour rich image with clear and partial alpha areas as GIF.
2. Decode the palette and frame.
3. Compare the intended still.

**Acceptance criteria:**

- The file has no more than 256 palette colours.
- Transparency follows GIF's binary alpha limitation.
- The export is a still capture rather than an invented animated movie.

**Alternative and failure path:** Record quantisation loss explicitly and do not claim exact true colour or semitransparent GIF output.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-010"></a>

## FILE-010 Import supported TIFF variants safely

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to import supported TIFF variants safely, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [IMPORT — Image format matrix](TEST-DATA.md#import) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open uncompressed 8 bit RGB RGBA and greyscale TIFF fixtures.
2. Inspect pixels.
3. Try an unsupported compression fixture.

**Acceptance criteria:**

- Supported variants decode accurately.
- Alpha is honoured for RGBA.
- Unsupported variants report their actual limitation.

**Alternative and failure path:** Malformed dimensions offsets or strip lengths must be rejected before memory use or partial document replacement.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-011"></a>

## FILE-011 Name a saved file predictably

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to name a saved file predictably, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enter a descriptive name with an existing image extension.
2. Save in another format.
3. Repeat with reserved filename characters and an empty name.

**Acceptance criteria:**

- The resulting extension matches the chosen format.
- Invalid filename characters are made safe.
- The fallback name is usable.

**Alternative and failure path:** The name must not acquire duplicated misleading extensions such as picture.png.jpg unintentionally.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-012"></a>

## FILE-012 Print the visible finished picture

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to print the visible finished picture, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Print on a cropped multilayer image.
2. Inspect browser print preview.
3. Cancel the print dialog.

**Acceptance criteria:**

- The preview contains the finished composition at the correct aspect ratio.
- Editing overlays are absent.
- Cancelling print leaves the document unchanged.

**Alternative and failure path:** Actual printer output and printer settings are external integration checks rather than a success inferred from opening print preview.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-013"></a>

## FILE-013 Save an independent editable project

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to save an independent editable project, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Save a project with layers objects recipes and live ink.
2. Retain the actual downloaded bytes and checksum.
3. Open the file in a fresh app session.

**Acceptance criteria:**

- The file identifies a supported RetroPaint project.
- All supported editing definitions survive.
- The reconstructed composition matches at a controlled time.

**Alternative and failure path:** A plain PNG renamed with a project extension must not pass project validation.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-014"></a>

## FILE-014 Reopen a project through the real file input

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to reopen a project through the real file input, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Close any active feature or photo draft deliberately.
2. Choose Open project.
3. Select the saved mixed project.

**Acceptance criteria:**

- The file chooser pathway loads the intended file.
- Layer order target camera and recipes are restored.
- Each type of content can be edited afterward.

**Alternative and failure path:** Calling a serializer and parser directly is useful supplementary coverage but does not substitute for this user workflow.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-015"></a>

## FILE-015 Read earlier project versions

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to read earlier project versions, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [LEGACY — Provenanced old project files](TEST-DATA.md#legacy) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open each available supported legacy project fixture.
2. Inspect converted state.
3. Save it as a new project.

**Acceptance criteria:**

- Earlier supported data remains visible and editable to its documented capability.
- Missing newer settings receive safe defaults.
- Resaving preserves the migrated picture.

**Alternative and failure path:** An unknown future project version must be explained rather than accepted with silently discarded fields.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-016"></a>

## FILE-016 Reject a damaged project atomically

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to reject a damaged project atomically, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [CORRUPT — Disposable invalid inputs](TEST-DATA.md#corrupt) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Keep a named unsaved picture open.
2. Try truncated JSON malformed images invalid IDs singular transforms and bad recipes.
3. Compare before and after.

**Acceptance criteria:**

- The current document remains unchanged after every rejection.
- The message identifies an actionable format problem.
- No partial layers become active.

**Alternative and failure path:** A valid opening immediately after a rejection must work so the failure cannot poison future imports.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-017"></a>

## FILE-017 Save a stable snapshot while encoding

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to save a stable snapshot while encoding, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Begin saving a large editable project.
2. Make a clearly different edit after snapshot capture if controls allow it.
3. Reopen the resulting file.

**Acceptance criteria:**

- The file represents one coherent captured state.
- Later edits do not leak into some encoded sheets only.
- The working document keeps the later edit.

**Alternative and failure path:** Do not require a particular timing shortcut: capture a deterministic test seam and record when the snapshot was taken.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-018"></a>

## FILE-018 Keep Save usable after a failed export

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep Save usable after a failed export, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [LIMIT — Boundaries in a disposable session](TEST-DATA.md#limit) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Cause an unsupported codec or resource failure in a disposable session.
2. Read the message.
3. Retry a small PNG or project.

**Acceptance criteria:**

- The failed action does not claim a successful file.
- Busy controls become usable again.
- Retry can produce a valid independently decoded file.

**Alternative and failure path:** Repeated rapid Save presses must not launch an unbounded set of duplicate encoding jobs.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-019"></a>

## FILE-019 Recover a draft after a refresh

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to recover a draft after a refresh, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Make settled edits and allow draft saving to finish.
2. Refresh the tab.
3. Choose Resume.

**Acceptance criteria:**

- The recovered picture includes supported layers objects live data and recipes.
- The prompt does not block a ready new canvas.
- The chosen draft is identified.

**Alternative and failure path:** An unsaved active gesture text draft or photo draft must not be mistaken for a safely settled recovery checkpoint.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-020"></a>

## FILE-020 Choose among recent drafts

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to choose among recent drafts, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create several distinct settled pictures.
2. Open Recent drafts.
3. Page through previews and restore a chosen one.

**Acceptance criteria:**

- The correct name size and preview identify each entry.
- Pagination reaches all retained drafts.
- Restoring chooses the requested complete picture.

**Alternative and failure path:** A missing or damaged stored entry must report failure without replacing the current drawing with an empty picture.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-021"></a>

## FILE-021 Undo a draft restore

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to undo a draft restore, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open a different unsaved picture.
2. Restore a known recent draft.
3. Undo the restoration.

**Acceptance criteria:**

- The earlier unsaved document returns with its editable content.
- Redo can return to the restored draft.
- The draft store remains independent.

**Alternative and failure path:** Recovery must not reset the history to a state from which the pre restore work is irretrievable.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-022"></a>

## FILE-022 Keep duplicated browser tabs independent

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep duplicated browser tabs independent, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Duplicate a working tab.
2. Make different settled edits in both.
3. Refresh and inspect recovery in each.

**Acceptance criteria:**

- Separate working identities protect each evolving picture.
- One tab does not overwrite the other's recovery data.
- Both can save independent project files.

**Alternative and failure path:** This is not simultaneous shared collaboration and no real time multiuser synchronization is implied.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-023"></a>

## FILE-023 Handle unavailable browser storage honestly

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to handle unavailable browser storage honestly, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Run with IndexedDB or preference storage unavailable.
2. Draw and save a project.
3. Inspect recovery feedback.

**Acceptance criteria:**

- Painting remains usable.
- The app does not falsely claim a browser draft is safely stored.
- Independent file saving remains offered.

**Alternative and failure path:** Quota or blocked database errors must not repeatedly interrupt every stroke or destroy the active document.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).

<a id="file-024"></a>

## FILE-024 Respect draft retention and large document limits

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to respect draft retention and large document limits, so I can keep independent copies and return to work with its intended editability intact.

**Setup:** Use a preserved copy of [LIMIT — Boundaries in a disposable session](TEST-DATA.md#limit) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create more than eight recovery candidates within a disposable database.
2. Approach its 128 MB budget.
3. Try a picture beyond automatic draft eligibility.

**Acceptance criteria:**

- Retention follows the defined count and storage budget.
- The newest valid working draft is protected as designed.
- Oversized work is directed to Save project.

**Alternative and failure path:** The 24 million stored pixel and 50 million serialized character draft cutoffs are distinct from the ordinary image and layer limits.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/editor.ts](../src/editor.ts), [src/export.ts](../src/export.ts), [src/project.ts](../src/project.ts), [src/image-codecs.ts](../src/image-codecs.ts), [src/recovery-ui.ts](../src/recovery-ui.ts), [src/recovery-store.ts](../src/recovery-store.ts), [src/png-stream.ts](../src/png-stream.ts).
