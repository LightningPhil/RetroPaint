# 3D history shells edge finishes lofts and sweeps

29 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Preview rebuilds a temporary complete result. Apply commits one coherent edit. Cancel leaves the saved recipe and original solid intact. Failed or timed out precision operations must not apply partial geometry. Surface checks include real cavities and edge references, not only a successful triangulation.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="feature-001"></a>

## FEATURE-001 Read and name the construction tree

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to read and name the construction tree, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Build a primitive plus a cut and finish.
2. Open History and expand each step.
3. Rename supported features.

**Acceptance criteria:**

- The tree exposes original inputs and operation order.
- The selected node corresponds to its source.
- Names survive save and reopen.

**Alternative and failure path:** Pagination must not omit hidden branches or confuse tree node identity after a rename.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-002"></a>

## FEATURE-002 Preview an earlier dimension change

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to preview an earlier dimension change, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select an original source sketch or primitive.
2. Change dimensions and Preview.
3. Compare saved project data before Apply.

**Acceptance criteria:**

- The workbench shows a rebuilt final result.
- Later supported features follow the edit.
- The saved document remains unchanged during Preview.

**Alternative and failure path:** An invalid preview stays in the editor with an explanation and the previous saved solid intact.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-003"></a>

## FEATURE-003 Apply one history edit atomically

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to apply one history edit atomically, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Preview a valid source change.
2. Choose Apply.
3. Undo then Redo.

**Acceptance criteria:**

- Apply produces the complete rebuilt result.
- One Undo returns the complete earlier model.
- Redo restores the applied result and feature data.

**Alternative and failure path:** The history must not contain separate intermediate states for every slider or preview rebuild.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-004"></a>

## FEATURE-004 Cancel a feature draft completely

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to cancel a feature draft completely, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Change several fields and preview.
2. Choose Cancel.
3. Compare saved data and mesh with the baseline.

**Acceptance criteria:**

- The original recipe is unchanged.
- The original final geometry returns.
- Draft helper outlines and pink edit overlays disappear.

**Alternative and failure path:** A worker response that arrives after cancellation must not commit or redisplay the cancelled edit.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-005"></a>

## FEATURE-005 Suppress and enable a build feature

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to suppress and enable a build feature, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Suppress a cut or shell step.
2. Inspect downstream geometry.
3. Enable it and Undo.

**Acceptance criteria:**

- Suppression retains the original feature definition.
- Its documented target passes through to later supported steps.
- Reenabling rebuilds the intended final model.

**Alternative and failure path:** Suppressing a required support may cause a clear rebuild error and must not fabricate a substitute face.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-006"></a>

## FEATURE-006 Inspect earlier geometry on the timeline

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to inspect earlier geometry on the timeline, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select each build step and move the playhead.
2. Choose Latest.
3. Inspect project data.

**Acceptance criteria:**

- Earlier geometry is temporary inspection.
- Latest restores the full solid.
- The project recipe never becomes the preview result.

**Alternative and failure path:** Construction and export while rolled back must require Latest or explain the restriction rather than save the wrong step.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-007"></a>

## FEATURE-007 Keep timeline and tree navigation reachable

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to keep timeline and tree navigation reachable, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Build enough steps to require pagination.
2. Reach the first middle and last steps in tree and timeline.
3. Resize the workspace.

**Acceptance criteria:**

- Every step remains addressable.
- The same chosen step is identified coherently.
- Controls remain usable on supported layouts.

**Alternative and failure path:** Navigating a page must not select a different feature merely because a temporary row index changed.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-008"></a>

## FEATURE-008 Edit a hole after its supporting body changes

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to edit a hole after its supporting body changes, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create an attached Through all hole.
2. Resize or rotate its source body.
3. Preview and apply.

**Acceptance criteria:**

- The hole follows the supporting face geometry.
- Its intended sketch dimensions remain.
- Through depth recalculates from the current body.

**Alternative and failure path:** If that face disappears or becomes ambiguous the app must retain the original and offer reselection or a fixed workplane choice.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-009"></a>

## FEATURE-009 Pick real edges rather than triangle diagonals

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to pick real edges rather than triangle diagonals, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose an analytic cube cylinder and drilled solid.
2. Activate Pick edges.
3. Tap straight edges circular rims and smooth seams.

**Acceptance criteria:**

- Geometric edges and whole circular rims are selectable.
- Triangle diagonals and smooth surface seams are excluded.
- Selected references remain identifiable.

**Alternative and failure path:** Picking a tessellated display edge is not acceptable if it changes unpredictably after a mesh rebuild.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-010"></a>

## FEATURE-010 Toggle multiple edges and clear them

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to toggle multiple edges and clear them, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Pick several edges.
2. Toggle one off.
3. Use Select all edges and clear selection.

**Acceptance criteria:**

- The highlighted set matches the chosen references.
- Clear removes the set.
- Orbit drags do not add random edges.

**Alternative and failure path:** An empty edge selection must leave Preview finish unavailable or explain the prerequisite.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-011"></a>

## FEATURE-011 Round a cube edge with a fillet

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to round a cube edge with a fillet, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select one cube edge.
2. Set a small known Fillet radius.
3. Preview apply and inspect a section.

