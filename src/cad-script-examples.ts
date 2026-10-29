/** More involved starters for the native OpenSCAD engine. No external files required. */
export const ADVANCED_SCRIPT_EXAMPLES:Record<string,string>={
  'Spiral lattice lantern':`// Two families of spiralling ribs join a pair of circular rims.
// Try twist=120 for tighter diamonds, or ribs=12 for a denser lattice.
$fn=64;
height=60; // Distance between the lower and upper rim bases, in mm.
radius=24; // Radius to the middle of each rib.
ribs=10; // Ribs in each direction; total count is twice this value.
twist=90; // Degrees turned by each rib from bottom to top.
rib_width=2.8;
assert(height>12 && radius>8 && ribs>=4 && ribs<=24);
assert(rib_width>=1 && rib_width<=5 && abs(twist)<=180);

module rim() {
  difference() {
    cylinder(h=4,r=radius+4); // Thick outside edge.
    translate([0,0,-1]) cylinder(h=6,r=radius-3); // Keep the centre open.
  }
}
union() {
  rim(); // Lower rim rests on Z=0.
  translate([0,0,height]) rim(); // Matching upper rim.
  for(direction=[-1,1]) // Opposite twists cross into a diamond lattice.
    for(i=[0:ribs-1])
      rotate([0,0,i*360/ribs])
        translate([0,0,2]) // Embed the rib ends 2 mm inside both rims.
          // Four profile segments keep square ribs efficient; slices smooth the twist.
          linear_extrude(height=height,twist=direction*twist,slices=48,segments=4)
            translate([radius,0]) square(rib_width,center=true);
}`,
  'Orbital sculpture':`// An armillary-style sculpture: three intersecting rings on a pedestal.
// Try orbit_radius=30 or ring_tilt=55 to change its silhouette.
$fn=64;
orbit_radius=25; // Distance from the centre to a ring's tube centre.
tube_radius=2.2;
ring_tilt=35; // Tilt of the third orbit relative to the horizontal.
planet_radius=7;
centre_height=orbit_radius+tube_radius+6; // Keep the rings above the base.
assert(orbit_radius>=16 && tube_radius>=1 && tube_radius<=4);
assert(planet_radius>3 && planet_radius<orbit_radius-tube_radius);

module orbit() {
  rotate_extrude(angle=360,$fn=80) // Sweep a circular tube around Z.
    translate([orbit_radius,0]) circle(tube_radius,$fn=16);
}
union() {
  cylinder(h=5,r1=18,r2=15); // Tapered pedestal.
  cylinder(h=centre_height,r=3); // Stem joins pedestal, rings and planet.
  translate([0,0,centre_height]) {
    sphere(planet_radius,$fn=40); // Central globe overlaps the stem.
    rotate([90,0,0]) orbit(); // First vertical ring.
    rotate([0,90,0]) orbit(); // Second vertical ring, at right angles.
    rotate([ring_tilt,0,0]) orbit(); // Sloping third ring intersects both.
  }
}`,
  'Twisted wave pen pot':`// A hollow pot with a rippled outline that twists as it rises.
// Try waves=10, twist=70, or height=80. The floor remains 4 mm thick.
$fn=80;
height=64;
radius=25; // Average outside radius.
waves=8; // Number of flutes around the pot.
ripple=2.5; // Depth of the wavy silhouette.
twist=40;
wall=3; // Minimum radial wall thickness at the narrowest flute.
floor=4;
assert(height>floor && radius-ripple-wall>3 && wall>=1);
assert(waves>=3 && waves<=16 && ripple>=0 && ripple<=5);

// Return the radius at an angle; cos makes it swell and shrink smoothly.
function outline_radius(a)=radius+ripple*cos(waves*a);
points=[for(i=[0:159]) let(a=i*360/160)
  [outline_radius(a)*cos(a),outline_radius(a)*sin(a)]];

difference() {
  union() {
    cylinder(h=4,r=radius+ripple+1); // Broad foot supports every flute.
    linear_extrude(height=height,twist=twist,slices=48)
      polygon(points); // Twist the entire filled outline first.
  }
  // Cut a straight cavity afterwards; start above the solid floor.
  translate([0,0,floor]) cylinder(h=height+1,r=radius-ripple-wall);
}`,
  'Rocket desk organiser':`// A rocket-shaped pen cup: tapered hull, three swept fins and an engine.
// Try fins=4 or height=85. The open nose is the pen opening.
$fn=64;
height=64; // Hull height above its engine.
radius=22; // Lower hull radius.
wall=3;
fins=3;
fin_reach=12; // Extra distance beyond the hull to each landing foot.
assert(height>=40 && radius>=16 && radius<=32);
assert(wall>=1.5 && wall<=5 && fins>=3 && fins<=6 && fin_reach>=6);

module fin() {
  hull() { // Bridge an attachment strip and a wider landing foot.
    translate([radius-5,-2,10]) cube([5,4,height*0.55]);
    translate([radius+fin_reach-4,-3,2]) cube([4,6,5]);
  }
}
difference() {
  union() {
    cylinder(h=3,r=radius+fin_reach+2); // Shared circular launch pad.
    cylinder(h=12,r1=12,r2=10); // Engine joins pad and hull.
    translate([0,0,8]) cylinder(h=height,r1=radius,r2=radius-4);
    for(i=[0:fins-1]) rotate([0,0,i*360/fins]) fin();
  }
  // Match the outside taper while leaving a 4 mm floor above the engine.
  translate([0,0,12])
    cylinder(h=height,r1=radius-wall-4*4/height,
             r2=radius-wall-4-4*4/height);
  // Round portholes cut into the outside between fins.
  for(i=[0:fins-1]) rotate([0,0,(i+0.5)*360/fins])
    translate([radius-2,0,8+height*0.55]) sphere(3.5,$fn=24);
}`,
  'Castle gatehouse':`// Four hollow towers, crenellated walls and a true arched entrance.
// Try tower_height=42 or battlements=10. All features share one base.
$fn=48;
tower_height=32;
wall_height=24;
battlements=8; // Blocks around each tower rim.
assert(tower_height>=wall_height+4 && tower_height<=60);
assert(wall_height>=24 && battlements>=6 && battlements<=12);

module tower() {
  difference() {
    union() {
      cylinder(h=tower_height,r=10);
      for(i=[0:battlements-1]) rotate([0,0,i*360/battlements])
        translate([8,0,tower_height+2]) cube([4,4,6],center=true);
    }
    // Hollow the tower, retaining a floor and a 3 mm thick wall.
    translate([0,0,5]) cylinder(h=tower_height+5,r=7);
  }
}
module arch() {
  // Flat arch: a rectangle topped by a semicircle; their areas overlap.
  union() {
    translate([-7,0]) square([14,14]);
    translate([0,14]) circle(7);
  }
}
union() {
  translate([-47,-37,0]) cube([94,74,4]); // Foundation joins everything.
  difference() {
    union() {
      for(x=[-32,32],y=[-22,22]) translate([x,y,3]) tower();
      for(y=[-22,22]) {
        translate([-32,y-2.5,3]) cube([64,5,wall_height]);
        for(x=[-24:8:24]) // Merlons: solid blocks above the wall walk.
          translate([x-2,y-2.5,wall_height+2]) cube([4,5,6]);
      }
      for(x=[-32,32]) {
        translate([x-2.5,-22,3]) cube([5,44,wall_height]);
        for(y=[-16:8:16])
          translate([x-2.5,y-2,wall_height+2]) cube([5,4,6]);
      }
    }
    // Stand the arch upright and cut only the front wall, down to the base.
    translate([0,-18,4]) rotate([90,0,0]) linear_extrude(12) arch();
  }
}`,
};
