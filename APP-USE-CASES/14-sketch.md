# 3D sketches dimensions constraints and boolean building

22 paired user stories and use cases. [Start here](START-HERE.md) · [Coverage matrix](COVERAGE-MATRIX.md) · [Testing protocol](TESTING-PROTOCOL.md).

## Expected behavior for this area

Sketch dimensions drive geometry rather than act as labels. Supporting faces are geometric references, not transient triangle numbers. Joins and cuts must honour entered endpoints while preserving a valid solid. Use independent analytic checks for simple fixtures.

The scenarios below define intended behavior. Their source links identify implementation entry points reviewed for scope; they do not establish conformance. Every case is **Not run** in this catalogue.

All cases inherit the preservation, evidence, interruption, input and comparison rules in the testing protocol. Use the exact fixture preparation before executing the flow.

<a id="sketch-001"></a>

## SKETCH-001 Sketch on every fixed workplane

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to sketch on every fixed workplane, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Floor XY Front XZ and Side YZ.
2. Draw the same rectangle on each.
3. Pull it by a known amount.

**Acceptance criteria:**

- The plane basis and pull direction match the selected view.
- Dimensions are measured in millimetres.
- Each result is a closed correctly oriented solid.

**Alternative and failure path:** Changing plane during an unfinished sketch must not commit points in a mixed coordinate system.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-002"></a>

## SKETCH-002 Draw dimensioned rectangles and circles

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to draw dimensioned rectangles and circles, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Enter rectangle start width and height.
2. Create a separate circle by centre and diameter.
3. Use the dimensions and pull.

**Acceptance criteria:**

- The rectangle bounds match its entered coordinates.
- The circle's size follows its diameter controls.
- The pulled shapes retain editable sketch definitions.

**Alternative and failure path:** A circle starts from its centre and must not be mistakenly positioned from a corner like a rectangle.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-003"></a>

## SKETCH-003 Draw and finish a custom polygon sketch

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to draw and finish a custom polygon sketch, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Tap a nonrectangular closed outline.
2. Finish with the supported control or Enter.
3. Pull it.

**Acceptance criteria:**

- The selected points remain in order.
- The completed profile closes once.
- The resulting solid has the intended concavity.

**Alternative and failure path:** Too few distinct points collinear points or self intersections must give a clear safe failure or supported defined result.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-004"></a>

## SKETCH-004 Pick a whole flat support face

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to pick a whole flat support face, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select a cube and choose Pick flat face.
2. Tap its top face then draw a sketch.
3. Orbit the view.

**Acceptance criteria:**

- The entire geometric support face is identified.
- The sketch lies on it in world space.
- Orbiting is distinct from adding a point.

**Alternative and failure path:** Curved faces or tessellation diagonals must not masquerade as supported flat sketch planes.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-005"></a>

## SKETCH-005 Pull a sketch into a new solid

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to pull a sketch into a new solid, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create a 10 by 10 rectangle on XY.
2. Set pull to 30 and New piece.
3. Make the solid.

**Acceptance criteria:**

- The result spans Z zero through 30 with volume 3000 cubic mm.
- The recipe retains the input outline and pull.
- Undo removes one created feature.

**Alternative and failure path:** Zero pull and invalid numeric input must leave the last valid sketch usable.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-006"></a>

## SKETCH-006 Pull in the negative direction

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to pull in the negative direction, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create the same rectangle on XY.
2. Pull by -10 as a new piece.
3. Inspect bounds and winding.

**Acceptance criteria:**

- The result extends to Z -10 without an unintended positive extension.
- Volume magnitude is 1000 cubic mm.
- Surface orientation is outward.

**Alternative and failure path:** Negative pull must not invert triangle winding or reverse an attached face reference unexpectedly.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-007"></a>

