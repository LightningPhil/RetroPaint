# Test data preparation and independent expected results

These are reproducible fixture specifications for future execution. They are not bundled binary fixtures and have no execution result. Create or collect the required bytes, preserve an untouched reference, record provenance and SHA256, and mark a dependent case Blocked if the required input or independent oracle is unavailable. Small synthetic images establish exact behavior; natural photos establish photographic appearance. Neither replaces the other.

Use a disposable document or independent copy for destructive, quota, malformed input and fault injection scenarios. Never use an unsaved personal original as the only fixture. Preserve separate baseline projects before testing save/reopen, which can otherwise overwrite the only evidence of a defect.

<a id="play"></a>

## PLAY Ready painting paper

Create a fresh 960 by 640 document with one opaque white Paper sheet. Use Raster mode, symmetry Off, no crop, no saved photo recipe and no live ink unless the steps ask for them. Keep a clean copy. Record size, Strength, applicator, colour and device input for each gesture. Use paper coordinates rather than screen coordinates.

<a id="patch"></a>

## PATCH Known pixels and alpha

Create a 960 by 640 RGBA PNG. Use a transparent background and labelled nonoverlapping rectangles at integer coordinates: red #FF0000 at x100 y100 width100 height80, blue #0000FF at x400 y100 width100 height80, green #00FF00 at x100 y300 width100 height80, and 50 percent alpha red at x400 y300 width100 height80. Add a one pixel black border on a separate copy where required. Keep opaque white and opaque black backing copies for edge inspection. Save the exact generator recipe, bytes and hash before testing.

<a id="pixel"></a>

## PIXEL Crisp pixel art

Create a 32 by 32 PNG with no alpha, only black white red and blue. Include a one pixel staircase from x2 y2 to x15 y15, a one pixel wide vertical line, and a four by four checkerboard. Enlarge the paper view without changing the source. Use the original 32 by 32 bytes as the oracle for source pixels, not a screenshot of an enlarged canvas.

<a id="fill"></a>

## FILL Connected regions and tolerance

Create a 320 by 240 RGBA image with a black one pixel rectangle from (20,20) through (140,140), a pale grey #E8E8E8 interior and white outside. Put a second disconnected pale grey island at (220,40) sized40 by40. Keep separate copies with a one pixel gap at (80,20), antialiased edges, a transparent island, and deterministic interior variation of plus or minus 8 channel levels. Document the flood similarity metric observed in source before choosing boundary colours for exact tolerance tests.

<a id="smudge"></a>

## SMUDGE Two wet colour regions

Use a transparent 320 by 240 sheet with an opaque red rectangle x40 to140 and opaque blue x160 to260, both y60 to180, and clear margins. Create both wet live and settled versions when supported. Trace a fixed horizontal drag from (120,120) to (200,120) at recorded size and Strength. The oracle checks local displacement, unchanged outside regions and alpha, without assuming random texture bytes are identical.

<a id="mix"></a>

## MIX Multilayer picture

Use a 960 by 640 document with Paper, an opaque blue Backdrop, a transparent Character sheet with red and green known patches, and a transparent Caption sheet with text and a stamp. Set Character opacity to0.5 in the relevant variant. Give every layer a unique name. Add a separate copy with live water and conveyor ink plus a saved photo recipe and editable objects. Save a baseline project and a controlled time composition.

<a id="vector"></a>

## VECTOR Mixed editable scene

Start from PLAY, choose Vectors, and create separately named rectangle, concave heart, line, text, stamp, Spiro path, transparent imported PNG and two independent raster brush gestures. Place several overlaps and one item partly outside the paper. Record object IDs kinds transforms original raster dimensions and layer order from a baseline project, plus an independent rendered reference.

<a id="photo"></a>

## PHOTO Photographic editing source

Use a legally usable local photograph at least1600 by1200 with a horizon neutral object dark detail bright detail fine texture and some varied colour. Record provenance bytes dimensions decoder and SHA256. Keep an untouched independent copy. Pair it with the synthetic TONAL COLOUR DETAIL and GEOMETRY fixtures for objective checks. A tiny synthetic patch cannot substitute for the natural photograph when judging ringing composition skin colour or photographic appearance. No private photo is included in this documentation.

<a id="tonal"></a>

## TONAL Known luminance ramp

