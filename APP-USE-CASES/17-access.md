# Responsive input accessibility comfort and resilience

18 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

These are normative usability and reliability requirements. Source presence is evidence of an entry point, not proof of accessibility compliance. Keyboard drawing equivalence, browser permissions and hardware behavior need explicit capability notes rather than invented support.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="access-001"></a>

## ACCESS-001 Reach every main tool on a phone

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to reach every main tool on a phone, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use 320 by 568 and 390 by 844 viewports.
2. Open each tool family and its extra controls.
3. Return to drawing.

**Acceptance criteria:**

- No required control lies outside an unreachable panel.
- Tool labels stay meaningful.
- The visible picture is not unexpectedly rescaled or edited by menu navigation.

**Alternative and failure path:** Touch scrolling inside a choice list must not draw on the paper behind it.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-002"></a>

## ACCESS-002 Work with a short landscape screen

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to work with a short landscape screen, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use 844 by 390 and the declared supported short layouts.
2. Visit Photo lab CAD History preferences and help.
3. Reach the last control.

**Acceptance criteria:**

- Every function remains reachable with the intended paging or compact selection.
- Layers does not cover the CAD tool controls.
- Important commit cancel and return actions remain available.

**Alternative and failure path:** Fit checks must inspect real control reachability and legibility as well as container rectangles.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-003"></a>

