# Editable vector and raster pieces

18 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Raster and vector describe how new marks are created, not a command to destroy existing pieces. Object transforms must stay nonsingular. Pixel effects on one selected piece must not flatten its neighbours.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="vector-001"></a>

## VECTOR-001 Switch a painting into editable piece mode

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to switch a painting into editable piece mode, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Make raster marks then choose More Draw with Vectors.
2. Select the existing artwork piece.
3. Add a vector shape.

**Acceptance criteria:**

- Existing paint remains visible and becomes addressable as intended.
- New vector geometry is a separate piece.
- Switching mode does not rescale the picture.

**Alternative and failure path:** Returning to Raster changes future drawing behavior without merging existing editable pieces.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-002"></a>

## VECTOR-002 Create an independently editable shape

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to create an independently editable shape, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw a filled vector heart and an arrow.
2. Select one and resize it.
3. Save and reopen.

**Acceptance criteria:**

- Each gesture creates a separate selectable shape.
- Resizing preserves its shape definition.
- The project retains editable geometry.

**Alternative and failure path:** An image export is allowed to rasterise its visible appearance but must not be mistaken for an editable project.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-003"></a>

## VECTOR-003 Keep brush gestures separate as raster pieces

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep brush gestures separate as raster pieces, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw two brush gestures and one spray burst in Vectors mode.
2. Select each.
3. Move only the second.

**Acceptance criteria:**

- Raster gestures have their own cropped surfaces.
- Piece bounds follow the actual content.
- Neighbours do not move or merge.

**Alternative and failure path:** Transparent padding must not intercept clicks over a different visible piece unnecessarily.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-004"></a>

## VECTOR-004 Keep text editable as a piece

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep text editable as a piece, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create styled text in Vectors mode.
2. Select move rotate and scale it.
3. Save and reopen.

**Acceptance criteria:**

- Text remains an individually editable scene item with its supported original text styling data.
- Transforms keep crisp geometry where applicable.
- Reopening retains its identity.

**Alternative and failure path:** Do not assume a general rich text editor exists: test only the text properties exposed by the app.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-005"></a>

## VECTOR-005 Place stamps as editable artwork

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to place stamps as editable artwork, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Place two stamps in vector mode.
2. Select one and flip it.
3. Reopen the project.

**Acceptance criteria:**

- Each stamp remains a separate supported piece.
- The chosen stamp and transform survive.
- Flipping one does not flip the other.

**Alternative and failure path:** Platform glyph differences must be recorded when comparing visual stamp appearance.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-006"></a>

## VECTOR-006 Select one piece or a group

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to select one piece or a group, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Click one object.
2. Shift click another then remove it from selection.
3. Drag a box around a group.

**Acceptance criteria:**

- Selection reflects the intended set.
- Group bounds enclose every selected piece.
- Later transforms apply only to that set.

**Alternative and failure path:** Blank paper clicks clear or settle selection according to the documented object interaction rule without deleting pieces.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-007"></a>

## VECTOR-007 Reach a piece hidden behind another

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to reach a piece hidden behind another, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Stack three overlapping objects.
2. Alt click through them.
3. Select a named off paper item in the piece list.

**Acceptance criteria:**

- Each intended object can be reached.
- The selection indication names the actual target.
- The piece list can recover objects outside the visible paper.

**Alternative and failure path:** Transparent gaps and fully hidden pieces need a consistent hit testing rule rather than always selecting the top bounding box.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-008"></a>

## VECTOR-008 Move precisely with arrows

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to move precisely with arrows, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a piece at a known coordinate.
2. Press arrows then Shift arrows.
3. Undo.

**Acceptance criteria:**

- Ordinary arrows move by one paper pixel.
- Shift arrows move by ten.
- The document zoom does not change that distance.

**Alternative and failure path:** Typing arrows into a numeric field must change that field rather than moving the object behind it.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-009"></a>

## VECTOR-009 Resize corners and sides accurately

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to resize corners and sides accurately, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a 100 by 80 object.
2. Drag a corner and a side handle.
3. Repeat with Shift.

**Acceptance criteria:**

- Corner and side handles affect the intended dimensions.
- Shift preserves proportions where offered.
- The new bounds reflect the full transform.

**Alternative and failure path:** Handle crossing or zero dimension input must remain a valid object or be rejected without losing the original.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-010"></a>

## VECTOR-010 Set exact position size and rotation

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to set exact position size and rotation, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open Exact size and arrange.
2. Enter left -20 top 30 width 200 height 160 and a rotation.
3. Apply each supported group.