Create a 1024 by256 RGBA image containing an opaque 0 through255 neutral ramp with four columns per value. Add separately defined uniform patches at32 64 128 192 and224 and fully transparent padding in a second copy. For exposure, compute linear light from the published sRGB transfer equation independently, multiply by2 for plus1 EV or0.5 for minus1 EV, clamp, then reencode. Histogram bins and clipping counts come from the independently decoded result.

<a id="colour"></a>

## COLOUR Hue and neutral samples

Create opaque patches for red orange yellow green aqua blue purple magenta and neutral levels32 128 and224. Include near boundary hues on both sides of red wrap and every mixer band. Include a grey patch deliberately cast by known channel gains and semitransparent versions with unchanged alpha. Save the exact RGB and alpha values and positions. Use a natural photo separately for appearance checks.

<a id="detail"></a>

## DETAIL Edges texture and reproducible noise

Create at least1024 by768 pixels with a sharp black to white edge, fine alternating lines, broad soft edges, flat neutral areas and coloured boundaries. For noise use a documented deterministic PRNG and seed12345, store both clean and noisy pixels, and measure variance in fixed interior regions away from borders. Add a transparent coloured edge copy. Do not generate a new noisy input for each comparison.

<a id="geometry"></a>

## GEOMETRY Coordinate and lens chart

Create a 960 by640 numbered grid with unique corner colours, a horizon with a known slope and a centred rectangle. Retain exact landmark coordinates. Create separate known barrel pincushion perspective and red blue channel offset variants with an independent documented mapping. Use full source data, not a previously cropped screenshot, to test retained crop margins.

<a id="import"></a>

## IMPORT Image format matrix

Prepare genuine independently encoded PNG JPEG WebP BMP GIF and uncompressed 8 bit TIFF RGB RGBA and greyscale files. Use asymmetric orientation labels and known dimensions. Include a source with an embedded orientation tag where the browser decoder supports it. Keep corrupt truncated and unsupported compressed TIFF variants separately. Record decoder limitations and never simply rename a PNG extension to create a valid format fixture.

<a id="legacy"></a>

## LEGACY Provenanced old project files

Collect genuine saved fixtures for every project version the current importer explicitly supports, starting with version1, from repository history or archived app builds. Record the producing revision and an expected rendered reference. Include old recipes with missing later optional fields. These fixtures are a planned requirement until such bytes exist: changing the version number of a current project is not valid migration evidence.

<a id="corrupt"></a>

## CORRUPT Disposable invalid inputs

Create copies of valid fixtures and independently alter one property at a time: truncate bytes, corrupt an image data URL, duplicate IDs, introduce NaN or invalid numeric encodings, singular object transforms, invalid crop bounds, broken workplanes, unsupported recipe kinds, mismatched STL counts and open mesh edges. Keep an unrelated unsaved picture open in a disposable session for atomicity comparison. Never damage the users original files.

<a id="limit"></a>

## LIMIT Boundaries in a disposable session

Use small fixtures to establish behavior first. Test image edge4096 and4097, sheet count16 and17, and stored pixel budget64000000 at the nearest reachable valid and invalid combinations. Three4096 squared sheets use50331648 pixels and a fourth would exceed the budget. Check draft pixel and character cutoffs separately. For CAD exercise128 top level pieces, 2 and16 loft profiles, 2 and64 path points, 64 constraints and their first invalid counts. Record machine memory and stop safely on allocation failure; do not allocate giant structures just to claim coverage.

<a id="network"></a>

## NETWORK Controlled local resource capture

Use a clean disposable browser profile or storage namespace on the intended app origin. Record browser version app revision network requests methods origins and request sizes. Run once uncached and once with assets cached. Keep source image and model hashes so any outgoing data can be identified. Permission denial network interruption and missing asset tests must be controlled reversibly. Do not expand host exposure or change user security settings to make a check pass.

<a id="cad"></a>

## CAD Known simple solids

Use a new 3D layer in a 960 by640 picture. A primitive20 mm cube is centred X0 Y0 Z10, with bounds[-10,-10,0] to[10,10,20] and analytic volume8000 cubic mm. Include a 20 by10 by30 asymmetric wedge or labelled rectangular solid for view and transform checks. Use no nonuniform scale or earlier features unless specified. Record units and recipe plus an independently decoded triangulated surface.

<a id="join"></a>

## JOIN Exact positive and negative pull

