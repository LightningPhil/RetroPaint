# RetroPaint

A tactile painting toy: chunky tools, live ink, symmetry, stamps, and a spirograph kit.

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

- Brushes & pens: marker, biro, calligraphy, textured poster paint, and watercolour.
- Spray: fine mist, splatter, or paper confetti. Pick Rainbow for multicoloured confetti.
- Smudge: drag to push wet paint with a smooth, feathered edge. Size controls the radius; Strength controls the push.
- Shapes: lines, rectangles, circles, polylines and smooth splines. Tap points, then Finish path or Enter. Tap the first point to close; Escape cancels.
- Select: choose rectangle or lasso, then drag the selected piece. Copy, Cut, Paste, Place and Cancel also have visible buttons. Transparent white paper removes white pixels when placing the piece. The clipboard belongs to this app session.
- Symmetry: vertical, horizontal, 4, 6, 8, 10 or 12 ways.
- Stamps: 131 pictures across eight illustrated categories, with size, turn and flip controls.
- Spiro: move the outer ring, resize using the yellow handle or Ring size slider, and choose gears. Opening it leaves paper colours unchanged.
- Neon and Glitter: choose a colour first, then the special ink. Glitter is stationary metallic pigment; Neon has a coloured halo and a bright centre.

Keyboard: Ctrl/Cmd+Z undoes; Ctrl/Cmd+C, X and V copy, cut and paste selections; Delete removes a selection; Escape cancels; Enter places a floating selection or finishes a path. Selecting a new tool places a floating selection.

## Rendering checks

With the dev server running, open `/tests/painting.html` for browser canvas regression checks and a visual sample sheet. These cover smudge resampling, falloff, selection transparency, cancel/undo, spline knots, symmetry, stationary glitter and Spiro resizing. The test page is excluded from the production build; no CI test workflow is added.