**Acceptance criteria:**

- Numeric fields use paper pixels and degrees consistently.
- Negative positions remain valid.
- Other objects stay unchanged.

**Alternative and failure path:** Invalid empty infinite or singular values must not become saved transforms.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-011"></a>

## VECTOR-011 Centre and arrange a group

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to centre and arrange a group, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select several pieces.
2. Centre on paper.
3. Change stacking with forward backward front and back controls.

**Acceptance criteria:**

- The chosen group is centred by its bounds.
- Relative arrangement is preserved during a group move.
- Stacking changes only the intended objects.

**Alternative and failure path:** At the top or bottom of the order an unavailable arrange action must not duplicate or drop a piece.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-012"></a>

## VECTOR-012 Duplicate a group without linking copies

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to duplicate a group without linking copies, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a group and duplicate it.
2. Move and resize the copy.
3. Undo.

**Acceptance criteria:**

- The duplicate has equivalent content and separate identities.
- Moving the copy does not move the source.
- Undo removes or restores the operation coherently.

**Alternative and failure path:** Wet raster surfaces must not remain unintentionally shared between the duplicate and source.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-013"></a>

## VECTOR-013 Copy and paste editable pieces

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to copy and paste editable pieces, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Copy multiple mixed objects.
2. Paste in the current document.
3. Reopen a saved copy.

**Acceptance criteria:**

- Supported geometry and material data remain separate pieces.
- Relative placement within the group is retained.
- The system clipboard fallback is honest about raster versus editable content.

**Alternative and failure path:** Copying to an external application may use a PNG and must not be advertised as vector interchange.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-014"></a>

## VECTOR-014 Apply a pixel effect to one piece

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to apply a pixel effect to one piece, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select one raster or supported editable object.
2. Choose a local pixel effect.
3. Compare its neighbours.

**Acceptance criteria:**

- The selected content receives the intended effect.
- Unselected objects retain their data and pixels.
- The resulting object's editability is represented honestly.

**Alternative and failure path:** An unsupported object effect must be explained rather than flattening the whole layer as a hidden fallback.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-015"></a>

## VECTOR-015 Preserve original raster detail while transforming

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to preserve original raster detail while transforming, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Insert a detailed image as a piece.
2. Shrink then enlarge before placement.
3. Compare with the original.

**Acceptance criteria:**

- Intermediate transforms reuse the retained original raster source.
- Detail is not repeatedly resampled.
- The final transform remains independently editable.

**Alternative and failure path:** Permanent off paper placement trimming has its separate documented retention rule and must be tested explicitly.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-016"></a>

## VECTOR-016 Settle editable pieces on the desk

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to settle editable pieces on the desk, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move an editable piece partly off paper.
2. Click blank desk or press Escape.
3. Select it again.

**Acceptance criteria:**

- The documented deselection action places the editable piece.
- Its geometry remains recoverable according to piece kind.
- No new paint mark is created on the desk.

**Alternative and failure path:** Ordinary floating raster Cancel behavior is different and must not be substituted for this case.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-017"></a>

## VECTOR-017 Keep materials and live ink on moved pieces

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep materials and live ink on moved pieces, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create a live or textured piece.
2. Move scale and rotate it.
3. Compare at a controlled time.

**Acceptance criteria:**

- The material follows the object transform.
- Its clipping and alpha follow the transformed bounds.
- Unrelated live objects keep their behavior.

**Alternative and failure path:** Frozen still comparisons must use one captured time so animation phase is not mistaken for transform damage.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).

<a id="vector-018"></a>

## VECTOR-018 Round trip a mixed scene

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to round trip a mixed scene, so I can keep individual parts adjustable as my illustration becomes more ambitious.

**Setup:** Use a preserved copy of [VECTOR — Mixed editable scene](TEST-DATA.md#vector) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Build shapes text stamps imported raster and Spiro objects.
2. Save project and reopen in a fresh session.
3. Edit one item of each kind.

**Acceptance criteria:**

- Piece kinds order transforms styling and supported source definitions survive.
- The composition matches at a controlled time.
- Editing each reopened item does not affect its neighbours.

**Alternative and failure path:** A malformed object in an external project must be rejected atomically without replacing the current scene.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/objects.ts](../src/objects.ts), [src/object-scene.ts](../src/object-scene.ts), [src/object-ui.ts](../src/object-ui.ts), [src/selection-commit.ts](../src/selection-commit.ts), [src/workspace-ui.ts](../src/workspace-ui.ts), [src/project.ts](../src/project.ts).
