# Getting started and protecting a picture

10 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Opening a control or changing a preference must not add paint. Destructive document changes must have a recoverable outcome. Basic mode is a simpler interface, not a separate document format.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="start-001"></a>

## START-001 Find the paper and make a first mark

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to find the paper and make a first mark, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open a fresh session without a saved preference.
2. Choose the illustrated Brushes tool and a bright colour.
3. Drag once across the paper.

**Acceptance criteria:**

- Paper is ready without an account or mandatory tutorial.
- The tool and chosen colour are visibly selected.
- A single gesture produces a mark and enables Undo.

**Alternative and failure path:** A returning recovery prompt must leave the ready canvas usable until the user chooses to resume.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-002"></a>

## START-002 Choose tools by picture and name

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to choose tools by picture and name, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Locate each main illustrated tool.
2. Open its choices and select one.
3. Close the choices and return to the paper.

**Acceptance criteria:**

- Each tool has a meaningful label as well as its illustration.
- The selected tool is distinguishable without colour alone.
- Opening choices does not move or mark the picture.

**Alternative and failure path:** Choosing the already active tool may open or close its drawer but must not erase its settings or artwork.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-003"></a>

## START-003 Keep my picture when I open More

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to keep my picture when I open More, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw an unmistakable mark.
2. Open More and visit File Image Advanced and View.
3. Close More and continue the mark.

**Acceptance criteria:**

- The same document remains active throughout.
- Drawers do not flatten layers or reset ink.
- Continuing the stroke uses the intended current tool.

**Alternative and failure path:** Clicking outside a drawer closes only that drawer and does not create an unintended canvas mark.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-004"></a>

## START-004 Undo my last complete action

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to undo my last complete action, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Make three separate strokes in three colours.
2. Activate Undo once then twice.
3. Redo the undone actions in order.

**Acceptance criteria:**

- Each Undo removes one complete user action.
- Redo restores its placement colour and appearance.
- The earlier strokes remain unchanged.

**Alternative and failure path:** After Undo followed by a new stroke the abandoned Redo branch must not reappear.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-005"></a>

## START-005 Keep an established picture instead of clearing it

**Primary user:** L1 beginning young artist. **Priority:** P0. **Execution:** Not run.

**User story:** As a beginning young artist, I want to keep an established picture instead of clearing it, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Make a mark and allow artwork age to exceed 120 seconds.
2. Press Clear.
3. Choose Keep drawing and then try Escape.

**Acceptance criteria:**

- The confirmation names the destructive action.
- Keep drawing has safe initial focus.
- Both dismissal paths retain every layer and editing state.

**Alternative and failure path:** Repeated Clear presses must not stack several dialogs or accidentally accept the destructive option.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-006"></a>

## START-006 Clear deliberately and recover with Undo

**Primary user:** L1 beginning young artist. **Priority:** P0. **Execution:** Not run.

**User story:** As a beginning young artist, I want to clear deliberately and recover with Undo, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open the Clear confirmation on an established picture.
2. Choose Clear picture.
3. Undo and then Redo.

**Acceptance criteria:**

- Clear has one defined document outcome rather than leaving stale visible fragments.
- Undo restores all affected pixels live ink and editable content.
- Redo repeats the same clear outcome.

**Alternative and failure path:** Repeat on a newly started picture where the current app may clear immediately: a clear must remain undoable even when no age warning is shown.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-007"></a>

## START-007 Grow into Advanced mode without losing work

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to grow into Advanced mode without losing work, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Make a basic drawing.
2. Enable Advanced mode in More.
3. Disable it then enable it again.

**Acceptance criteria:**

- Layers and Photo lab become discoverable in advanced mode.
- The underlying layers recipes and picture do not change when controls hide.
- The chosen mode is remembered on this device.

**Alternative and failure path:** Basic hides vector authoring and the 3D workshop as well as Layers, Photo lab and enhancement. Enable Advanced to enter 3D; it then exposes Layers. Switching back to Basic preserves saved advanced content and creates new raster artwork. This mode boundary supersedes the earlier auto-promotion behavior by user request on 2026-10-29.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-008"></a>

## START-008 Understand what is selected and editable

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to understand what is selected and editable, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a normal paint sheet then a hidden sheet.
2. Select an editable object and finally a CAD layer.
3. Inspect the target and available actions each time.

**Acceptance criteria:**

- The target is named before an edit.
- Hidden targets and unavailable actions have visible explanations.
- Paint object and solid selection are not confused with one another.

**Alternative and failure path:** Typing into a name field must not trigger a drawing or CAD shortcut.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-009"></a>

## START-009 Resume after help without changing my tool

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to resume after help without changing my tool, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose a stamp and its size.
2. Open shortcut help and browse every category.
3. Close help with Done or Escape.

**Acceptance criteria:**

- Help fits the available screen.
- Focus returns to a meaningful control.
- The selected stamp size and picture survive.

**Alternative and failure path:** While the dialog is open ordinary drawing and document shortcuts must not act behind it.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).

<a id="start-010"></a>

## START-010 Keep an unavailable action understandable

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep an unavailable action understandable, so I can learn by trying things while keeping control of my picture.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Start with no selection and one layer.
2. Inspect selection transforms merge and Redo.
3. Perform the setup that makes each action available.

**Acceptance criteria:**

- Unavailable controls are disabled or explain the missing prerequisite.
- Trying them leaves the document untouched.
- They become available when their prerequisites are satisfied.

**Alternative and failure path:** A stale button press during a busy operation must not create a partial edit or an extra Undo step.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [index.html](../index.html), [src/main.ts](../src/main.ts), [src/ui.ts](../src/ui.ts), [src/advanced-mode.ts](../src/advanced-mode.ts), [src/clear-confirmation.ts](../src/clear-confirmation.ts), [src/artwork.ts](../src/artwork.ts), [src/history.ts](../src/history.ts).