**Acceptance criteria:**

- The sharp corner is replaced by a real constant radius surface within tolerance.
- The result is closed.
- Apply is one Undo step.

**Alternative and failure path:** A smooth shaded sharp mesh is not an acceptable replacement for changed solid geometry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-012"></a>

## FEATURE-012 Bevel an edge with a chamfer

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to bevel an edge with a chamfer, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select an edge and choose equal distance Chamfer.
2. Set a known setback.
3. Preview and apply.

**Acceptance criteria:**

- The two adjacent faces are cut back by the intended distance.
- The bevel is a real planar face.
- The remaining solid is closed.

**Alternative and failure path:** Chamfer distance must not be interpreted as the fillet radius or applied in display pixels.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-013"></a>

## FEATURE-013 Finish circular rims and hole entrances

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to finish circular rims and hole entrances, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Pick an outer cylinder rim and a drilled hole entrance in separate copies.
2. Apply supported fillets or chamfers.
3. Inspect sections.

**Acceptance criteria:**

- Whole concentric edge references are respected.
- The intended rim changes while unrelated rims do not.
- The bore remains as designed.

**Alternative and failure path:** Nested circular edges with similar radii must not silently swap because of mesh index ordering.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-014"></a>

## FEATURE-014 Reselect the original edges of a finish

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to reselect the original edges of a finish, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Edit an existing finish and choose Reselect edges.
2. Pick a different original edge.
3. Preview then Cancel or Apply.

**Acceptance criteria:**

- The picker shows the intact sharp source.
- The revised set belongs to that source.
- Cancel restores the saved finish and Apply rebuilds later features.

**Alternative and failure path:** Picking edges on the already rounded result must not replace the source references by unstable tiny fragments.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-015"></a>

## FEATURE-015 Reject an impossible fillet or chamfer safely

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to reject an impossible fillet or chamfer safely, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Request a radius or setback larger than neighbouring geometry permits.
2. Preview.
3. Correct to a valid size.

**Acceptance criteria:**

- The invalid draft explains its geometric failure.
- The original model remains unchanged.
- The corrected draft can succeed in the same editing session.

**Alternative and failure path:** No partial bevel or deleted source piece may become the saved result on error or timeout.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-016"></a>

## FEATURE-016 Hollow a simple box inward

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to hollow a simple box inward, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose a 20 mm cube.
2. Pick its top face and a 3 mm wall.
3. Preview shell then Apply.

**Acceptance criteria:**

- Outside bounds remain 20 by 20 by 20 mm.
- Side walls and floor are 3 mm.
- The open cavity is real and the result is closed.

**Alternative and failure path:** For the simple box the independent analytic remaining volume is 4668 cubic mm rather than the 8000 cubic mm of a filled cube.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-017"></a>

## FEATURE-017 Make an enclosed cavity or several openings

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to make an enclosed cavity or several openings, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Shell a supported solid with no open faces.
2. Repeat with two chosen openings.
3. Inspect a section and mesh.

**Acceptance criteria:**

- No selected face means an enclosed cavity.
- Each chosen opening is actually removed.
- The outer size and intended wall direction stay fixed.

**Alternative and failure path:** Volume and interior samples must distinguish a sealed hollow solid from a solid body that merely looks transparent.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-018"></a>

