/** Plain-language introductions complement the detailed reference in cad-wiki-content. */
export interface WikiLesson { beginner:string[]; deeper:string }
const lesson=(idea:string,reading:string,deeper:string):WikiLesson=>({beginner:[idea,reading],deeper});
export const WIKI_LESSONS:Record<string,WikiLesson>={
  start:lesson(
    'Think of a script as a recipe for a part. You describe a block, describe a round cutting tool, then ask the computer to remove the tool’s volume from the block. You do not need to draw individual edges.',
    'A name followed by parentheses is an instruction. The numbers inside are its settings, called arguments. cube([30,20,8]); makes a box 30 mm wide, 20 mm deep and 8 mm high. Square brackets collect related values; a semicolon ends an instruction. Lines starting with // are notes for people and are ignored when building the part.',
    'Read an example from the innermost shape outward: create the cylinder, move it, then subtract it. Braces { } group the shapes belonging to an operation. The short syntax summaries use placeholder names such as shape(); copy the complete worked examples when you want something runnable.'),
  workflow:lesson(
    'Code studio is a workbench with a recipe on one side and its result on the other. Preview builds the recipe so you can inspect it. Add to scene keeps that result in your workshop. Until you add or update it, editing the recipe does not replace an existing workshop part.',
    'A .scad file is a text file containing the recipe. A project may also need helper recipes, pictures or imported shapes. The entry script is the main recipe; the edit file is simply the file you are currently reading or changing. They need not be the same.',
    'Keep helper files beside the main file in a predictable folder structure. In the example, main.scad asks parts/post.scad for a reusable post. Preview evaluates main.scad even if you are editing the helper. Save the RetroPaint project after applying the part to retain both files.'),
  coordinates:lesson(
    'Imagine three rulers meeting at one corner: X runs across the work plane, Y runs along it and Z points upward. Their meeting point is the origin, written [0,0,0]. A point such as [15,10,5] is 15 mm along X, 10 along Y and 5 up.',
    'Moving a shape and turning it are different instructions. A shape turns around the origin, so moving it before turning can make it swing around like a hand on a clock. A small overlap between joined pieces helps the computer recognise them as one solid.',
    'The example’s base ends at Z=5; the boss begins at Z=4.9. That shared 0.1 mm is deliberate. It is a numerical overlap for a reliable join, not the clearance needed between two separately manufactured parts.'),
  cube:lesson(
    'Despite its name, cube() can make any rectangular box: a brick, a thin plate or a tall post. Give it one number for equal sides, or three numbers for width, depth and height.',
    'The example is a 30 × 18 × 6 mm block. center=true places its middle at the origin; without that setting, its lower corner is at the origin. true and false are yes/no values, not quoted words.',
    'For the centred example, X extends from −15 to +15, Y from −9 to +9 and Z from −3 to +3. This makes symmetric holes and rotations easier to place. Use an uncentred box when measurements from a bottom corner are more convenient.'),
  sphere:lesson(
    'sphere() makes a ball. Radius is the distance from its centre to the outside; diameter is twice that distance. A radius of 10 therefore makes a ball 20 mm across.',
    'The example stretches the ball into an oval solid. scale([1.5,1,0.7]) means make it one-and-a-half times as wide, leave its depth alone and reduce its height to 70 percent. The ball’s centre stays at the origin.',
    'The resulting ideal dimensions are 30 × 20 × 14 mm. Curves are represented by many flat triangles; $fn controls their detail. That approximation explains why a measured mesh bound can differ slightly from a perfect mathematical sphere.'),
  cylinder:lesson(
    'A cylinder is a round post or disk. Its height runs upward along Z. If the bottom and top have different radii, it becomes a tapered post; if one radius is zero, it becomes a pointed cone.',
    'The example makes a tapered sleeve by removing a smaller cylinder from a larger one. The smaller shape is a cutting tool: it disappears from the finished result along with the material it occupies.',
    'The outside radius changes from 12 at the bottom to 8 at the top, while the bore remains radius 5. The wall is therefore thinner at the top. Extending the bore below and above the sleeve avoids a cutter that only touches an end face.'),
  polyhedron:lesson(
    'Use polyhedron() when you want to build a solid by listing its corners and the surfaces between them. Think of assembling a cardboard model: every face needs its own outline and the finished model must have no missing panels.',
    'The points list is a numbered address book of corners, starting at number 0. A face such as [0,1,2,3] means join those four corners in that order. The pyramid example has four base corners and one top corner.',
    'Changing a point changes every face that refers to its index. Face order determines which side faces outward, so it is not just a drawing order. Keep shared indices, consistent winding and two faces per edge; polygon plus extrusion is simpler for shapes with a constant cross-section.'),
  square:lesson(
    'square() draws a filled rectangle on the flat XY work plane. It has area but no thickness, like the outline of a sheet viewed from above. Two numbers set its width and depth.',
    'To turn that flat area into something solid, put linear_extrude() around it. The example lifts a 30 × 18 rectangle by 4 mm, making a plate. The outer instruction acts on the shape immediately following it.',
    'Build slots and holes in the flat profile before extruding when they should pass through the full thickness. This keeps the design in two dimensions until the final step and often makes it easier to inspect.'),
  circle:lesson(
    'circle() makes a filled round area on the work plane. It is flat until you give it thickness. Radius measures from the centre to the rim; diameter measures all the way across.',
    '$fn says how many straight sides approximate the circle. Usually you use enough sides to look smooth, but $fn=6 deliberately makes a hexagon. The example subtracts a round hole from a hexagon, then lifts the remaining area into a spacer.',
    'The hexagon’s radius is measured to a corner. Its distance across the flats is smaller than twice that radius, which matters when fitting a nut or a spanner. The inner and outer boundaries can have independent segment counts.'),
  polygon:lesson(
    'A polygon is a filled outline made from straight edges. Write down the corner coordinates in order around the boundary; the last corner automatically connects back to the first.',
    'The example calculates five points equally spaced around a circle, then joins them into a pentagon and gives it thickness. You can also enter points directly, such as [[0,0],[20,0],[10,12]] for a triangle.',
    'The generated points are data, not geometry, until polygon() uses them. Ordered points trace the boundary; a crossed order can produce a bow-tie rather than a usable face. paths lets several loops refer to a shared point list when you need an outer boundary and holes.'),
  text:lesson(
    'text() turns words into flat letter shapes. Put the words in quotation marks. A font is the design of the lettering, and size controls its nominal scale. Extrude those shapes to make raised letters or a cutting tool for engraving.',
    'The example places BOX on a plate. The letters begin just inside the plate’s top surface so they become attached to it. Without the plate, dots and separate letters may be separate physical pieces.',
    'halign and valign anchor the text around its own origin. They do not move the plate. Font measurements are not the same as the visible outline, so use textmetrics for an automatically fitted plate and use identical font settings when measuring and drawing.'),
  projection:lesson(
    'Projection turns a 3D part into a flat shape. With cut=false it is like the shadow seen from directly above. With cut=true it is like slicing the part exactly at work-plane height and keeping the filled slice.',
    'The example lowers a ball so the work plane cuts through its upper half. The resulting circular slice is then extruded into a small disk. A slice that misses the object entirely has nothing to show.',
    'A sphere of radius 10 shifted down by 6 intersects Z=0 at radius sqrt(10²−6²)=8. Projection removes all height information; rotate or translate the original solid before the projection to select the direction or level you need.'),
  'linear-extrude':lesson(
    'Extruding is like pulling a flat shape upward to give it thickness. A circle becomes a post, a rectangle becomes a box and an outline with a hole becomes a hollow part.',
    'The example starts from a rectangle and pulls it up 30 mm. twist=90 turns the top a quarter turn relative to the bottom; scale=0.65 makes the top smaller. slices controls how many steps are used along the height.',
    'Build and position the profile in XY first. Then extrude it, then position the resulting solid in the scene. Twisting changes intermediate cross-sections, so a coarse slice count can visibly distort the side walls even when the starting outline is detailed.'),
  'rotate-extrude':lesson(
    'Revolving is like making a pot on a potter’s wheel. Draw a filled slice through one side of the pot and spin that slice around the vertical axis to make the whole object.',
    'In this special drawing, X is distance from the spinning axis and Y becomes the finished height. A profile touching the axis can make a closed bottom. A small circle held away from the axis makes a doughnut-shaped ring, called a torus.',
    'Trace the bowl profile from the bottom centre, along the underside, up the outside, across the rim, down the inside and back across the floor. It describes the material in the wall, not the empty space inside the bowl. A full 360-degree sweep repeats that material all the way around.'),
  union:lesson(
    'union() keeps all the material from its child shapes. Think of pressing two lumps of clay together: the overlapping space is counted once and the outside surfaces form the new part.',
    'The example joins a round boss, meaning a raised mounting feature, onto a rectangular base. Both shapes go inside the same pair of braces. Separated shapes are still separated pieces even if they are in one union.',
    'Use an explicit union when several additive shapes must be treated as the first child of difference(). Otherwise a later additive shape may accidentally be interpreted as a cutter. group() organises children but union() states the intended geometric combination.'),
  difference:lesson(
    'difference() removes material. Put the part you want to keep first, then put every cutting shape after it. The cutters do not appear as extra objects in the result.',
    'To make a hole, imagine a drill bit made from a cylinder and pass it through the block. To make a pocket, stop the cutter partway into the block. A cutter that never meets the block cannot change it.',
    'Order matters: A minus B is generally different from B minus A. Group several stock shapes inside union() if they should all survive before cuts. Extend through-cut tools beyond both faces instead of making their ends exactly flush.'),
  intersection:lesson(
    'intersection() keeps only the space shared by every child. Imagine two overlapping solid objects and keep just the material that lies inside both at once.',
    'This is useful for trimming a shape to an envelope. It differs from joining, which keeps everything, and cutting, which removes the later shapes. No shared volume means an empty result.',
    'intersection_for() intersects the shapes generated by each loop iteration. An ordinary for loop normally combines its outputs, so wrapping one loop as a single child is not the same instruction as intersecting every iteration.'),
  hull:lesson(
    'hull() stretches an imaginary tight rubber skin around the outside of its child shapes and fills the inside. It bridges gaps and removes inward dents.',
    'Place small circles at the ends of a slot and hull them to get a rounded outline. The example uses two circles as the rounded ends of a capsule-shaped plate, then gives the flat outline thickness.',
    'A hull is convex: a straight line between any two points inside stays inside. This makes it useful for transitions and rounded outlines but unsuitable for preserving holes or concave notches. Subtract those details after constructing the hull.'),
  minkowski:lesson(
    'minkowski() grows one shape by the size and shape of another. Imagine sliding a small ball over every point in a block; the swept volume is a larger block with rounded edges.',
    'The example combines a 26 × 16 × 6 mm block with a radius-2 ball. Because the ball grows it by 2 mm on each side, the finished ideal dimensions are 30 × 20 × 10 mm.',
    'This is a geometric sum, not a union of two objects at their current positions. It can greatly increase computation and triangle count. Use a modestly detailed kernel and subtract final-size holes afterwards so they are not changed by the growth operation.'),
  fill:lesson(
    'fill() plugs enclosed holes in a flat shape. Imagine colouring in the empty middle of a ring while keeping its outside edge unchanged.',
    'The example first makes a ring by cutting a small circle from a larger circle. fill() closes that opening, then extrusion gives the filled disk thickness. It is useful for turning an imported logo outline into a solid backing shape.',
    'This operates on 2D areas before extrusion. It preserves inward bends in the outer boundary, unlike hull(), which stretches a convex envelope around them. Deliberate holes can be subtracted again after filling.'),
  translate:lesson(
    'translate() means move. Its list says how far to move along X, Y and Z. Positive and negative numbers move in opposite directions; zero leaves that axis alone.',
    'translate([12,0,0]) moves a shape 12 mm along X. The example uses the same instruction twice, once at −12 and once at +12, to place two posts on either side of the origin.',
    'Translation changes location, not dimensions. The instruction acts on its following child, so a semicolon immediately after translate() would leave it with no child to move. Braces let one translation move several shapes together.'),
  rotate:lesson(
    'rotate() turns a shape. A full turn is 360 degrees and a quarter turn is 90. The three-number form gives the turns around the X, Y and Z axes.',
    'Cylinders normally stand upright along Z. In the example, rotate([0,90,0]) tips the cutting cylinder sideways so it drills through the block from left to right.',
    'The pivot is the origin. A centred cutter can turn without shifting its centre, which is useful for symmetric bores. When a rotation is outside a translation, it rotates the moved position as well, making an orbit around the origin.'),
  scale:lesson(
    'scale() stretches a shape by a multiplier. A factor of 2 doubles a size; 0.5 halves it; 1 keeps it unchanged. Three factors let width, depth and height change independently.',
    'The example stretches a round disk only along X. Its circular top becomes an ellipse, or oval. This changes every feature along that axis, including holes if the shape already has them.',
    'Positions are multiplied relative to the origin as well as dimensions. Scale a local, centred shape before placing it when you want only the part itself to stretch. A zero factor collapses volume and does not make a usable solid.'),
  resize:lesson(
    'resize() asks for a finished outside size instead of a multiplier. It measures the shape’s bounding box: the smallest box aligned with X, Y and Z that encloses it.',
    'The example makes a small ball 30 mm wide. Zeros leave the other sizes unspecified, and auto=true scales those directions in proportion so the ball keeps its shape.',
    'Unlike changing a design parameter, resizing stretches all existing details. A wall and a hole become larger too. It is useful for imported objects of unknown scale, but changing the original parameters is preferable when some dimensions must stay fixed.'),
  mirror:lesson(
    'mirror() makes a reflected version, like a shape seen in a mirror. It replaces the child with its reflection; it does not automatically keep the original as well.',
    'The example keeps an original tab and adds a reflected tab using union(). The vector [1,0,0] means reflect across the plane where X=0, swapping positive and negative X.',
    'The vector is perpendicular to the mirror plane. Its length is unimportant; its direction selects the plane. To reflect around a different location, move that location to the origin, reflect, then move the result back.'),
  multmatrix:lesson(
    'A matrix is a table of numbers describing how coordinates change. You can usually use move, rotate and scale first; multmatrix() is useful when you need a custom change such as leaning a block sideways without rotating its top.',
    'The example is a shear. Each point moves farther along X the higher it is, so the bottom stays put while the top shifts. The block becomes slanted while its top and bottom remain parallel.',
    'Read each row as a formula. The first row [1,0,0.4,0] gives new X = old X + 0.4 × old Z. With a 20 mm height, the top shifts 8 mm. The other rows keep Y and Z unchanged; the final row supplies the standard affine coordinate convention.'),
  color:lesson(
    'Colour changes appearance, not the shape of material. A red cube is still the same solid cube. Transparency also does not create a hole: use a cutting operation for that.',
    'Code studio receives the finished geometry through STL, a shape-only format. The example’s colour instruction is accepted, but the preview uses the studio’s material. Choose the object colour in the workshop after adding it.',
    'The punctuation modifiers are debugging controls inherited from desktop OpenSCAD. In particular, % marks background geometry that is excluded from the final solid, and * disables a shape. Use them carefully when comparing a desktop preview to this rendered result.'),
  offset:lesson(
    'offset() moves a flat outline’s boundary inward or outward. Think of drawing a new outline a fixed distance from the old one. A positive distance grows it; a negative distance shrinks it.',
    'The example grows two rectangles with rounded corners, subtracts the smaller outline from the larger, then extrudes the remaining frame. It starts from flat areas rather than trying to round an existing 3D object.',
    'The r form makes rounded joins; delta preserves straight-edge intersections or optionally bevels them. An outward offset also shrinks existing holes, so narrow gaps may close. Check the whole result rather than just its outside dimensions.'),
  resolution:lesson(
    'A computer model draws curved surfaces using lots of small flat faces. More faces look smoother, but take longer to calculate. Resolution is the choice of how many pieces approximate a curve.',
    'The example puts three posts side by side with 6, 16 and 48 sides. They have the same nominal radius, but the first is visibly hexagonal. $fn is a setting name; the dollar sign is part of it.',
    'Use modest resolution while designing, then increase it where the final shape benefits. A high global $fn affects every curved primitive unless overridden locally. It can multiply the work in booleans, spheres and Minkowski sums; convexity does not control this mesh resolution.'),
  variables:lesson(
    'A variable gives a value a useful name, like width=32. Use that name wherever the same measurement belongs so one edit updates the design consistently.',
    'In the example, depth is calculated from width. Changing width therefore changes both the width and depth of the box, while height stays 5. Text in quotes is a string; true/false are yes/no values; numbers do not need quotes.',
    'Treat these names as descriptions of values, not storage boxes repeatedly changed over time. OpenSCAD evaluates a declarative model. Use distinct names for intermediate calculations and module parameters for reusable parts instead of writing imperative update steps.'),
  operators:lesson(
    'Operators are the symbols used in calculations and questions: + adds, * multiplies, > asks whether one value is larger, and == asks whether two values are equal.',
    'The expression wide ? 32 : 18 means “if wide is true, use 32; otherwise use 18”. The example uses that choice for a box width. && means both conditions must be true; || means either one can be true.',
    'A single = assigns a name; == compares values. Brackets form lists, and parentheses control calculation order. Numeric vectors have mathematical multiplication rules, so v*v is a dot product rather than a list of squared components.'),
  lists:lesson(
    'A list keeps related values together inside square brackets. [8,12,18] could be three post heights; [20,10,5] could be a single box’s dimensions. Its meaning depends on where you use it.',
    'Positions in a list start at zero: heights[0] is the first height. A range such as [0:2] supplies 0, 1 and 2. The example uses those positions to choose a height and move each post to a different location.',
    'len(heights)-1 is the final valid index. This lets a loop adapt when you add another height. Keep the distinction between a list of coordinates and a list of points: polygon needs a list whose elements are themselves [x,y] lists.'),
  for:lesson(
    'A for loop repeats a modelling instruction for each value in a list or range. It saves you from copying nearly identical code for every hole or post.',
    'The example counts from 0 to 5 to create six cutters. Each cutter is moved away from the centre and rotated by a different multiple of 60 degrees, placing the holes evenly around a disk.',
    'The loop variable i belongs to one iteration at a time. Use i*360/count for even angular spacing and stop at count−1 so the last item does not duplicate the first at 360 degrees. A loop inside difference can supply all the cutting tools.'),
  if:lesson(
    'if asks a yes/no question and includes a shape only when the answer is true. else supplies the alternative. This is useful for optional holes, feet and different versions of a part.',
    'In the example, hole=true includes the round cutting tool. Changing it to false removes the cutter, so the block is solid. The condition controls geometry, not just its visibility.',
    'Use if/else for shape-producing statements and the ? : expression when you need to choose a numeric value. Add braces around branches containing several statements so it is clear which branch owns them.'),
  let:lesson(
    'let() gives temporary names to calculations used by the next instruction. It is like jotting a subtotal beside one step of a recipe without changing the main ingredient list.',
    'The example calculates a different height h and radius r for each post. Those short names are meaningful only within that iteration’s let block, which keeps the outer script tidy.',
    'Bindings are evaluated in order, so a later binding can use an earlier one. They do not change an outer variable of the same name. Use this for readable formulas in loops, functions and list comprehensions.'),
  modules:lesson(
    'A module is a named recipe for geometry. Define it once, then call its name to create a part. Parameters are the measurements callers are allowed to change.',
    'The example defines post with default height, radius and wall thickness. Writing post(h=18); creates a taller version while keeping the other defaults. Merely defining the module creates no visible object.',
    'Decide where the part’s origin should be and keep that convention consistent. This post starts at Z=0, making it easy to place on a base. Modules emit geometry; use functions for calculations that return a number or point.'),
  children:lesson(
    'A wrapper module is a recipe that accepts another shape as its input. children() means “put the caller’s supplied shape here”. This lets one repeater work with posts, boxes or any other child.',
    'In the example, radial() receives a cylinder and places copies around a circle. Change the supplied cylinder to a cube and the same wrapper repeats cubes instead.',
    '$children counts supplied statements, not final pieces of mesh. children(0) selects the first statement, while children() includes all. assert checks that the wrapper received something to repeat before it tries to build the pattern.'),
  functions:lesson(
    'A function is a named calculation. Give it input values and it returns a value, such as a length or a point. A module makes shapes; a function supplies the numbers or lists those shapes need.',
    'The example’s radial_point calculates a point at an angle and radius. A list alternates large and small radii, producing a star outline. polygon draws that outline and extrusion makes it solid.',
    'The function returns a single expression. let can name intermediate results, and ? : can choose between results. Recursive functions call themselves and must have a stopping condition; a comprehension is usually clearer for a simple sequence of points.'),
  comprehensions:lesson(
    'A list comprehension is a compact way to build a list using a repeated calculation. It makes data, such as corner coordinates, rather than directly making objects.',
    'The example first lists angles, leaving two out, then calculates a point at each remaining angle. polygon connects those points and extrusion creates the part. The omitted points change the outline’s edges.',
    'Read [for(a=angles) expression] as “collect one result of expression for each a”. if filters which results are collected; each inserts items from another list instead of nesting that list as one item. Keep point lists nested when a geometry module expects coordinate pairs.'),
  math:lesson(
    'These helpers answer everyday size questions. abs removes a minus sign, sign tells you the direction of a signed number, min chooses the smallest value and max chooses the largest.',
    'The example limits a requested wall thickness to between 1 and 4 mm. min(4,requested) caps it at 4; max(1,...) prevents it from falling below 1. This is called clamping.',
    'Clamping changes the requested value silently, which can be helpful for experiments. Use assert instead when silently changing a dimension would be misleading. abs(a-b) measures the difference between two dimensions regardless of which is larger.'),
  trig:lesson(
    'Trigonometry connects angles to lengths. sin and cos turn an angle into coordinates on a circle; tan turns an angle into the slope of a straight ramp.',
    'The example gives a wedge a length of 30 and an angle of 25 degrees. Its end height is length*tan(angle). You can use this without memorising the formula: a steeper angle should make the wedge taller.',
    'OpenSCAD uses degrees, so a quarter turn is 90, not PI/2. asin, acos and atan work backwards from ratios to angles. They have limits: asin and acos need values between −1 and 1, and tan approaches an unusably large value near a vertical 90-degree slope.'),
  atan2:lesson(
    'atan2 finds the direction in which a point lies. Give it the Y distance first and the X distance second; it returns an angle in degrees.',
    'The example points a bar from the origin towards [20,12]. norm measures how long that direction vector is, while atan2 supplies the turn needed to aim along it.',
    'Using atan(y/x) alone loses information about which side of the origin the point lies on and fails for x=0. atan2 preserves the quadrant. A vector [0,0] has no meaningful direction, so validate it before using it for placement.'),
  rounding:lesson(
    'floor rounds down, ceil rounds up and round chooses the nearest whole number. Use them when a calculation must give a count of complete items rather than part of an item.',
    'The example divides a 45 mm span by a 12 mm spacing. The result is 3.75; floor chooses three complete repeats. max(1,...) ensures at least one post.',
    'Rounding down is toward negative infinity: floor(−1.2) is −2, not −1. To snap a dimension to a chosen step, divide by the step, round, then multiply by the step. Counts and physical lengths need separate checks.'),
  powers:lesson(
    'pow(x,y) raises a number to a power, and sqrt takes a square root. They are useful when a length comes from geometry rather than a measurement you type directly.',
    'The example finds the diagonal across a 20 by 12 rectangle using sqrt(20²+12²), then aims a brace along that diagonal. exp, ln and log describe exponential growth and its inverse rather than ordinary straight-line changes.',
    'sqrt needs a nonnegative input; logarithms need positive inputs. exp uses the mathematical base e, ln reverses exp, and log uses base 10. Reject invalid input before it becomes a dimension, because an unusable result may cause an error far from the original calculation.'),
  'norm-cross':lesson(
    'A vector is a list describing a direction and distance. norm tells you its length. cross finds a direction perpendicular to two 3D vectors, like the direction sticking out of a tabletop defined by two edges.',
    'In the example, crossing X and Z gives the negative Y direction. That computed direction is used as a rotation axis. Turning the cylinder around this sideways axis makes it visibly lean.',
    'The order of cross matters: reversing its inputs reverses its direction. Parallel inputs give a zero vector and cannot define a useful perpendicular axis. To make a vector length 1, divide it by norm(v), after checking that the length is not zero.'),
  rands:lesson(
    'rands() produces a list of randomly chosen numbers within a range. These can control heights or positions to create an irregular pattern.',
    'The example creates five post heights between 6 and 18. The final number, 123, is a seed: keeping it fixed makes the same sequence repeat each time you preview.',
    'Save the generated list in a variable, then index it for each part. A fixed seed makes a design reproducible within the engine, while an unseeded call can change on rebuild. Bounds on height do not guarantee spacing or structural strength; those are separate design constraints.'),
  concat:lesson(
    'len tells you how many items a list contains. concat joins lists end to end. Neither creates a shape by itself; they help organise the information used to build one.',
    'The example stores an outline in two point lists and joins them before passing the combined list to polygon(). The order is preserved, so the boundary continues from the last point of the first list to the first point of the second.',
    'concat flattens only the supplied top level: the coordinate pairs remain pairs. Numeric list addition has a different meaning, adding corresponding components. Use str to join words and numbers into text rather than concat.'),
  lookup:lesson(
    'lookup reads a small table of measured points and estimates a value between them. It draws straight-line changes from one table row to the next, like joining dots on a graph.',
    'The example’s table gives radius at different heights. At height 0 the radius is 8, at 10 it is 12 and at 20 it is 6. Intermediate heights get intermediate radii, forming the side outline of a turned part.',
    'Each row is [key,value]. The key here is height; the returned value is radius. This is linear interpolation, not a smooth curved spline. Keep keys unique and ordered; beyond the table ends, the endpoint value is used instead of extending the slope.'),
  search:lesson(
    'search finds where a value appears in a list. It returns positions, not the values themselves. The first position is 0, the second is 1, and so on.',
    'The example finds 10 in [6,10,14], gets position 1, then reads that entry as a diameter for a cylinder. A result list is used because a search can find more than one match.',
    'Inspect search results with echo before indexing unfamiliar tables. Multiple queries and all-match searches can return nested lists. A missing match needs its own handling; blindly taking [0] may produce undef rather than a usable dimension.'),
  str:lesson(
    'A string is text inside quotation marks. str joins text and numbers into one string, which is useful for labels that follow your design parameters.',
    'The example joins "M" and the number 6 to make "M6", then draws and extrudes that label. chr turns character codes into text; ord reads the code of the first character in text.',
    'Numbers and text are different types: 6 is numeric, while "6" is a character. str converts values to printable text. Character codes identify symbols, but the selected font must also contain those symbols before they can produce visible letter geometry.'),
  types:lesson(
    'A type describes what a value is: a number, text, a yes/no value, a list or something else. Type tests ask which kind of value you received and return true or false.',
    'The example accepts an optional width. undef means no width was supplied, so it chooses 20. It then checks that the chosen value is a positive number before making a block.',
    'Type and validity are separate questions. is_list does not prove a list contains three numeric coordinates, and is_num does not prove a useful positive dimension. Combine type tests with length and range checks in reusable modules.'),
  textmetrics:lesson(
    'Two words written at the same font size can have different widths. textmetrics measures the actual lettering so you can make a plate fit the words automatically.',
    'The returned value is an object with named measurements. m.size gives width and height; m.position tells you where the lettering’s lower bounding corner lies. The example adds 2 mm of padding on all four sides.',
    'Measure with exactly the same font, size and alignment used to draw. Visible bounds differ from advance, which is the distance to the next text cursor position. fontmetrics describes the font as a whole, while textmetrics describes this particular string.'),
  assert:lesson(
    'assert is a check that stops an impossible design with an explanation. It is like checking that the walls will fit before trying to build the box.',
    'The example checks that wall thickness is greater than zero and less than half the outside width. If the condition is false, the message explains the problem instead of producing a confusing shape.',
    'Use assertions for relationships as well as individual ranges: a bolt circle must leave room for its holes, and an inner cavity must leave a base. Put checks near the parameters that cause them. A successful assertion only proves the condition you wrote, not every aspect of printability.'),
  diagnostics:lesson(
    'Diagnostics are messages from the builder. echo prints values so you can see what your calculations produced. It is a note in the output, not lettering on your model.',
    'The example prints the radius and diameter before making a cylinder. When a model fails, start with the first relevant error, check its file and line, then inspect nearby values or missing files.',
    'Separate syntax problems from geometric problems: a missing bracket prevents reading the recipe, whereas a cutter removing everything leaves no solid after a valid calculation. render requests geometry evaluation but is not a mesh repair tool.'),
  'include-use':lesson(
    'A library is another .scad file containing reusable recipes. use loads its modules and functions so you can call them. include reads the whole file, including top-level values and any shapes it creates.',
    'The filename goes inside angle brackets, such as use <parts/post.scad>. The slash means the helper lives in a subfolder. Supply the helper with the project; a filename in the code does not download it automatically.',
    'Prefer use for a geometry library whose demonstrations should not appear in your model. Use include when you need shared constants at the calling scope. Keep relative paths stable and avoid importing different libraries that define the same name with different meanings.'),
  import:lesson(
    'import() brings in an existing drawing or mesh. An SVG drawing is flat; an STL mesh is a 3D surface. The file must be supplied alongside the script.',
    'The example includes an SVG rectangle with a rectangular opening. import reads the flat area, and linear_extrude makes it a 4 mm thick plate with a hole. Open Included example files to see the small drawing file.',
    'The dimensions and units come from the asset and its format. Inspect the preview bounds before trusting scale. A mesh intended for solid work must close around a volume; importing an open surface does not automatically fill its gaps.'),
  surface:lesson(
    'A height map is a grid of numbers or image brightnesses used as elevations. Think of a table of hill heights: one value per position on the ground.',
    'The example supplies a small text grid. Larger numbers become higher points, and surface joins the samples into terrain with sides and a base. scale spreads the grid out and adjusts its vertical height.',
    'The DAT file is data, not OpenSCAD code: each row contains heights separated by spaces. Grid sample spacing and height scale are independent. Start with a small grid because doubling both image dimensions produces roughly four times as many samples.'),
  version:lesson(
    'The engine version tells you which OpenSCAD build is running. This matters when a script uses a feature introduced after someone else’s desktop installation.',
    'The example prints the version and makes a simple block so there is still a visible object. version returns a list of version components; version_num gives a number convenient for comparisons.',
    'Use a version check to explain requirements or select an explicitly tested alternative. It cannot switch on disabled experimental features. Test the required operation as well as comparing a release number.'),
  special:lesson(
    'Some names beginning with $ are special OpenSCAD settings. A few control geometry, while others belong to the desktop application’s camera or animation system.',
    'Code studio’s camera is controlled by dragging its preview, not by $vpr or $vpt. The example uses an ordinary pose parameter to choose a fixed angle that reliably changes the model.',
    '$preview is false during this rendered-solid calculation. Code that creates shapes only in a $preview branch may therefore produce nothing here. Use ordinary model parameters for stored poses and reserve $fn, $fa and $fs for supported tessellation settings.'),
  experimental:lesson(
    'Some function names seen online belong to experimental builds or old versions. A familiar-looking name is not proof that it is available in the bundled engine.',
    'The reference lists these names so you can recognise them and find a supported route. The runnable example makes a simple roof from a triangular outline and extrusion without requiring the experimental roof operation.',
    'A library can define extra modules of its own, while an engine extension must be enabled in the engine itself. Unknown-name messages need that distinction: supply a missing library when appropriate, or replace an unavailable extension with supported construction steps.'),
  limits:lesson(
    'The workshop needs a real 3D volume, like a closed container full of material. A flat drawing or an open skin is not yet a solid that can be joined, cut or exported reliably.',
    'A browser also has a limited amount of time and memory. If a complicated model fails, try a simpler version with fewer repeated parts and lower curve detail before increasing those settings again.',
    'A successful render proves the engine produced transferable geometry within the current limits; it does not prove manufacturing fit or strength. Keep enough wall thickness, verify units and supply all external dependencies. The limits below explain where this browser workflow differs from desktop OpenSCAD.'),
  'recipe-flange':lesson(
    'A flange is a plate around an opening, often used to bolt one component to another. This recipe makes a round plate with a central bore and evenly spaced bolt holes.',
    'Start by choosing the outside size and thickness, then the large centre opening, then the small hole positions. pitch here means the radius of the circle passing through the hole centres, not the spacing between neighbouring holes.',
    'The assertion keeps each bolt hole away from the outer edge and central bore. A loop supplies the evenly spaced cutters. Changing holes adjusts the angular spacing automatically, but you still need to check that neighbouring holes leave enough material.'),
  'recipe-box':lesson(
    'An open box can be made by taking a solid block and removing a smaller block from inside it. Lift the inner cutter so some material remains as a floor.',
    'The example uses one wall value for both side thickness and floor thickness. The cavity starts wall millimetres from each side and wall millimetres above the bottom, then extends through the open top.',
    'The cavity width and depth each lose two wall thicknesses, one at either side. Its starting height, rather than its total cutter height, sets the floor. For a separate lid, introduce a clearance allowance instead of making the lid exactly equal to the opening.'),
  'recipe-pocket':lesson(
    'A pocket is a recess that stops inside a part. A boss is a raised feature. A through-hole passes all the way through. This example combines all three on a single plate.',
    'First join the base and boss into the material to keep. Next subtract a shallow rectangular cutter and a long round cutter. Keeping those stages visibly separate makes the recipe easier to change.',
    'The base top is Z=6 and the pocket starts at Z=3, leaving a 3 mm floor. The boss starts at Z=5.9 so it overlaps the plate; its bore begins below the plate and ends above the boss. Each coordinate follows a physical feature, not an arbitrary offset.'),
  'recipe-rounded':lesson(
    'Rounding can mean two different things: softening the outline when viewed from above, or rounding every edge of the 3D part. Choose which result you need before choosing the tool.',
    'This recipe rounds every edge by growing a smaller centred block with a small ball. Two cylindrical cutters then make mounting holes that stay the chosen diameter.',
    'A radius-2 ball adds 4 mm to each total dimension. The starting 36 × 20 × 4 block therefore becomes approximately 40 × 24 × 8. Cut the holes after growth; otherwise their geometry would be affected by the rounding operation too.'),
  'recipe-bowl':lesson(
    'To make a cup, draw the material in one vertical slice through its wall and floor, then spin that filled slice around the centre line.',
    'Each point is [radius,height]. Follow the example from the bottom centre to the bottom outside edge, up the outside, across the rim, down the inside and back to the centre above the floor.',
    'The outer radius is 18 and the inner radius is 15, giving a 3 mm vertical wall. The inner floor begins at height 3, giving a 3 mm base. These independent measurements are clearer than trying to subtract two almost matching revolved solids.'),
  'recipe-label':lesson(
    'Raised lettering adds material; engraving removes material. Both start with the same flat text outlines, given thickness by extrusion.',
    'The runnable example engraves PART 1 into a plate. Its text cutter starts inside the top surface and extends above it, so the letters leave shallow recesses rather than passing all the way through.',
    'The centred plate is 4 mm thick, so its top is Z=2. Starting the cutter at Z=0.8 creates 1.2 mm deep lettering. The linked textmetrics example shows how to size a supporting plate automatically when the words change.'),
  mcad:lesson(
    'MCAD is a toolbox of ready-made part recipes bundled with Code studio. Instead of constructing every nut recess or rounded box yourself, load the relevant file and call its module.',
    'A library module looks like a built-in instruction when you use it, but it only exists after the correct file is loaded. The examples show the exact use line needed for a rounded box and a nut cutter.',
    'Read signatures in declaration order: roundedCube takes dimensions, radius, a sides-only option and a centring option. The older roundedBox name is retained for compatibility. nutHole uses a nominal fastener size rather than a direct polygon radius. Library conventions can differ, so check the original comments and inspect the result before using it as a manufacturing dimension.'),
};
