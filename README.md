# RetroPaint

A tactile painting toy and image editor: chunky tools, live ink, symmetry, stamps, a spirograph kit, and familiar Paint editing tools.

**Author:** Philip Leichauer  
**License:** [MIT](LICENSE)

## Scripts

```bash
npm install
npm run dev      # http://localhost:8080
npm run build    # typecheck + compile to dist/
npm run preview  # serve dist/ on port 8080
```

Requires Node 20+.

## GitHub Pages

Pushes to `main` (or `master`) run `.github/workflows/pages.yml`, which compiles the app and publishes `dist/`. In the repo settings, set **Pages → Build and deployment → Source** to **GitHub Actions**.

The Vite `base` is `./`, so the site works at `https://<user>.github.io/RetroPaint/`.

There is no test workflow. Do not add one.

Every tool is available immediately. The canvas fills the space left by the tool bin, top bar, and material tray. Save downloads a PNG.

## Painting and playing

- Brushes & pens: marker, biro, calligraphy, textured poster paint, and watercolour. Open **Classic brushes** for a one-pixel pencil, classic brush, oil brush, crayon and natural pencil. Sizes run from 1 to 96 pixels.
- Spray: fine mist, splatter, or paper confetti. Pick Rainbow for multicoloured confetti.
- Smudge: drag to push wet paint with a smooth, feathered edge. Size controls the radius; Strength controls the push.
- Shapes: lines, rectangles, circles, polylines and smooth splines. **More shapes & fill** adds ovals, rounded rectangles, polygons, triangles, diamonds, pentagons, hexagons, stars, hearts, lightning, arrows and speech/thought bubbles. Choose brush or solid outlines, and primary/secondary colour fills. Hold Shift to constrain proportions or snap lines to 45° angles. Tap path points, then Finish path or Enter; Polygon closes automatically.
- Select: rectangle, lasso, or a connected-colour wand. Drag a piece or its corner handles to move or resize it; Shift keeps proportions. **More edits & transforms** provides select all, invert selection, delete, flip, rotate and crop. Transparent white paper removes white pixels when placing a piece. Copy also writes a PNG to the system clipboard when the browser allows it; the session clipboard remains available as a fallback.
- Text: choose a font, size, alignment, bold, italic, underline, strike-through and transparent or opaque background. Tap the paper to position it, then Place text. The result becomes a selection that can be resized or rotated. Ctrl+Enter also places text.
- Pick colour: sample the visible picture, including other layers. Right-click samples the second colour; right-click while drawing uses it. The colour wheel also accepts exact hex and RGB values.
- Symmetry: vertical, horizontal, 4, 6, 8, 10 or 12 ways.
- Stamps: 131 pictures across eight illustrated categories, with size, turn and flip controls.
- Spiro: move the outer ring, resize using the yellow handle or Ring size slider, and choose gears. Opening it leaves paper colours unchanged.
- Neon and Glitter: choose a colour first, then the special ink. Glitter is stationary metallic pigment; Neon has a coloured halo and a bright centre.

## Editing toolbox

The **More** button opens four drawers within the existing layout:

- **File:** new/open/insert images, paste screenshots, redo, print, and save as PNG, JPEG, WebP, BMP, GIF or TIFF. Drag files onto the paper to insert them. Save/open `.retropaint` projects to keep layers and animated ink.
- **Image:** crop, resize in pixels or percentages, change paper size without scaling artwork, rotate by any angle, flip, skew, and invert colours. Tick **Transform the selection** to edit a piece instead of the whole image. Turn off smooth resizing for pixel art. Edge background removal clears the region connected to the top-left corner; adjust bucket/wand tolerance for flat-colour backgrounds.
- **Layers:** opens the same stack available from the **Layers** button beside the paper. Choose **New layer** for a clear sheet, tap a preview to paint on it, use the eye to show/hide it, and drag the dots to change which sheet sits on top. The selected sheet says **Painting here**. Live thumbnails show your animated ink. **Layer options** holds rename, opacity, duplicate, remove, move up/down and combine. On a phone the stack closes after adding or choosing a sheet. Press **L** to toggle it; arrow keys choose a sheet and Alt+↑/↓ reorder it. New layers erase to transparency. Hide Paper to export transparent artwork; JPEG and BMP flatten transparency onto white. Undo/redo restore layer edits and live ink; combining layers captures the current animation frame.
- **View:** fit, actual pixels, zoom/pan, pixel grid, rulers and full screen. Ctrl/Cmd+wheel zooms; Move paper or Space+drag pans. View changes never change saved image resolution.

Images are limited to 4096 × 4096 pixels, 16 layers and 64 million pixels across layers. GIF uses a 256-colour palette and binary transparency. TIFF import supports uncompressed 8-bit RGB/RGBA or greyscale. Projects and images stay in the browser; no server or account is required. Microsoft Paint's service/device-dependent generative AI features are not included.

Keyboard: Ctrl/Cmd+Z undoes; Y or Shift+Z redoes; A selects all; C/X/V copy, cut and paste; O opens an image; S saves a PNG; P prints. Delete removes a selection; Escape cancels; Enter places a floating selection or finishes a path. B/E/F/I/T/R choose brush, eraser, bucket, picker, text and selection. Selecting a new tool places a floating selection.

## Rendering checks

With the dev server running, open `/tests/painting.html` for browser canvas regression checks and a visual sample sheet. These also cover layers, redo, transforms, text, image codecs and project round-trips. `/tests/mobile.html?frame=390x844` (or `320x568`, `844x390`) checks phone layouts in a frame of the specified size. Add `&preview` for an interactive app preview at that size. Existing test pages remain excluded from the production build; no runner or CI workflow is added.