## FEATURE-018 Shell a joined cylinder and cube through a complex cap

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to shell a joined cylinder and cube through a complex cap, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [SHELL — Joined cube and cylinder plus simple shell oracle](TEST-DATA.md#shell) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Join the overlapping cube and cylinder fixture.
2. Pick the combined nonrectangular flat cap.
3. Preview and apply a 3 mm shell.

**Acceptance criteria:**

- The chosen complex cap becomes an opening.
- Outer dimensions stay unchanged.
- Independent section samples confirm continuous 3 mm walls and floor around straight and curved portions.

**Alternative and failure path:** Repeat on the opposite cap and with the cylinder buried one third of its diameter into the cube;success on a plain square face does not cover this case.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-019"></a>

## FEATURE-019 Reselect shell openings and edit wall thickness

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to reselect shell openings and edit wall thickness, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open the shell step in History.
2. Reselect openings on its intact input.
3. Change thickness and Preview.

**Acceptance criteria:**

- The picker exposes the original unshelled source.
- Selected face references stay tied to that source.
- Later supported features rebuild with the new cavity.

**Alternative and failure path:** Cancel must restore both the saved wall thickness and its previous opening set.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-020"></a>

## FEATURE-020 Reject impossible or ambiguous shells

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to reject impossible or ambiguous shells, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [SHELL — Joined cube and cylinder plus simple shell oracle](TEST-DATA.md#shell) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Request a wall too thick for the joined body.
2. Try a source edit that removes an opening face.
3. Correct or cancel.

**Acceptance criteria:**

- The original valid shell and recipe remain.
- The message identifies thickness or reference failure.
- No fallback may silently save a filled solid as a successful shell.

**Alternative and failure path:** Geometric volume removal must be checked independently because a returned mesh can still be the wrong filled body.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-021"></a>

## FEATURE-021 Build a loft from ordered profiles

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to build a loft from ordered profiles, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Loft and create three differently sized profiles on separated planes.
2. Preview and Make loft.
3. Inspect History.

**Acceptance criteria:**

- Profiles retain their order placement and outlines.
- The loft is a closed volume.
- One Apply or creation action forms one reversible feature.

**Alternative and failure path:** Reversing order must be deliberate and a collapsed or self intersecting profile stack must fail safely.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-022"></a>

## FEATURE-022 Edit add remove and reorder loft profiles

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to edit add remove and reorder loft profiles, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select each profile in a loft.
2. Edit size centre plane position and turn.
3. Add remove and reorder profiles within limits.

**Acceptance criteria:**

- Each profile has independent saved values.
- The draft guide and rebuilt volume follow the current ordered list.
- History exposes the selected profile correctly.

**Alternative and failure path:** The supported 2 to 16 profile boundaries must prevent an invalid one profile or seventeenth profile result.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-023"></a>

## FEATURE-023 Choose smooth or ruled loft sides

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to choose smooth or ruled loft sides, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Build identical profile sets with smooth and ruled sides.
2. Compare side sections.
3. Save both.

**Acceptance criteria:**

- Ruled sides use the intended straight transitions.
- Smooth sides form the intended smooth interpolation.
- Both remain valid closed volumes.

**Alternative and failure path:** Changing side style must not reset profile placement or discard constraints.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-024"></a>

## FEATURE-024 Copy an existing outline into a loft independently

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to copy an existing outline into a loft independently, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Copy a saved source sketch or the current drawn outline into one loft profile.
2. Move and edit the copy.
3. Modify the original source.

**Acceptance criteria:**

- The copied outline starts equivalent.
- The loft profile keeps its own placement.
- Later changes to the original do not secretly mutate the independent copy.

**Alternative and failure path:** Unavailable or invalid source sketches must be explained without replacing the current valid profile.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-025"></a>

## FEATURE-025 Sweep a profile along an open path

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to sweep a profile along an open path, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Sweep with a simple closed profile and a three point 3D path.
2. Make sweep.
3. Inspect sections.

**Acceptance criteria:**

- The section starts perpendicular to the initial tangent.
- It follows the complete open path.
- The result has closed end caps and a saved path recipe.

**Alternative and failure path:** A closed or zero length path is not equivalent to the supported open path and requires safe rejection or explicit supported handling.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-026"></a>

## FEATURE-026 Edit sweep path projections and exact points

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to edit sweep path projections and exact points, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Open the sweep path editor.
2. Drag points in front top and side projection.
3. Enter exact x y z values then Preview.

**Acceptance criteria:**

- Projected drags change the intended coordinate pair.
- Numeric and plotted points agree.
- The path keeps its 2 to 64 point supported limits.

**Alternative and failure path:** Duplicate consecutive or degenerate points must not create invalid tangents or a partial committed sweep.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-027"></a>

## FEATURE-027 Choose sweep transitions smoothness and initial turn

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to choose sweep transitions smoothness and initial turn, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Compare straight miter straight round and smooth path settings where offered.
2. Change initial profile turn.
3. Inspect bends.

**Acceptance criteria:**

- Each transition style has its defined geometry.
- The section transport avoids unintended extra twist.
- The initial turn is retained in the recipe.

**Alternative and failure path:** A path bend too tight for the section must fail without replacing the original with self intersecting geometry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-028"></a>

## FEATURE-028 Dimension loft and sweep profiles

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to dimension loft and sweep profiles, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [HISTORY — Nested editable construction](TEST-DATA.md#history) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Add driving dimensions and relations to their profile editors.
2. Change a value.
3. Preview Apply Undo and save reopen.

**Acceptance criteria:**

- The profile solver changes the actual rebuilt volume.
- The constraints persist on the correct profile.
- The complete later feature tree remains coherent.

**Alternative and failure path:** A conflict on one profile must not reset other profiles or silently strip their constraints.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).

<a id="feature-029"></a>

## FEATURE-029 Recover from a precision worker timeout

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to recover from a precision worker timeout, so I can refine an earlier design and preserve its construction instead of rebuilding it from scratch.

**Setup:** Use a preserved copy of [LIMIT — Boundaries in a disposable session](TEST-DATA.md#limit) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Start a controlled operation that exceeds the configured 45 second precision execution limit.
2. Observe the failure.
3. Retry a simpler valid operation.

**Acceptance criteria:**

- The timeout leaves the saved recipe and geometry intact.
- The engine can restart for the next job.
- The message gives a practical correction path.

**Alternative and failure path:** A late message from a terminated worker must not apply a stale edit or resolve the wrong queued request.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-feature-ui.ts](../src/cad-feature-ui.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-form-ui.ts](../src/cad-form-ui.ts), [src/cad-profiles.ts](../src/cad-profiles.ts), [src/cad-brep.ts](../src/cad-brep.ts), [src/cad-face-picker.ts](../src/cad-face-picker.ts), [src/cad-edge-picker.ts](../src/cad-edge-picker.ts).
