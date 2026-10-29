/** Complete runnable lessons: comments travel with copied code. */
export interface WikiExampleLesson {code:string;result:string;experiment:string}
const example=(result:string,experiment:string,code:string):WikiExampleLesson=>({result,experiment,code:code.trim()});
export const WIKI_EXAMPLES:Record<string,WikiExampleLesson>={
  'Fill a ring to make a backing disk':example('A solid disk 24 mm across and 3 mm thick; the intermediate ring’s hole is filled.','Remove fill() to keep the hole and make a washer instead.',`
// Read from the circles outward: ring, fill, then thickness.
linear_extrude(3) // Give the finished flat area 3 mm of height.
  fill()         // Close the ring's enclosed hole.
    difference() {
      circle(12, $fn=48); // Outer radius: 12 mm.
      circle(5, $fn=32);  // Remove a radius-5 opening first.
    }`),
  'Your first drilled block':example('A 30 × 20 × 8 mm block with an 8 mm diameter hole through its centre.','Change the cutter radius r=4 to r=6; the hole becomes 12 mm across.',`
// Keep the first shape; subtract every later shape.
difference() {
  cube([30,20,8]); // Stock: width, depth, height in millimetres.
  // Centre the drill in X/Y; start 1 mm below the stock.
  translate([15,10,-1])
    cylinder(h=10, r=4, $fn=48); // Pass through both faces.
}`),
  'A project with a helper':example('One upright post, 12 mm tall and 8 mm across, created by the supplied helper file.','Change post(12) to post(20); only the height changes. When copying, also supply parts/post.scad from Included example files.',`
// Load the reusable module from the included helper file.
use <parts/post.scad>
// Call that module with a height of 12 mm.
post(12);`),
  'A boss with overlap':example('A rectangular base and a central round boss joined into one solid.','Change the boss height from 8.1 to 12.1; its top rises 4 mm while the join stays overlapped.',`
union() { // Combine all overlapping material.
  cube([30,20,5]); // Base runs from Z=0 to Z=5.
  // Start just inside the base so the join shares material.
  translate([15,10,4.9])
    cylinder(h=8.1, r=5, $fn=40); // Top ends at Z=13.
}`),
  'A centred rectangular block':example('A 30 × 18 × 6 mm block with its centre at [0,0,0].','Set center=false; the same-sized block starts at the origin instead of straddling it.',`
// Dimensions follow X, Y, Z: width, depth, height.
// Centre it so half of each dimension lies on either side of zero.
cube([30,18,6], center=true);`),
  'An ellipsoid':example('An oval solid approximately 30 mm wide, 20 mm deep and 14 mm tall.','Change the last scale factor from 0.7 to 1; the oval becomes taller.',`
// Stretch X by 1.5 and compress Z to 70%; leave Y unchanged.
scale([1.5,1,0.7])
  sphere(r=10, $fn=48); // Start from a ball 20 mm across.`),
  'A tapered hollow sleeve':example('A 20 mm tall tapered sleeve with a straight 10 mm diameter bore.','Change the top radius r2=8 to r2=12; the outer wall becomes a straight cylinder.',`
difference() {
  // Outside tapers from radius 12 at the bottom to 8 at the top.
  cylinder(h=20, r1=12, r2=8, $fn=48);
  // A longer cutter ensures the bore opens at both ends.
  translate([0,0,-1]) cylinder(h=22, r=5, $fn=48);
}`),
  'A square-based pyramid':example('A pyramid with a 20 × 20 mm base and an 18 mm high tip.','Change the tip [10,10,18] to [10,10,28]; the same base supports a taller pyramid.',`
polyhedron(
  // Points 0..3 are base corners; point 4 is the tip.
  points=[[0,0,0], [20,0,0], [20,20,0], [0,20,0], [10,10,18]],
  // One base and four sides. Each number refers to a point above.
  // Order runs clockwise when each face is viewed from outside.
  faces=[[0,1,2,3], [0,4,1], [1,4,2], [2,4,3], [3,4,0]]
);`),
  'A rectangular plate':example('A centred rectangular outline lifted into a 30 × 18 × 4 mm plate.','Change height=4 to height=8; the footprint stays the same and thickness doubles.',`
// Turn the flat child area into a 4 mm thick solid.
linear_extrude(height=4)
  square([30,18], center=true); // Flat width and depth in XY.`),
  'A hexagonal spacer':example('A 6 mm thick hexagonal spacer with a round 8 mm diameter centre hole.','Change the outer $fn=6 to $fn=8; the outside becomes octagonal while the bore remains round.',`
linear_extrude(height=6) // Lift the complete outline, including its hole.
  difference() {
    circle(r=10, $fn=6); // Six sides deliberately make a hexagon.
    circle(r=4, $fn=40); // Remove a smoother round opening.
  }`),
  'An extruded pentagonal profile':example('A regular five-sided plate, 5 mm thick.','Change the extrusion height from 5 to 10; the same pentagon becomes a taller prism.',`
// Five corners, 72 degrees apart, each 12 mm from the centre.
pts=[for(i=[0:4]) [12*cos(i*72), 12*sin(i*72)]];
linear_extrude(5) // Give the outline thickness.
  polygon(pts);   // Join the corners and close the last edge.`),
  'Raised label':example('A plate with attached raised BOX lettering.','Replace "BOX" with "LID"; the lettering changes while the plate keeps its size.',`
union() {
  cube([36,18,3], center=true); // Plate top is at Z=1.5.
  // Begin at 1.4 so the letters overlap the plate by 0.1 mm.
  translate([0,0,1.4]) linear_extrude(1.6)
    text("BOX", size=8, font="Noto Sans",
         halign="center", valign="center"); // Anchor to the plate centre.
}`),
  'Extrude a sliced sphere outline':example('A 3 mm thick disk from a sphere’s off-centre slice; its ideal diameter is 16 mm.','Change the sphere offset from −6 to 0; the central slice gives a wider, 20 mm disk.',`
linear_extrude(3) // Rebuild the flat slice as a short solid.
  projection(cut=true) // Keep only the section at Z=0.
    translate([0,0,-6]) // Move the ball down to select the slice.
      sphere(10, $fn=40);`),
  'Twisted, tapered column':example('A 30 mm tall column whose rectangular top is smaller and turned 90 degrees.','Set twist=0; the tapered column loses its spiral sides.',`
// Turn and shrink the profile progressively from bottom to top.
linear_extrude(height=30, twist=90, scale=0.65, slices=36)
  square([12,8], center=true); // Centring keeps the twist around its middle.`),
  'A hollow bowl':example('A flared bowl, 50 mm across at the rim and 24 mm tall, with a closed floor.','Change angle=360 to angle=270; the missing quarter exposes the wall cross-section.',`
// Spin the material cross-section once around the vertical axis.
rotate_extrude(angle=360, start=0, $fn=64)
  polygon([
    [0,0],   // Bottom centre, on the axis.
    [12,0],  // Outside edge of the base.
    [25,24], // Outside rim.
    [22,24], // Inside rim: cross the wall thickness.
    [10,3],  // Inside wall meets the floor.
    [0,3]    // Floor centre; the closing edge completes the base.
  ]);`),
  'A torus':example('A doughnut-shaped ring with a 6 mm thick circular tube and an approximately 26 mm central opening.','Change translate([16,0]) to translate([22,0]); the ring grows wider while tube thickness stays the same.',`
rotate_extrude(angle=360, start=0, $fn=64) // Sweep a full ring.
  translate([16,0]) // Hold the tube section away from the axis.
    circle(3, $fn=24); // Radius 3 gives a 6 mm thick tube.`),
  'A fused base and boss':example('A centred base with a cylindrical boss fused to its top.','Increase r=6 to r=8; the boss widens without changing the base.',`
union() { // Both children contribute material.
  cube([30,20,5], center=true); // Top at Z=2.5.
  // Overlap the base by 0.1 mm for a dependable join.
  translate([0,0,2.4]) cylinder(h=8, r=6, $fn=40);
}`),
  'A slot and a round bore':example('A plate with one round through-hole and one rectangular through-slot.','Change the slot’s width from 12 to 8; the rectangular opening narrows along X.',`
difference() {
  cube([40,24,8]); // First child is the material to keep.
  // Both cutters extend from Z=-1 to Z=9, beyond the plate.
  translate([8,12,-1]) cylinder(h=10, r=4, $fn=40);
  translate([22,8,-1]) cube([12,8,10]); // Rectangular slot cutter.
}`),
  'A rounded cube':example('A cube clipped by a sphere, with flat face centres and curved edges/corners.','Increase the sphere radius from 12 to 14; more of the cube survives and the clipped regions shrink.',`
// Keep only the material inside BOTH centred shapes.
intersection() {
  cube([18,18,18], center=true); // Supplies the flat faces.
  sphere(12, $fn=40); // Limits the edges and corners.
}`),
  'Intersect rotated bars':example('A compact polygonal block: only the common middle of three rotated bars survives.','Replace intersection_for with for; you get the combined overlapping bars instead of only their shared centre.',`
// Intersect each iteration, rather than joining the bars.
intersection_for(a=[0,60,120])
  rotate([0,0,a]) // Turn each bar around the same centre.
    cube([30,16,8], center=true);`),
  'A capsule plate':example('A 5 mm thick capsule-shaped plate with semicircular ends.','Move the circles from ±12 to ±18; the straight middle becomes longer while the end radius stays 6.',`
linear_extrude(5) // Give the flat capsule thickness.
  hull() { // Stretch a convex outline between the two disks.
    translate([-12,0]) circle(6, $fn=32); // Left end.
    translate([12,0]) circle(6, $fn=32);  // Right end.
  }`),
  'Rounded stock':example('A block with all edges rounded, approximately 30 × 20 × 10 mm overall.','Change the sphere radius from 2 to 1; rounding becomes smaller and overall dimensions shrink by 2 mm on each axis.',`
minkowski() {
  cube([26,16,6], center=true); // Smaller starting stock.
  // Grow by 2 mm in every direction, rounding all edges.
  sphere(2, $fn=32); // Moderate detail keeps calculation manageable.
}`),
  'Two spaced posts':example('Two separate 12 mm tall posts whose centres are 24 mm apart.','Change the list to [-18,18]; the centre spacing becomes 36 mm.',`
for(x=[-12,12]) // Repeat at the two specified X positions.
  translate([x,0,0]) // Move this iteration's post.
    cylinder(h=12, r=4, $fn=32);`),
  'A horizontal through-bore':example('A centred block with a round hole running along X rather than vertically.','Change rotate([0,90,0]) to rotate([90,0,0]); the bore runs along Y instead.',`
difference() {
  cube([22,18,18], center=true); // Stock centred on the pivot.
  rotate([0,90,0]) // Tip the Z-aligned cutter onto X.
    cylinder(h=24, r=5, center=true, $fn=40); // Longer than the stock.
}`),
  'An elliptical puck':example('An oval puck approximately 32 × 20 mm across and 6 mm thick.','Change the X factor from 1.6 to 1; the puck becomes circular.',`
// Stretch only X; retain the original Y size and Z height.
scale([1.6,1,1])
  cylinder(h=6, r=10, $fn=48); // Start with a round disk.`),
  'Set a ball’s width proportionally':example('A ball resized to 30 mm along X while retaining its proportions.','Change [30,0,0] to [40,0,0]; all dimensions grow together.',`
// Set X to 30; let the zero-valued axes follow proportionally.
resize([30,0,0], auto=true)
  sphere(5, $fn=32); // The original radius need not be calculated manually.`),
  'Paired mirrored tabs':example('Two separate rectangular tabs mirrored across X=0, with a 6 mm gap between them.','Change the tab offset from 3 to 5; the gap increases to 10 mm.',`
module tab() {
  // Leave space between this tab and the mirror plane.
  translate([3,0,0]) cube([12,8,4]);
}
union() {
  tab(); // Keep an original copy.
  mirror([1,0,0]) tab(); // Add the copy reflected across X=0.
}`),
  'Shear a block':example('A slanted block whose top is shifted 8 mm along X relative to its bottom.','Change 0.4 to 0.2 in the first row; the top shift becomes 4 mm.',`
multmatrix([
  [1,0,0.4,0], // New X = X + 0.4*Z: higher points lean farther.
  [0,1,0,0],   // Keep Y unchanged.
  [0,0,1,0],   // Keep Z unchanged.
  [0,0,0,1]    // Standard last row for an affine transform.
]) cube([15,12,20]); // Top at Z=20, so its X shift is 8.`),
  'Colour does not change the solid':example('A 20 × 12 × 6 mm block shown in the studio’s material, even though the script asks for red.','Change "red" to "blue"; geometry and studio preview colour remain unchanged because STL carries no colour.',`
// Accepted OpenSCAD colour metadata is not retained in STL transfer.
color("red")
  cube([20,12,6]); // Set the applied object's colour in the workshop.`),
  'A rounded frame':example('A 5 mm thick rectangular frame with rounded outer and inner corners.','Change the extrusion from 5 to 8; the outline stays unchanged and the frame gets taller.',`
linear_extrude(5) // Lift the remaining flat frame.
  difference() {
    // Grow a rectangle outward with radius-3 corner arcs.
    offset(r=3) square([24,14], center=true);
    // Remove a smaller rounded area to leave a wall.
    offset(r=1) square([22,12], center=true);
  }`),
  'Same radius, different profiles':example('Three separate posts, from visibly hexagonal to progressively smoother.','Change the middle segment count from 16 to 8; its flat sides become easier to see.',`
for(i=[0:2]) // Three copies, with indices 0, 1 and 2.
  translate([i*24,0,0]) // Space the copies so they can be compared.
    // Use the matching entry in the resolution list for this copy.
    cylinder(h=6, r=9, $fn=[6,16,48][i]);`),
  'A parameter-driven block':example('A block 32 mm wide, 19.2 mm deep and 5 mm high.','Change width to 40; depth follows automatically to 24 while height remains 5.',`
width=32;        // Main measurement to edit.
depth=width*0.6; // Keep depth at 60% of the width.
height=5;        // Independent thickness.
cube([width,depth,height]); // Build from the named dimensions.`),
  'Choose a size with a condition':example('A 32 × 16 × 4 mm block selected by a yes/no parameter.','Set wide=false; the block becomes 18 × 9 × 4 mm.',`
wide=true;          // A yes/no choice, without quotation marks.
w=wide ? 32 : 18;  // Choose a width according to that choice.
assert(w>0 && w<100); // Both comparisons must be true.
cube([w,w/2,4]);    // Depth follows half the chosen width.`),
  'Posts with different heights':example('Three separate posts, 8, 12 and 18 mm tall.','Add 24 to the heights list; the loop automatically creates a fourth, taller post.',`
heights=[8,12,18]; // One height per post.
// The last valid index is one less than the number of entries.
for(i=[0:len(heights)-1])
  translate([i*14,0,0]) // Keep neighbouring posts separate.
    cylinder(h=heights[i], r=4, $fn=24); // Read this entry's height.`),
  'A six-hole bolt circle':example('A disk with six 5 mm diameter through-holes arranged evenly around its centre.','Change the cutter radius from 2.5 to 3; every hole becomes 6 mm across.',`
difference() {
  cylinder(h=6, r=24, $fn=64); // The plate to keep.
  for(i=[0:5]) // Six positions; do not duplicate 360 degrees.
    rotate([0,0,i*60]) // Swing the moved cutter around the origin.
      translate([17,0,-1]) // Radius of the bolt circle; below the base.
        cylinder(h=8, r=2.5, $fn=24); // Extend above the plate too.
}`),
  'Optional centre hole':example('A centred 24 mm square plate with a circular through-hole.','Set hole=false; the cutting cylinder is omitted and the plate becomes solid.',`
hole=true; // Include or omit the cutting feature.
difference() {
  cube([24,24,6], center=true);
  // No cutter is generated when the condition is false.
  if(hole) cylinder(h=8, r=4, center=true, $fn=32);
}`),
  'Local dimensions for each post':example('Four posts that become progressively taller and wider.','Change h=6+i*4 to h=6+i*2; successive heights increase by 2 mm instead of 4.',`
for(i=[0:3]) // Indices for four posts.
  let(h=6+i*4, r=2+i/2) // Temporary dimensions for this iteration only.
    translate([i*12,0,0])
      cylinder(h=h, r=r, $fn=24); // Use those named dimensions.`),
  'A reusable hollow post':example('An 18 mm tall hollow post with outer radius 6 and wall thickness 2.','Call post(h=18,wall=1); the bore widens while the outside stays the same.',`
// Define a reusable shape; its base always sits at Z=0.
module post(h=12, r=6, wall=2) {
  difference() {
    cylinder(h=h, r=r, $fn=32); // Outside of the post.
    // Leave the requested wall, and open both ends of the bore.
    translate([0,0,-1]) cylinder(h=h+2, r=r-wall, $fn=32);
  }
}
post(h=18); // Create one post, overriding only its default height.`),
  'A circular repeater':example('Six separate short cylinders spaced around a circle.','Change radial() to radial(n=8); eight copies share the same circle.',`
module radial(n=6, r=14) {
  assert($children>0, "Supply a child shape"); // Require an input.
  for(i=[0:n-1]) // One copy per angular position.
    rotate([0,0,i*360/n])
      translate([r,0,0]) children(); // Place the caller's shape here.
}
// Supply a cylinder as the child of the reusable wrapper.
radial() cylinder(h=6, r=3, $fn=24);`),
  'A calculated star profile':example('A five-pointed star plate, 5 mm thick.','Change the inner radius 7 to 10; the star’s indentations become shallower.',`
// Return a 2D point at angle a and distance r from the origin.
function radial_point(a,r)=[r*cos(a),r*sin(a)];
// Ten corners alternate outer radius 14 and inner radius 7.
// i%2 is the remainder after division by 2: zero on even indices.
pts=[for(i=[0:9]) radial_point(i*36, i%2==0 ? 14 : 7)];
linear_extrude(5) polygon(pts); // Convert the data into a solid.`),
  'Filtered circular points':example('A polygonal plate with wider flat edges where the 90° and 270° points were skipped.','Remove the if condition in the angles list; the outline becomes a regular 12-sided polygon.',`
// Collect angles every 30 degrees, excluding two opposite points.
angles=[for(a=[0:30:330]) if(a!=90 && a!=270) a];
// Calculate coordinates for the angles that survived the filter.
pts=[for(a=angles) [12*cos(a),12*sin(a)]];
linear_extrude(4) polygon(pts); // Draw the list and add thickness.`),
  'Clamp a safe wall thickness':example('An open tray whose requested 10 mm wall is limited to 4 mm. Diagnostics also show abs and sign on a signed distance.','Set requested=2; the resulting walls become 2 mm. Set it to 0; the minimum keeps them at 1 mm.',`
requested=10; // The input may be outside the desired range.
wall=max(1,min(4,requested)); // Clamp to the interval 1..4.
echo(distance=abs(-7), direction=sign(-7)); // Magnitude 7, direction -1.
difference() {
  cube([24,18,10]); // Outside envelope.
  // Inset the cavity on both sides and lift it to leave a floor.
  translate([wall,wall,wall]) cube([24-2*wall,18-2*wall,10]);
}`),
  'A triangular wedge from a slope':example('A triangular prism with a 25° sloping edge in its XY profile. Diagnostics demonstrate the inverse angle calculations.','Change angle from 25 to 40; the wedge’s triangular end becomes taller.',`
angle=25;  // Degrees, not radians.
length=30; // Horizontal run of the triangular outline.
// Ratios become angles again through the inverse functions.
echo(asin(sin(angle)), acos(cos(angle)), atan(tan(angle)));
linear_extrude(10) // Thickness along Z.
  polygon([[0,0], [length,0], [length,length*tan(angle)]]); // Rise = run*slope.`),
  'Align a bar with a vector':example('A 4 mm thick bar whose long bottom edge aims from the origin towards [20,12].','Change v to [20,-12]; the bar points to the opposite side of the X axis.',`
v=[20,12]; // Target displacement in XY.
rotate([0,0,atan2(v.y,v.x)]) // atan2 takes Y before X.
  cube([norm(v),4,4]); // Length equals the distance to the target.`),
  'Fit posts along a span':example('Three short square posts at 12 mm spacing; diagnostics compare the rounded counts.','Change span to 60; five posts are generated.',`
span=45;  // Available length for this simple repetition rule.
pitch=12; // Spacing between corresponding post corners.
n=max(1,floor(span/pitch)); // Fit complete repeats, with at least one.
echo(down=floor(span/pitch), up=ceil(span/pitch), nearest=round(span/pitch));
// Use the chosen whole-number count to generate geometry.
for(i=[0:n-1]) translate([i*pitch,0,0]) cube([6,6,8]);`),
  'Size a diagonal brace':example('A bar aligned with the diagonal of a 20 × 12 rectangle, about 23.32 mm long.','Change b from 12 to 20; the bar becomes longer and points at 45 degrees.',`
a=20; // Horizontal displacement.
b=12; // Vertical displacement in the XY plane.
length=sqrt(pow(a,2)+pow(b,2)); // Pythagoras: square, sum, square root.
echo(exp(1), ln(exp(1)), log(100)); // e, 1, 2: growth and inverse examples.
rotate([0,0,atan2(b,a)]) // Aim along that diagonal.
  cube([length,4,4]);`),
  'A cylinder rotated around a computed axis':example('A cylinder tilted 30 degrees around the negative Y axis.','Change the rotation angle from 30 to 60; the cylinder leans farther.',`
// X crossed with Z gives the perpendicular negative-Y direction.
axis=cross([1,0,0],[0,0,1]);
echo(axis=axis, length=norm(axis)); // Inspect the direction and its length.
rotate(a=30, v=axis) // Turn around the calculated axis.
  cylinder(h=18, r=4, $fn=32);`),
  'Repeatable varying posts':example('Five separate posts with irregular but repeatable heights between 6 and 18 mm.','Change seed 123 to 456; you get a different fixed height pattern.',`
heights=rands(6,18,5,123); // Five values; fixed seed keeps rebuilds stable.
for(i=[0:4]) // Use each generated height once.
  translate([i*10,0,0])
    cylinder(h=heights[i], r=3, $fn=20);`),
  'Combine two point lists':example('A five-cornered plate with a pointed right end.','Change the point [12,0] to [18,0]; the right-hand tip extends farther.',`
left=[[-12,-8],[0,-8]]; // First part of the boundary.
right=[[12,0],[0,8],[-12,8]]; // Continue around the same boundary.
echo(points=len(concat(left,right))); // Five points after joining.
linear_extrude(4)
  polygon(concat(left,right)); // Preserve pairs while joining the lists.`),
  'A sampled turned profile':example('A solid turned part that widens at mid-height and narrows towards its top.','Change the middle table radius from 12 to 16; the middle bulge grows.',`
table=[[0,8],[10,12],[20,6]]; // [height, radius] samples.
// Interpolate a radius at every 2 mm of height.
outer=[for(z=[0:2:20]) [lookup(z,table),z]];
rotate_extrude(angle=360, $fn=48)
  // Add axis endpoints to close the material cross-section.
  polygon(concat([[0,0]],outer,[[0,20]]));`),
  'Find a size in a list':example('A cylinder 10 mm across and 8 mm tall, selected by searching a size list.','Change search(10,sizes) to search(14,sizes); the diameter becomes 14 mm.',`
sizes=[6,10,14]; // Available diameters.
index=search(10,sizes)[0]; // First matching position is index 1.
// Read the matching diameter, then divide by two for the radius.
cylinder(h=8, r=sizes[index]/2, $fn=32);`),
  'A numbered label':example('Separate solid M6 letters, 2 mm thick, without a supporting plate.','Change the number 6 to 8; the lettering becomes M8.',`
echo(letter=chr(77), code=ord("M")); // Character M and its code 77.
linear_extrude(2) // Give the flat letters thickness.
  text(str("M",6), size=12, font="Noto Sans"); // Join text and number.`),
  'A checked module':example('A block using the default width of 20 mm, with diagnostics demonstrating value types.','Call block(30) for a wider block. Calling block(-2) deliberately stops with “Width must be positive”.',`
module block(w=undef) { // No supplied width is represented by undef.
  size=is_undef(w) ? 20 : w; // Choose a default before checking it.
  assert(is_num(size) && size>0, "Width must be positive");
  cube([size,12,5]); // Geometry only runs after successful validation.
}
// Predicates return true/false; they do not create shapes.
echo(is_bool(true), is_string("box"), is_list([1,2]));
echo(is_function(function(x) x*2), is_object(textmetrics("A")));
block(); // Omit the argument to exercise the default.`),
  'A plate sized to its label':example('A raised Flange label on a plate that fits its visible text bounds with 2 mm padding.','Replace "Flange" with "Component 1"; the plate automatically grows to fit.',`
label="Flange"; // The words drive the plate dimensions.
s=10; // Use the same size for measurement and drawing.
m=textmetrics(label, size=s, font="Noto Sans");
echo(fontmetrics(size=s, font="Noto Sans")); // Font-wide measurements.
union() {
  // Start 2 mm before the text bounds, and add 4 mm total padding.
  translate([m.position.x-2,m.position.y-2,0])
    cube([m.size.x+4,m.size.y+4,2]);
  // Overlap the plate's top by 0.1 mm to attach every letter.
  translate([0,0,1.9]) linear_extrude(1.2)
    text(label, size=s, font="Noto Sans");
}`),
  'Reject an impossible wall':example('An open square tray with 3 mm walls and a 3 mm floor.','Set wall=13 to trigger the explanatory assertion. Restore it to 3 to render again.',`
outer=24; // Outside width and depth.
wall=3; // Also used as the floor thickness in this tray.
assert(wall>0 && wall<outer/2 && wall<12,
       "Wall must fit inside the block and below its top");
difference() {
  cube([outer,outer,12]);
  // Inset the cavity and lift it to preserve the base.
  translate([wall,wall,wall]) cube([outer-2*wall,outer-2*wall,12]);
}`),
  'Inspect a computed dimension':example('A cylinder with radius 8, plus diagnostic output showing radius 8 and diameter 16.','Change radius to 10; the model widens and the printed diameter becomes 20.',`
radius=8; // A value used by both diagnostics and geometry.
echo(radius=radius, diameter=2*radius); // Print named values, not 3D text.
// The studio already renders solids; render() is harmless here.
render() cylinder(h=6, r=radius, $fn=32);`),
  'A library without its demo geometry':example('Two short tapered feet; the helper’s 100 mm demonstration foot is excluded by use.','Change use to include; the helper’s tall top-level demonstration also appears. Supply the helper file when copying.',`
// Load definitions without running the helper's top-level demo.
use <parts/foot.scad>
for(x=[0,20]) // Place two independently generated feet.
  translate([x,0,0]) foot(8); // Override the default height.`),
  'Extrude an SVG asset':example('A rectangular plate 4 mm thick with a rectangular hole inherited from the SVG.','Change the extrusion height from 4 to 8; the drawing stays the same and the plate thickens. Copy the included SVG too.',`
// The supplied SVG defines a filled outline and an enclosed opening.
linear_extrude(4) // Convert that 2D drawing into a 3D plate.
  import("outline.svg"); // Relative to this script's project folder.`),
  'A small terrain tile':example('A small faceted terrain tile with a closed base and several raised peaks.','Change the Z scale from 2 to 4; the relief becomes twice as tall. The included DAT file is a grid of heights, not executable code.',`
// Grid spacing grows sixfold in XY; sampled heights double in Z.
scale([6,6,2])
  surface(file="heights.dat", center=true); // Read the supplied height grid.`),
  'Report the bundled engine':example('A small block, with the engine version shown in the preview’s diagnostic text.','Change the cube height from 4 to 8; only the geometry changes, not the reported version.',`
// Report list and numeric forms for compatibility checks.
echo(version(), version_num());
cube([16,12,4]); // Keep a solid result: echo alone produces no geometry.`),
  'Choose a fixed pose':example('A long centred block turned 25 degrees in the work plane.','Set pose=90; the block makes a quarter turn around Z.',`
pose=25; // Explicit model angle, independent of the preview camera.
rotate([0,0,pose]) // Rotate the geometry itself.
  cube([30,8,5], center=true); // Its middle stays at the origin.`),
  'A roof without experimental features':example('A triangular roof prism made with supported polygon and extrusion operations.','Change the peak point [0,10] to [0,16]; the roof becomes taller.',`
rotate([90,0,0]) // Stand the finished triangular cross-section upright.
  linear_extrude(20) // Extend it along the roof's length.
    polygon([[-12,0],[12,0],[0,10]]); // Two eaves and one peak.`),
  'Six-hole flange':example('A 56 mm diameter flange with a central bore and six smaller bolt holes.','Change holes=6 to holes=8; eight holes are evenly distributed on the same bolt circle.',`
$fn=48; // Shared curve detail unless a shape overrides it.
outer=28; // Outside radius.
thickness=6;
bore=7; // Centre-hole radius.
pitch=20; // Radius to bolt-hole centres.
holes=6;
// Reserve at least 3 mm around hole centres, including the 2.5 mm cutter.
assert(pitch+3<outer && pitch-3>bore);
difference() {
  cylinder(h=thickness, r=outer); // Starting disk.
  // Main bore: extend beyond both faces.
  translate([0,0,-1]) cylinder(h=thickness+2, r=bore);
  for(i=[0:holes-1]) // Stop before repeating the first hole at 360 degrees.
    rotate([0,0,i*360/holes])
      translate([pitch,0,-1]) cylinder(h=thickness+2, r=2.5);
}`),
  'Open storage tray':example('A 40 × 28 × 18 mm open tray with 2 mm side walls and a 2 mm floor.','Change wall to 3; the outside stays fixed while the cavity becomes narrower and shallower.',`
width=40; // Outside dimensions.
depth=28;
height=18;
wall=2; // Side and floor thickness.
assert(wall>0 && 2*wall<min(width,depth) && wall<height);
difference() {
  cube([width,depth,height]); // The full outer box.
  // Lift the cavity to leave a floor; extend it beyond the top.
  translate([wall,wall,wall])
    cube([width-2*wall,depth-2*wall,height]);
}`),
  'Feature plate':example('One plate with a shallow rectangular pocket and a raised boss drilled through its centre.','Move the pocket’s starting Z from 3 to 4; its recess becomes 1 mm shallower.',`
difference() {
  union() { // Treat all additive features as one stock child.
    cube([44,28,6]); // Main base, top at Z=6.
    translate([32,14,5.9]) // Overlap the base by 0.1 mm.
      cylinder(h=10.1, r=7, $fn=40); // Boss ends at Z=16.
  }
  translate([4,4,3]) cube([18,20,4]); // Pocket leaves a 3 mm floor.
  // Drill through both the base and the entire boss.
  translate([32,14,-1]) cylinder(h=18, r=3, $fn=32);
}`),
  'Rounded plate with two holes':example('A fully rounded mounting plate approximately 40 × 24 × 8 mm with two 6 mm bores.','Change the hole positions from ±12 to ±10; their spacing decreases from 24 to 20 mm.',`
$fn=24; // Modest sphere detail keeps the rounding operation efficient.
difference() {
  minkowski() { // Grow the stock by 2 mm on every side.
    cube([36,20,4], center=true);
    sphere(2); // Round all edges, not just the top outline.
  }
  // Cut afterwards so rounding does not alter hole diameter.
  for(x=[-12,12]) translate([x,0,-5]) cylinder(h=10, r=3, $fn=32);
}`),
  'A straight-walled cup':example('A cup 36 mm across and 24 mm tall with a 3 mm wall and 3 mm floor.','Change both inner-radius values 15 to 14; the vertical wall thickens to 4 mm while the outside stays fixed.',`
rotate_extrude(angle=360, start=0, $fn=64) // Spin the material slice.
  polygon([
    [0,0],   // Bottom centre.
    [18,0],  // Outside bottom corner.
    [18,24], // Outside top corner.
    [15,24], // Cross the rim to the inside.
    [15,3],  // Inside wall ends at the floor.
    [0,3]    // Floor centre; close back down the axis.
  ]);`),
  'Engraved component label':example('PART 1 engraved 1.2 mm into the top of a 4 mm thick plate.','Change the cutter start from Z=0.8 to Z=1.4; the engraving becomes 0.6 mm deep.',`
difference() {
  cube([52,20,4], center=true); // Plate top is Z=2.
  // Start 1.2 mm below the top and extend above it.
  translate([0,0,0.8]) linear_extrude(2)
    text("PART 1", size=9, font="Noto Sans",
         halign="center", valign="center"); // Centre the cutter on the plate.
}`),
  'A bundled rounded box':example('A 30 × 20 × 8 mm solid box with rounded side corners and flat top/bottom edges.','Change sidesonly=true to sidesonly=false; the library rounds the top and bottom edges too.',`
use <MCAD/boxes.scad> // Load the module definition from the bundled library.
// Use named arguments so the two yes/no settings are unambiguous.
roundedCube([30,20,8], r=3, sidesonly=true, center=true);`),
  'A hexagonal nut recess':example('A centred block with a hexagonal recess opening in its top for the library’s nominal size-6 nut.','Change nutHole(6) to nutHole(8); the recess grows according to the library’s fastener-size table.',`
use <MCAD/nuts_and_bolts.scad> // Supplies a ready-made nut-shaped cutter.
difference() {
  cube([20,20,8], center=true); // Top is Z=4; bottom is Z=-4.
  // Raise the library cutter so it opens through the top, leaving a floor.
  translate([0,0,3]) nutHole(6);
}`),
};