Use the CAD20 mm cube. Place a centred10 by10 rectangle on fixed XY at Z0, then union its extrusion with the cube. Positive pull30 produces bounds Z0 to30 and volume9000 cubic mm. Negative pull-10 produces bounds Z-10 to20 and volume9000 cubic mm. For face recesses use a10 by10 top face sketch cut5 mm, removing500 cubic mm. Preserve entered values and compare far endpoints independently.

<a id="boolean"></a>

## BOOLEAN Analytic overlap and cutter

Use cube A bounds[0,0,0] to[20,20,20] and cube B bounds[10,0,0] to[30,20,20]. Each volume is8000, overlap is4000, union12000, subtraction of B from A4000, intersection4000 and convex hull12000 cubic mm. Add a separate inside cylinder cutter and disjoint copies for scope tests. Keep an asymmetric target name so subtraction order is unambiguous. For an independent Hull versus Union discriminator, use two 10 mm cubes with bounds [0,0,0] to [10,10,10] and [20,0,0] to [30,10,10]. Hull volume is 3000 cubic mm and union volume is 2000 cubic mm, with a genuine 10 mm gap between source pieces.

<a id="history"></a>

## HISTORY Nested editable construction

Build a named source body, an attached dimensioned rectangle or circle, a Through all hole, a supported small edge finish, and a separate shell version. Save a known valid baseline with unique feature IDs and at least enough separate steps to force paging. Keep variants with loft and sweep profile constraints. The baseline must already be geometrically checked before testing a downstream rebuild so source defects cannot be blamed on a later edit.

<a id="shell"></a>

## SHELL Joined cube and cylinder plus simple shell oracle

Cube20 by20 by20 has centre[0,0,10]. Cylinder diameter20 height20 has centre[15,0,10], so the union has outside bounds[-10,-10,0] to[25,10,20] and a complex planar top cap. Shell the top inward by3 mm. Check floor height3 and wall offsets using independent section rays in straight curved and junction regions, not a single approximate total volume. Repeat with bottom cap. For the one third diameter overlap variant use cylinder centre X=40/3 mm, giving overlap depth20/3 mm at the cube right edge. Separately shell a simple20 mm open top cube: remaining volume4668 cubic mm. Retain unmodified source unions inside project recipes.

<a id="cadmix"></a>

## CADMIX Solid picture and guide

Use a 960 by640 picture with Paper, a green opaque Backdrop or a local guide photo, one CAD layer containing the SHELL joined model, and a transparent Paint above3D sheet with text and a coloured arrow. Save a known camera view in both perspective and orthographic variants. Set source photo adjustments and a shared crop in separate copies. Layer order must be exactly documented before comparing front and back picture canvases.

<a id="stl"></a>

## STL Independent mesh input

Prepare genuine binary and ASCII tetrahedra cubes and a simple closed curved mesh with known coordinates. Include a2 unit cube for unit scaling and an offset copy for centering. Build counts at 200000 triangles and200001 separately where feasible, and byte sizes at 20000000 and20000001. Use an independent encoder, preserve source hashes and record the manifold status. A valid large disconnected solid collection is distinct from a corrupt high count file.

<a id="hollow"></a>

## HOLLOW Nested oriented mesh shells

Create an independently encoded outer cube10 mm edge, an inner fully enclosed6 mm cavity, a nested2 mm material island and a separate4 mm cube away from them. Analytic total signed material volume is1000-216+8+64=856 cubic mm. Produce variants with all faces reversed, one face reversed, mixed component winding, permuted triangles and both binary and ASCII encoding. Require manifold edges and independent containment checks. Never use the importer under test to build the expected oriented result.

## Comparison tolerances

For ordinary integer aligned opaque PNG patches, sizes, alpha masks and unchanged regions, require exact decoded values unless the operation explicitly introduces interpolation. For simple CAD box bounds and analytic volumes, begin with an absolute linear tolerance of0.001 mm and volume tolerance of0.02 cubic mm in these small fixtures. Curved tessellated shapes need a separate error budget based on tessellation, curvature and surface area; record that budget before seeing the result. A generic percentage tolerance is not permission to fill a cavity or move a far endpoint.

For JPEG and neural enhancement, define task specific perceptual or model comparison tolerances in the run plan before execution. Font and emoji raster pixels can differ by OS; verify content geometry identity and usability independently, and use platform specific visual references when needed. Random marks need a seed or distribution mask and Undo consistency checks. A frozen animation time is required for pixel comparison of live artwork.
