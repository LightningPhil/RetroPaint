# Coverage matrix and required expansions

The 349 cases cover the user-facing feature families below. Named variants expand those cases; they do not inflate the case count or imply execution. The source snapshot contains 131 stamp choices across 8 banks and 25 shape choices. All family execution states are Not run.

See [Testing protocol](TESTING-PROTOCOL.md) before marking coverage complete. Some Cartesian products are too large to run exhaustively; the exact selected pairwise plan must be retained. Every individually named option still needs a direct exercise.

## Painting tools

**Case references:** [START-002](01-start.md#start-002), [ACCESS-001](17-access.md#access-001).

**Required values:**

```json
[
  "Brushes",
  "Shapes",
  "Bucket",
  "Spray",
  "Smudge",
  "Select",
  "Eraser",
  "Stamps",
  "Symmetry",
  "Spiro",
  "Text",
  "Pick colour"
]
```

**Execution rule:** Exercise every entry on desktop and touch layouts. Symmetry is a modifier family as well as a main illustrated control.

**Execution status:** Not run.

## Brush applicators

**Case references:** [PAINT-001](02-paint.md#paint-001), [PAINT-002](02-paint.md#paint-002), [PAINT-003](02-paint.md#paint-003), [PAINT-004](02-paint.md#paint-004), [PAINT-005](02-paint.md#paint-005), [PAINT-006](02-paint.md#paint-006), [PAINT-007](02-paint.md#paint-007).

**Required values:**

```json
[
  "marker",
  "biro",
  "callig",
  "gouache",
  "watercolor",
  "pencil",
  "brush",
  "oil",
  "crayon",
  "natural"
]
```

**Execution rule:** Run tap slow curve fast curve size endpoints strength endpoints and Undo for each actual applicator. Test random materials with fixed seeds where available.

**Execution status:** Not run.

## Spray applicators

**Case references:** [PAINT-010](02-paint.md#paint-010), [PAINT-011](02-paint.md#paint-011), [PAINT-012](02-paint.md#paint-012).

**Required values:**

```json
[
  "mist",
  "splatter",
  "confetti"
]
```

**Execution rule:** Each needs stationary and moving input, edge clipping and release/cancel checks.

**Execution status:** Not run.

## Eraser modes

**Case references:** [PAINT-014](02-paint.md#paint-014), [PAINT-015](02-paint.md#paint-015), [PAINT-016](02-paint.md#paint-016), [PAINT-017](02-paint.md#paint-017), [PAINT-018](02-paint.md#paint-018).

**Required values:**

```json
[
  "scrub",
  "blackhole",
  "pixelate",
  "invert",
  "emboss"
]
```

**Execution rule:** Use both opaque Paper and a transparent sheet where the effect supports alpha. Each mode gets an independent before state.

**Execution status:** Not run.

## Shape choices

**Case references:** [PLAY-001](04-play.md#play-001), [PLAY-002](04-play.md#play-002), [PLAY-003](04-play.md#play-003), [PLAY-004](04-play.md#play-004), [PLAY-005](04-play.md#play-005), [PLAY-006](04-play.md#play-006), [PLAY-007](04-play.md#play-007), [PLAY-008](04-play.md#play-008), [PLAY-009](04-play.md#play-009), [PLAY-010](04-play.md#play-010).

**Required values:**

```json
[
  "line",
  "rect",
  "circle",
  "poly",
  "spline",
  "ellipse",
  "roundRect",
  "triangle",
  "rightTriangle",
  "diamond",
  "pentagon",
  "hexagon",
  "star4",
  "star5",
  "star6",
  "heart",
  "lightning",
  "arrowRight",
  "arrowLeft",
  "arrowUp",
  "arrowDown",
  "callout",
  "ovalCallout",
  "cloud",
  "polygon"
]
```

**Execution rule:** Every shape requires forward/reverse drag, tiny and normal bounds, fill/outline combinations and Undo. Polygon polyline and spline use their explicit point completion workflow.

**Execution status:** Not run.

## Symmetry choices

**Case references:** [PLAY-011](04-play.md#play-011), [PLAY-012](04-play.md#play-012), [PLAY-013](04-play.md#play-013).

**Required values:**

```json
[
  "off",
  "v",
  "h",
  "4",
  "6",
  "8",
  "10",
  "12"
]
```

**Execution rule:** Every active repeat count needs an asymmetric off axis motif. Test Mask on/off and a working sector boundary.

**Execution status:** Not run.

## Textures

**Case references:** [INK-009](03-ink.md#ink-009), [INK-017](03-ink.md#ink-017), [INK-018](03-ink.md#ink-018).

**Required values:**

```json
[
  "tex-brick",
  "tex-dots",
  "tex-weave",
  "tex-grass",
  "tex-stone",
  "tex-water",
  "tex-static"
]
```

**Execution rule:** Exercise paint and supported fill behavior. Freeze times for frame comparisons, and distinguish the two animated textures from static textures.

**Execution status:** Not run.

## Gradient presets

**Case references:** [INK-012](03-ink.md#ink-012), [INK-013](03-ink.md#ink-013), [INK-014](03-ink.md#ink-014).

**Required values:**

```json
[
  "grad-sunset",
  "grad-rainbow",
  "grad-ocean",
  "grad-candy"
]
```

**Execution rule:** Enter Bucket first because the gradient tray is context sensitive. Test preset stops and user endpoints separately.

**Execution status:** Not run.

## Stamp inventory

**Case references:** [PLAY-014](04-play.md#play-014), [PLAY-015](04-play.md#play-015), [PLAY-016](04-play.md#play-016), [VECTOR-005](07-vector.md#vector-005).

**Required values:**

```json
[
  {
    "id": "critters",
    "label": "🐾 Animals",
    "items": [
      "🐶",
      "🐱",
      "🐭",
      "🐰",
      "🦊",
      "🐸",
      "🐧",
      "🐢",
      "🐙",
      "🦋",
      "🦄",
      "🦁",
      "🐨",
      "🐼",
      "🐝",
      "🐬",
      "🦉",
      "🦕"
    ]
  },
  {
    "id": "scenery",
    "label": "🌿 Nature",
    "items": [
      "🌳",
      "🌴",
      "🌵",
      "🌸",
      "⭐",
      "🌈",
      "⛰️",
      "🌊",
      "☀️",
      "🌙",
      "🍄",
      "🌻",
      "🍀",
      "❄️",
      "🌎",
      "🌺",
      "🍁",
      "🐚"
    ]
  },
  {
    "id": "rides",
    "label": "🚀 Rides",
    "items": [
      "🚗",
      "🚌",
      "🏎️",
      "🚜",
      "✈️",
      "🚀",
      "🛸",
      "⛵",
      "🚲",
      "🚂",
      "🚁",
      "🚒",
      "🚑",
      "🛵",
      "🎈",
      "🛶",
      "🚢",
      "🛰️"
    ]
  },
  {
    "id": "history",
    "label": "🏰 Adventure",
    "items": [
      "🏰",
      "👑",
      "⚔️",
      "🛡️",
      "🗿",
      "🏺",
      "🦖",
      "🌋",
      "📯",
      "⚓",
      "🧙",
      "🧚",
      "🐉",
      "💎",
      "🗺️",
      "🏴‍☠️",
      "🔮",
      "🦴"
    ]
  },
  {
    "id": "cartoons",
    "label": "🤖 Faces",
    "items": [
      "🤖",
      "👽",
      "👾",
      "🤡",
      "👻",
      "🎃",
      "😀",
      "😎",
      "🤩",
      "💩",
      "🥳",
      "😴",
      "😍",
      "🙃",
      "😺",
      "🥸",
      "😇",
      "🤠"
    ]
  },
  {
    "id": "treats",
    "label": "🍓 Treats",
    "items": [
      "🍓",
      "🍉",
      "🍒",
      "🍋",
      "🍎",
      "🍇",
      "🍍",
      "🥕",
      "🍕",
      "🍔",
      "🍟",
      "🍿",
      "🍩",
      "🍪",
      "🧁",
      "🍦",
      "🍭",
      "🎂"
    ]
  },
  {
    "id": "play",
    "label": "⚽ Play",
    "items": [
      "⚽",
      "🏀",
      "🎾",
      "🏈",
      "🏓",
      "🪁",
      "🎸",
      "🥁",
      "🎹",
      "🎺",
      "🎨",
      "🧩",
      "🎲",
      "🧸",
      "🎁",
      "🏆",
      "🎯",
      "🎪"
    ]
  },
  {
    "id": "shapes",
    "label": "★ Shapes",
    "items": [
      "vec:star",
      "vec:heart",
      "vec:triangle",
      "vec:diamond",
      "vec:blob"
    ]
  }
]
```

**Execution rule:** Test every individual stamp at least once in raster and editable mode where supported. Emoji glyph rendering depends on platform; assert recognizable presence and identity before pixel comparisons. Do not count one stamp per bank as all stamp coverage.

**Execution status:** Not run.

## Spiro stators gears and holes

**Case references:** [PLAY-017](04-play.md#play-017), [PLAY-018](04-play.md#play-018), [PLAY-019](04-play.md#play-019), [PLAY-020](04-play.md#play-020), [PLAY-021](04-play.md#play-021), [PLAY-022](04-play.md#play-022).

**Required values:**

```json
{
  "stators": [
    "circle",
    "oval",
    "square",
    "cross"
  ],
  "outer_teeth": [
    72,
    84,
    96,
    105,
    120
  ],
  "gears": {
    "pink": [
      24,
      5
    ],
    "purple": [
      30,
      6
    ],
    "red": [
      36,
      7
    ],
    "yellow": [
      42,
      8
    ],
    "green": [
      48,
      8
    ],
    "orange": [
      54,
      10
    ]
  },
  "drive": [
    "manual",
    "auto"
  ]
}
```

**Execution rule:** Each gear and offered hole needs a valid drawing check. Cover each stator and outer tooth choice, plus pairwise combinations and documented invalid combinations; do not claim the full Cartesian product unless run.

**Execution status:** Not run.

## Live conveyor settings

**Case references:** [INK-015](03-ink.md#ink-015), [INK-016](03-ink.md#ink-016), [INK-017](03-ink.md#ink-017), [INK-019](03-ink.md#ink-019).

**Required values:**

```json
{
  "slots": "0 through 8 filled slots",
  "speed": [
    -8,
    0,
    8
  ],
  "mode": [
    "snap",
    "ooze"
  ],
  "armed": [
    false,
    true
  ]
}
```

**Execution rule:** Test slot replacement capacity reverse zero speed and stable save/reopen. A serialized legacy rainbow-time recipe is import compatibility coverage, not proof of an exposed new UI control.

**Execution status:** Not run.

## Selection and outline choices

**Case references:** [EDIT-001](05-edit.md#edit-001), [EDIT-002](05-edit.md#edit-002), [EDIT-003](05-edit.md#edit-003), [EDIT-009](05-edit.md#edit-009), [EDIT-015](05-edit.md#edit-015), [PLAY-003](04-play.md#play-003).

**Required values:**

```json
{
  "selection": [
    "rect",
    "lasso",
    "wand"
  ],
  "outline": [
    "brush",
    "solid",
    "none"
  ],
  "fill": [
    "none",
    "primary",
    "secondary"
  ],
  "scope": [
    "selection",
    "whole picture"
  ]
}
```

**Execution rule:** Exercise the meaningful combinations with explicit scope; reject unavailable combinations honestly.

**Execution status:** Not run.

## Text properties

**Case references:** [EDIT-021](05-edit.md#edit-021), [EDIT-022](05-edit.md#edit-022), [EDIT-023](05-edit.md#edit-023), [EDIT-024](05-edit.md#edit-024), [VECTOR-004](07-vector.md#vector-004).

**Required values:**

```json
{
  "fonts": [
    "Trebuchet MS",
    "Arial",
    "Georgia",
    "Courier New",
    "Comic Sans MS",
    "Impact"
  ],
  "alignment": [
    "left",
    "centre",
    "right"
  ],
  "style": [
    "bold",
    "italic",
    "underline",
    "strike-through"
  ],
  "background": [
    "clear",
    "secondary colour"
  ]
}
```

**Execution rule:** Each font and property needs a visible result and project persistence check. Record fallback fonts rather than inventing identical glyphs across platforms.

**Execution status:** Not run.

## Photo scalar settings

**Case references:** [PHOTO-007](08-photo.md#photo-007), [PHOTO-008](08-photo.md#photo-008), [PHOTO-009](08-photo.md#photo-009), [PHOTO-010](08-photo.md#photo-010), [PHOTO-011](08-photo.md#photo-011), [PHOTO-012](08-photo.md#photo-012), [PHOTO-013](08-photo.md#photo-013), [COLOUR-001](09-colour.md#colour-001), [COLOUR-002](09-colour.md#colour-002), [COLOUR-005](09-colour.md#colour-005), [COLOUR-006](09-colour.md#colour-006), [COLOUR-007](09-colour.md#colour-007), [FINISH-001](10-finish.md#finish-001), [FINISH-002](10-finish.md#finish-002), [FINISH-003](10-finish.md#finish-003), [FINISH-004](10-finish.md#finish-004), [FINISH-005](10-finish.md#finish-005), [FINISH-006](10-finish.md#finish-006), [FINISH-007](10-finish.md#finish-007), [FINISH-008](10-finish.md#finish-008), [FINISH-009](10-finish.md#finish-009), [FINISH-010](10-finish.md#finish-010), [FINISH-018](10-finish.md#finish-018), [FINISH-019](10-finish.md#finish-019), [FINISH-020](10-finish.md#finish-020), [FINISH-021](10-finish.md#finish-021), [FINISH-022](10-finish.md#finish-022), [FINISH-023](10-finish.md#finish-023).

**Required values:**

```json
[
  "exposure",
  "brightness",
  "contrast",
  "highlights",
  "shadows",
  "whites",
  "blacks",
  "temperature",
  "tint",
  "saturation",
  "vibrance",
  "hue",
  "sharpness",
  "radius",
  "threshold",
  "texture",
  "clarity",
  "pop",
  "dehaze",
  "noise",
  "colourNoise",
  "vignette",
  "midpoint",
  "feather",
  "roundness",
  "grain",
  "grainSize",
  "grainRoughness",
  "distortion",
  "aberration",
  "vertical",
  "horizontal",
  "angle",
  "zoom",
  "flipX",
  "flipY"
]
```

**Execution rule:** Exercise default minimum maximum and a meaningful intermediate value for every exposed scalar using its declared source range. Crop coordinates are covered by their frame contract, not as unrelated global sliders.

**Execution status:** Not run.

## Photo categories and groups

**Case references:** [PHOTO-002](08-photo.md#photo-002), [ACCESS-002](17-access.md#access-002).

**Required values:**

```json
[
  "light-basic",
  "light-tone",
  "colour-balance",
  "colour-basic",
  "colour-mixer",
  "curves",
  "detail-presence",
  "detail-sharp",
  "detail-noise",
  "effects-vignette",
  "effects-grain",
  "geometry-crop",
  "geometry-align",
  "geometry-perspective",
  "geometry-lens"
]
```

**Execution rule:** Every group must be reached through the real UI in desktop portrait and short screen navigation.

**Execution status:** Not run.

## Looks colour mixer and curves

**Case references:** [PHOTO-015](08-photo.md#photo-015), [PHOTO-016](08-photo.md#photo-016), [COLOUR-008](09-colour.md#colour-008), [COLOUR-009](09-colour.md#colour-009), [COLOUR-010](09-colour.md#colour-010), [COLOUR-011](09-colour.md#colour-011), [COLOUR-012](09-colour.md#colour-012), [COLOUR-013](09-colour.md#colour-013), [COLOUR-014](09-colour.md#colour-014).

**Required values:**

```json
{
  "looks": [
    "normal",
    "natural",
    "punch",
    "mono",
    "warm",
    "cool",
    "custom"
  ],
  "mixer": [
    "red",
    "orange",
    "yellow",
    "green",
    "aqua",
    "blue",
    "purple",
    "magenta"
  ],
  "curves": [
    "rgb",
    "red",
    "green",
    "blue"
  ]
}
```

**Execution rule:** Custom is an indicated state, not an extra preset action. Test each actual selectable value and saved baseline behavior.

**Execution status:** Not run.

## Photo crop ratios

**Case references:** [FINISH-011](10-finish.md#finish-011), [FINISH-012](10-finish.md#finish-012), [FINISH-013](10-finish.md#finish-013), [FINISH-014](10-finish.md#finish-014), [FINISH-015](10-finish.md#finish-015), [FINISH-016](10-finish.md#finish-016).

**Required values:**

```json
[
  "free",
  "original ratio",
  "1:1",
  "4:3",
  "3:2",
  "16:9",
  "9:16",
  "4:5"
]
```

**Execution rule:** Exercise every offered ratio on portrait and landscape sources, with edge clamps, rounding and Cancel. Original ratio depends on the actual source dimensions.

**Execution status:** Not run.

## Image formats

**Case references:** [FILE-002](11-file.md#file-002), [FILE-006](11-file.md#file-006), [FILE-007](11-file.md#file-007), [FILE-008](11-file.md#file-008), [FILE-009](11-file.md#file-009), [FILE-010](11-file.md#file-010), [FILE-011](11-file.md#file-011).

**Required values:**

```json
[
  "PNG",
  "JPEG",
  "WebP",
  "BMP",
  "GIF",
  "TIFF"
]
```

**Execution rule:** Open real fixtures and independently decode real downloads. Record lossy palette alpha and TIFF limitations per format.

**Execution status:** Not run.

## Enhancement dimensions and areas

**Case references:** [ENHANCE-002](12-enhance.md#enhance-002), [ENHANCE-003](12-enhance.md#enhance-003), [ENHANCE-007](12-enhance.md#enhance-007), [ENHANCE-008](12-enhance.md#enhance-008), [ENHANCE-009](12-enhance.md#enhance-009), [ENHANCE-010](12-enhance.md#enhance-010), [ENHANCE-012](12-enhance.md#enhance-012).

**Required values:**

```json
{
  "scale": [
    2,
    4
  ],
  "area": [
    64,
    128,
    256
  ],
  "backend": [
    "WebGL",
    "CPU"
  ],
  "output_edge_limit": 16384
}
```

**Execution rule:** Use small deterministic samples for broad combinations and separately run whole image boundary tests with recorded resource constraints.

**Execution status:** Not run.

## CAD primitives

**Case references:** [SOLID-002](13-solid.md#solid-002), [SOLID-003](13-solid.md#solid-003), [SOLID-008](13-solid.md#solid-008), [SOLID-010](13-solid.md#solid-010).

**Required values:**

```json
[
  "box",
  "sphere",
  "cylinder",
  "cone",
  "torus",
  "tube",
  "pyramid",
  "wedge"
]
```

**Execution rule:** Each primitive needs bounds volume closed surface and save/reopen, not merely a visible thumbnail.

**Execution status:** Not run.

## CAD transforms alignment and patterns

**Case references:** [SOLID-005](13-solid.md#solid-005), [SOLID-006](13-solid.md#solid-006), [SOLID-007](13-solid.md#solid-007), [SOLID-008](13-solid.md#solid-008), [SOLID-009](13-solid.md#solid-009), [SOLID-017](13-solid.md#solid-017), [SOLID-018](13-solid.md#solid-018), [SOLID-019](13-solid.md#solid-019), [SOLID-020](13-solid.md#solid-020), [SOLID-021](13-solid.md#solid-021), [SOLID-022](13-solid.md#solid-022).

**Required values:**

```json
{
  "axis": [
    "X",
    "Y",
    "Z"
  ],
  "grid_mm": [
    0.1,
    0.5,
    1,
    5,
    10
  ],
  "angle_deg": [
    1,
    5,
    15,
    45,
    90
  ],
  "alignment": [
    "centre",
    "min",
    "max",
    "after",
    "before"
  ],
  "pattern": [
    "linear extra copies",
    "circular around Z origin",
    "mirror X",
    "mirror Y",
    "mirror Z"
  ]
}
```

**Execution rule:** Test each direction, positive and negative coordinates, locked pieces and transformed world bounds. Extra copies means count plus the original, not total count.

**Execution status:** Not run.

## CAD sketch and constraint families

**Case references:** [SKETCH-001](14-sketch.md#sketch-001), [SKETCH-002](14-sketch.md#sketch-002), [SKETCH-003](14-sketch.md#sketch-003), [SKETCH-004](14-sketch.md#sketch-004), [SKETCH-005](14-sketch.md#sketch-005), [SKETCH-006](14-sketch.md#sketch-006), [SKETCH-007](14-sketch.md#sketch-007), [SKETCH-008](14-sketch.md#sketch-008), [SKETCH-009](14-sketch.md#sketch-009), [SKETCH-010](14-sketch.md#sketch-010), [SKETCH-017](14-sketch.md#sketch-017), [SKETCH-018](14-sketch.md#sketch-018), [SKETCH-019](14-sketch.md#sketch-019), [SKETCH-020](14-sketch.md#sketch-020), [SKETCH-021](14-sketch.md#sketch-021), [SKETCH-022](14-sketch.md#sketch-022).

**Required values:**

```json
{
  "plane": [
    "xy",
    "xz",
    "yz",
    "picked flat face"
  ],
  "outline": [
    "rectangle",
    "circle",
    "polygon"
  ],
  "operation": [
    "new",
    "join",
    "cut"
  ],
  "constraint": [
    "length",
    "angle",
    "angle-between",
    "diameter",
    "horizontal",
    "vertical",
    "parallel",
    "perpendicular"
  ]
}
```

**Execution rule:** Every supported constraint needs actual rebuilt geometry, persistence and a conflict variant. Diameter applies to circle sketches, other line constraints to appropriate noncircle outlines.

**Execution status:** Not run.

## CAD boolean and revolve families

**Case references:** [SKETCH-012](14-sketch.md#sketch-012), [SKETCH-013](14-sketch.md#sketch-013), [SKETCH-014](14-sketch.md#sketch-014), [SKETCH-015](14-sketch.md#sketch-015), [SKETCH-016](14-sketch.md#sketch-016).

**Required values:**

```json
{
  "boolean": [
    "union",
    "subtract",
    "intersect",
    "hull"
  ],
  "revolve_profile": [
    "vase",
    "goblet",
    "knob",
    "custom"
  ],
  "revolve_angle": [
    "partial",
    "full"
  ]
}
```

**Execution rule:** Use analytic simple cases and nontrivial joined cases. Check every operation target semantics and boundary orientation.

**Execution status:** Not run.

## CAD history and precision families

**Case references:** [FEATURE-001](15-feature.md#feature-001), [FEATURE-002](15-feature.md#feature-002), [FEATURE-003](15-feature.md#feature-003), [FEATURE-004](15-feature.md#feature-004), [FEATURE-005](15-feature.md#feature-005), [FEATURE-006](15-feature.md#feature-006), [FEATURE-008](15-feature.md#feature-008), [FEATURE-011](15-feature.md#feature-011), [FEATURE-012](15-feature.md#feature-012), [FEATURE-013](15-feature.md#feature-013), [FEATURE-014](15-feature.md#feature-014), [FEATURE-015](15-feature.md#feature-015), [FEATURE-016](15-feature.md#feature-016), [FEATURE-017](15-feature.md#feature-017), [FEATURE-018](15-feature.md#feature-018), [FEATURE-019](15-feature.md#feature-019), [FEATURE-020](15-feature.md#feature-020), [FEATURE-021](15-feature.md#feature-021), [FEATURE-022](15-feature.md#feature-022), [FEATURE-023](15-feature.md#feature-023), [FEATURE-024](15-feature.md#feature-024), [FEATURE-025](15-feature.md#feature-025), [FEATURE-026](15-feature.md#feature-026), [FEATURE-027](15-feature.md#feature-027), [FEATURE-028](15-feature.md#feature-028), [FEATURE-029](15-feature.md#feature-029).

**Required values:**

```json
{
  "feature": [
    "primitive",
    "extrude",
    "revolve",
    "boolean",
    "finish",
    "shell",
    "loft",
    "sweep",
    "mesh"
  ],
  "finish": [
    "fillet",
    "chamfer"
  ],
  "loft": [
    "smooth",
    "ruled"
  ],
  "sweep": [
    "straight miter",
    "straight round",
    "smooth"
  ],
  "draft": [
    "preview",
    "apply",
    "cancel",
    "invalid",
    "timeout"
  ],
  "reference": [
    "unchanged",
    "moved",
    "removed",
    "ambiguous"
  ]
}
```

**Execution rule:** Expand each supported feature editor and its original sketch/path child nodes. Not every kernel combination is supported; unsupported combinations must preserve the original and explain the limitation.

**Execution status:** Not run.

## CAD inspection import and export

**Case references:** [DELIVER-001](16-deliver.md#deliver-001), [DELIVER-002](16-deliver.md#deliver-002), [DELIVER-003](16-deliver.md#deliver-003), [DELIVER-004](16-deliver.md#deliver-004), [DELIVER-005](16-deliver.md#deliver-005), [DELIVER-006](16-deliver.md#deliver-006), [DELIVER-008](16-deliver.md#deliver-008), [DELIVER-009](16-deliver.md#deliver-009), [DELIVER-014](16-deliver.md#deliver-014), [DELIVER-015](16-deliver.md#deliver-015), [DELIVER-016](16-deliver.md#deliver-016), [DELIVER-019](16-deliver.md#deliver-019), [DELIVER-020](16-deliver.md#deliver-020), [DELIVER-021](16-deliver.md#deliver-021), [DELIVER-022](16-deliver.md#deliver-022).

**Required values:**

```json
{
  "projection": [
    "perspective",
    "orthographic"
  ],
  "view": [
    "iso",
    "top",
    "bottom",
    "front",
    "back",
    "left",
    "right"
  ],
  "appearance": [
    "solid",
    "xray",
    "wireframe"
  ],
  "section_axis": [
    "X",
    "Y",
    "Z"
  ],
  "stl_encoding": [
    "binary",
    "ASCII"
  ],
  "import_unit": [
    "mm",
    "cm",
    "in"
  ],
  "export_scope": [
    "visible",
    "layer",
    "selection"
  ],
  "place_on_bed": [
    false,
    true
  ]
}
```

**Execution rule:** Separate view-only checks from physical geometry checks. Inspect every exported scope and every nested shell orientation variant independently.

**Execution status:** Not run.

## Document boundaries and storage

**Case references:** [LAYER-012](06-layer.md#layer-012), [FILE-016](11-file.md#file-016), [FILE-024](11-file.md#file-024), [ENHANCE-012](12-enhance.md#enhance-012), [FEATURE-022](15-feature.md#feature-022), [FEATURE-026](15-feature.md#feature-026), [FEATURE-029](15-feature.md#feature-029), [DELIVER-017](16-deliver.md#deliver-017).

**Required values:**

```json
{
  "image_edge": [
    1,
    4096,
    4097
  ],
  "layers": [
    1,
    16,
    17
  ],
  "total_stored_pixels": 64000000,
  "draft_max_stored_pixels": 24000000,
  "draft_max_serialized_characters": 50000000,
  "draft_count": 8,
  "draft_budget_bytes": 128000000,
  "cad_top_level_pieces": 128,
  "stl_triangles": 200000,
  "stl_file_bytes": 20000000,
  "loft_profiles": [
    2,
    16
  ],
  "sweep_points": [
    2,
    64
  ],
  "sketch_constraints": 64
}
```

**Execution rule:** Test accepted boundary and first rejected boundary in disposable sessions; exact limits are source baseline values, not forever frozen product design.

**Execution status:** Not run.

## Workspace matrix

**Case references:** [START-002](01-start.md#start-002), [START-007](01-start.md#start-007), [ACCESS-001](17-access.md#access-001), [ACCESS-002](17-access.md#access-002), [ACCESS-003](17-access.md#access-003), [ACCESS-005](17-access.md#access-005), [ACCESS-006](17-access.md#access-006), [ACCESS-007](17-access.md#access-007), [ACCESS-012](17-access.md#access-012), [ACCESS-014](17-access.md#access-014), [ACCESS-017](17-access.md#access-017), [ACCESS-018](17-access.md#access-018).

**Required values:**

```json
{
  "viewport": [
    "320x568",
    "390x844",
    "844x390",
    "1280x720",
    "2560x1215"
  ],
  "input": [
    "mouse",
    "touch",
    "pen where available",
    "keyboard controls"
  ],
  "mode": [
    "basic",
    "advanced",
    "raster",
    "vector",
    "CAD"
  ],
  "capability": [
    "clipboard allowed",
    "clipboard denied",
    "storage allowed",
    "storage blocked",
    "WebGL available",
    "WebGL unavailable"
  ]
}
```

**Execution rule:** Use explicit supported browser and hardware records. Cover high risk combinations exhaustively and lower risk interactions pairwise; do not claim every Cartesian combination unless executed.

**Execution status:** Not run.