## SKETCH-007 Join a fixed plane pull with exact endpoints

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to join a fixed plane pull with exact endpoints, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [JOIN — Exact positive and negative pull](TEST-DATA.md#join) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use the 10 by 10 sketch on XY through the cube.
2. Join with pull 30 then -10 in separate copies.
3. Inspect mesh bounds and volume.

**Acceptance criteria:**

- Positive result has Z zero to 30 and volume 9000 cubic mm.
- Negative result has Z -10 to 20 and volume 9000 cubic mm.
- History retains the exact entered pull.

**Alternative and failure path:** A robustness overlap allowance must not add 0.02 mm to the far endpoint or alter the requested overall size.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-008"></a>

## SKETCH-008 Cut a dimensioned recess

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to cut a dimensioned recess, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Sketch a centred 10 by 10 rectangle on a cube face.
2. Cut inward by 5.
3. Inspect a section and Undo.

**Acceptance criteria:**

- The recess floor is 5 mm below its support face.
- The outside size is unchanged.
- Removed volume is 500 cubic mm for the simple fixture.

**Alternative and failure path:** The cut must not pass through the whole body or extend beyond the requested depth because of contact tolerances.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-009"></a>

## SKETCH-009 Cut all the way through

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to cut all the way through, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Sketch a circular hole on a solid face.
2. Choose Through all.
3. Increase the source body's depth through History.

**Acceptance criteria:**

- The opening reaches both intended sides.
- The downstream cut rebuilds for the new depth.
- The original hole sketch remains editable.

**Alternative and failure path:** A changed support face that cannot be resolved must stop rebuilding rather than cut in an arbitrary plane.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-010"></a>

## SKETCH-010 Join a sketch on a picked face

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to join a sketch on a picked face, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Pick a flat face of a transformed cube.
2. Sketch a smaller pad.
3. Join with a known positive height.

**Acceptance criteria:**

- The pad grows from that support face.
- Any inward contact allowance preserves the far endpoint.
- The result is one valid joined solid.

**Alternative and failure path:** Repeat on opposite faces and after source size changes so a hard coded world Z assumption cannot pass.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-011"></a>

## SKETCH-011 Taper and twist an extrusion

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to taper and twist an extrusion, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Pull an asymmetric sketch with Top size multiplier then Twist.
2. Compare with neutral values.
3. Edit it in History.

**Acceptance criteria:**

- Taper changes top profile size relative to bottom.
- Twist turns the profile through the specified angle.
- Neutral settings reproduce the untapered untwisted case.

**Alternative and failure path:** Collapsed tapered tops self intersections or unsupported precision operations must fail with the original retained.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-012"></a>

## SKETCH-012 Revolve a predefined profile

**Primary user:** L2 adventurous older child. **Priority:** P1. **Execution:** Not run.

**User story:** As an adventurous older child, I want to revolve a predefined profile, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Hollow vase Goblet and Knob profiles in separate setups.
2. Revolve through a full turn.
3. Inspect a cutaway.

**Acceptance criteria:**

- Each preset makes its intended closed solid.
- Hollow profiles contain real empty space.
- The profile remains accessible in History.

**Alternative and failure path:** A displayed silhouette alone cannot prove that the central cavity exists in exported geometry.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-013"></a>

## SKETCH-013 Draw a custom revolve profile

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to draw a custom revolve profile, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Choose Draw my own.
2. Add and drag radius height points.
3. Edit the coordinate list and finish.

**Acceptance criteria:**

- Profile points and numeric list agree.
- Radius stays on the supported side of the axis.
- The revolved result uses the intended profile.

**Alternative and failure path:** Duplicate points self intersections negative radius or a profile on the axis must be rejected or constrained safely.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-014"></a>

## SKETCH-014 Make a partial revolution

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to make a partial revolution, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Revolve a known annular profile by 180 degrees.
2. Inspect its end caps.
3. Edit the angle.

**Acceptance criteria:**

- The partial solid has closed end faces.
- Its volume follows the chosen fraction of the analytic full revolution.
- Editing retains its axis and profile.

**Alternative and failure path:** Near zero or invalid angles must not produce an open broken printable mesh.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-015"></a>

## SKETCH-015 Join subtract intersect and wrap solids

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to join subtract intersect and wrap solids, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [BOOLEAN — Analytic overlap and cutter](TEST-DATA.md#boolean) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Use overlapping cubes and a separate cutter.
2. Perform Join Subtract Keep overlap and Wrap with hull on independent copies.
3. Undo each.

**Acceptance criteria:**

- Join removes internal overlap.
- Subtract retains the named target and removes cutter volume.
- Intersection and Hull have their respective analytic expected bounds and volume.
- On the separate gapped cube fixture, Hull fills the gap and has volume 3000 cubic mm, while Union retains the two components with volume 2000 cubic mm.

**Alternative and failure path:** Select at least two supported pieces and test target order so commutative Join cannot conceal a reversed subtraction.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-016"></a>

## SKETCH-016 Keep boolean source pieces editable

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to keep boolean source pieces editable, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [BOOLEAN — Analytic overlap and cutter](TEST-DATA.md#boolean) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Join or subtract two named primitives.
2. Expand History.
3. Change an original size and apply.

**Acceptance criteria:**

- Source definitions remain nested in the result.
- Later geometry rebuilds from the changed input.
- Undo restores one complete edit.

**Alternative and failure path:** A failed rebuild must keep the previous final solid and the draft inputs rather than replacing them with a partial tree.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-017"></a>

## SKETCH-017 Add a driving line length

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to add a driving line length, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw an irregular sketch.
2. Select a numbered line and add a length dimension.
3. Change its value.

**Acceptance criteria:**

- The line reaches the entered millimetre length within solver tolerance.
- The definition is saved.
- Dependent solid geometry rebuilds.

**Alternative and failure path:** An impossible length combined with existing relations must retain the last valid sketch and explain the conflict.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-018"></a>

## SKETCH-018 Constrain horizontal and vertical lines

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to constrain horizontal and vertical lines, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Select suitable lines.
2. Add horizontal and vertical relations.
3. Drag or dimension neighbouring geometry.

**Acceptance criteria:**

- The constrained directions remain horizontal or vertical in the sketch plane.
- Other free points can still move.
- The controls identify the active relations.

**Alternative and failure path:** Redundant or conflicting relations must not cause a jump to an unrelated far away configuration.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-019"></a>

## SKETCH-019 Control line angles and relations

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to control line angles and relations, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Prepare separate valid sketches for angle to X, parallel, perpendicular and angle between two lines.
2. Select the appropriate numbered lines and add each requested relation.
3. Edit each supported angle value and rebuild the solid to inspect its geometry.

**Acceptance criteria:**

- Each relation solves its stated geometric condition.
- Angle between directed lines uses the declared 0 to 180 degree convention.
- Stored relations survive reopening.

**Alternative and failure path:** Selecting the same line twice or an invalid line index must be rejected without altering the sketch.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-020"></a>

## SKETCH-020 Dimension a circle by diameter

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to dimension a circle by diameter, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Draw an elliptical circle type outline.
2. Add a diameter dimension and edit it.
3. Pull the constrained outline.

**Acceptance criteria:**

- The diameter constraint produces a round section.
- Its physical diameter matches the entered value.
- The solid updates from the constrained outline.

**Alternative and failure path:** A polygon cannot acquire an unsupported circle diameter relation through stale controls.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-021"></a>

## SKETCH-021 Edit remove and persist constraints

**Primary user:** L3 confident maker. **Priority:** P1. **Execution:** Not run.

**User story:** As a confident maker, I want to edit remove and persist constraints, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Add several valid dimensions.
2. Edit one via its label and remove another.
3. Save and reopen.

**Acceptance criteria:**

- Labels and selectors refer to the same definitions.
- Removing a relation frees the intended degree of freedom.
- The reopened constraints still drive geometry.

**Alternative and failure path:** A decorative annotation that does not change rebuilt geometry must fail this case.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).

<a id="sketch-022"></a>

## SKETCH-022 Reject conflicting dimensions without losing a sketch

**Primary user:** L3 confident maker. **Priority:** P0. **Execution:** Not run.

**User story:** As a confident maker, I want to reject conflicting dimensions without losing a sketch, so I can describe a shape by its dimensions and make predictable additions and cuts.

**Setup:** Use a preserved copy of [CAD — Known simple solids](TEST-DATA.md#cad) and the shared setup rules in the testing protocol. The main flow states any additional editing state required.

**Trigger and main flow:**

1. Create a constrained rectangle.
2. Request an incompatible extra angle or length.
3. Cancel or correct the value.

**Acceptance criteria:**

- The last valid geometry stays visible and saved.
- The message identifies a conflict.
- The draft can be corrected without restarting the whole model.

**Alternative and failure path:** Do not accept silently deleting an existing constraint or relaxing the requested tolerance as a successful solve.

**Evidence to retain:** Before/after state, observations for every criterion, and interaction evidence. Retain independently reopened output bytes for save/export cases. Use the area oracle and required variants in the testing protocol and coverage matrix.

**Implementation entry points:** [src/cad-ui.ts](../src/cad-ui.ts), [src/cad-sketch-ui.ts](../src/cad-sketch-ui.ts), [src/cad-sketch-constraints.ts](../src/cad-sketch-constraints.ts), [src/cad-attachment.ts](../src/cad-attachment.ts), [src/cad-features.ts](../src/cad-features.ts), [src/cad-kernel.ts](../src/cad-kernel.ts).