## ACCESS-003 Preserve paper coordinates while zooming and panning

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to preserve paper coordinates while zooming and panning, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [PATCH — Known pixels and alpha](TEST-DATA.md#patch) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Zoom around a known patch.
2. Pan with Move paper and Space drag.
3. Draw at the same source point.

**Acceptance criteria:**

- The mark lands at the corresponding paper coordinate.
- Fit and actual pixels give coherent scale.
- View changes leave exported resolution unchanged.

**Alternative and failure path:** Wheel gestures over a slider or dialog must not unexpectedly zoom or paint the document.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-004"></a>

## ACCESS-004 Use rulers and pixel grid as overlays

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to use rulers and pixel grid as overlays, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [PIXEL — Crisp pixel art](TEST-DATA.md#pixel) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable rulers and pixel grid.
2. Zoom to inspect exact pixels.
3. Export PNG.

**Acceptance criteria:**

- Grid and ruler units agree with paper coordinates.
- Visibility adapts usefully to zoom.
- Neither overlay enters the file.

**Alternative and failure path:** At extreme zoom or after resizing the source the labels and grid origin must remain aligned.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-005"></a>

## ACCESS-005 Navigate tabs without a mouse

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to navigate tabs without a mouse, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Focus each tool category tablist.
2. Use Left Right Home and End.
3. Activate a setting and return.

**Acceptance criteria:**

- Focus moves through available tabs in predictable order.
- Selected state and visible panel agree.
- Disabled or hidden tabs are skipped.

**Alternative and failure path:** Arrow keys inside a curve editor numeric field or CAD manipulation context must not be hijacked by unrelated tab navigation.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-006"></a>

## ACCESS-006 Understand controls with assistive technology

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to understand controls with assistive technology, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Inspect accessible names roles selected states and status announcements.
2. Use keyboard navigation through paint photo layers and CAD controls.
3. Open and close dialogs.

**Acceptance criteria:**

- Icon only actions have meaningful names.
- Current target busy state errors and selected values can be identified.
- Dialogs contain focus and return it meaningfully.

**Alternative and failure path:** This case requires an actual supported assistive technology pass before any accessibility compliance claim; DOM labels alone are insufficient.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-007"></a>

## ACCESS-007 Keep shortcuts scoped to the active workspace

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep shortcuts scoped to the active workspace, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use painting shortcuts in Paint and W E R F in CAD.
2. Type the same keys in fields.
3. Open a modal dialog and retry.

**Acceptance criteria:**

- The active workspace receives its intended commands.
- Text entry remains text entry.
- Modal dialogs prevent background edits.

**Alternative and failure path:** Ctrl or Cmd S in CAD saves a project while the normal painting save shortcut downloads PNG, as visibly documented.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-008"></a>

## ACCESS-008 Choose a comfortable desk colour

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to choose a comfortable desk colour, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select Mint Lilac Oat and Night.
2. Reopen the app.
3. Compare exported pixels.

**Acceptance criteria:**

- Only the workspace theme changes.
- The saved preference is restored.
- Paper and image colour data remain unchanged.

**Alternative and failure path:** Unrecognised or unavailable preference storage must fall back safely without blocking drawing.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-009"></a>

## ACCESS-009 Mute and set sound volume consistently

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to mute and set sound volume consistently, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use the speaker button M and Sound and feel.
2. Set volume and painting sounds.
3. Reopen.

**Acceptance criteria:**

- All sound controls show coherent current state.
- Mute silences both feedback and painting sounds as intended.
- Preferences persist when storage is available.

**Alternative and failure path:** A muted or zero volume app must not play a loud preview sound or unexpectedly unmute during another workflow.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-010"></a>

## ACCESS-010 Reduce interface motion without freezing art

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to reduce interface motion without freezing art, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enable Reduce interface motion.
2. Open and close drawers.
3. Observe live ink and a motor drawing.

**Acceptance criteria:**

- Decorative interface motion is reduced.
- Artwork animation remains intentional.
- The preference does not change exported art.

**Alternative and failure path:** Do not treat every animation as removable UI decoration when the animation is part of the picture itself.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-011"></a>

## ACCESS-011 Keep the pointer preview useful at every zoom

**Primary user:** L1 beginning young artist. **Priority:** P1. **Execution:** Not run.

**User story:** As a beginning young artist, I want to keep the pointer preview useful at every zoom, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Move a brush eraser smudge stamp and picker pointer at low and high zoom.
2. Change size.
3. Export.

**Acceptance criteria:**

- The footprint follows the effective paper area.
- Stamp and picker previews are informative.
- Cursor redraws do not leave permanent paint trails.

**Alternative and failure path:** When the pointer leaves or changes tool the previous preview must disappear without requiring a full destructive repaint.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-012"></a>

## ACCESS-012 Stop gestures after interruption

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to stop gestures after interruption, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [PLAY — Ready painting paper](TEST-DATA.md#play) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Begin brush selection drag Spiro gear drag crop and CAD handle gestures.
2. Trigger pointer cancellation or window blur.
3. Continue safely.

**Acceptance criteria:**

- Each interaction releases capture and clears transient drag state.
- The document has a coherent commit or cancellation outcome.
- The next gesture works independently.

**Alternative and failure path:** Release outside the app must not leave a hidden stroke spray or transform running.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-013"></a>

## ACCESS-013 Keep idle work responsive without wasted redraws

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep idle work responsive without wasted redraws, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Observe a static picture with no input.
2. Move only the cursor.
3. Then add live ink and a preview.

**Acceptance criteria:**

- Static content does not continuously repaint unnecessarily.
- Cursor feedback can update independently.
- Live and preview content continues rendering when required.

**Alternative and failure path:** A rendering optimisation that freezes active art or misses the final short stroke must fail despite reduced CPU activity.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-014"></a>

## ACCESS-014 Recover from a failed worker or memory operation

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to recover from a failed worker or memory operation, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [LIMIT — Boundaries in a disposable session](TEST-DATA.md#limit) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use controlled disposable failures during photo enhancement and CAD jobs.
2. Read the message.
3. Perform a simple valid operation afterward.

**Acceptance criteria:**

- The current saved document remains intact.
- Busy state clears.
- The feature can retry or explain its continuing unavailability.

**Alternative and failure path:** A worker restart must ignore obsolete responses and must not resolve a new request with old data.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-015"></a>

## ACCESS-015 Keep local artwork private in normal workflows

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep local artwork private in normal workflows, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [NETWORK — Controlled local resource capture](TEST-DATA.md#network) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Record network activity during image open editing photo adjustments project saving CAD and enhancement.
2. Inspect requests and payloads.
3. Repeat with required assets cached.

**Acceptance criteria:**

- Image and model payloads remain local to the browser.
- Normal operations require no account or remote image processing.
- Only declared application assets are fetched.

**Alternative and failure path:** This does not promise that an uncached app will launch offline or replace a full security audit of extensions browser settings and the host.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-016"></a>

## ACCESS-016 Respect busy and incompatible editing states

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to respect busy and incompatible editing states, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Start a photo draft CAD feature draft or active long operation.
2. Try unrelated edits open and save actions.
3. Finish or cancel deliberately.

**Acceptance criteria:**

- Controls clearly identify unavailable actions.
- No incompatible state partially commits.
- Settlement returns to a usable target.

**Alternative and failure path:** A disabled button must not be the only protection against a keyboard route or a stale asynchronous callback.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-017"></a>

## ACCESS-017 Enter and leave full screen without losing context

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to enter and leave full screen without losing context, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [MIX — Multilayer picture](TEST-DATA.md#mix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Full screen from View.
2. Draw or inspect the composition.
3. Leave with the browser supported exit action.

**Acceptance criteria:**

- The same document target and view remain usable.
- Layout adapts to the available bounds.
- Leaving full screen does not change saved dimensions or content.

**Alternative and failure path:** A browser that denies full screen must leave the workspace usable and must not falsely display an active full screen state.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).

<a id="access-018"></a>

## ACCESS-018 Use real touch targets rather than tiny fitted controls

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to use real touch targets rather than tiny fitted controls, so I can keep creating comfortably across devices and recover from interruptions.

**Setup:** Use a preserved copy of [CADMIX — Solid picture and guide](TEST-DATA.md#cadmix) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Measure interactive hit rectangles on the supported phone layouts.
2. Tap numeric fields tabs commit cancel and layer eyes with touch input.
3. Repeat during feature editing.

**Acceptance criteria:**

- Required touch targets have at least a 44 by 44 CSS pixel effective hit area under the proposed product target.
- Scaled text remains readable without magnification.
- All important controls remain distinguishable and operable.

**Alternative and failure path:** A panel fitting its container is not sufficient if CSS zoom shrinks the actual targets below the intended usability requirement.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/accessible-tabs.ts](../src/accessible-tabs.ts), [src/shortcuts-ui.ts](../src/shortcuts-ui.ts), [src/preferences-ui.ts](../src/preferences-ui.ts), [src/preferences-store.ts](../src/preferences-store.ts), [src/paper-view.ts](../src/paper-view.ts), [src/cursor-renderer.ts](../src/cursor-renderer.ts), [src/loop.ts](../src/loop.ts), [src/render-state.ts](../src/render-state.ts), [src/audio.ts](../src/audio.ts), [src/input.ts](../src/input.ts).
