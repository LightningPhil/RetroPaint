# Intended behavior and source sensitive decisions

## How to read expected behavior

The case criteria are normative: they state the result a user should receive. Source review establishes feature scope and important distinctions. It does not prove the criteria hold today. A mismatch is a future defect or an explicit product decision, not grounds to rewrite the criterion after running it. No new application feature or test outcome is implemented by this documentation.

## Experience levels and discoverability

The three personas describe increasing confidence. They are not real age gates or separate permission systems. Basic and Advanced mode use the same document. Basic provides painting and play; Advanced adds layers, vector authoring, Photo lab, enhancement and 3D. Entering the 3D workshop requires Advanced mode. The workshop exposes Layers automatically and returns it open to Paint. Ordinary compact-layer selection outside the workshop retains its separate auto-close behavior. Basic creates raster artwork without losing the project's vector preference or existing editable content.

**2026-10-29 product decision (START-007, SOLID-001):** The user explicitly requested a whole-app Basic / Advanced split. This supersedes the previous behavior that allowed launching 3D from Basic and automatically enabled Advanced. Historical audit evidence remains unchanged; it is evidence of the earlier behavior, not certification of the new mode boundary.

## Draft completion rules

Photo lab Done saves a recipe; Cancel, Close and Escape discard the current draft. Existing saved adjustments and original pixels survive. Before compares with the original source and is not Undo. A look begins from the saved pre-look baseline; Normal restores that baseline even after Custom edits to a tried look.

CAD Preview is temporary, Apply is one complete undoable change, and Cancel retains the saved solid and recipe. Timeline rollback and inspection must not be exported as final construction. Invalid dimensions, ambiguous support references and precision failures leave a valid document and a usable correction path.

An ordinary floating raster selection can be cancelled. An editable object is placed/deselected by the supported Escape or blank-desk action. These are intentionally different contracts. A pending gradient is cancelled by Escape. The source can retain a pending gradient across a tool switch until its next settlement; test that transition and ensure no hidden draft leaks into saved output. Gradients are reached through the Bucket context, not a permanently visible tray tab.

## Permanent raster trim and source retention

Before permanent placement a raster selection's full source can be moved back onto the paper. At permanent placement or supported editable-raster deselection, off-paper raster pixels are discarded, retaining the in-paper transform and source resolution. Undo restores discarded pixels. Vector geometry remains complete outside paper. Shared photo crop is different: it changes the visible frame while projects retain every sheet's hidden source margins.

## Live data and file meanings

An ordinary image export captures one coherent rendered frame. A project retains supported live conveyor/texture definitions and editable content. The current project writer deliberately bakes procedural rainbow stroke content into source images and filters those procedural strokes from saved live arrays. Do not promise that every special ink remains procedurally animated after reopen. Test this deliberate exception separately from a defect that flattens all live ink.

PNG, JPEG, WebP, BMP, GIF and TIFF are finished image formats. JPEG and BMP receive a white transparency matte. GIF is palette-limited with binary transparency and is not an animated GIF authoring workflow. Browser decoding and TIFF's explicitly supported uncompressed 8 bit variants are capability boundaries. A filename extension alone does not establish a real file format.

Projects preserve supported editable definitions. STL carries surface geometry, not colours, original sketches or a camera. An imported mesh can keep later cuts and transforms without magically recreating the source author's lost design history.

## CAD physical requirements

All physical units are millimetres. Robustness allowances must preserve entered far endpoints. Shell walls grow inward and retain outside dimensions. A complex cap on a joined cylinder/cube must be tested as a whole geometric face, including the one-third overlap and opposite-cap variants. A fallback returning the original filled solid is a failure even when it returns a closed mesh.

Surface orientation repair must distinguish outer material, enclosed cavity shells and nested material islands. Do not orient every connected shell outward or take every shell's absolute volume. Native precision operations can reject unsupported complicated imported meshes; they must explain that limitation and preserve the original. The presence of a mesh import function does not establish universal shell/fillet support for arbitrary STL.

Linear and radial repeat controls specify extra copies in the current UI. Circular copies rotate around world Z through the origin. Exact view choices are camera operations. A measurement's reported face-normal angle is not a general three-point angle tool. Printer checks use user-entered build volume and do not promise slicer readiness or physical print success.

## Proposed usability targets and likely coverage gaps

ACCESS-018 defines an intended 44 by44 CSS pixel effective touch target for required controls and legible text after all layout scaling. This is a proposed product acceptance target, not a claim of current compliance or a cited external standard. Existing mobile checks mainly test panel bounds and scrolling; CSS zoom can make controls fit while leaving them too small. The future acceptance pass must measure the actual hit area and record failures, rather than inherit a passing layout test as proof of usability.

The one-second foreground cancellation acknowledgment target in the testing protocol is likewise a proposed acceptance threshold. It needs measured evidence on a named reference device. Timing, subjective photographic improvement, font rendering and neural detail quality need recorded test conditions and appropriate oracles. They must not be marked Pass merely because source contains a control or a worker.

Screen-reader usability needs actual assistive technology execution. Permission-denial paths need genuine controlled capability conditions. Legacy compatibility needs authentic old fixture bytes. These are explicit execution prerequisites, not hidden exemptions that can be used to avoid failures.

## Boundaries rather than invented features

No cases assume accounts, cloud sharing, collaborative editing, RAW sensor development, EXIF metadata preservation, automatic photo subject segmentation, automatic lens profiles, vector interchange, raised 3D text from a paint caption, a slicer, direct printer transmission or guaranteed cold-cache offline launch. If desired later, those need separately proposed requirements. The local network case checks application data handling, not the security of every browser extension or the user's host.

## Keeping decisions honest

Record changes with date, case IDs, reason, approval and affected baselines. A new implementation limit is not automatically an approved scope reduction. Preserve old failures. If a requirement is ambiguous, mark that portion Blocked pending a decision; do not silently choose whichever interpretation the current build happens to satisfy.
